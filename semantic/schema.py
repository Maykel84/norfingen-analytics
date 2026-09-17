"""Discovered schema constants and the semantic mapping used by metrics.py.

Discovered via information_schema introspection (see project handoff notes).
Base tables of interest: customers, orders, order_lines, vouchers, postings,
accounts, departments, employees, hour_entries, projects.
Pre-built views available in the DB: v_sales_flat, v_pl_monthly, v_headcount_monthly.
"""

# Account-number ranges used to bucket postings into cost categories.
COST_ACCOUNT_RANGES = {
    "cogs": (4000, 4999),
    "labor_cost": (5000, 5999),
    "operating_cost": (6000, 7999),
}

CUSTOMER_SEGMENTS = ["Enterprise", "Mid-market", "SMB"]

DATE_GRANULARITIES = ["day", "week", "month", "quarter", "year"]

# maps a granularity to the Postgres date_trunc field
DATE_TRUNC_FIELD = {
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}

DIMENSIONS = {
    "company": "Customer name",
    "location": "City",
    "segment": "Segment",
    "nace_name": "Industry",
    "cost_bucket": "Cost type",
}

MEASURES = {
    "revenue": "Revenue",
    "cost": "Cost",
    "profit": "Profit",
    "margin_pct": "Margin %",
    "order_count": "Orders",
}

# Size band is derived (no size column exists): lifetime-revenue terciles
# across the 50 customers, computed in metrics.get_client_summary().
SIZE_BANDS = ["Small", "Medium", "Large"]

PERIOD_TYPES = ["month", "quarter", "year", "custom"]
