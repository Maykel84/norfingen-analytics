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


def _fetch_revenue_cost_combined(
    group_by: list[str],
    granularity: str | None,
    date_range: tuple | None,
    filters: dict | None,
    company_scoped: bool,
) -> pd.DataFrame:
    """revenue + cost in one round trip (two CTEs, FULL OUTER JOINed in
    Postgres) instead of two separate queries + a pandas outer-merge —
    profiling showed each round trip to the Supabase pooler costs a flat
    ~180-210ms regardless of query shape, so profit/margin_pct (which
    always needed both) was paying that twice on every request.

    Only dims valid on the revenue side (company/location/segment/
    nace_name) can be a join key — cost_bucket has no revenue-side
    counterpart. That matches the old two-query path exactly: its
    pd.merge used `[k for k in join_keys if k in revenue_df.columns and
    k in cost_df.columns]`, which silently dropped cost_bucket the same
    way for the same reason (never present in revenue_df).
    """
    dims = [d for d in group_by if d in _REVENUE_DIM_COLUMNS]

    revenue_select = [f"{_REVENUE_DIM_COLUMNS[d]} AS {d}" for d in dims]
    revenue_group = [_REVENUE_DIM_COLUMNS[d] for d in dims]
    period_rev = _period_expr(granularity, "o.order_date")
    if period_rev:
        revenue_select.insert(0, f"{period_rev} AS period")
        revenue_group.insert(0, period_rev)
    revenue_select.append("SUM(ol.amount_excluding_vat_currency) AS revenue")
    revenue_select.append("COUNT(DISTINCT o.id) AS order_count")
    rev_where_sql, rev_where_params = _date_range_clause(date_range, "o.order_date")
    rev_filt_sql, rev_filt_params = _build_filters(filters, _REVENUE_DIM_COLUMNS)
    revenue_group_clause = f"GROUP BY {', '.join(revenue_group)}" if revenue_group else ""

    cost_select = [f"{_COST_DIM_COLUMNS[d]} AS {d}" for d in dims]
    cost_group = [_COST_DIM_COLUMNS[d] for d in dims]
    period_cost = _period_expr(granularity, "v.date")
    if period_cost:
        cost_select.insert(0, f"{period_cost} AS period")
        cost_group.insert(0, period_cost)
    cost_select.append("SUM(p.amount) AS cost")

    company_filter_keys = ("company", "location", "segment", "nace_name")
    has_company_filters = bool(filters) and any(filters.get(k) for k in company_filter_keys)
    needs_customer_join = company_scoped or any(d in company_filter_keys for d in dims) or has_company_filters
    cost_join_clause = "LEFT JOIN customers c ON c.id = p.customer_id" if needs_customer_join else ""
    customer_required = " AND p.customer_id IS NOT NULL" if needs_customer_join else ""

    cost_where_sql, cost_where_params = _date_range_clause(date_range, "v.date")
    cost_filt_sql, cost_filt_params = _build_filters(filters, _COST_DIM_COLUMNS)
    cost_group_clause = f"GROUP BY {', '.join(cost_group)}" if cost_group else ""

    # Plain "=" (not IS NOT DISTINCT FROM): Postgres only allows a FULL JOIN
    # on hash/merge-joinable conditions, which IS NOT DISTINCT FROM isn't
    # ("FULL JOIN is only supported with merge-joinable or hash-joinable
    # join conditions" — a real error hit while building this, not a
    # hypothetical). "=" also matches the old pandas pd.merge(how="outer")
    # behavior exactly: pandas doesn't match NaN-to-NaN on a merge key
    # either, so a NULL dim value (e.g. a customer with no city) wasn't
    # joining across revenue/cost before this change and still won't.
    join_keys = (["period"] if period_rev else []) + dims
    on_clause = " AND ".join(f"r.{k} = c.{k}" for k in join_keys) or "TRUE"
    key_select = ", ".join(f"COALESCE(r.{k}, c.{k}) AS {k}" for k in join_keys)
    outer_select = (f"{key_select}, " if key_select else "") + (
        "COALESCE(r.revenue, 0) AS revenue, COALESCE(r.order_count, 0) AS order_count, "
        "COALESCE(c.cost, 0) AS cost"
    )

    sql = f"""
        WITH revenue_cte AS (
            SELECT {', '.join(revenue_select)}
            FROM orders o
            JOIN order_lines ol ON ol.order_id = o.id
            JOIN customers c ON c.id = o.customer_id
            WHERE 1=1 {rev_where_sql} {rev_filt_sql}
            {revenue_group_clause}
        ),
        cost_cte AS (
            SELECT {', '.join(cost_select)}
            FROM postings p
            JOIN vouchers v ON v.id = p.voucher_id
            {cost_join_clause}
            WHERE p.account_number BETWEEN 4000 AND 7999 {customer_required} {cost_where_sql} {cost_filt_sql}
            {cost_group_clause}
        )
        SELECT {outer_select}
        FROM revenue_cte r
        FULL OUTER JOIN cost_cte c ON {on_clause}
    """
    # rev_*_params and cost_*_params share the same bind names (:date_start,
    # :filt_<dim>) for the same underlying values (same date_range/filters
    # apply to both sides) — merging them is safe, not a collision.
    params = {**rev_where_params, **rev_filt_params, **cost_where_params, **cost_filt_params}
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

    # Only fetch what this measure actually needs — profiling showed each
    # round trip to the Supabase pooler costs ~180-210ms regardless of query
    # complexity or row count (network latency dominates, not execution
    # time), so an unconditional second query here was pure waste on every
    # revenue/cost/order_count request, not just a minor inefficiency.
    if measure in ("revenue", "order_count"):
        return _fetch_revenue(group_by, granularity, date_range, filters)

    if measure == "cost":
        return _fetch_cost(group_by, granularity, date_range, filters, company_scoped)

    # profit / margin_pct: both are genuinely needed — one combined round
    # trip (see _fetch_revenue_cost_combined) instead of two + a pandas
    # outer-merge; the SQL-side FULL OUTER JOIN + COALESCE already leaves
    # revenue/cost with no NaNs, so this only adds profit/margin_pct.
    merged = _fetch_revenue_cost_combined(group_by, granularity, date_range, filters, company_scoped)
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


