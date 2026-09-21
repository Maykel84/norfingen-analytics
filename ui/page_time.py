import datetime as dt

import pandas as pd
import streamlit as st

from semantic.metrics import get_companies, get_date_bounds, get_measure
from semantic.schema import MEASURES
from ui.charts import bar_breakdown, line_over_time
from ui.components import format_currency, format_delta_pct, format_int, format_pct, kpi_tile, segmented_control
from ui.i18n import t

FORMATTERS = {
    "revenue": format_currency,
    "cost": format_currency,
    "profit": format_currency,
    "order_count": format_int,
    "margin_pct": format_pct,
}

PERIOD_TO_GRANULARITY = {"month": "month", "quarter": "quarter", "year": "year", "custom": "month"}

# Cost postings never carry a customer_id (0% tagged, not partial) — cost is
# only measurable whole-company or by time period/cost bucket, never broken
# down by a customer-attribute dimension. See README's "Cost attribution".
CUSTOMER_ATTR_DIMS = {"company", "location", "segment", "nace_name"}
BREAKDOWN_SAFE_MEASURES = {"revenue", "order_count"}


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year (from the header's global selector) bounds every date
    picker on this page to that single year — the main filter range and
    both comparison periods — so "all data in the report" genuinely means
    all of it, not just Overview/Operations. Pick "All years" globally to
    get the previous unrestricted (full-history, cross-year) behavior."""
    data_min, data_max = get_date_bounds()
    if selected_year is not None:
        min_date = max(data_min, dt.date(selected_year, 1, 1))
        max_date = min(data_max, dt.date(selected_year, 12, 31))
    else:
        min_date, max_date = data_min, data_max
    companies_df = get_companies()

    if "period_type" not in st.session_state:
        st.session_state.period_type = "month"

    st.markdown(f'<div class="section-label">{t("period_type", lang)}</div>', unsafe_allow_html=True)
    st.session_state.period_type = segmented_control(
        [
            ("month", t("month", lang)),
            ("quarter", t("quarter", lang)),
            ("year", t("year", lang)),
            ("custom", t("custom", lang)),
        ],
        st.session_state.period_type,
        "period_type",
    )
    granularity = PERIOD_TO_GRANULARITY[st.session_state.period_type]

    filt_col1, filt_col2, filt_col3, filt_col4 = st.columns([2, 2, 2, 3])
    with filt_col1:
        selected_measures = st.multiselect(
            t("measures", lang), options=list(MEASURES.keys()), default=["revenue", "profit"],
            format_func=lambda k: t(k, lang), key="time_measures",
        )
    with filt_col2:
        group_by = st.multiselect(
            t("group_by", lang), options=["company", "location", "segment", "nace_name"],
            default=["location"], format_func=lambda k: t(k, lang), key="time_group_by",
        )
    with filt_col3:
        segment_filter = st.multiselect(
            t("segment", lang), options=sorted(companies_df["segment"].dropna().unique()), key="time_segment",
        )
    with filt_col4:
        default_range = (min_date, max_date) if selected_year is not None else (
            max(min_date, max_date - dt.timedelta(days=365)), max_date
        )
        date_range = st.date_input(
            t("date_range", lang), value=default_range,
            min_value=min_date, max_value=max_date, key=f"time_date_range_{selected_year}",
        )

    filters = {}
    if segment_filter:
        filters["segment"] = segment_filter
    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_range_param = date_range
    else:
        date_range_param = (min_date, max_date)

    if not selected_measures:
        st.info(t("select_measure", lang))
        return

    st.write("")
    totals = get_measure("profit", group_by=[], date_range=date_range_param, filters=filters)
    kpi_cols = st.columns(len(selected_measures))
    for i, m in enumerate(selected_measures):
        value = totals[m].iloc[0] if m in totals.columns and not totals.empty else None
        with kpi_cols[i]:
            kpi_tile(t(m, lang), FORMATTERS.get(m, str)(value) if value is not None else "—", theme)

    st.write("")
    st.markdown(f'<div class="section-label">{t("over_time", lang)}</div>', unsafe_allow_html=True)
    for m in selected_measures:
        ts_df = get_measure(m, group_by=[], date_range=date_range_param, granularity=granularity, filters=filters)
        if ts_df.empty or "period" not in ts_df.columns:
            continue
        y_col = m if m in ts_df.columns else "profit"
        fig = line_over_time(ts_df.sort_values("period"), "period", y_col, None, t(m, lang), theme)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if group_by:
        st.write("")
        st.markdown(f'<div class="section-label">{t("breakdown", lang)}</div>', unsafe_allow_html=True)

        restricted = any(d in CUSTOMER_ATTR_DIMS for d in group_by)
        breakdown_measures = [
            m for m in selected_measures if not restricted or m in BREAKDOWN_SAFE_MEASURES
        ]
        if restricted and len(breakdown_measures) < len(selected_measures):
            st.caption(f"ℹ️ {t('cost_by_dimension_note', lang)}")

        bcols = st.columns(min(2, len(breakdown_measures)) or 1)
        for i, m in enumerate(breakdown_measures):
            df = get_measure(m, group_by=group_by, date_range=date_range_param, filters=filters)
            if df.empty:
                continue
            y_col = m if m in df.columns else "profit"
            x_col = group_by[0]
            sorted_df = df.sort_values(y_col, ascending=False).head(20)
            fig = bar_breakdown(
                sorted_df, x_col, y_col, group_by[1] if len(group_by) > 1 else None, t(m, lang), theme,
            )
            with bcols[i % len(bcols)]:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.write("")
    st.markdown(f'<div class="section-label">{t("compare_periods", lang)}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if selected_year is not None:
        # A single year is pinned globally — compare its two halves rather
        # than an arbitrary trailing-days window that no longer applies.
        midpoint = dt.date(selected_year, 7, 1)
        default_a = (min_date, midpoint - dt.timedelta(days=1))
        default_b = (midpoint, max_date)
    else:
        default_a = (max_date - dt.timedelta(days=455), max_date - dt.timedelta(days=365))
        default_b = (max_date - dt.timedelta(days=90), max_date)
    with col1:
        st.caption(t("period_a", lang))
        period_a = st.date_input(
            "period_a_input", value=default_a,
            min_value=min_date, max_value=max_date, key=f"period_a_{selected_year}", label_visibility="collapsed",
        )
    with col2:
        st.caption(t("period_b", lang))
        period_b = st.date_input(
            "period_b_input", value=default_b,
            min_value=min_date, max_value=max_date, key=f"period_b_{selected_year}", label_visibility="collapsed",
        )

    if (
        isinstance(period_a, tuple) and len(period_a) == 2
        and isinstance(period_b, tuple) and len(period_b) == 2
    ):
        totals_a = get_measure("profit", group_by=[], date_range=period_a, filters=filters)
        totals_b = get_measure("profit", group_by=[], date_range=period_b, filters=filters)
        cols = st.columns(len(selected_measures))
        for i, m in enumerate(selected_measures):
            val_a = totals_a[m].iloc[0] if m in totals_a.columns and not totals_a.empty else None
            val_b = totals_b[m].iloc[0] if m in totals_b.columns and not totals_b.empty else None
            with cols[i]:
                delta = format_delta_pct(val_b, val_a) if val_a is not None and val_b is not None else None
                kpi_tile(
                    f"{t(m, lang)} — B", FORMATTERS.get(m, str)(val_b) if val_b is not None else "—",
                    theme, delta=delta,
                )
