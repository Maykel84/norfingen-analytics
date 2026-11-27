"""Lightweight unit tests for the semantic layer's aggregation math.

These don't hit the live database — they test the pure aggregation/merge
logic in semantic.metrics against small synthetic DataFrames.
"""

import datetime as dt
from unittest.mock import patch

import pandas as pd
import pytest

from semantic import metrics


def _fake_revenue_df():
    return pd.DataFrame(
        {
            "period": pd.to_datetime(["2026-01-01", "2026-02-01"]),
            "revenue": [1000.0, 2000.0],
            "order_count": [3, 5],
        }
    )


def _fake_combined_df():
    """What _fetch_revenue_cost_combined returns: revenue + cost already in
    one frame (the SQL-side FULL OUTER JOIN + COALESCE), before get_measure
    adds profit/margin_pct."""
    return pd.DataFrame(
        {
            "period": pd.to_datetime(["2026-01-01", "2026-02-01"]),
            "revenue": [1000.0, 2000.0],
            "order_count": [3, 5],
            "cost": [400.0, 500.0],
        }
    )


def test_profit_equals_revenue_minus_cost():
    with patch.object(metrics, "_fetch_revenue_cost_combined", return_value=_fake_combined_df()):
        df = metrics.get_measure(
            "profit",
            group_by=[],
            granularity="month",
            date_range=(dt.date(2026, 1, 1), dt.date(2026, 2, 28)),
        )
    df = df.sort_values("period").reset_index(drop=True)
    assert list(df["profit"]) == [600.0, 1500.0]


def test_margin_pct_matches_profit_over_revenue():
    with patch.object(metrics, "_fetch_revenue_cost_combined", return_value=_fake_combined_df()):
        df = metrics.get_measure(
            "margin_pct",
            group_by=[],
            granularity="month",
            date_range=(dt.date(2026, 1, 1), dt.date(2026, 2, 28)),
        )
    df = df.sort_values("period").reset_index(drop=True)
    expected = [600.0 / 1000.0 * 100, 1500.0 / 2000.0 * 100]
    assert df["margin_pct"].round(4).tolist() == [round(v, 4) for v in expected]


def test_totals_roll_up_across_periods_when_ungrouped():
    with patch.object(metrics, "_fetch_revenue_cost_combined") as mock_combined:
        mock_combined.return_value = pd.DataFrame({"revenue": [1000.0], "order_count": [8], "cost": [900.0]})
        df = metrics.get_measure("profit", group_by=[], granularity=None)
    assert df["revenue"].iloc[0] == 1000.0
    assert df["cost"].iloc[0] == 900.0
    assert df["profit"].iloc[0] == 100.0
    assert df["margin_pct"].iloc[0] == pytest.approx(10.0)


def test_revenue_measure_passthrough():
    """measure="revenue" only calls _fetch_revenue — not _fetch_cost or the
    combined revenue+cost fetch — since it never needs cost at all."""
    with patch.object(metrics, "_fetch_revenue", return_value=_fake_revenue_df()), patch.object(
        metrics, "_fetch_cost"
    ) as mock_cost, patch.object(metrics, "_fetch_revenue_cost_combined") as mock_combined:
        df = metrics.get_measure("revenue", group_by=[], granularity="month")
    assert df["revenue"].sum() == 3000.0
    mock_cost.assert_not_called()
    mock_combined.assert_not_called()


def test_whole_company_cost_and_profit_totals_are_unaffected():
    """Cost postings never carry a customer_id, but that only blocks
    per-client attribution — the whole-company (no group_by) total must
    still aggregate the full, correct cost figure."""
    with patch.object(metrics, "_fetch_cost") as mock_cost, patch.object(
        metrics, "_fetch_revenue_cost_combined"
    ) as mock_combined:
        mock_cost.return_value = pd.DataFrame({"cost": [3200.0]})
        mock_combined.return_value = pd.DataFrame({"revenue": [5000.0], "order_count": [12], "cost": [3200.0]})

        cost_df = metrics.get_measure("cost", group_by=[], granularity=None)
        profit_df = metrics.get_measure("profit", group_by=[], granularity=None)

    assert cost_df["cost"].iloc[0] == 3200.0
    assert profit_df["revenue"].iloc[0] == 5000.0
    assert profit_df["cost"].iloc[0] == 3200.0
    assert profit_df["profit"].iloc[0] == 1800.0


