"""Semantic layer query interface.

This is the only module that knows raw table/column names for facts and
measures. UI code calls get_measure() / get_companies() / get_date_bounds()
and never writes SQL itself.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from data.db import run_query
from semantic.schema import COST_ACCOUNT_RANGES

# --- dimension -> SQL column, per fact table -------------------------------

_REVENUE_DIM_COLUMNS = {
    "company": "c.name",
    "location": "c.city",
    "segment": "c.segment",
    "nace_name": "c.nace_name",
}

_COST_DIM_COLUMNS = {
    "company": "c.name",
    "location": "c.city",
    "segment": "c.segment",
    "nace_name": "c.nace_name",
    "cost_bucket": "cost_bucket",
}

_DATE_TRUNC = {
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}

_COST_BUCKET_CASE = """
    CASE
        WHEN p.account_number BETWEEN {cogs_lo} AND {cogs_hi} THEN 'cogs'
        WHEN p.account_number BETWEEN {labor_lo} AND {labor_hi} THEN 'labor_cost'
        WHEN p.account_number BETWEEN {opex_lo} AND {opex_hi} THEN 'operating_cost'
        ELSE 'other'
    END
""".format(
    cogs_lo=COST_ACCOUNT_RANGES["cogs"][0],
    cogs_hi=COST_ACCOUNT_RANGES["cogs"][1],
    labor_lo=COST_ACCOUNT_RANGES["labor_cost"][0],
    labor_hi=COST_ACCOUNT_RANGES["labor_cost"][1],
    opex_lo=COST_ACCOUNT_RANGES["operating_cost"][0],
    opex_hi=COST_ACCOUNT_RANGES["operating_cost"][1],
)


def _to_naive_datetime(series: pd.Series) -> pd.Series:
    """Postgres may return date_trunc() results as tz-aware or tz-naive
    depending on the query shape; normalize so revenue/cost frames always
    merge on a consistent dtype."""
    parsed = pd.to_datetime(series)
    if isinstance(parsed.dtype, pd.DatetimeTZDtype):
        parsed = parsed.dt.tz_localize(None)
    return parsed


def _period_expr(granularity: str | None, date_column: str) -> str | None:
    if not granularity:
        return None
    field = _DATE_TRUNC[granularity]
    return f"date_trunc('{field}', {date_column})"


def _build_filters(filters: dict | None, alias_map: dict) -> tuple[str, dict]:
    """filters: dict of dimension -> list of values. Returns (sql_clause, params)."""
    clauses = []
    params = {}
    if not filters:
        return "", params
    for dim, values in filters.items():
        if not values:
            continue
        column = alias_map.get(dim)
        if column is None:
            continue
        key = f"filt_{dim}"
        clauses.append(f"{column} = ANY(:{key})")
        params[key] = list(values)
    sql = (" AND " + " AND ".join(clauses)) if clauses else ""
    return sql, params


def _date_range_clause(date_range: tuple | None, date_column: str) -> tuple[str, dict]:
    if not date_range:
        return "", {}
    start, end = date_range
    return (
        f" AND {date_column} >= :date_start AND {date_column} <= :date_end",
        {"date_start": start, "date_end": end},
    )


def _fetch_revenue(
    group_by: list[str],
    granularity: str | None,
    date_range: tuple | None,
    filters: dict | None,
) -> pd.DataFrame:
    dims = [d for d in group_by if d in _REVENUE_DIM_COLUMNS]
    select_cols = [f"{_REVENUE_DIM_COLUMNS[d]} AS {d}" for d in dims]
    group_cols = [_REVENUE_DIM_COLUMNS[d] for d in dims]

    period = _period_expr(granularity, "o.order_date")
    if period:
        select_cols.insert(0, f"{period} AS period")
        group_cols.insert(0, period)

    select_cols.append("SUM(ol.amount_excluding_vat_currency) AS revenue")
    select_cols.append("COUNT(DISTINCT o.id) AS order_count")

    where_sql, where_params = _date_range_clause(date_range, "o.order_date")
    filt_sql, filt_params = _build_filters(filters, _REVENUE_DIM_COLUMNS)

    group_clause = f"GROUP BY {', '.join(group_cols)}" if group_cols else ""

    sql = f"""
        SELECT {', '.join(select_cols)}
        FROM orders o
        JOIN order_lines ol ON ol.order_id = o.id
        JOIN customers c ON c.id = o.customer_id
        WHERE 1=1 {where_sql} {filt_sql}
        {group_clause}
    """
    params = {**where_params, **filt_params}
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    return df


def _fetch_cost(
    group_by: list[str],
    granularity: str | None,
    date_range: tuple | None,
    filters: dict | None,
    company_scoped: bool,
) -> pd.DataFrame:
    dims = [d for d in group_by if d in _COST_DIM_COLUMNS]
    select_cols = []
    group_cols = []
    for d in dims:
        if d == "cost_bucket":
            select_cols.append(f"{_COST_BUCKET_CASE} AS cost_bucket")
            group_cols.append(_COST_BUCKET_CASE)
        else:
            col = _COST_DIM_COLUMNS[d]
            select_cols.append(f"{col} AS {d}")
            group_cols.append(col)

    period = _period_expr(granularity, "v.date")
    if period:
        select_cols.insert(0, f"{period} AS period")
        group_cols.insert(0, period)

    company_filter_keys = ("company", "location", "segment", "nace_name")
    has_company_filters = bool(filters) and any(filters.get(k) for k in company_filter_keys)
    needs_customer_join = (
        company_scoped
        or any(d in company_filter_keys for d in dims)
        or has_company_filters
    )

    select_cols.append("SUM(p.amount) AS cost")

    where_sql, where_params = _date_range_clause(date_range, "v.date")
    cost_filter_alias_map = {**_COST_DIM_COLUMNS, "cost_bucket": _COST_BUCKET_CASE}
    filt_sql, filt_params = _build_filters(filters, cost_filter_alias_map)

    join_clause = (
        "LEFT JOIN customers c ON c.id = p.customer_id" if needs_customer_join else ""
    )
    customer_required = " AND p.customer_id IS NOT NULL" if needs_customer_join else ""

    outer_select = ", ".join(select_cols)
    group_clause = f"GROUP BY {', '.join(group_cols)}" if group_cols else ""

    sql = f"""
        SELECT {outer_select}
        FROM postings p
        JOIN vouchers v ON v.id = p.voucher_id
        {join_clause}
        WHERE p.account_number BETWEEN 4000 AND 7999 {customer_required} {where_sql} {filt_sql}
        {group_clause}
    """
    params = {**where_params, **filt_params}
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    return df


def get_measure(
    measure: str,
    group_by: list[str] | None = None,
    date_range: tuple[dt.date, dt.date] | None = None,
    granularity: str | None = None,
    filters: dict | None = None,
) -> pd.DataFrame:
    """Return a DataFrame with the requested measure(s) aggregated by group_by dims.

    measure: one of "revenue", "cost", "profit", "margin_pct", "order_count"
    group_by: list of dimension names (see semantic.schema.DIMENSIONS)
    date_range: (start_date, end_date) inclusive
    granularity: one of semantic.schema.DATE_GRANULARITIES, or None for a single total
    filters: {dimension: [values]}
    """
    group_by = group_by or []
    company_scoped = any(d in ("company", "location", "segment", "nace_name") for d in group_by)

    join_keys = [d for d in group_by if d != "cost_bucket"]
    if granularity:
        join_keys = ["period"] + join_keys

    revenue_df = _fetch_revenue(group_by, granularity, date_range, filters)
    cost_df = _fetch_cost(group_by, granularity, date_range, filters, company_scoped)

    if measure in ("revenue", "order_count"):
        return revenue_df

    if measure == "cost":
        return cost_df

    # profit / margin_pct: merge revenue and cost on shared keys
    merge_keys = [k for k in join_keys if k in revenue_df.columns and k in cost_df.columns]
    if not merge_keys:
        rev_total = revenue_df["revenue"].sum() if not revenue_df.empty else 0.0
        cost_total = cost_df["cost"].sum() if not cost_df.empty else 0.0
        result = pd.DataFrame(
            {
                "revenue": [rev_total],
                "cost": [cost_total],
                "profit": [rev_total - cost_total],
                "margin_pct": [
                    (rev_total - cost_total) / rev_total * 100 if rev_total else 0.0
                ],
            }
        )
        return result

    merged = pd.merge(
        revenue_df,
        cost_df.groupby(merge_keys, as_index=False)["cost"].sum() if merge_keys else cost_df,
        on=merge_keys,
        how="outer",
    )
    merged["revenue"] = merged["revenue"].fillna(0.0)
    merged["cost"] = merged["cost"].fillna(0.0)
    merged["profit"] = merged["revenue"] - merged["cost"]
    merged["margin_pct"] = merged.apply(
        lambda r: (r["profit"] / r["revenue"] * 100) if r["revenue"] else 0.0, axis=1
    )
    return merged


def get_companies() -> pd.DataFrame:
    """Return the customer dimension table (id, name, city, segment,
    nace_name, plus onboarding/churn dates used to determine which
    customers were active in a given year)."""
    sql = """
        SELECT id, name, city, postal_code, segment, nace_name, nace_code,
               onboarding_date, churn_date
        FROM customers
        ORDER BY name
    """
    return run_query(sql)


def get_date_bounds() -> tuple[dt.date, dt.date]:
    sql = "SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM orders"
    df = run_query(sql)
    return df["min_date"].iloc[0], df["max_date"].iloc[0]


def get_available_years() -> list[int]:
    sql = "SELECT DISTINCT EXTRACT(YEAR FROM order_date)::int AS year FROM orders ORDER BY year"
    df = run_query(sql)
    return df["year"].tolist()


def get_yearly_totals(year: int | None) -> dict:
    """Headline KPIs for the Overview landing page, optionally scoped to one year."""
    date_range = None
    if year is not None:
        date_range = (dt.date(year, 1, 1), dt.date(year, 12, 31))
    totals = get_measure("profit", group_by=[], date_range=date_range, granularity=None)
    company_count_sql = """
        SELECT COUNT(DISTINCT o.customer_id) AS n
        FROM orders o
        WHERE 1=1 {date_filter}
    """
    if date_range:
        df = run_query(
            company_count_sql.format(date_filter="AND o.order_date BETWEEN :d1 AND :d2"),
            {"d1": date_range[0], "d2": date_range[1]},
        )
    else:
        df = run_query(company_count_sql.format(date_filter=""))
    company_count = int(df["n"].iloc[0]) if not df.empty else 0
    return {
        "revenue": float(totals["revenue"].iloc[0]) if not totals.empty else 0.0,
        "cost": float(totals["cost"].iloc[0]) if not totals.empty else 0.0,
        "profit": float(totals["profit"].iloc[0]) if not totals.empty else 0.0,
        "margin_pct": float(totals["margin_pct"].iloc[0]) if not totals.empty else 0.0,
        "company_count": company_count,
    }


def get_multi_year_trend() -> pd.DataFrame:
    """Full-history revenue/cost/profit by year, for the landing page trend chart."""
    return get_measure("profit", group_by=[], granularity="year")


def get_monthly_trend_for_year(year: int | None) -> pd.DataFrame:
    date_range = (dt.date(year, 1, 1), dt.date(year, 12, 31)) if year else None
    return get_measure("profit", group_by=[], date_range=date_range, granularity="month")


def get_city_density() -> pd.DataFrame:
    """Company count + the actual company names per city, for the Overview
    coverage map (size/color = count, hover = names, not just the number)."""
    sql = """
        SELECT city, COUNT(*) AS company_count, STRING_AGG(name, ', ' ORDER BY name) AS company_names
        FROM customers
        WHERE city IS NOT NULL
        GROUP BY city
    """
    return run_query(sql)


def get_client_summary(filters: dict | None = None, date_range: tuple | None = None) -> pd.DataFrame:
    """One row per customer (all 50, even those with zero orders): revenue/
    order_count, sector (=nace_name), and a derived size band (revenue
    tercile across all customers). date_range=None means all-time (lifetime);
    pass a (start, end) tuple to scope to a single year — e.g. the global
    year selector in the header.

    Deliberately excludes cost/profit/margin: cost postings (account range
    4000-7999) never carry a customer_id in this dataset — 0% tagged, not a
    partial-tagging gap — so cost cannot be attributed to an individual
    client by any method. Returning 0 kr here would misleadingly read as
    "this client costs nothing" rather than "not tracked at this level".
    See README's "Cost attribution" section.
    """
    companies = get_companies()
    if date_range is not None:
        # "Active in year": onboarded on/before the range ends, and not
        # churned before the range starts — excludes clients who didn't
        # exist yet or had already left, rather than showing all 50
        # customers-as-of-today regardless of which year is selected.
        range_start, range_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        onboarding = pd.to_datetime(companies["onboarding_date"])
        churn = pd.to_datetime(companies["churn_date"])
        onboarded_mask = onboarding.isna() | (onboarding <= range_end)
        not_churned_mask = churn.isna() | (churn >= range_start)
        companies = companies[onboarded_mask & not_churned_mask]
    revenue_df = _fetch_revenue(["company"], None, date_range, filters)

    merged = companies.merge(revenue_df, left_on="name", right_on="company", how="left")
    merged["revenue"] = merged["revenue"].fillna(0.0)
    merged["order_count"] = merged["order_count"].fillna(0).astype(int)

    if not merged.empty:
        try:
            merged["size_band"] = pd.qcut(
                merged["revenue"].rank(method="first"), 3, labels=["Small", "Medium", "Large"]
            )
        except ValueError:
            merged["size_band"] = "Medium"
    else:
        merged["size_band"] = pd.Series(dtype=str)

    merged = merged.rename(columns={"nace_name": "sector"})
    return merged


def get_client_history(
    company_name: str, granularity: str | None, date_range: tuple | None = None
) -> pd.DataFrame:
    """Revenue history for a single client, scoped by period. Cost/profit are
    intentionally excluded — see get_client_summary()'s docstring."""
    filters = {"company": [company_name]}
    return _fetch_revenue([], granularity, date_range, filters)