def get_partial_month_starts() -> list[dt.date]:
    """First day of every month v_pl_monthly flags `is_partial` (a month whose
    last day is later than the newest generated voucher/order date). Payroll
    and COGS are booked at month end, so such a month carries its revenue but
    not its costs — any profit/margin that includes it is inflated.

    The flag lives in the view so there is exactly one definition of "open
    month"; this app computes revenue/cost from the raw tables (same formulas
    as the view) and only borrows the flag."""
    df = run_query("SELECT month FROM v_pl_monthly WHERE is_partial ORDER BY month")
    return [dt.datetime.strptime(m, "%Y-%m").date() for m in df["month"]]


def _month_end(month_start: dt.date) -> dt.date:
    return (month_start.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)


def get_partial_months_in_range(date_range: tuple | None) -> list[dt.date]:
    """The open month(s) a (start, end) range overlaps; None = all time."""
    partial = get_partial_month_starts()
    if date_range is None:
        return partial
    start, end = date_range
    return [p for p in partial if p <= end and _month_end(p) >= start]


def exclude_partial_months(date_range: tuple | None) -> tuple | None:
    """Trim a (start, end) range so it stops at the last full month — the
    equivalent of `WHERE NOT is_partial` for aggregates computed from the raw
    tables. None (all time) becomes (first order date, last full month end).

    If the whole range sits inside the open month there is nothing to keep, so
    the range is returned unchanged (callers show a "month in progress" note
    instead of an empty, misleading zero)."""
    partial = get_partial_month_starts()
    if not partial:
        return date_range
    cutoff = partial[0] - dt.timedelta(days=1)
    start, end = date_range if date_range is not None else (get_date_bounds()[0], cutoff)
    if start > cutoff:
        return date_range
    return (start, min(end, cutoff))


