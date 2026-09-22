import datetime as dt

import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_absence_by_department,
    get_absence_trend,
    get_cash_flow_trend,
    get_cost_by_account,
    get_customer_lifecycle_events,
    get_payroll_by_employee,
    get_payroll_trend,
    get_product_revenue,
    get_staffing_summary,
    get_supplier_spend,
    get_utilization_trend,
)
from ui.charts import bar_breakdown, grouped_bar_compare, line_over_time
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
        x_title=t("product", lang), y_title=t("revenue", lang),
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
        x_title=t("supplier", lang), y_title=t("spend", lang),
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
        x_title=t("department", lang), y_title=t("headcount", lang),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


_ABSENCE_LABELS = {
    "VACATION": "vacation", "SICK": "sick", "PARENTAL_LEAVE": "parental_leave", "WELFARE_LEAVE": "welfare_leave",
}


def _utilization_section(lang: str, theme: str, date_range: tuple | None) -> None:
    # Billable/internal HOURS and absence DAYS are two different units — never
    # one chart (see get_utilization_trend/get_absence_trend docstrings: the
    # DB now logs vacation/sick/parental/welfare leave as day-markers with
    # hours always 0, which would draw as flat zero lines if mixed in here).
    #
    # Yearly bars, not monthly area: a 100+-point monthly series of bursty
    # data (vacation concentrated in a few months a year) reads as jagged
    # noise in an area fill with no readable values. Yearly bars collapse
    # that to ~8 bars per series with a clean per-bar hover value.
    df = get_utilization_trend(granularity="year", date_range=date_range)
    if not df.empty:
        label_map = {"BILLABLE": t("billable", lang), "INTERNAL": t("internal", lang)}
        df = df.copy()
        df["year"] = df["period"].dt.year
        df[t("activity_type", lang)] = df["activity_type"].map(lambda a: label_map.get(a, a.title()))
        fig = bar_breakdown(
            df, "year", "hours", t("activity_type", lang), t("hours", lang), theme,
            x_title=t("year", lang), y_title=t("hours", lang),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.write("")
    st.markdown(f'<div class="section-label">{t("absences", lang)}</div>', unsafe_allow_html=True)
    absence_df = get_absence_trend(date_range=date_range)
    if not absence_df.empty:
        absence_df = absence_df.copy()
        absence_df["year"] = absence_df["period"].dt.year
        absence_df[t("activity_type", lang)] = absence_df["activity_type"].map(
            lambda a: t(_ABSENCE_LABELS.get(a, ""), lang) if a in _ABSENCE_LABELS else a.title()
        )
        fig_absence = bar_breakdown(
            absence_df, "year", "days", t("activity_type", lang), t("days", lang), theme,
            x_title=t("year", lang), y_title=t("days", lang),
        )
        st.plotly_chart(fig_absence, use_container_width=True, config={"displayModeBar": False})

    # "Where" (department) x "how" (absence type) — a grouped bar answers
    # exactly that question, which a time trend alone can't. Department is
    # an aggregate of several employees, not personally identifying — see
    # get_absence_by_department()'s docstring for the privacy line this
    # respects (no per-employee breakdown without separate sign-off).
    st.write("")
    st.markdown(f'<div class="section-label">{t("absences_by_department", lang)}</div>', unsafe_allow_html=True)
    dept_df = get_absence_by_department(date_range)
    if dept_df.empty:
        return
    dept_df = dept_df.copy()
    dept_df[t("activity_type", lang)] = dept_df["activity_type"].map(
        lambda a: t(_ABSENCE_LABELS.get(a, ""), lang) if a in _ABSENCE_LABELS else a.title()
    )
    fig_dept = bar_breakdown(
        dept_df, "department", "days", t("activity_type", lang), t("days", lang), theme,
        x_title=t("department", lang), y_title=t("days", lang),
    )
    st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False})