# --- Operations: previously-unused tables (products, suppliers, staffing,
# hours, GL accounts, payroll, bank transactions, customer lifecycle) ------


def get_product_revenue(date_range: tuple | None = None) -> pd.DataFrame:
    """Revenue/order-count by product and its parent service. Fully
    attributable — order_lines.product_id is 100% populated, so this carries
    none of the per-client cost-attribution caveat (it's revenue, not cost)."""
    where_sql, params = _date_range_clause(date_range, "o.order_date")
    sql = f"""
        SELECT
            p.name AS product,
            s.name AS service,
            s.billing_model,
            SUM(ol.amount_excluding_vat_currency) AS revenue,
            COUNT(DISTINCT o.id) AS order_count
        FROM order_lines ol
        JOIN orders o ON o.id = ol.order_id
        JOIN products p ON p.id = ol.product_id
        LEFT JOIN services s ON s.code = p.service_code
        WHERE 1=1 {where_sql}
        GROUP BY p.name, s.name, s.billing_model
        ORDER BY revenue DESC
    """
    return run_query(sql, params)


def get_supplier_spend(date_range: tuple | None = None) -> pd.DataFrame:
    """Spend by supplier, from supplier_invoices — the cost-side complement
    to the Clients tab (cost-to-supplier is fully attributable, unlike
    cost-to-customer)."""
    where_sql, params = _date_range_clause(date_range, "si.invoice_date")
    sql = f"""
        SELECT
            s.name AS supplier,
            COUNT(*) AS invoice_count,
            SUM(si.amount_excluding_vat_currency) AS spend,
            SUM(CASE WHEN si.status = 'UNPAID' THEN si.amount_excluding_vat_currency ELSE 0 END) AS unpaid_amount
        FROM supplier_invoices si
        JOIN suppliers s ON s.id = si.supplier_id
        WHERE 1=1 {where_sql}
        GROUP BY s.name
        ORDER BY spend DESC
    """
    return run_query(sql, params)


