import datetime as dt

import pandas as pd
import streamlit as st

from data.geocoding import CITY_COORDINATES
from semantic.metrics import get_client_history, get_client_projects, get_client_summary, get_date_bounds
from ui.charts import company_scatter_map, grouped_bar_compare, line_over_time
from ui.components import format_currency, format_int, kpi_tile, segmented_control
from ui.i18n import t, t_sector

MAX_COMPARE = 3


def _ensure_state():
    if "compare_list" not in st.session_state:
        st.session_state.compare_list = []
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    if "clients_view" not in st.session_state:
        st.session_state.clients_view = "list"


def _toggle_compare(name: str, checked: bool):
    lst = st.session_state.compare_list
    if checked and name not in lst and len(lst) < MAX_COMPARE:
        lst.append(name)
    elif not checked and name in lst:
        lst.remove(name)
    st.session_state.compare_list = lst


def _render_list(lang: str, theme: str, summary: pd.DataFrame):
    st.caption(f"ℹ️ {t('no_cost_note', lang)}")
    col_search, col_sector, col_size = st.columns([3, 2, 2])
    with col_search:
        query = st.text_input(t("search_clients", lang), key="client_search")
    with col_sector:
        sector_filter = st.multiselect(
            t("sector", lang), options=sorted(summary["sector"].dropna().unique()), key="client_sector",
            format_func=lambda s: t_sector(s, lang),
        )
    with col_size:
        size_filter = st.multiselect(
            t("size_band", lang), options=["Small", "Medium", "Large"], key="client_size"
        )

    filtered = summary.copy()
    if query:
        filtered = filtered[filtered["name"].str.contains(query, case=False, na=False)]
    if sector_filter:
        filtered = filtered[filtered["sector"].isin(sector_filter)]
    if size_filter:
        filtered = filtered[filtered["size_band"].astype(str).isin(size_filter)]
    filtered = filtered.sort_values("revenue", ascending=False)

    if st.session_state.compare_list:
        bar1, bar2 = st.columns([5, 1])
        with bar1:
            st.caption(f"{t('compare_limit', lang)}: {', '.join(st.session_state.compare_list)}")
        with bar2:
            if st.button(t("clear_compare", lang), key="clear_compare_btn"):
                st.session_state.compare_list = []
                st.rerun()
        if len(st.session_state.compare_list) >= 2:
            if st.button(t("compare_selected", lang), key="go_compare_btn", type="primary"):
                st.session_state.clients_view = "compare"
                st.rerun()

    at_cap = len(st.session_state.compare_list) >= MAX_COMPARE

    for _, row in filtered.head(60).iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            with c1:
                st.markdown(f"**{row['name']}**")
                st.caption(f"{t_sector(row['sector'], lang)} · {row['size_band']}")
            with c2:
                st.markdown(f"{t('revenue', lang)}")
                st.markdown(f"**{format_currency(row['revenue'])}**")
            with c3:
                st.markdown(f"{t('order_count', lang)}")
                st.markdown(f"**{format_int(row['order_count'])}**")
            with c4:
                if st.button(t("client_profile", lang), key=f"view_{row['id']}", use_container_width=True):
                    st.session_state.selected_client = row["name"]
                    st.session_state.clients_view = "detail"
                    st.rerun()
            with c5:
                is_checked = row["name"] in st.session_state.compare_list
                disabled = at_cap and not is_checked
                checked = st.checkbox(
                    t("add_to_compare", lang), value=is_checked, key=f"cmp_{row['id']}",
                    disabled=disabled, help=t("compare_limit", lang) if disabled else None,
                )
                if checked != is_checked:
                    _toggle_compare(row["name"], checked)
                    st.rerun()
            st.markdown("<hr style='margin:4px 0'>", unsafe_allow_html=True)