def _cost_by_account_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_cost_by_account(date_range)
    if df.empty:
        return
    fig = bar_breakdown(
        df.head(12), "account", "cost", None, t("cost", lang), theme,
        orientation="h", value_suffix=" kr", color_scale="warm",
        x_title=t("account", lang), y_title=t("cost", lang),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _payroll_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_payroll_trend(date_range=date_range)
    if not df.empty:
        fig = line_over_time(
            df, "period", "payroll", None, t("payroll", lang), theme, value_suffix=" kr", fill=True,
            x_title=t("month", lang), y_title=t("payroll", lang), granularity="month",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.write("")
    st.markdown(f'<div class="section-label">{t("payroll_by_employee", lang)}</div>', unsafe_allow_html=True)
    emp_df = get_payroll_by_employee()
    if emp_df.empty:
        return

    full_years = emp_df.loc[emp_df["is_full_year"], "year"]
    latest_year = int(full_years.max()) if not full_years.empty else int(emp_df["year"].max())
    latest = emp_df[emp_df["year"] == latest_year].sort_values("gross_annual", ascending=False).copy()
    latest["yoy_growth_pct"] = latest["yoy_growth_pct"].map(
        lambda v: f"{v:+.1f}%" if pd.notna(v) else "—"
    )
    table = latest.rename(
        columns={
            "employee": t("employee", lang), "department": t("department", lang),
            "gross_annual": t("gross_annual", lang), "yoy_growth_pct": t("yoy_growth", lang),
            "employer_cost": t("employer_cost", lang),
        }
    )
    table[t("gross_annual", lang)] = table[t("gross_annual", lang)].map(format_currency)
    table[t("employer_cost", lang)] = table[t("employer_cost", lang)].map(format_currency)
    st.caption(f"{t('payroll_year_label', lang)} {latest_year} · {t('employer_cost_note', lang)}")
    st.dataframe(
        table[[
            t("employee", lang), t("department", lang), t("gross_annual", lang),
            t("yoy_growth", lang), t("employer_cost", lang),
        ]],
        use_container_width=True, hide_index=True,
    )

    st.write("")
    employees = sorted(emp_df["employee"].unique())
    selected_emp = st.selectbox(t("select_employee", lang), employees, key="payroll_employee_select")
    emp_trend = emp_df[emp_df["employee"] == selected_emp].sort_values("year")
    if not emp_trend.empty and not bool(emp_trend.iloc[-1]["is_full_year"]):
        st.caption(f"{int(emp_trend.iloc[-1]['year'])}: {t('partial_year_note', lang)}")
    melted = emp_trend.melt(
        id_vars=["year"], value_vars=["gross_annual", "employer_cost"],
        var_name="cost_type", value_name="amount",
    )
    melted["cost_type"] = melted["cost_type"].map(
        {"gross_annual": t("gross_annual", lang), "employer_cost": t("employer_cost", lang)}
    )
    melted = melted.rename(columns={"cost_type": t("amount_type", lang)})
    # Grouped, not stacked: employer_cost already includes gross_annual
    # (it's gross x 1.141), so stacking would double-count it.
    fig_emp = grouped_bar_compare(
        melted, "year", "amount", t("amount_type", lang), t("amount", lang), theme, value_suffix=" kr",
        x_title=t("year", lang), y_title=t("amount", lang),
    )
    st.plotly_chart(fig_emp, use_container_width=True, config={"displayModeBar": False})


def _cash_flow_section(lang: str, theme: str, date_range: tuple | None) -> None:
    df = get_cash_flow_trend(date_range=date_range)
    if df.empty:
        return
    melted = df.melt(id_vars=["period"], value_vars=["incoming", "outgoing"], var_name="flow", value_name="amount")
    melted["flow"] = melted["flow"].map({"incoming": t("incoming", lang), "outgoing": t("outgoing", lang)})
    melted = melted.rename(columns={"flow": t("flow_type", lang)})
    fig = line_over_time(
        melted, "period", "amount", t("flow_type", lang), t("cash_flow", lang), theme, value_suffix=" kr",
        x_title=t("month", lang), y_title=t("amount", lang), granularity="month",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _lifecycle_section(lang: str, theme: str, date_range: tuple | None) -> None:
    # One row per client: acquisition date + current status (active/churned)
    # — not a flat event log. 50/50 clients have an onboarding date but only
    # 3/50 have ever churned, so a log of "events" was almost entirely
    # onboarding rows and never actually answered "is this client active?".
    df = get_customer_lifecycle_events(date_range)
    if df.empty:
        return
    status_map = {"active": t("active_status", lang), "churned": t("churned", lang)}
    df = df.copy()
    df["status"] = df["status"].map(lambda s: status_map.get(s, s))
    table = df.rename(
        columns={
            "name": t("company", lang), "segment": t("segment", lang),
            "onboarding_date": t("onboarded", lang), "churn_date": t("churned", lang),
            "status": t("status_label", lang),
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)


_SECTION_KEYS = [
    "products", "suppliers", "staffing", "utilization",
    "cost_by_account", "payroll", "cash_flow", "lifecycle",
]
_SECTION_LABEL_KEYS = {
    "products": "products_services", "suppliers": "suppliers", "staffing": "staffing",
    "utilization": "utilization", "cost_by_account": "cost_by_account", "payroll": "payroll",
    "cash_flow": "cash_flow", "lifecycle": "lifecycle_events",
}


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year (None = all years) comes from the global year selector
    in the header — every section here respects it (staffing is current-
    headcount only, so it's the one exception with no time dimension).

    Uses a session_state-backed st.radio for the sub-section picker instead
    of st.tabs(): Streamlit runs the Python body of every st.tabs() panel on
    every rerun regardless of which one is visually active (only CSS hides
    the rest), so all 8 sections' queries fired on every single interaction
    — profiling measured ~2.5s of that, ~2.1s of it pure DB round-trip time
    for sections the user wasn't even looking at. A radio's selected value
    is known before any section code runs, so only the one actually being
    viewed executes.
    """
    date_range = _year_to_range(selected_year)

    if "operations_section" not in st.session_state:
        st.session_state.operations_section = _SECTION_KEYS[0]

    with st.container(key="pill_operations_section"):
        st.radio(
            "operations_section_picker", options=_SECTION_KEYS,
            format_func=lambda k: t(_SECTION_LABEL_KEYS[k], lang),
            horizontal=True, key="operations_section", label_visibility="collapsed",
        )
    selected = st.session_state.operations_section

    st.write("")
    with st.spinner(t("loading_data", lang)):
        if selected == "products":
            _products_section(lang, theme, date_range)
        elif selected == "suppliers":
            _suppliers_section(lang, theme, date_range)
        elif selected == "staffing":
            _staffing_section(lang, theme)
        elif selected == "utilization":
            _utilization_section(lang, theme, date_range)
        elif selected == "cost_by_account":
            _cost_by_account_section(lang, theme, date_range)
        elif selected == "payroll":
            _payroll_section(lang, theme, date_range)
        elif selected == "cash_flow":
            _cash_flow_section(lang, theme, date_range)
        elif selected == "lifecycle":
            _lifecycle_section(lang, theme, date_range)
