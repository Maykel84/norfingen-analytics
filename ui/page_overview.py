import datetime as dt

import pandas as pd
import streamlit as st

from semantic.metrics import (
    get_city_density, get_monthly_trend_for_year, get_multi_year_trend, get_partial_months_in_range, get_yearly_totals,
)
from ui.charts import coverage_map, line_over_time
from ui.components import format_currency, format_pct, kpi_tile, partial_month_caption
from ui.i18n import t
from ui.theme import tokens


_EXTRA_SERIES = ("ebitda", "depreciation", "financial_result", "tax", "net_result")


def _ratio_strip(totals: dict, lang: str, theme: str) -> None:
    """EBIT margin, net margin and client count in one card, three columns with thin dividers."""
    tk = tokens(theme)
    items = (
        (t("margin_pct", lang), format_pct(totals["margin_pct"])),
        (t("net_margin_pct", lang), format_pct(totals["net_margin_pct"])),
        (t("client_count", lang), f"{totals['company_count']:,}"),
    )
    label_css = (
        f"font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:{tk['text_muted']};"
    )
    cells = "".join(
        f'<div style="flex:1;padding:0 20px;{"border-left:1px solid " + tk["divider"] + ";" if i else ""}">'
        f'<div style="{label_css}">{label}</div>'
        f'<div style="font-size:22px;font-weight:600;color:{tk["text_primary"]};">{value}</div></div>'
        for i, (label, value) in enumerate(items)
    )
    st.markdown(
        f'<div style="background:{tk["surface"]};border-radius:16px;box-shadow:0 2px 10px {tk["shadow"]};'
        f'display:flex;padding:14px 0;">{cells}</div>',
        unsafe_allow_html=True,
    )


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year (None = all years) comes from the global year selector
    in the header, next to the brand — shared with the Operations tab so
    both respect the same "which year" filter rather than each having its
    own control. Both the History chart and the Coverage map must follow
    it: the chart switches from the full multi-year trend to that year's
    monthly breakdown, and the map narrows to companies active that year
    (previously neither was wired to selected_year at all — both always
    showed the full, unfiltered history regardless of the selector)."""
    date_range = (dt.date(selected_year, 1, 1), dt.date(selected_year, 12, 31)) if selected_year else None

    with st.spinner(t("loading_data", lang)):
        totals = get_yearly_totals(selected_year)

        # Row 1: the money, from revenue down to the net result. Row 2: the ratios and the client count.
        # Both rows use the same four columns so the tiles line up; a gap keeps the rows apart.
        amounts = st.columns(4)
        for col, (label, value) in zip(amounts, [
            (t("revenue", lang), totals["revenue"]), (t("cost", lang), totals["cost"]),
            (t("profit", lang), totals["profit"]), (t("net_result", lang), totals["net_result"]),
        ]):
            with col:
                kpi_tile(label, format_currency(value), theme)
        st.write("")
        _ratio_strip(totals, lang, theme)
        partial_month_caption(get_partial_months_in_range(date_range), lang, excluded=True)
        # Say what the two result lines are: EBIT (operating result) and the net result after
        # financial items and income tax — both from v_pl_monthly, full months only.
        st.caption(t("profit_definition", lang))
        st.caption(t("fin_items_note", lang).format(
            fin=format_currency(totals["financial_result"]), tax=format_currency(totals["tax"]),
        ))
        if totals["tax_pending_year"]:
            st.caption(t("tax_pending_note", lang).format(year=totals["tax_pending_year"]))

        st.write("")
        trend_col, map_col = st.columns([3, 2])

        with trend_col:
            st.markdown(f'<div class="section-label">{t("history", lang)}</div>', unsafe_allow_html=True)
            # The key carries the language so the tags are re-labelled on a language switch
            # (a plain key keeps the old-language labels); the choice is carried over by hand.
            extra = st.multiselect(
                t("extra_series", lang), options=list(_EXTRA_SERIES), key=f"overview_extra_series_{lang}",
                default=st.session_state.get("overview_extra_sel", []), format_func=lambda k: t(k, lang),
            )
            st.session_state["overview_extra_sel"] = extra
            if selected_year is not None:
                history_df = get_monthly_trend_for_year(selected_year)
                chart_granularity = "month"
            else:
                history_df = get_multi_year_trend()
                chart_granularity = "year"
            if not history_df.empty:
                melted = history_df.sort_values("period").melt(
                    id_vars=["period"], value_vars=["revenue", "cost", "profit", *extra],
                    var_name=t("measure_label", lang), value_name="value",
                )
                measure_col = t("measure_label", lang)
                melted[measure_col] = melted[measure_col].map(lambda m: t(m, lang))
                fig = line_over_time(
                    melted, "period", "value", measure_col, "", theme, value_suffix=" kr",
                    x_title=t(chart_granularity, lang), y_title=t("amount", lang), granularity=chart_granularity,
                    partial_periods=get_partial_months_in_range(date_range) if chart_granularity == "month" else None,
                    partial_label=t("partial_month_label", lang),
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                if chart_granularity == "month":
                    partial_month_caption(get_partial_months_in_range(date_range), lang)

        with map_col:
            st.markdown(f'<div class="section-label">{t("coverage", lang)}</div>', unsafe_allow_html=True)
            density_df = get_city_density(date_range)
            from data.geocoding import CITY_COORDINATES

            density_df["lat"] = density_df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[0])
            density_df["lon"] = density_df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[1])
            density_df = density_df.dropna(subset=["lat", "lon"])
            if not density_df.empty:
                fig_map = coverage_map(density_df, "company_count", theme, "")
                fig_map.update_layout(height=420)
                st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
