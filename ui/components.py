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


def nav_bar(
    active: str, lang: str, theme: str, t_func, years: list[int] | None = None, selected_year: str | int = "all",
) -> tuple[str, str, str, str | int]:
    """Renders the persistent two-row header. Returns
    (new_active, new_lang, new_theme, new_year).

    Row 1 ("identity_bar"): wordmark + a global year selector + language/
    theme icon buttons — a slim settings/identity strip, no card background,
    sitting directly on the page. Row 2 ("app_nav"): the Today/Overview/Time
    Analysis/Clients/Operations tabs. The year selector lives here (next to
    the brand) rather than duplicated per-page, since both Overview and
    Operations need the same "which year" filter.
    """
    from ui.i18n import LANGUAGES, NAV_ITEMS

    new_active, new_lang, new_theme, new_year = active, lang, theme, selected_year

    show_year = years and active != "today"

    with st.container(key="identity_bar"):
        if show_year:
            left, year_col, mid, right = st.columns([2, 2, 2, 2])
        else:
            left, mid, right = st.columns([4, 2, 2])
        with left:
            c = tokens(theme)
            # Three ascending bars in the exact chart-categorical palette
            # (sage/terracotta/slate, ui/charts.py's CATEGORICAL) rather
            # than a generic "◆" bullet — a small, literal nod to what the
            # product actually does (an analytics/reporting app), and it
            # reuses colors already meaningful everywhere else in the UI
            # instead of introducing a new one just for the wordmark.
            logo_svg = f"""
            <svg width="26" height="26" viewBox="0 0 18 18" fill="none"
                 xmlns="http://www.w3.org/2000/svg" class="brand-mark">
                <rect x="1" y="10" width="4" height="7" rx="1.2" fill="{c['sage']}"/>
                <rect x="7" y="5" width="4" height="12" rx="1.2" fill="{c['terracotta']}"/>
                <rect x="13" y="0" width="4" height="17" rx="1.2" fill="{c['slate']}"/>
            </svg>
            """
            st.markdown(
                f'<div class="brand">{logo_svg}<span>{t_func("app_title", lang)}</span></div>',
                unsafe_allow_html=True,
            )
        if show_year:
            with year_col:
                with st.container(key="select_years"):
                    options = ["all"] + list(years)
                    labels = {"all": t_func("all_years", lang), **{y: str(y) for y in years}}
                    index = options.index(selected_year) if selected_year in options else 0
                    new_year = st.selectbox(
                        "year", options=options, index=index, format_func=lambda o: labels.get(o, str(o)),
                        key="global_year_select", label_visibility="collapsed",
                    )
        with mid:
            with st.container(key="toggle_lang"):
                lang_cols = st.columns(len(LANGUAGES))
                for col, code in zip(lang_cols, LANGUAGES.keys()):
                    with col:
                        btn_type = "primary" if code == lang else "secondary"
                        if st.button(code.upper(), key=f"lang_{code}", use_container_width=True, type=btn_type):
                            new_lang = code
        with right:
            with st.container(key="toggle_theme"):
                t_cols = st.columns(2)
                with t_cols[0]:
                    if st.button("☀", key="theme_light", use_container_width=True, type="primary" if theme == "light" else "secondary"):
                        new_theme = "light"
                with t_cols[1]:
                    if st.button("☾", key="theme_dark", use_container_width=True, type="primary" if theme == "dark" else "secondary"):
                        new_theme = "dark"

    with st.container(key="app_nav"):
        cols = st.columns(len(NAV_ITEMS))
        for col, key in zip(cols, NAV_ITEMS):
            with col:
                label = t_func(f"nav_{key}", lang)
                btn_type = "primary" if key == active else "secondary"
                if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                    new_active = key

    return new_active, new_lang, new_theme, new_year


def year_switcher(years: list[int], selected: str | int, label_all: str) -> str | int:
    """Single dropdown: 'All years' + one entry per year. Returns the selection.

    Wrapped in a "select_years" container so ui/theme.py can restyle the
    dropdown's chrome (border/radius/font) to match the app rather than
    Streamlit's default BaseWeb select look.
    """
    options = ["all"] + list(years)
    labels = {"all": f"📅 {label_all}", **{y: f"🗓 {y}" for y in years}}
    index = options.index(selected) if selected in options else 0
    with st.container(key="select_years"):
        result = st.selectbox(
            "year", options=options, index=index, format_func=lambda o: labels.get(o, str(o)),
            key="overview_year_select", label_visibility="collapsed",
        )
    return result


def segmented_control(
    options: list[tuple[str, str]], selected: str, key_prefix: str, state_key: str | None = None,
) -> str:
    """options: list of (value, label). Returns selected value.

    Wrapped in a "pill_<key_prefix>" container — see year_switcher's
    docstring for why this scoping matters.

    Pass state_key (the st.session_state key holding `selected`) to fix a
    one-rerun lag: Streamlit draws every button's primary/secondary style
    from `selected` BEFORE it learns which button was just clicked, so in
    the very rerun a click changes the value, the OLD option is still the
    one drawn highlighted — the new selection only looks right on some
    later, unrelated rerun. Writing the new value straight into session
    state and forcing an immediate st.rerun() here skips that stale frame
    entirely, so the clicked pill lights up right away. Without state_key,
    callers keep the old (laggy) assignment pattern.
    """
    result = selected
    with st.container(key=f"pill_{key_prefix}"):
        cols = st.columns(len(options))
        for col, (value, label) in zip(cols, options):
            with col:
                btn_type = "primary" if value == selected else "secondary"
                if st.button(label, key=f"{key_prefix}_{value}", use_container_width=True, type=btn_type):
                    result = value
    if state_key and result != selected:
        st.session_state[state_key] = result
        st.rerun()
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
