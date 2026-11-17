import datetime as dt

import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_companies, get_date_bounds, get_measure, get_partial_months_in_range, snap_to_full_months,
)
from semantic.schema import MEASURES
from ui.charts import bar_breakdown, line_over_time, measure_color
from ui.components import format_currency, format_delta_pct, format_int, format_pct, kpi_tile, partial_month_caption, segmented_control
from ui.i18n import t, t_sector

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
    segmented_control(
        [
            ("month", t("month", lang)),
            ("quarter", t("quarter", lang)),
            ("year", t("year", lang)),
            ("custom", t("custom", lang)),
        ],
        st.session_state.period_type,
        "period_type",
        state_key="period_type",
    )
    granularity = PERIOD_TO_GRANULARITY[st.session_state.period_type]

    # Two rows (Measures+Group by, then Segment+Date range) rather than all
    # four crammed into one row — same controls, same widths relative to
    # their row, just clearer visual grouping.
    row1_col1, row1_col2 = st.columns([2, 2])
    with row1_col1:
        selected_measures = st.multiselect(
            t("measures", lang), options=list(MEASURES.keys()), default=["revenue", "profit"],
            format_func=lambda k: t(k, lang), key="time_measures",
        )
    with row1_col2:
        group_by = st.multiselect(
            t("group_by", lang), options=["company", "location", "segment", "nace_name"],
            default=["location"], format_func=lambda k: t(k, lang), key="time_group_by",
        )

    row2_col1, row2_col2 = st.columns([2, 3])
    with row2_col1:
        segment_filter = st.multiselect(
            t("segment", lang), options=sorted(companies_df["segment"].dropna().unique()), key="time_segment",
        )
    with row2_col2:
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
    with st.spinner(t("loading_data", lang)):
        # Profit/cost/margin only make sense over whole months: snap the picked range
        # (start -> 1st, end -> last day of the last FULL month). Revenue/orders keep
        # the exact dates only for an explicit custom range.
        snapped = snap_to_full_months(date_range_param)
        is_custom = st.session_state.period_type == "custom"
        totals = get_measure("profit", group_by=[], date_range=snapped, filters=filters) if snapped else None
        exact = get_measure("profit", group_by=[], date_range=date_range_param, filters=filters) if is_custom else None
        exact_measures = ("revenue", "order_count") if is_custom else ()
        kpi_cols = st.columns(len(selected_measures))
        for i, m in enumerate(selected_measures):
            source = exact if m in exact_measures else totals
            value = source[m].iloc[0] if source is not None and m in source.columns and not source.empty else None
            with kpi_cols[i]:
                kpi_tile(t(m, lang), FORMATTERS.get(m, str)(value) if value is not None else "—", theme)
        if snapped is None:
            st.caption(f"ℹ️ {t('no_full_month', lang)}")
        else:
            a_label, b_label = f"{snapped[0]:%Y-%m}", f"{snapped[1]:%Y-%m}"
            aligned = date_range_param[0] == snapped[0] and date_range_param[1] == snapped[1]
            if is_custom and not aligned:
                st.warning(t("range_unaligned_warning", lang).format(start=a_label, end=b_label))
            elif not is_custom:
                st.caption(f"ℹ️ {t('range_aligned', lang).format(start=a_label, end=b_label)}")
            st.caption(t("profit_definition", lang))

        # KPI, series and breakdown must describe the same months: outside a custom range the
        # series start at the 1st of the first month (a half-month point is not a result) and
        # the breakdown uses exactly the KPI's aligned range.
        series_range = (snapped[0], date_range_param[1]) if (snapped and not is_custom) else date_range_param
        breakdown_range = snapped if (snapped and not is_custom) else date_range_param
        open_months = get_partial_months_in_range(series_range)

        st.write("")
        st.markdown(f'<div class="section-label">{t("over_time", lang)}</div>', unsafe_allow_html=True)
        for m in selected_measures:
            ts_df = get_measure(
                m, group_by=[], date_range=series_range, granularity=granularity, filters=filters,
            )
            if ts_df.empty or "period" not in ts_df.columns:
                continue
            y_col = m if m in ts_df.columns else "profit"
            fig = line_over_time(
                ts_df.sort_values("period"), "period", y_col, None, t(m, lang), theme,
                x_title=t(granularity, lang), y_title=t(m, lang), granularity=granularity,
                line_color=measure_color(m, theme),
                partial_periods=open_months if granularity == "month" and m in ("cost", "profit", "margin_pct") else None,
                partial_label=t("partial_month_label", lang),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if granularity == "month" and any(m in ("cost", "profit", "margin_pct") for m in selected_measures):
            partial_month_caption(open_months, lang)

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
                df = get_measure(m, group_by=group_by, date_range=breakdown_range, filters=filters)
                if df.empty:
                    continue
                y_col = m if m in df.columns else "profit"
                x_col = group_by[0]
                sorted_df = df.sort_values(y_col, ascending=False).head(20)
                if x_col == "nace_name":
                    sorted_df = sorted_df.copy()
                    sorted_df[x_col] = sorted_df[x_col].map(lambda s: t_sector(s, lang))
                color_col = None
                if len(group_by) > 1:
                    if group_by[1] == "nace_name":
                        sorted_df[group_by[1]] = sorted_df[group_by[1]].map(lambda s: t_sector(s, lang))
                    color_col = t(group_by[1], lang)
                    sorted_df = sorted_df.rename(columns={group_by[1]: color_col})
                fig = bar_breakdown(
                    sorted_df, x_col, y_col, color_col, t(m, lang), theme,
                    x_title=t(group_by[0], lang), y_title=t(m, lang),
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
    # Bounded by the full data range (data_min/data_max), not min_date/
    # max_date — those are clipped to the globally-selected year, which
    # would make it impossible to compare e.g. March 2020 against March
    # 2023 whenever a single year is pinned. Comparing across years is the
    # whole point of this section, so it stays unrestricted regardless of
    # the year selector up top.
    with col1:
        st.caption(t("period_a", lang))
        period_a = st.date_input(
            "period_a_input", value=default_a,
            min_value=data_min, max_value=data_max, key=f"period_a_{selected_year}", label_visibility="collapsed",
        )
    with col2:
        st.caption(t("period_b", lang))
        period_b = st.date_input(
            "period_b_input", value=default_b,
            min_value=data_min, max_value=data_max, key=f"period_b_{selected_year}", label_visibility="collapsed",
        )

    if (
        isinstance(period_a, tuple) and len(period_a) == 2
        and isinstance(period_b, tuple) and len(period_b) == 2
    ):
        snap_a, snap_b = snap_to_full_months(period_a), snap_to_full_months(period_b)
        totals_a = get_measure("profit", group_by=[], date_range=snap_a, filters=filters) if snap_a else pd.DataFrame()
        totals_b = get_measure("profit", group_by=[], date_range=snap_b, filters=filters) if snap_b else pd.DataFrame()
        if snap_a and snap_b:
            st.caption(f"ℹ️ A: {snap_a[0]:%Y-%m} … {snap_a[1]:%Y-%m} · B: {snap_b[0]:%Y-%m} … {snap_b[1]:%Y-%m} (full months)")
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