def get_yearly_totals(year: int | None) -> dict:
    """Headline KPIs for the Overview landing page, optionally scoped to one
    year. Full months only (see exclude_partial_months): the open month has
    revenue but not yet its payroll/COGS, which would inflate profit/margin."""
    date_range = None
    if year is not None:
        date_range = (dt.date(year, 1, 1), dt.date(year, 12, 31))
    date_range = exclude_partial_months(date_range)
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
    """Full-history revenue/cost/profit by year, for the landing page trend
    chart. A yearly bucket is an aggregate, so the open month is left out of
    the latest year (same as the API's /pl/yearly)."""
    return get_measure(
        "profit", group_by=[], date_range=exclude_partial_months(None), granularity="year",
    )


def get_monthly_trend_for_year(year: int | None) -> pd.DataFrame:
    """Month-by-month series. Deliberately keeps the open month (callers mark
    it with get_partial_months_in_range) — a monthly chart is not an aggregate."""
    date_range = (dt.date(year, 1, 1), dt.date(year, 12, 31)) if year else None
    return get_measure("profit", group_by=[], date_range=date_range, granularity="month")


def get_city_density(date_range: tuple | None = None) -> pd.DataFrame:
    """Company count + the actual company names per city, for the Overview
    coverage map (size/color = count, hover = names, not just the number).

    date_range=None (the "All years" default) counts every customer ever
    onboarded, matching the map's original full-history behavior. A
    (start, end) tuple restricts to customers active during that range —
    onboarded on/before it ends and not churned before it starts — the same
    "active in year" definition get_client_summary() uses, so the year
    switcher means the same thing on every page that respects it.
    """
    where_sql, params = "", {}
    if date_range is not None:
        where_sql = """
            AND (onboarding_date IS NULL OR onboarding_date <= :range_end)
            AND (churn_date IS NULL OR churn_date >= :range_start)
        """
        params = {"range_start": date_range[0], "range_end": date_range[1]}
    sql = f"""
        SELECT city, COUNT(*) AS company_count, STRING_AGG(name, ', ' ORDER BY name) AS company_names
        FROM customers
        WHERE city IS NOT NULL {where_sql}
        GROUP BY city
    """
    return run_query(sql, params)


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


# employments.payroll_tax_zone is ZONE_1 for every employee in this DB —
# Norway's official employer's National Insurance contribution
# ("arbeidsgiveravgift") rate for Zone 1 is 14.1%. Not broken out anywhere
# in postings (which don't split labor cost per employee), so it's applied
# as a flat multiplier here rather than sourced from a per-posting amount.
EMPLOYER_COST_MULTIPLIER = 1.141


def get_payroll_by_employee() -> pd.DataFrame:
    """Gross annual pay per employee per year, YoY growth, and estimated
    employer cost (gross x EMPLOYER_COST_MULTIPLIER).

    Named per-employee data, shown only because the user explicitly asked
    for a named salary breakdown (confirmed 2026-09-21) — unlike absence
    data, which stays department-level by default. Ignores the global year
    filter: a year-over-year growth view is inherently multi-year.
    """
    sql = """
        SELECT
            e.id AS employee_id,
            e.first_name || ' ' || e.last_name AS employee,
            d.name AS department,
            EXTRACT(YEAR FROM p.date)::int AS year,
            COUNT(DISTINCT EXTRACT(MONTH FROM p.date)) AS months_paid,
            SUM(p.amount) AS gross_annual
        FROM payslips p
        JOIN employees e ON e.id = p.employee_id
        LEFT JOIN departments d ON d.id = e.department_id
        GROUP BY e.id, employee, d.name, year
        ORDER BY e.id, year
    """
    df = run_query(sql)
    if df.empty:
        return df
    df = df.sort_values(["employee_id", "year"])
    # A year with fewer than 12 paid months (the current, still-running year)
    # would show as a fake pay cut against a full prior year — pct_change
    # skips it by comparing only full years.
    df["is_full_year"] = df["months_paid"] >= 12
    full = df[df["is_full_year"]].copy()
    full["yoy_growth_pct"] = full.groupby("employee_id")["gross_annual"].pct_change() * 100
    df = df.merge(full[["employee_id", "year", "yoy_growth_pct"]], on=["employee_id", "year"], how="left")
    df["employer_cost"] = df["gross_annual"] * EMPLOYER_COST_MULTIPLIER
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