def test_get_client_summary_has_no_cost_profit_margin_columns():
    """Cost postings are 0% tagged with customer_id in this dataset (not a
    partial-tagging gap), so per-client cost/profit/margin is unmeasurable —
    get_client_summary() must not return those columns at all, not even as 0."""
    fake_companies = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Acme AS", "Nord AS"],
            "city": ["Oslo", "Bergen"],
            "postal_code": ["0001", "5001"],
            "segment": ["Enterprise", "SMB"],
            "nace_name": ["Consulting", "Retail"],
            "nace_code": ["70.1", "47.1"],
        }
    )
    fake_revenue = pd.DataFrame(
        {"company": ["Acme AS", "Nord AS"], "revenue": [10000.0, 4000.0], "order_count": [5, 2]}
    )

    with patch.object(metrics, "get_companies", return_value=fake_companies), patch.object(
        metrics, "_fetch_revenue", return_value=fake_revenue
    ):
        summary = metrics.get_client_summary()

    for forbidden in ("cost", "profit", "margin_pct"):
        assert forbidden not in summary.columns
    assert set(summary.columns) >= {"name", "sector", "size_band", "revenue", "order_count"}
    assert summary.loc[summary["name"] == "Acme AS", "revenue"].iloc[0] == 10000.0


# --- open (partial) month handling -----------------------------------------

def _with_partial(months):
    return patch.object(metrics, "get_partial_month_starts", return_value=months)


def test_exclude_partial_months_trims_range_end_to_last_full_month():
    with _with_partial([dt.date(2026, 11, 1)]):
        out = metrics.exclude_partial_months((dt.date(2026, 1, 1), dt.date(2026, 11, 16)))
    assert out == (dt.date(2026, 1, 1), dt.date(2026, 10, 31))


def test_exclude_partial_months_leaves_closed_range_alone():
    rng = (dt.date(2025, 1, 1), dt.date(2025, 12, 31))
    with _with_partial([dt.date(2026, 11, 1)]):
        assert metrics.exclude_partial_months(rng) == rng


def test_exclude_partial_months_noop_without_open_month():
    rng = (dt.date(2026, 1, 1), dt.date(2026, 11, 30))
    with _with_partial([]):
        assert metrics.exclude_partial_months(rng) == rng


def test_exclude_partial_months_range_entirely_in_open_month_is_unchanged():
    rng = (dt.date(2026, 11, 2), dt.date(2026, 11, 16))
    with _with_partial([dt.date(2026, 11, 1)]):
        assert metrics.exclude_partial_months(rng) == rng


def test_exclude_partial_months_none_means_all_time_up_to_last_full_month():
    with _with_partial([dt.date(2026, 11, 1)]), patch.object(
        metrics, "get_data_start", return_value=dt.date(2019, 1, 2)
    ):
        assert metrics.exclude_partial_months(None) == (dt.date(2019, 1, 2), dt.date(2026, 10, 31))


def test_partial_months_in_range_overlap():
    with _with_partial([dt.date(2026, 11, 1)]):
        assert metrics.get_partial_months_in_range((dt.date(2026, 1, 1), dt.date(2026, 11, 16))) == [dt.date(2026, 11, 1)]
        assert metrics.get_partial_months_in_range((dt.date(2025, 1, 1), dt.date(2025, 12, 31))) == []


# --- receivables ------------------------------------------------------------

def test_get_receivables_normalises_types():
    raw = pd.DataFrame({
        "order_id": [1], "customer": ["A"], "invoice_date": ["2026-01-02"], "due_date": ["2026-02-02"],
        "paid_date": [None], "amount": ["125.00"], "amount_net": ["100.00"], "invoice_status": ["OVERDUE"],
        "days_past_due": [dt.timedelta(days=5)], "paid_late": [None], "write_off_pending": [True],
        "write_off_planned_date": ["2026-12-23"],
    })
    with patch.object(metrics, "run_query", return_value=raw):
        df = metrics.get_receivables(2026)
    assert df["amount"].dtype == float
    assert df["days_past_due"].iloc[0] == 5
    assert df["paid_late"].dtype == bool and not df["paid_late"].iloc[0]
    assert df["write_off_pending"].dtype == bool and df["write_off_pending"].iloc[0]
    assert df["amount_net"].iloc[0] == 100.0
    assert pd.api.types.is_datetime64_any_dtype(df["invoice_date"])
    assert pd.api.types.is_datetime64_any_dtype(df["write_off_planned_date"])


