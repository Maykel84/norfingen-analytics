import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_available_years,
    get_city_density,
    get_monthly_trend_for_year,
    get_multi_year_trend,
    get_yearly_totals,
)
from ui.charts import coverage_map, line_over_time
from ui.components import format_currency, format_pct, kpi_tile, year_switcher
from ui.i18n import t


def render(lang: str, theme: str) -> None:
    years = get_available_years()

    if "overview_year" not in st.session_state:
        st.session_state.overview_year = "all"

    st.markdown(f'<div class="section-label">{t("date_range", lang)}</div>', unsafe_allow_html=True)
    st.session_state.overview_year = year_switcher(
        years, st.session_state.overview_year, t("all_years", lang)
    )
    selected_year = None if st.session_state.overview_year == "all" else int(st.session_state.overview_year)

    totals = get_yearly_totals(selected_year)
    trend_df = get_monthly_trend_for_year(selected_year) if selected_year else get_multi_year_trend()

    st.write("")
    cols = st.columns(5)
    with cols[0]:
        kpi_tile(
            t("revenue", lang), format_currency(totals["revenue"]), theme,
            spark_values=trend_df["revenue"] if "revenue" in trend_df.columns else None,
        )
    with cols[1]:
        kpi_tile(
            t("cost", lang), format_currency(totals["cost"]), theme,
            spark_values=trend_df["cost"] if "cost" in trend_df.columns else None,
        )
    with cols[2]:
        kpi_tile(
            t("profit", lang), format_currency(totals["profit"]), theme,
            spark_values=trend_df["profit"] if "profit" in trend_df.columns else None,
        )
    with cols[3]:
        kpi_tile(t("margin_pct", lang), format_pct(totals["margin_pct"]), theme)
    with cols[4]:
        kpi_tile(t("client_count", lang), f"{totals['company_count']:,}", theme)

    st.write("")
    trend_col, map_col = st.columns([3, 2])

    with trend_col:
        st.markdown(f'<div class="section-label">{t("history", lang)}</div>', unsafe_allow_html=True)
        history_df = get_multi_year_trend()
        if not history_df.empty:
            melted = history_df.melt(
                id_vars=["period"], value_vars=["revenue", "cost", "profit"], var_name="measure", value_name="value"
            )
            melted["measure"] = melted["measure"].map(lambda m: t(m, lang))
            fig = line_over_time(melted, "period", "value", "measure", "", theme)
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with map_col:
        st.markdown(f'<div class="section-label">{t("coverage", lang)}</div>', unsafe_allow_html=True)
        density_df = get_city_density()
        from data.geocoding import CITY_COORDINATES

        density_df["lat"] = density_df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[0])
        density_df["lon"] = density_df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[1])
        density_df = density_df.dropna(subset=["lat", "lon"])
        if not density_df.empty:
            fig_map = coverage_map(density_df, "company_count", theme, "")
            fig_map.update_layout(height=420)
            st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