# Invoice status is DERIVED, never read from orders.status (that column is the
# generator's modelled intent, not what happened). Same rule as the
# `Faktury_sprzedazy` export in the generator repo (export_queries.py):
#   WRITTEN_OFF  orders.write_off_voucher_id is set
#   PAID         a customer payment is booked in the bank (INCOMING)
#   OVERDUE      unpaid and the due date (a Saturday/Sunday moved to Monday)
#                is before "today"
#   OPEN         unpaid, not yet due
# "Today" is the newest generated date, NOT the clock: the generator only runs
# on weekdays, so the clock is routinely ahead of the data.
_INVOICE_STATUS_CTES = """
    data_today AS (
        SELECT GREATEST((SELECT MAX(date) FROM vouchers), (SELECT MAX(order_date) FROM orders)) AS d
    ),
    payments AS (
        SELECT order_id, MIN(date) AS paid_date
        FROM bank_transactions
        WHERE transaction_type = 'INCOMING' AND order_id IS NOT NULL
        GROUP BY order_id
    )
"""
_INVOICE_STATUS_CASE = """
    CASE
        WHEN o.write_off_voucher_id IS NOT NULL THEN 'WRITTEN_OFF'
        WHEN pay.paid_date IS NOT NULL THEN 'PAID'
        WHEN (o.invoice_date + o.invoices_due_in
              + CASE EXTRACT(ISODOW FROM o.invoice_date + o.invoices_due_in)
                    WHEN 6 THEN 2 WHEN 7 THEN 1 ELSE 0 END) < dtd.d THEN 'OVERDUE'
        ELSE 'OPEN'
    END
"""


def get_orders_invoice_payment_status(anchor_day: dt.date, days: int) -> pd.DataFrame:
    """Orders placed in the last `days` (ending at anchor_day), with whether
    each has been invoiced (invoice_date set and not later than the newest
    generated date) and its derived invoice_status (PAID / OPEN / OVERDUE /
    WRITTEN_OFF) — the Today page's invoice/payment follow-up view."""
    start = anchor_day - dt.timedelta(days=days - 1)
    sql = f"""
        WITH {_INVOICE_STATUS_CTES}
        SELECT
            o.id, o.order_date, c.name AS customer,
            SUM(ol.amount_excluding_vat_currency) AS amount,
            (o.invoice_date IS NOT NULL AND o.invoice_date <= dtd.d) AS invoiced,
            {_INVOICE_STATUS_CASE} AS invoice_status
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN order_lines ol ON ol.order_id = o.id
        CROSS JOIN data_today dtd
        LEFT JOIN payments pay ON pay.order_id = o.id
        WHERE o.order_date BETWEEN :start AND :end
        GROUP BY o.id, o.order_date, c.name, o.invoice_date, o.invoices_due_in,
                 o.write_off_voucher_id, pay.paid_date, dtd.d
        ORDER BY o.order_date DESC, o.id DESC
    """
    return run_query(sql, {"start": start, "end": anchor_day})