def test_invoice_status_queries_join_the_view_and_never_read_orders_status():
    raw = pd.DataFrame({
        "order_id": [1], "customer": ["A"], "invoice_date": ["2026-01-02"], "due_date": ["2026-02-02"],
        "paid_date": [None], "amount": ["1"], "amount_net": ["1"], "invoice_status": ["OPEN"],
        "days_past_due": [-3], "paid_late": [False], "write_off_pending": [False], "write_off_planned_date": [None],
    })
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        metrics.get_receivables()
        metrics.get_orders_invoice_payment_status(dt.date(2026, 11, 16), 14)
    for call in rq.call_args_list:
        sql = call.args[0]
        assert "v_invoice_status" in sql
        assert "o.status" not in sql and "orders.status" not in sql and "write_off_voucher_id" not in sql


def test_get_write_offs_by_month_passes_year_param():
    raw = pd.DataFrame({"period": [pd.Timestamp("2026-01-01")], "written_off": ["41616.79"], "written_off_gross": ["52020.99"]})
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        df = metrics.get_write_offs_by_month(2026)
    assert rq.call_args.args[1] == {"year": 2026}
    assert df["written_off"].iloc[0] == pytest.approx(41616.79)


# --- liquidity & financing --------------------------------------------------

def test_bank_balance_is_cumulative_from_first_posting():
    raw = pd.DataFrame({"day": ["2019-01-02", "2019-01-03"], "movement": ["100.00", "-30.00"]})
    with patch.object(metrics, "run_query", return_value=raw):
        df = metrics.get_bank_balance_daily()
    assert df["balance"].tolist() == [100.0, 70.0]


def test_owner_loan_outstanding_steps_down_and_never_negative():
    # drawdown is a credit (negative), instalments debits (positive)
    raw = pd.DataFrame({
        "period": [pd.Timestamp("2021-01-01"), pd.Timestamp("2021-03-01"), pd.Timestamp("2021-04-01")],
        "principal_net": [-300.0, 100.0, 200.0 + 1e-9],
        "principal_repaid": [None, 100.0, 200.0 + 1e-9],
        "interest": [5.0, 3.0, 1.0],
    })
    with patch.object(metrics, "run_query", return_value=raw):
        df = metrics.get_owner_loan_monthly()
    assert df["period"].tolist() == list(pd.date_range("2021-01-01", "2021-04-01", freq="MS"))  # gap month filled
    assert df["outstanding"].tolist() == [300.0, 300.0, 200.0, 0.0]
    assert (df["outstanding"] >= 0).all()


def test_financing_structure_shows_credits_as_positive():
    raw = pd.DataFrame({"share_capital": ["500000"], "owner_loan": ["3500000"]})
    with patch.object(metrics, "run_query", return_value=raw):
        assert metrics.get_financing_structure() == {"share_capital": 500000.0, "owner_loan": 3500000.0}


# --- profitability ----------------------------------------------------------

def _prof_raw():
    return pd.DataFrame({
        "customer": ["A", "B", "C"], "revenue": ["600", "400", "0"], "labor_cost": ["100", "500", "50"],
        "billable_hours": ["10", "20", "0"], "cogs_total": ["200", "200", "200"],
    })


def test_customer_profitability_allocates_cogs_pro_rata_to_revenue():
    with patch.object(metrics, "_full_month_range", return_value=(dt.date(2026, 1, 1), dt.date(2026, 10, 31))), \
         patch.object(metrics, "run_query", return_value=_prof_raw()):
        df = metrics.get_customer_profitability(2026).set_index("customer")
    assert df["cogs_alloc"].sum() == pytest.approx(200.0)
    assert df.loc["A", "cogs_alloc"] == pytest.approx(120.0)
    assert df.loc["A", "contribution"] == pytest.approx(600 - 120 - 100)
    assert df.loc["B", "contribution"] < 0  # labor outweighs revenue
    assert pd.isna(df.loc["C", "contribution_pct"]) and pd.isna(df.loc["C", "revenue_per_hour"])


def test_employee_utilization_handles_zero_hours():
    raw = pd.DataFrame({
        "employee": ["X", "Y"], "department": ["D", "D"],
        "billable_hours": ["30", "0"], "internal_hours": ["70", "0"],
    })
    with patch.object(metrics, "run_query", return_value=raw):
        df = metrics.get_employee_utilization()
    assert df["utilization_pct"].iloc[0] == pytest.approx(30.0)
    assert pd.isna(df["utilization_pct"].iloc[1])


# --- snap_to_full_months (Time Analysis fix) -----------------------------------

def test_snap_default_last_12_months_matches_trailing_12_full_months():
    # default picker range 2025-11-16 .. 2026-11-16 with Nov 2026 still open
    with _with_partial([dt.date(2026, 11, 1)]):
        assert metrics.snap_to_full_months((dt.date(2025, 11, 16), dt.date(2026, 11, 16))) == (
            dt.date(2025, 11, 1), dt.date(2026, 10, 31),
        )