def get_staffing_summary() -> pd.DataFrame:
    """Current headcount by department and employment type (current =
    employments with no end_date)."""
    sql = """
        SELECT
            d.name AS department,
            emp.employment_type,
            COUNT(*) AS headcount
        FROM employments emp
        JOIN employees e ON e.id = emp.employee_id
        LEFT JOIN departments d ON d.id = e.department_id
        WHERE emp.end_date IS NULL
        GROUP BY d.name, emp.employment_type
        ORDER BY headcount DESC
    """
    return run_query(sql)



# hour_entries.activity_type as of the latest schema check: BILLABLE and
# INTERNAL carry real hours; VACATION/SICK/PARENTAL_LEAVE/WELFARE_LEAVE are
# day-markers with hours always 0 (absence is logged as a day entry, not a
# duration) — verified directly against the live DB, not assumed. Mixing
# the two in one hours-summed chart would draw the absence types as flat
# zero lines, so they're tracked separately as day counts (get_absence_trend).
HOUR_BASED_ACTIVITY_TYPES = ("BILLABLE", "INTERNAL")
ABSENCE_ACTIVITY_TYPES = ("VACATION", "SICK", "PARENTAL_LEAVE", "WELFARE_LEAVE")


def get_utilization_trend(granularity: str = "month", date_range: tuple | None = None) -> pd.DataFrame:
    """Hours by activity type (billable/internal only — see module note
    above) over time — the richest previously-unused table (54k+ rows)."""
    period = _period_expr(granularity, "he.date")
    where_sql, params = _date_range_clause(date_range, "he.date")
    sql = f"""
        SELECT
            {period} AS period,
            he.activity_type,
            SUM(he.hours) AS hours
        FROM hour_entries he
        WHERE he.activity_type = ANY(:hour_types) {where_sql}
        GROUP BY {period}, he.activity_type
        ORDER BY period
    """
    params = {**params, "hour_types": list(HOUR_BASED_ACTIVITY_TYPES)}
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    return df