def get_receivables(year: int | None = None) -> pd.DataFrame:
    """One row per invoiced order (invoice_date not later than the newest
    generated date) with its derived status — the base for the Receivables
    page, which aggregates it in pandas (≈2k rows; one round trip).

    amount is GROSS (incl. VAT): that is what the customer owes and what a
    write-off removes. due_date is the contractual date moved off a weekend
    (same rule as the OVERDUE test); days_past_due is measured from it to the
    newest generated date (negative = not yet due). paid_late: paid more than
    7 days after the unadjusted due date (the generator's definition)."""
    year_clause = "AND EXTRACT(YEAR FROM o.invoice_date) = :year" if year is not None else ""
    sql = f"""
        WITH {_INVOICE_STATUS_CTES},
        due AS (
            SELECT o.id AS order_id,
                   o.invoice_date + o.invoices_due_in AS raw_due,
                   o.invoice_date + o.invoices_due_in
                     + CASE EXTRACT(ISODOW FROM o.invoice_date + o.invoices_due_in)
                           WHEN 6 THEN 2 WHEN 7 THEN 1 ELSE 0 END AS due_date
            FROM orders o
        )
        SELECT o.id AS order_id, c.name AS customer, o.invoice_date,
               due.due_date, pay.paid_date,
               SUM(ol.amount_currency) AS amount,
               {_INVOICE_STATUS_CASE} AS invoice_status,
               (dtd.d - due.due_date) AS days_past_due,
               COALESCE(pay.paid_date > due.raw_due + 7, FALSE) AS paid_late
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN order_lines ol ON ol.order_id = o.id
        JOIN due ON due.order_id = o.id
        CROSS JOIN data_today dtd
        LEFT JOIN payments pay ON pay.order_id = o.id
        WHERE o.invoice_date IS NOT NULL AND o.invoice_date <= dtd.d {year_clause}
        GROUP BY o.id, c.name, o.invoice_date, due.due_date, due.raw_due, pay.paid_date,
                 o.invoices_due_in, o.write_off_voucher_id, dtd.d
        ORDER BY o.invoice_date, o.id
    """
    df = run_query(sql, {"year": year} if year is not None else None)
    for col in ("invoice_date", "due_date", "paid_date"):
        df[col] = pd.to_datetime(df[col])
    df["amount"] = df["amount"].astype(float)
    df["days_past_due"] = pd.to_numeric(df["days_past_due"].map(lambda d: getattr(d, "days", d)))
    df["paid_late"] = df["paid_late"].astype(bool)
    return df


def get_write_offs_by_month(year: int | None = None) -> pd.DataFrame:
    """Receivable write-offs (account 7830 "Tap på krav") per voucher month.
    postings.amount is debit-positive, so a write-off is a positive number."""
    year_clause = "AND EXTRACT(YEAR FROM v.date) = :year" if year is not None else ""
    sql = f"""
        SELECT DATE_TRUNC('month', v.date) AS period, SUM(p.amount) AS written_off
        FROM vouchers v JOIN postings p ON p.voucher_id = v.id
        WHERE p.account_number = 7830 {year_clause}
        GROUP BY 1 ORDER BY 1
    """
    df = run_query(sql, {"year": year} if year is not None else None)
    df["period"] = _to_naive_datetime(df["period"])
    df["written_off"] = df["written_off"].astype(float)
    return df


# --- liquidity & financing (accounts 1910 bank, 2000/2290 financing, 8150 interest, 2700/2710/2740 VAT) ----
# postings.amount is debit-positive / credit-negative (verified: 1910 nets to a
# positive cash balance, 2000/2290/2740 to negative = credit balances).
# Liabilities and equity are therefore shown as `-amount` to read as positive.

def get_bank_balance_daily() -> pd.DataFrame:
    """Cumulative bank (1910) balance at the end of every day that has a
    posting, over the whole history — callers slice it by period so that the
    running balance is never re-based by a year filter."""
    sql = """
        SELECT v.date AS day, SUM(p.amount) AS movement
        FROM vouchers v JOIN postings p ON p.voucher_id = v.id
        WHERE p.account_number = 1910
        GROUP BY v.date ORDER BY v.date
    """
    df = run_query(sql)
    df["day"] = pd.to_datetime(df["day"])
    df["balance"] = df["movement"].astype(float).cumsum()
    return df[["day", "balance"]]