def _render_detail(lang: str, theme: str, summary: pd.DataFrame, date_range: tuple | None):
    name = st.session_state.selected_client
    row = summary[summary["name"] == name]
    if row.empty:
        st.session_state.clients_view = "list"
        st.rerun()
        return
    row = row.iloc[0]

    if st.button(f"← {t('back_to_list', lang)}", key="back_btn"):
        st.session_state.clients_view = "list"
        st.rerun()

    st.markdown(f"### {name}")
    st.caption(f"{t_sector(row['sector'], lang)} · {row['size_band']} · {row.get('city', '')}")

    st.caption(f"ℹ️ {t('no_cost_note', lang)}")
    cols = st.columns(3)
    revenue_label = t("revenue", lang) if date_range else t("lifetime_revenue", lang)
    with cols[0]:
        kpi_tile(revenue_label, format_currency(row["revenue"]), theme)
    with cols[1]:
        kpi_tile(t("order_count", lang), format_int(row["order_count"]), theme)

    st.write("")
    map_col, history_col = st.columns([1, 2])
    with map_col:
        st.markdown(f'<div class="section-label">{t("client_map", lang)}</div>', unsafe_allow_html=True)
        lat, lon = CITY_COORDINATES.get(row.get("city"), (None, None))
        if lat is not None:
            point_df = pd.DataFrame(
                {
                    "name": [name], "city": [row.get("city")], "lat": [lat], "lon": [lon],
                    "revenue": [max(row["revenue"], 1)], "order_count": [row["order_count"]],
                }
            )
            fig = company_scatter_map(
                point_df, "revenue", "revenue", "order_count", t("order_count", lang), "", theme,
                hover_extra_label=t("city", lang), color_label=t("revenue", lang),
            )
            with st.container(key="map_card"):
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with history_col:
        st.markdown(f'<div class="section-label">{t("history", lang)}</div>', unsafe_allow_html=True)
        if "client_period_type" not in st.session_state:
            st.session_state.client_period_type = "month"
        segmented_control(
            [
                ("month", t("month", lang)), ("quarter", t("quarter", lang)),
                ("year", t("year", lang)),
            ],
            st.session_state.client_period_type, "client_period_type",
            state_key="client_period_type",
        )
        history_df = get_client_history(name, st.session_state.client_period_type, date_range)
        if not history_df.empty and "period" in history_df.columns:
            fig = line_over_time(
                history_df.sort_values("period"), "period", "revenue", None, t("revenue", lang), theme,
                x_title=t(st.session_state.client_period_type, lang), y_title=t("revenue", lang),
                granularity=st.session_state.client_period_type,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    projects_df = get_client_projects(name)
    if not projects_df.empty:
        st.write("")
        st.markdown(f'<div class="section-label">{t("projects", lang)}</div>', unsafe_allow_html=True)
        table = projects_df.rename(
            columns={
                "number": t("project_number", lang), "name": t("project_name", lang),
                "status": t("status", lang), "start_date": t("start_date", lang), "end_date": t("end_date", lang),
            }
        )
        st.dataframe(table, use_container_width=True, hide_index=True)


def _render_compare(lang: str, theme: str, summary: pd.DataFrame):
    names = st.session_state.compare_list
    if st.button(f"← {t('back_to_list', lang)}", key="back_from_compare"):
        st.session_state.clients_view = "list"
        st.rerun()

    subset = summary[summary["name"].isin(names)]
    st.markdown(f"### {t('compare_selected', lang)}")
    st.caption(f"ℹ️ {t('no_cost_note', lang)}")

    table = subset[["name", "sector", "size_band", "revenue", "order_count"]].copy()
    table["sector"] = table["sector"].map(lambda s: t_sector(s, lang))
    table.columns = [
        t("company", lang), t("sector", lang), t("size_band", lang), t("revenue", lang), t("order_count", lang),
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_rev = grouped_bar_compare(
            subset, "name", "revenue", "name", t("revenue", lang), theme,
            x_title=t("company", lang), y_title=t("revenue", lang),
        )
        st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})
    with chart_col2:
        fig_orders = grouped_bar_compare(
            subset, "name", "order_count", "name", t("order_count", lang), theme,
            x_title=t("company", lang), y_title=t("order_count", lang),
        )
        st.plotly_chart(fig_orders, use_container_width=True, config={"displayModeBar": False})

    map_rows = []
    for _, r in subset.iterrows():
        lat, lon = CITY_COORDINATES.get(r.get("city"), (None, None))
        if lat is not None:
            map_rows.append(
                {"name": r["name"], "city": r["city"], "lat": lat, "lon": lon,
                 "revenue": max(r["revenue"], 1), "order_count": r["order_count"]}
            )
    if map_rows:
        map_df = pd.DataFrame(map_rows)
        fig_map = company_scatter_map(
            map_df, "revenue", "revenue", "order_count", t("order_count", lang), "", theme,
            hover_extra_label=t("city", lang), color_label=t("revenue", lang),
        )
        with st.container(key="map_card"):
            st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """selected_year comes from the header's global year selector — revenue/
    order counts here become "this year" instead of lifetime when it's set,
    consistently with every other tab."""
    _ensure_state()
    date_range = (dt.date(selected_year, 1, 1), dt.date(selected_year, 12, 31)) if selected_year else None
    summary = get_client_summary(date_range=date_range)

    if st.session_state.clients_view == "detail" and st.session_state.selected_client:
        _render_detail(lang, theme, summary, date_range)
    elif st.session_state.clients_view == "compare" and st.session_state.compare_list:
        _render_compare(lang, theme, summary)
    else:
        st.session_state.clients_view = "list"
        _render_list(lang, theme, summary)
