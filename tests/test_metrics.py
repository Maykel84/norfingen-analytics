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


def _fake_cost_df():
    return pd.DataFrame(
        {
            "period": pd.to_datetime(["2026-01-01", "2026-02-01"]),
            "cost": [400.0, 500.0],
        }
    )


def test_profit_equals_revenue_minus_cost():
    with patch.object(metrics, "_fetch_revenue", return_value=_fake_revenue_df()), patch.object(
        metrics, "_fetch_cost", return_value=_fake_cost_df()
    ):
        df = metrics.get_measure(
            "profit",
            group_by=[],
            granularity="month",
            date_range=(dt.date(2026, 1, 1), dt.date(2026, 2, 28)),
        )
    df = df.sort_values("period").reset_index(drop=True)
    assert list(df["profit"]) == [600.0, 1500.0]


def test_margin_pct_matches_profit_over_revenue():
    with patch.object(metrics, "_fetch_revenue", return_value=_fake_revenue_df()), patch.object(
        metrics, "_fetch_cost", return_value=_fake_cost_df()
    ):
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
    with patch.object(metrics, "_fetch_revenue") as mock_rev, patch.object(
        metrics, "_fetch_cost"
    ) as mock_cost:
        mock_rev.return_value = pd.DataFrame({"revenue": [1000.0], "order_count": [8]})
        mock_cost.return_value = pd.DataFrame({"cost": [900.0]})
        df = metrics.get_measure("profit", group_by=[], granularity=None)
    assert df["revenue"].iloc[0] == 1000.0
    assert df["cost"].iloc[0] == 900.0
    assert df["profit"].iloc[0] == 100.0
    assert df["margin_pct"].iloc[0] == pytest.approx(10.0)


def test_revenue_measure_passthrough():
    with patch.object(metrics, "_fetch_revenue", return_value=_fake_revenue_df()), patch.object(
        metrics, "_fetch_cost", return_value=_fake_cost_df()
    ):
        df = metrics.get_measure("revenue", group_by=[], granularity="month")
    assert df["revenue"].sum() == 3000.0


def test_whole_company_cost_and_profit_totals_are_unaffected():
    """Cost postings never carry a customer_id, but that only blocks
    per-client attribution — the whole-company (no group_by) total must
    still aggregate the full, correct cost figure."""
    with patch.object(metrics, "_fetch_revenue") as mock_rev, patch.object(
        metrics, "_fetch_cost"
    ) as mock_cost:
        mock_rev.return_value = pd.DataFrame({"revenue": [5000.0], "order_count": [12]})
        mock_cost.return_value = pd.DataFrame({"cost": [3200.0]})

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