def get_owner_loan_monthly() -> pd.DataFrame:
    """Per month: principal repaid (debits on 2290), interest (8150) and the
    principal still outstanding at month end (credit balance on 2290, shown
    positive). Months run continuously from the drawdown to the last month
    with a loan posting, so the outstanding balance steps down cleanly."""
    sql = """
        SELECT DATE_TRUNC('month', v.date) AS period,
               SUM(p.amount) FILTER (WHERE p.account_number = 2290) AS principal_net,
               SUM(p.amount) FILTER (WHERE p.account_number = 2290 AND p.amount > 0) AS principal_repaid,
               SUM(p.amount) FILTER (WHERE p.account_number = 8150) AS interest
        FROM vouchers v JOIN postings p ON p.voucher_id = v.id
        WHERE p.account_number IN (2290, 8150)
        GROUP BY 1 ORDER BY 1
    """
    df = run_query(sql)
    df["period"] = _to_naive_datetime(df["period"])
    df = df.set_index("period").astype(float).fillna(0.0)
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="MS"), fill_value=0.0)
    df["outstanding"] = (-df["principal_net"].cumsum()).round(2).abs()  # abs: kills -0.00 float dust
    df.index.name = "period"
    return df.reset_index()[["period", "principal_repaid", "interest", "outstanding"]]


def get_financing_structure() -> dict:
    """Initial financing: share capital (2000) vs owner-loan drawdown (credits
    on 2290)."""
    sql = """
        SELECT -SUM(p.amount) FILTER (WHERE p.account_number = 2000) AS share_capital,
               -SUM(p.amount) FILTER (WHERE p.account_number = 2290 AND p.amount < 0) AS owner_loan
        FROM postings p WHERE p.account_number IN (2000, 2290)
    """
    row = run_query(sql).iloc[0]
    return {"share_capital": float(row["share_capital"] or 0), "owner_loan": float(row["owner_loan"] or 0)}


def get_vat_monthly() -> pd.DataFrame:
    """Output VAT (2700, credits) vs input VAT (2710, debits) per month.
    The two-monthly settlement vouchers clear both accounts into 2740, so they
    are excluded — otherwise every term-end month would net to ~0."""
    sql = """
        SELECT DATE_TRUNC('month', v.date) AS period,
               -SUM(p.amount) FILTER (WHERE p.account_number = 2700) AS output_vat,
               SUM(p.amount) FILTER (WHERE p.account_number = 2710) AS input_vat
        FROM vouchers v JOIN postings p ON p.voucher_id = v.id
        WHERE p.account_number IN (2700, 2710)
          AND v.id NOT IN (SELECT voucher_id FROM vat_settlements)
        GROUP BY 1 ORDER BY 1
    """
    df = run_query(sql)
    df["period"] = _to_naive_datetime(df["period"])
    for col in ("output_vat", "input_vat"):
        df[col] = df[col].astype(float).fillna(0.0)
    return df


def get_vat_settlements() -> pd.DataFrame:
    """Two-monthly VAT returns. balance = output - input: > 0 is paid to the
    tax authority (a credit on 2740 until the bank payment), < 0 is refunded."""
    sql = """
        SELECT vs.period_year || '-T' || vs.term AS term, vs.period_start, vs.period_end,
               vs.output_vat, vs.input_vat, vs.balance, vs.payment_date, vs.status
        FROM vat_settlements vs ORDER BY vs.period_end
    """
    df = run_query(sql)
    for col in ("period_start", "period_end", "payment_date"):
        df[col] = pd.to_datetime(df[col])
    for col in ("output_vat", "input_vat", "balance"):
        df[col] = df[col].astype(float)
    return df


def get_cogs_payables() -> pd.DataFrame:
    """COGS pass-through liabilities (accounts 4291/4292), one row per monthly
    accrual: net, VAT and gross amounts, due date, status and the bank payment
    date (NULL while unpaid)."""
    sql = """
        SELECT cp.id AS payable_id, cp.accrual_date, cp.payment_due_date, s.name AS supplier,
               cp.account_number, cp.description,
               cp.amount_excluding_vat_currency AS amount_net, cp.vat_amount_currency AS vat_amount,
               cp.amount_currency AS amount_gross, cp.status, b.date AS paid_date
        FROM cogs_payables cp
        JOIN suppliers s ON s.id = cp.supplier_id
        LEFT JOIN bank_transactions b ON b.cogs_payable_id = cp.id AND b.transaction_type = 'OUTGOING'
        ORDER BY cp.accrual_date DESC, cp.id DESC
    """
    df = run_query(sql)
    for col in ("accrual_date", "payment_due_date", "paid_date"):
        df[col] = pd.to_datetime(df[col])
    for col in ("amount_net", "vat_amount", "amount_gross"):
        df[col] = df[col].astype(float)
    return df


