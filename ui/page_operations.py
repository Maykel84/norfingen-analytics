import datetime as dt

import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_cash_flow_trend,
    get_cost_by_account,
    get_customer_lifecycle_events,
    get_payroll_trend,
    get_product_revenue,
    get_staffing_summary,
    get_supplier_spend,
    get_utilization_trend,
)
from ui.charts import bar_breakdown, line_over_time, stacked_area
from ui.components import format_currency, format_int
from ui.i18n import t


def _year_to_range(year: int | None) -> tuple | None:
    if year is None:
        return None
    return (dt.date(year, 1, 1), dt.date(year, 12, 31))


def _products_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_product_revenue(date_range)
    if df.empty:
        return
    fig = bar_breakdown(
        df.head(10), "product", "revenue", None, t("revenue", lang), theme,
        orientation="h", value_suffix=" kr", color_scale="sage",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    table = df.rename(
        columns={
            "product": t("product", lang), "service": t("service", lang),
            "revenue": t("revenue", lang), "order_count": t("order_count", lang),
        }
    )
    table[t("revenue", lang)] = table[t("revenue", lang)].map(format_currency)
    st.dataframe(table.drop(columns=["billing_model"]), use_container_width=True, hide_index=True)


def _suppliers_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_supplier_spend(date_range)
    if df.empty:
        return
    fig = bar_breakdown(
        df, "supplier", "spend", None, t("spend", lang), theme,
        orientation="h", value_suffix=" kr", color_scale="warm",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    table = df.rename(
        columns={
            "supplier": t("supplier", lang), "invoice_count": t("order_count", lang),
            "spend": t("spend", lang), "unpaid_amount": t("unpaid", lang),
        }
    )
    table[t("spend", lang)] = table[t("spend", lang)].map(format_currency)
    table[t("unpaid", lang)] = table[t("unpaid", lang)].map(format_currency)
    st.dataframe(table, use_container_width=True, hide_index=True)


def _staffing_section(lang: str, theme: str) -> None:
    df = get_staffing_summary()
    if df.empty:
        return
    df = df.rename(columns={"employment_type": t("employment_type", lang)})
    fig = bar_breakdown(
        df, "department", "headcount", t("employment_type", lang), t("headcount", lang), theme, value_suffix="",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _utilization_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_utilization_trend(date_range=date_range)
    if df.empty:
        return
    label_map = {"BILLABLE": t("billable", lang), "INTERNAL": t("internal", lang), "SICK": t("sick", lang)}
    df = df.copy()
    df[t("activity_type", lang)] = df["activity_type"].map(lambda a: label_map.get(a, a.title()))
    # Stacked area, not stacked bars — a long monthly time series (100+
    # periods) reads as noise as adjacent bars; an area chart shows the
    # same billable/internal/sick composition as a smoother trend.
    fig = stacked_area(df, "period", "hours", t("activity_type", lang), t("hours", lang), theme, value_suffix="")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _cost_by_account_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_cost_by_account(date_range)
    if df.empty:
        return
    fig = bar_breakdown(
        df.head(12), "account", "cost", None, t("cost", lang), theme,
        orientation="h", value_suffix=" kr", color_scale="warm",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _payroll_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_payroll_trend(date_range=date_range)
    if df.empty:
        return
    fig = line_over_time(df, "period", "payroll", None, t("payroll", lang), theme, value_suffix=" kr", fill=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _cash_flow_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_cash_flow_trend(date_range=date_range)
    if df.empty:
        return
    melted = df.melt(id_vars=["period"], value_vars=["incoming", "outgoing"], var_name="flow", value_name="amount")
    melted["flow"] = melted["flow"].map({"incoming": t("incoming", lang), "outgoing": t("outgoing", lang)})
    melted = melted.rename(columns={"flow": t("flow_type", lang)})
    fig = line_over_time(
        melted, "period", "amount", t("flow_type", lang), t("cash_flow", lang), theme, value_suffix=" kr",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _lifecycle_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_customer_lifecycle_events(date_range)
    if df.empty:
        return
    label_map = {"onboarded": t("onboarded", lang), "churned": t("churned", lang)}
    df = df.copy()
    df["event_type"] = df["event_type"].map(lambda e: label_map.get(e, e))
    table = df.rename(
        columns={
            "name": t("company", lang), "segment": t("segment", lang),
            "event_date": t("event_date", lang), "event_type": t("event_type", lang),
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year (None = all years) comes from the global year selector
    in the header — every section here respects it (staffing is current-
    headcount only, so it's the one exception with no time dimension)."""
    date_range = _year_to_range(selected_year)

    tabs = st.tabs(
        [
            t("products_services", lang), t("suppliers", lang), t("staffing", lang),
            t("utilization", lang), t("cost_by_account", lang), t("payroll", lang),
            t("cash_flow", lang), t("lifecycle_events", lang),
        ]
    )
    with tabs[0]:
        _products_section(lang, theme, date_range)
    with tabs[1]:
        _suppliers_section(lang, theme, date_range)
    with tabs[2]:
        _staffing_section(lang, theme)
    with tabs[3]:
        _utilization_section(lang, theme, date_range)
    with tabs[4]:
        _cost_by_account_section(lang, theme, date_range)
    with tabs[5]:
        _payroll_section(lang, theme, date_range)
    with tabs[6]:
        _cash_flow_section(lang, theme, date_range)
    with tabs[7]:
        _lifecycle_section(lang, theme, date_range)