def test_snap_aligns_start_and_end_to_month_edges_when_all_months_closed():
    with _with_partial([]):
        assert metrics.snap_to_full_months((dt.date(2024, 3, 17), dt.date(2024, 5, 3))) == (
            dt.date(2024, 3, 1), dt.date(2024, 5, 31),
        )


def test_snap_returns_none_when_range_is_only_the_open_month():
    with _with_partial([dt.date(2026, 11, 1)]):
        assert metrics.snap_to_full_months((dt.date(2026, 11, 2), dt.date(2026, 11, 16))) is None


# --- coverage map framing (Overview fix) ------------------------------------------

def test_coverage_map_view_fits_all_cities():
    from ui.charts import _fit_map_view

    df = pd.DataFrame({"lat": [58.1, 69.6, 59.9], "lon": [8.0, 18.9, 10.7]})  # Kristiansand .. Tromsø
    center, zoom = _fit_map_view(df)
    assert center["lat"] == pytest.approx(63.85) and center["lon"] == pytest.approx(13.45)
    assert 3.0 <= zoom <= 4.2  # far lower than the old fixed 3.6 centre-on-64.5 framing would clip the south
    # the whole lat span must fit the 320 px viewport at this zoom
    import math
    deg_per_px = 360 / (512 * 2**zoom) * math.cos(math.radians(center["lat"]))
    assert (69.6 - 58.1) / deg_per_px <= 320 + 1


def test_coverage_map_single_city_does_not_zoom_to_infinity():
    from ui.charts import _fit_map_view

    _, zoom = _fit_map_view(pd.DataFrame({"lat": [59.9], "lon": [10.7]}))
    assert zoom <= 6.0


def test_write_off_gross_is_net_plus_reversed_vat_and_tile_matches_chart_total():
    raw = pd.DataFrame({
        "period": [pd.Timestamp("2022-02-01"), pd.Timestamp("2026-01-01")],
        "written_off": ["256381.33", "41616.79"], "written_off_gross": ["320476.66", "52020.99"],
    })
    with patch.object(metrics, "run_query", return_value=raw):
        df = metrics.get_write_offs_by_month()
    # the Receivables tile is df.written_off.sum(); the chart's last running-total point is the same cumsum
    assert df["written_off"].sum() == pytest.approx(df["written_off"].cumsum().iloc[-1])
    assert df["written_off_gross"].sum() == pytest.approx(df["written_off"].sum() * 1.25, rel=1e-4)


def test_data_start_is_earlier_of_first_order_and_first_voucher():
    raw = pd.DataFrame({"d": [dt.date(2019, 1, 2)]})
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        assert metrics.get_data_start() == dt.date(2019, 1, 2)
    assert "LEAST" in rq.call_args.args[0]


def test_financial_expense_uses_8xxx_accounts_and_date_range():
    raw = pd.DataFrame({"expense": ["794791.61"]})
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        assert metrics.get_financial_expense((dt.date(2019, 1, 1), dt.date(2025, 12, 31))) == pytest.approx(794791.61)
    assert "BETWEEN 8000 AND 8299" in rq.call_args.args[0]


# --- Operations review fixes (round 2, point 3) ----------------------------------

def test_supplier_spend_includes_cogs_payables():
    raw = pd.DataFrame({"supplier": ["X"], "invoice_count": [2], "spend": ["10"], "unpaid_amount": ["0"]})
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        metrics.get_supplier_spend()
    sql = rq.call_args.args[0]
    assert "supplier_invoices" in sql and "cogs_payables" in sql and "UNION ALL" in sql


def test_absence_types_cover_every_non_hour_activity():
    assert {"CHILD_CARE_LEAVE", "FLEX_LEAVE"} <= set(metrics.ABSENCE_ACTIVITY_TYPES)


def test_payroll_gross_comes_from_specifications_and_employer_cost_uses_multiplier():
    raw = pd.DataFrame({
        "employee_id": [1, 1], "employee": ["A", "A"], "department": ["D", "D"], "year": [2024, 2025],
        "months_paid": [12, 12], "gross_annual": ["100", "110"], "net_annual": ["70", "77"],
    })
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        df = metrics.get_payroll_by_employee()
    assert "wage_type_id IN (100, 260)" in rq.call_args.args[0]
    assert df["employer_cost"].iloc[1] == pytest.approx(110 * metrics.EMPLOYER_COST_MULTIPLIER)
    assert df["yoy_growth_pct"].iloc[1] == pytest.approx(10.0)


# --- suppliers and COGS (generator change 2026-11-17) --------------------------------