# --- profitability (step D) -------------------------------------------------
# Cost postings carry no customer_id (0% tagged), so per-customer cost is a
# MODEL, not a ledger fact:
#   * direct labor  = billable hours on the customer's projects x the employee's
#     loaded cost per hour. The month's ledger labor (accounts 5000-5999) is
#     split over employees by their share of that month's payslips, then divided
#     by the employee's billable+internal hours — so the allocation always ties
#     back to the ledger and never invents salary data.
#   * COGS (4291/4292 pass-through) = allocated pro rata to revenue: monthly COGS
#     tracks no single product (checked), so there is nothing finer to key on.
# Not allocated: equipment purchases (4290), operating costs, and non-billable
# (internal) hours — the result is a contribution margin, not a net margin.

def _full_month_range(year: int | None) -> tuple[dt.date, dt.date]:
    start = dt.date(year, 1, 1) if year else get_date_bounds()[0]
    end = dt.date(year, 12, 31) if year else get_date_bounds()[1]
    return exclude_partial_months((start, end))


def get_customer_profitability(year: int | None = None) -> pd.DataFrame:
    """One row per customer for full months in the period: revenue, allocated
    COGS, direct labor (see the model note above), billable hours."""
    start, end = _full_month_range(year)
    sql = """
        WITH rev AS (
            SELECT o.customer_id, SUM(ol.amount_excluding_vat_currency) AS revenue
            FROM orders o JOIN order_lines ol ON ol.order_id = o.id
            WHERE o.order_date BETWEEN :start AND :end GROUP BY 1
        ),
        cogs AS (
            SELECT COALESCE(SUM(p.amount), 0) AS total
            FROM postings p JOIN vouchers v ON v.id = p.voucher_id
            WHERE p.account_number IN (4291, 4292) AND v.date BETWEEN :start AND :end
        ),
        labor_m AS (
            SELECT DATE_TRUNC('month', v.date) AS m, SUM(p.amount) AS l
            FROM postings p JOIN vouchers v ON v.id = p.voucher_id
            WHERE p.account_number BETWEEN 5000 AND 5999 AND v.date BETWEEN :start AND :end GROUP BY 1
        ),
        pay AS (
            SELECT employee_id, DATE_TRUNC('month', date) AS m, SUM(amount) AS a
            FROM payslips WHERE date BETWEEN :start AND :end GROUP BY 1, 2
        ),
        paytot AS (SELECT m, SUM(a) AS t FROM pay GROUP BY m),
        hrs AS (
            SELECT employee_id, DATE_TRUNC('month', date) AS m, SUM(hours) AS tot
            FROM hour_entries
            WHERE activity_type IN ('BILLABLE', 'INTERNAL') AND date BETWEEN :start AND :end GROUP BY 1, 2
        ),
        lab AS (
            SELECT pr.customer_id,
                   SUM(he.hours * lm.l * pay.a / paytot.t / NULLIF(hrs.tot, 0)) AS labor_cost,
                   SUM(he.hours) AS billable_hours
            FROM hour_entries he
            JOIN projects pr ON pr.id = he.project_id
            JOIN pay ON pay.employee_id = he.employee_id AND pay.m = DATE_TRUNC('month', he.date)
            JOIN paytot ON paytot.m = pay.m
            JOIN labor_m lm ON lm.m = pay.m
            JOIN hrs ON hrs.employee_id = he.employee_id AND hrs.m = pay.m
            WHERE he.activity_type = 'BILLABLE' AND he.date BETWEEN :start AND :end
            GROUP BY 1
        )
        SELECT c.name AS customer, COALESCE(rev.revenue, 0) AS revenue, COALESCE(lab.labor_cost, 0) AS labor_cost,
               COALESCE(lab.billable_hours, 0) AS billable_hours, cogs.total AS cogs_total
        FROM customers c
        CROSS JOIN cogs
        LEFT JOIN rev ON rev.customer_id = c.id
        LEFT JOIN lab ON lab.customer_id = c.id
        WHERE rev.revenue IS NOT NULL OR lab.labor_cost IS NOT NULL
    """
    df = run_query(sql, {"start": start, "end": end})
    for col in ("revenue", "labor_cost", "billable_hours", "cogs_total"):
        df[col] = df[col].astype(float)
    total_rev = df["revenue"].sum()
    df["cogs_alloc"] = df["cogs_total"] * df["revenue"] / total_rev if total_rev else 0.0
    df = df.drop(columns="cogs_total")
    df["contribution"] = df["revenue"] - df["cogs_alloc"] - df["labor_cost"]
    df["contribution_pct"] = df["contribution"] / df["revenue"].where(df["revenue"] > 0) * 100
    df["revenue_per_hour"] = df["revenue"] / df["billable_hours"].where(df["billable_hours"] > 0)
    return df.sort_values("contribution", ascending=False).reset_index(drop=True)


