import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_cost_by_category_monthly, get_customer_profitability, get_employee_utilization, get_partial_months_in_range,
)
from ui.charts import bar_breakdown, stacked_bar_over_time
from ui.components import format_currency, format_int, format_pct, kpi_tile
from ui.i18n import t, t_department


def _section(label: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """Profitability: per-customer contribution (a model — see note), per-
    employee utilization, and monthly cost by category."""
    with st.spinner(t("loading_data", lang)):
        customers = get_customer_profitability(selected_year)
        util = get_employee_utilization(selected_year)
        costs = get_cost_by_category_monthly()

    # ---- customers -----------------------------------------------------------
    _section(t("prf_customers", lang))
    if customers.empty:
        st.caption(t("no_activity", lang))
    else:
        rev, cogs, labor = customers["revenue"].sum(), customers["cogs_alloc"].sum(), customers["labor_cost"].sum()
        contribution = rev - cogs - labor
        cols = st.columns(4)
        with cols[0]:
            kpi_tile(t("revenue", lang), format_currency(rev), theme)
        with cols[1]:
            kpi_tile(t("prf_cogs_alloc", lang), format_currency(cogs), theme)
        with cols[2]:
            kpi_tile(t("prf_labor", lang), format_currency(labor), theme)
        with cols[3]:
            kpi_tile(t("prf_contribution", lang), format_currency(contribution), theme)
            st.caption(format_pct(contribution / rev * 100 if rev else 0))
        st.caption(f"ℹ️ {t('prf_method_note', lang)}")

        top = customers.head(15).iloc[::-1]
        fig = bar_breakdown(
            top, "customer", "contribution", None, t("prf_top_contribution", lang), theme, orientation="h",
            value_suffix=" kr", color_scale="sage", x_title=t("company", lang), y_title=t("prf_contribution", lang),
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        table = pd.DataFrame({
            t("company", lang): customers["customer"],
            t("revenue", lang): customers["revenue"].map(format_currency),
            t("prf_cogs_alloc", lang): customers["cogs_alloc"].map(format_currency),
            t("prf_labor", lang): customers["labor_cost"].map(format_currency),
            t("prf_contribution", lang): customers["contribution"].map(format_currency),
            t("prf_contribution_pct", lang): customers["contribution_pct"].map(lambda v: format_pct(v) if pd.notna(v) else "—"),
            t("prf_billable_hours", lang): customers["billable_hours"].map(format_int),
            t("prf_revenue_per_hour", lang): customers["revenue_per_hour"].map(lambda v: format_currency(v) if pd.notna(v) else "—"),
        })
        st.dataframe(table, use_container_width=True, hide_index=True, height=420)

    # ---- utilization ---------------------------------------------------------
    st.write("")
    _section(t("prf_utilization", lang))
    long = util.melt(
        id_vars=["employee"], value_vars=["billable_hours", "internal_hours"], var_name="type", value_name="hours",
    )
    long["type"] = long["type"].map({"billable_hours": t("prf_billable_hours", lang), "internal_hours": t("prf_internal_hours", lang)})
    order = util.sort_values("billable_hours")["employee"].tolist()
    long["employee"] = pd.Categorical(long["employee"], categories=order, ordered=True)
    fig = bar_breakdown(
        long.sort_values("employee"), "employee", "hours", "type", "", theme, orientation="h",
        value_suffix=" h", x_title=t("employee", lang), y_title=t("hours", lang),
    )
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    table = pd.DataFrame({
        t("employee", lang): util["employee"],
        t("department", lang): util["department"].map(lambda d: t_department(d, lang)),
        t("prf_billable_hours", lang): util["billable_hours"].map(format_int),
        t("prf_internal_hours", lang): util["internal_hours"].map(format_int),
        t("prf_utilization_pct", lang): util["utilization_pct"].map(lambda v: format_pct(v) if pd.notna(v) else "—"),
    })
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(f"ℹ️ {t('prf_utilization_note', lang)}")

    # ---- cost by category ----------------------------------------------------
    st.write("")
    _section(t("prf_cost_by_category", lang))
    view = costs if selected_year is None else costs[costs["period"].dt.year == selected_year]
    if not view.empty:
        fig = stacked_bar_over_time(
            view, "period",
            {
                "cogs_passthrough": t("prf_cat_cogs", lang), "labor": t("prf_cat_labor", lang),
                "operating": t("prf_cat_operating", lang), "equipment": t("prf_cat_equipment", lang),
            },
            theme, x_title=t("month", lang), y_title=t("amount", lang),
        )
        fig.update_layout(height=420, legend=dict(y=-0.3))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if get_partial_months_in_range((view["period"].min().date(), pd.Timestamp.max.date())):
            st.caption(f"ℹ️ {t('prf_cost_note', lang)}")
