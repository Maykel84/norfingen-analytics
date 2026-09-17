"""Reusable UI pieces: nav shell, KPI tiles, year switcher, segmented control,
client cards. Built against the tokens in ui/theme.py.
"""

import streamlit as st

from ui.charts import sparkline
from ui.theme import tokens


def format_currency(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f} kr"


def format_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.1f}%"


def format_int(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}"


def format_delta_pct(current: float, previous: float) -> str | None:
    if previous in (None, 0) or current is None:
        return None
    change = (current - previous) / abs(previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


def kpi_tile(label: str, value: str, theme: str, delta: str | None = None, spark_values=None) -> None:
    t = tokens(theme)
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-up" if delta.startswith("+") else "kpi-delta-down" if delta.startswith("-") else ""
        delta_html = f'<div class="{cls}">{delta}</div>'
    st.markdown(
        f"""
        <div class="kpi-tile">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if spark_values is not None and len(spark_values) > 1:
        positive = spark_values.iloc[-1] >= spark_values.iloc[0]
        fig = sparkline(spark_values, theme, positive=positive)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"spark_{label}")


def nav_bar(active: str, lang: str, theme: str, t_func) -> tuple[str, str, str]:
    """Renders the persistent top nav shell. Returns (new_active, new_lang, new_theme)."""
    from ui.i18n import LANGUAGES

    new_active, new_lang, new_theme = active, lang, theme
    with st.container(key="app_nav"):
        left, mid, right = st.columns([2, 5, 3])
        with left:
            st.markdown(f'<div class="brand">◆ {t_func("app_title", lang)}</div>', unsafe_allow_html=True)

        nav_items = [
            ("overview", t_func("nav_overview", lang)),
            ("time", t_func("nav_time", lang)),
            ("clients", t_func("nav_clients", lang)),
        ]
        with mid:
            cols = st.columns(len(nav_items))
            for col, (key, label) in zip(cols, nav_items):
                with col:
                    btn_type = "primary" if key == active else "secondary"
                    if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                        new_active = key

        with right:
            c1, c2 = st.columns(2)
            with c1:
                new_lang = st.selectbox(
                    "lang", options=list(LANGUAGES.keys()), format_func=lambda k: k.upper(),
                    index=list(LANGUAGES.keys()).index(lang), key="lang_select", label_visibility="collapsed",
                )
            with c2:
                new_theme = st.selectbox(
                    "theme", options=["light", "dark"], format_func=lambda k: "☀" if k == "light" else "☾",
                    index=["light", "dark"].index(theme), key="theme_select", label_visibility="collapsed",
                )
    return new_active, new_lang, new_theme


def year_switcher(years: list[int], selected: str | int, label_all: str) -> str | int:
    """Row of pill buttons: one per year + 'All years'. Returns the selection."""
    options = ["all"] + list(years)
    cols = st.columns(len(options))
    result = selected
    for col, opt in zip(cols, options):
        with col:
            label = f"📅 {label_all}" if opt == "all" else f"🗓 {opt}"
            btn_type = "primary" if opt == selected else "secondary"
            if st.button(label, key=f"year_{opt}", use_container_width=True, type=btn_type):
                result = opt
    return result


def segmented_control(options: list[tuple[str, str]], selected: str, key_prefix: str) -> str:
    """options: list of (value, label). Returns selected value."""
    cols = st.columns(len(options))
    result = selected
    for col, (value, label) in zip(cols, options):
        with col:
            btn_type = "primary" if value == selected else "secondary"
            if st.button(label, key=f"{key_prefix}_{value}", use_container_width=True, type=btn_type):
                result = value
    return result


def client_card_html(name: str, sector: str, size_band: str, revenue: float, order_count: int, theme: str) -> str:
    return f"""
    <div class="client-card">
        <div class="name">{name}</div>
        <div class="meta">{sector} · {size_band}</div>
        <div style="margin-top:8px;display:flex;justify-content:space-between;">
            <div>
                <div class="kpi-label" style="margin-bottom:0;">Revenue</div>
                <div style="font-weight:700;font-variant-numeric:tabular-nums;">{format_currency(revenue)}</div>
            </div>
            <div>
                <div class="kpi-label" style="margin-bottom:0;">Orders</div>
                <div style="font-weight:700;font-variant-numeric:tabular-nums;">{format_int(order_count)}</div>
            </div>
        </div>
    </div>
    """