def get_employee_utilization(year: int | None = None) -> pd.DataFrame:
    """Billable vs internal hours per employee (all employees, including those
    with no hours). Utilisation = billable / (billable + internal). Invoices
    are fixed monthly lines, not hours, so there is no "billed hours" figure
    per employee to compare against."""
    where_sql, params = ("AND EXTRACT(YEAR FROM he.date) = :year", {"year": year}) if year else ("", None)
    sql = f"""
        SELECT e.first_name || ' ' || e.last_name AS employee, COALESCE(d.name, 'Unassigned') AS department,
               COALESCE(SUM(he.hours) FILTER (WHERE he.activity_type = 'BILLABLE'), 0) AS billable_hours,
               COALESCE(SUM(he.hours) FILTER (WHERE he.activity_type = 'INTERNAL'), 0) AS internal_hours
        FROM employees e
        LEFT JOIN departments d ON d.id = e.department_id
        LEFT JOIN hour_entries he ON he.employee_id = e.id {where_sql}
        GROUP BY e.id, employee, d.name
        ORDER BY billable_hours DESC
    """
    df = run_query(sql, params)
    for col in ("billable_hours", "internal_hours"):
        df[col] = df[col].astype(float)
    total = df["billable_hours"] + df["internal_hours"]
    df["utilization_pct"] = df["billable_hours"] / total.where(total > 0) * 100
    return df


def get_cost_by_category_monthly() -> pd.DataFrame:
    """Monthly cost by category (ledger, debit-positive): pass-through COGS
    (4291/4292), equipment cash purchases (4290), labor (5xxx) and operating
    cost (6000-7999, including 7830 write-offs)."""
    sql = """
        SELECT DATE_TRUNC('month', v.date) AS period,
               SUM(p.amount) FILTER (WHERE p.account_number IN (4291, 4292)) AS cogs_passthrough,
               SUM(p.amount) FILTER (WHERE p.account_number = 4290) AS equipment,
               SUM(p.amount) FILTER (WHERE p.account_number BETWEEN 5000 AND 5999) AS labor,
               SUM(p.amount) FILTER (WHERE p.account_number BETWEEN 6000 AND 7999) AS operating
        FROM vouchers v JOIN postings p ON p.voucher_id = v.id
        WHERE p.account_number BETWEEN 4000 AND 7999
        GROUP BY 1 ORDER BY 1
    """
    df = run_query(sql)
    df["period"] = _to_naive_datetime(df["period"])
    cats = ["cogs_passthrough", "equipment", "labor", "operating"]
    df[cats] = df[cats].astype(float).fillna(0.0)
    return df