def get_absence_trend(granularity: str = "year", date_range: tuple | None = None) -> pd.DataFrame:
    """Absence *days* (not hours — see module note above) by type over time,
    company-wide. Company-level aggregate by default — see
    get_absence_by_department()'s docstring for why department (but not
    employee) breakdown is also offered. Defaults to yearly granularity:
    monthly absence counts are naturally bursty (vacation concentrated in
    a handful of months) and read as noise at that resolution."""
    period = _period_expr(granularity, "he.date")
    where_sql, params = _date_range_clause(date_range, "he.date")
    sql = f"""
        SELECT
            {period} AS period,
            he.activity_type,
            COUNT(*) AS days
        FROM hour_entries he
        WHERE he.activity_type = ANY(:absence_types) {where_sql}
        GROUP BY {period}, he.activity_type
        ORDER BY period
    """
    params = {**params, "absence_types": list(ABSENCE_ACTIVITY_TYPES)}
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    return df


def get_absence_by_department(date_range: tuple | None = None) -> pd.DataFrame:
    """Absence days by department and type — answers "where" (which part of
    the org) and "how" (which kind of absence). Department is an aggregate
    of several employees, not personally identifying, so this stays within
    the same privacy default as company-wide totals; a per-employee version
    would need explicit sign-off first (see module note above)."""
    where_sql, params = _date_range_clause(date_range, "he.date")
    sql = f"""
        SELECT
            COALESCE(d.name, 'Unassigned') AS department,
            he.activity_type,
            COUNT(*) AS days
        FROM hour_entries he
        JOIN employees e ON e.id = he.employee_id
        LEFT JOIN departments d ON d.id = e.department_id
        WHERE he.activity_type = ANY(:absence_types) {where_sql}
        GROUP BY d.name, he.activity_type
        ORDER BY days DESC
    """
    params = {**params, "absence_types": list(ABSENCE_ACTIVITY_TYPES)}
    return run_query(sql, params)


