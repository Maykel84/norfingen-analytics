import pandas as pd
import streamlit as st

from semantic.metrics import get_city_density, get_multi_year_trend, get_yearly_totals
from ui.charts import coverage_map, line_over_time
from ui.components import format_currency, format_pct, kpi_tile
from ui.i18n import t


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year (None = all years) comes from the global year selector
    in the header, next to the brand — shared with the Operations tab so
    both respect the same "which year" filter rather than each having its
    own control."""
    with st.spinner(t("loading_data", lang)):
        totals = get_yearly_totals(selected_year)

        cols = st.columns(5)
        with cols[0]:
            kpi_tile(t("revenue", lang), format_currency(totals["revenue"]), theme)
        with cols[1]:
            kpi_tile(t("cost", lang), format_currency(totals["cost"]), theme)
        with cols[2]:
            kpi_tile(t("profit", lang), format_currency(totals["profit"]), theme)
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
                    id_vars=["period"], value_vars=["revenue", "cost", "profit"],
                    var_name=t("measure_label", lang), value_name="value",
                )
                measure_col = t("measure_label", lang)
                melted[measure_col] = melted[measure_col].map(lambda m: t(m, lang))
                fig = line_over_time(
                    melted, "period", "value", measure_col, "", theme, value_suffix=" kr",
                    x_title=t("year", lang), y_title=t("amount", lang), granularity="year",
                )
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
