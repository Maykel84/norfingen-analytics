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
    """Return the customer dimension table (id, name, city, segment, nace_name)."""
    sql = """
        SELECT id, name, city, postal_code, segment, nace_name, nace_code
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
    """Company count per city, for the Overview coverage map."""
    sql = """
        SELECT city, COUNT(*) AS company_count
        FROM customers
        WHERE city IS NOT NULL
        GROUP BY city
    """
    return run_query(sql)


def get_client_summary(filters: dict | None = None) -> pd.DataFrame:
    """One row per customer (all 50, even those with zero orders): lifetime
    revenue/order_count, sector (=nace_name), and a derived size band
    (revenue tercile across all customers).

    Deliberately excludes cost/profit/margin: cost postings (account range
    4000-7999) never carry a customer_id in this dataset — 0% tagged, not a
    partial-tagging gap — so cost cannot be attributed to an individual
    client by any method. Returning 0 kr here would misleadingly read as
    "this client costs nothing" rather than "not tracked at this level".
    See README's "Cost attribution" section.
    """
    companies = get_companies()
    revenue_df = _fetch_revenue(["company"], None, None, filters)

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