def test_cogs_by_supplier_shares_sum_to_100_and_come_from_the_data():
    raw = pd.DataFrame({"supplier": ["Ingram Micro AS", "Atea AS", "X"], "net_cogs": ["33", "26", "41"]})
    with patch.object(metrics, "run_query", return_value=raw) as rq:
        df = metrics.get_cogs_by_supplier((dt.date(2025, 1, 1), dt.date(2025, 12, 31)))
    assert df["share_pct"].sum() == pytest.approx(100.0)
    assert "cogs_payables" in rq.call_args.args[0]
    assert "Ingram" not in rq.call_args.args[0]  # nothing hard-coded to a supplier name


# --- absence colors (round 3) -------------------------------------------------------

def test_every_absence_type_has_its_own_color_in_every_theme_and_palette():
    from ui.charts import ABSENCE_COLORS

    for family, themes in ABSENCE_COLORS.items():
        for theme, colors in themes.items():
            assert set(colors) == set(metrics.ABSENCE_ACTIVITY_TYPES), (family, theme)
            assert len(set(colors.values())) == len(colors), f"duplicate colour in {family}/{theme}"


# --- P&L from v_pl_monthly (EBIT vs net result) ------------------------------

def _fake_pl_view():
    return pd.DataFrame({
        "month": ["2025-11", "2025-12", "2026-01", "2026-02"],
        "revenue": [100.0, 100.0, 100.0, 100.0],
        "labor_cost": [40.0, 40.0, 40.0, 0.0],
        "operating_cost": [20.0, 20.0, 20.0, 5.0],
        "cogs": [30.0, 30.0, 30.0, 0.0],
        "operating_result": [10.0, 10.0, 10.0, 95.0],
        "is_partial": [False, False, False, True],
        "depreciation": [2.0, 2.0, 2.0, 0.0],
        "ebitda": [12.0, 12.0, 12.0, 95.0],
        "financial_result": [-1.0, -1.0, 0.0, 0.0],
        "tax": [0.0, 4.0, 0.0, 0.0],
        "net_result": [9.0, 5.0, 10.0, 95.0],
    })


def test_yearly_totals_use_full_months_and_split_ebit_from_net_result():
    with patch.object(metrics, "run_query", side_effect=[_fake_pl_view(), pd.DataFrame({"n": [7]})]):
        t = metrics.get_yearly_totals(2025)
    assert t["profit"] == 20.0 and t["net_result"] == 14.0
    assert t["tax"] == 4.0 and t["financial_result"] == -2.0
    assert t["margin_pct"] == 10.0 and t["company_count"] == 7
    assert t["tax_pending_year"] is None


def test_yearly_totals_exclude_open_month_and_flag_tax_not_booked_yet():
    with patch.object(metrics, "run_query", side_effect=[_fake_pl_view(), pd.DataFrame({"n": [3]})]):
        t = metrics.get_yearly_totals(2026)
    assert t["revenue"] == 100.0 and t["profit"] == 10.0  # February (open) left out
    assert t["tax_pending_year"] == 2026


def test_multi_year_trend_drops_open_month_and_sums_extra_series():
    with patch.object(metrics, "run_query", return_value=_fake_pl_view()):
        df = metrics.get_multi_year_trend().set_index("period")
    assert list(df.index.year) == [2025, 2026]
    assert df.loc["2026-01-01", "revenue"] == 100.0
    assert df.loc["2025-01-01", "net_result"] == 14.0
    assert df.loc["2025-01-01", "cost"] == 180.0  # includes depreciation (inside operating_cost)


# --- balance sheet -------------------------------------------------------------

def test_balance_check_max_is_zero_when_balanced_and_flags_a_gap():
    ok = pd.DataFrame({"balance_check": [0.0, -0.0, 0.0]})
    bad = pd.DataFrame({"balance_check": [0.0, -0.37, 0.12]})
    assert metrics.balance_check_max(ok) == 0.0
    assert metrics.balance_check_max(bad) == pytest.approx(0.37)


def test_fixed_assets_monthly_is_cumulative_and_net_of_depreciation():
    ledger = pd.DataFrame({"month": ["2026-01", "2026-03"], "cost_m": [1000.0, 500.0], "dep_m": [-20.0, -30.0]})
    months = pd.DataFrame({"month": ["2026-01", "2026-02", "2026-03"]})
    with patch.object(metrics, "run_query", side_effect=[ledger, months]):
        df = metrics.get_fixed_assets_monthly()
    assert list(df["cost"]) == [1000.0, 1000.0, 1500.0]
    assert list(df["accumulated_depreciation"]) == [20.0, 20.0, 50.0]
    assert list(df["net"]) == [980.0, 980.0, 1450.0]