def get_cost_by_account(date_range: tuple | None = None) -> pd.DataFrame:
    """Whole-company cost broken down by individual GL account (finer than
    the 3-bucket cogs/labor/opex split) — no per-customer attribution
    involved, so no caveat applies."""
    where_sql, params = _date_range_clause(date_range, "v.date")
    sql = f"""
        SELECT
            a.name AS account,
            {_COST_BUCKET_CASE} AS cost_bucket,
            SUM(p.amount) AS cost
        FROM postings p
        JOIN vouchers v ON v.id = p.voucher_id
        JOIN accounts a ON a.number = p.account_number
        WHERE p.account_number BETWEEN 4000 AND 7999 {where_sql}
        GROUP BY a.name, {_COST_BUCKET_CASE}
        ORDER BY cost DESC
    """
    return run_query(sql, params)


def get_payroll_trend(granularity: str = "month", date_range: tuple | None = None) -> pd.DataFrame:
    """Total payroll disbursed per period, from payslips."""
    period = _period_expr(granularity, "date")
    where_sql, params = _date_range_clause(date_range, "date")
    sql = f"""
        SELECT {period} AS period, SUM(amount) AS payroll
        FROM payslips
        WHERE 1=1 {where_sql}
        GROUP BY {period}
        ORDER BY period
    """
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    return df


