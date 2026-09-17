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