def get_cash_flow_trend(granularity: str = "month", date_range: tuple | None = None) -> pd.DataFrame:
    """Incoming vs. outgoing bank cash flow per period."""
    period = _period_expr(granularity, "date")
    where_sql, params = _date_range_clause(date_range, "date")
    sql = f"""
        SELECT
            {period} AS period,
            SUM(CASE WHEN transaction_type = 'INCOMING' THEN amount ELSE 0 END) AS incoming,
            SUM(CASE WHEN transaction_type = 'OUTGOING' THEN amount ELSE 0 END) AS outgoing
        FROM bank_transactions
        WHERE 1=1 {where_sql}
        GROUP BY {period}
        ORDER BY period
    """
    df = run_query(sql, params)
    if "period" in df.columns:
        df["period"] = _to_naive_datetime(df["period"])
    df["net"] = df["incoming"] - df["outgoing"]
    return df


def get_customer_lifecycle_events(date_range: tuple | None = None) -> pd.DataFrame:
    """One row per customer: when they were acquired (onboarding_date) and
    their current status (active / churned), derived from
    customers.onboarding_date/churn_date (the same fields the NorFinGen
    API's /events endpoint exposes; computed here directly from Postgres
    rather than calling that external API).

    Previously this was a flat onboarded/churned *event* log — but 50/50
    customers have an onboarding_date and only 3/50 have ever churned, so
    that log was almost entirely "onboarded" rows and never actually
    answered "is this client active?" A status table does. date_range
    filters to customers onboarded on/before the range (i.e. who existed
    yet) — churn status is always their current status, not scoped to the
    period, since "active as of now" is what the label means either way.
    """
    where_onboard, params = _date_range_clause(date_range, "onboarding_date")
    sql = f"""
        SELECT
            name, segment, onboarding_date, churn_date,
            CASE WHEN churn_date IS NULL THEN 'active' ELSE 'churned' END AS status
        FROM customers
        WHERE onboarding_date IS NOT NULL {where_onboard}
        ORDER BY onboarding_date DESC
    """
    return run_query(sql, params)


def get_client_projects(company_name: str) -> pd.DataFrame:
    """Projects belonging to a single client."""
    sql = """
        SELECT pr.number, pr.name, pr.status, pr.start_date, pr.end_date
        FROM projects pr
        JOIN customers c ON c.id = pr.customer_id
        WHERE c.name = :name
        ORDER BY pr.start_date DESC
    """
    return run_query(sql, {"name": company_name})


def get_most_recent_activity_date(year: int | None = None) -> dt.date | None:
    """Latest date with any order activity — for the Today page's fallback
    when the live calendar date has no data yet, or (with year set) the
    "most recent day in that year" used when the global year selector
    points at a past year rather than the live calendar."""
    if year is not None:
        sql = "SELECT MAX(order_date) AS d FROM orders WHERE EXTRACT(YEAR FROM order_date) = :year"
        df = run_query(sql, {"year": year})
    else:
        sql = "SELECT MAX(order_date) AS d FROM orders"
        df = run_query(sql)
    return df["d"].iloc[0] if not df.empty else None


def get_daily_snapshot(day: dt.date) -> dict:
    """Today page: what happened on a specific day."""
    orders_sql = """
        SELECT o.id, o.order_date, c.name AS customer, SUM(ol.amount_excluding_vat_currency) AS amount
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN order_lines ol ON ol.order_id = o.id
        WHERE o.order_date = :day
        GROUP BY o.id, o.order_date, c.name
        ORDER BY amount DESC
    """
    orders_df = run_query(orders_sql, {"day": day})
    return {
        "orders": orders_df,
        "revenue": float(orders_df["amount"].sum()) if not orders_df.empty else 0.0,
        "order_count": len(orders_df),
        "client_count": orders_df["customer"].nunique() if not orders_df.empty else 0,
    }


def get_orders_window_stats(anchor_day: dt.date, days: int) -> dict:
    """Rolling-window order count/revenue ending at anchor_day (inclusive),
    e.g. the Today page's "last 3 days" / "last 7 days" tiles."""
    start = anchor_day - dt.timedelta(days=days - 1)
    sql = """
        SELECT COUNT(DISTINCT o.id) AS order_count, COALESCE(SUM(ol.amount_excluding_vat_currency), 0) AS revenue
        FROM orders o
        JOIN order_lines ol ON ol.order_id = o.id
        WHERE o.order_date BETWEEN :start AND :end
    """
    df = run_query(sql, {"start": start, "end": anchor_day})
    return {"order_count": int(df["order_count"].iloc[0]), "revenue": float(df["revenue"].iloc[0])}


def get_orders_invoice_payment_status(anchor_day: dt.date, days: int) -> pd.DataFrame:
    """Orders placed in the last `days` (ending at anchor_day), with whether
    each has been invoiced (orders.invoice_date set and not in the future)
    and whether a matching customer payment has landed in bank_transactions
    — the Today page's invoice/payment follow-up view."""
    start = anchor_day - dt.timedelta(days=days - 1)
    sql = """
        SELECT
            o.id, o.order_date, c.name AS customer,
            SUM(ol.amount_excluding_vat_currency) AS amount,
            (o.invoice_date IS NOT NULL AND o.invoice_date <= CURRENT_DATE) AS invoiced,
            EXISTS (
                SELECT 1 FROM bank_transactions bt
                WHERE bt.order_id = o.id AND bt.transaction_type = 'INCOMING'
            ) AS paid
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN order_lines ol ON ol.order_id = o.id
        WHERE o.order_date BETWEEN :start AND :end
        GROUP BY o.id, o.order_date, c.name, o.invoice_date
        ORDER BY o.order_date DESC
    """
    return run_query(sql, {"start": start, "end": anchor_day})
