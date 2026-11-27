import pandas as pd
import streamlit as st

from semantic.metrics import (
    BALANCE_ASSET_SERIES, BALANCE_EQUITY_SERIES, BALANCE_LIABILITY_SERIES, balance_check_max, get_balance_monthly,
    get_fixed_assets_monthly, get_partial_months_in_range,
)
from ui.charts import SEQUENTIAL, SEQUENTIAL_WARM, line_over_time, ramp_colors, stacked_bars_colored
from ui.components import format_currency, format_pct, kpi_tile
from ui.i18n import t


def _section(label: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


def _series(df: pd.DataFrame, columns: tuple[str, ...], ramp: list[str], lang: str) -> list[tuple[str, str, str]]:
    """(column, translated label, colour) for the columns that carry any value in the view."""
    used = [c for c in columns if (df[c].abs() > 0.005).any()]
    return [(c, t(f"bs_{c}", lang), col) for c, col in zip(used, ramp_colors(ramp, len(used)))]


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """Balance sheet at every month end (v_balance_monthly). Balances are cumulative since
    the first voucher: the year selector only slices the view, it never re-bases a balance."""
    with st.spinner(t("loading_data", lang)):
        balance = get_balance_monthly()
        fixed = get_fixed_assets_monthly()

    view = balance[balance["period"].dt.year == selected_year] if selected_year is not None else balance
    fixed_view = fixed[fixed["period"].isin(view["period"])]
    full = view[~view["is_partial"]]
    if full.empty:
        st.info(t("bs_no_full_month", lang))
        return
    open_months = get_partial_months_in_range((view["period"].min().date(), view["period"].max().date()))
    open_months = [m for m in open_months if m in set(view["period"].dt.date)]

    # ---- KPI cards: latest FULL month -----------------------------------------
    latest = full.iloc[-1]
    assets, equity = float(latest["total_assets"]), float(latest["total_equity"])
    net_debt = float(latest["long_term_debt"]) - float(latest["cash"])
    cols = st.columns(4)
    with cols[0]:
        kpi_tile(t("bs_total_assets", lang), format_currency(assets), theme)
    with cols[1]:
        kpi_tile(t("bs_total_equity", lang), format_currency(equity), theme)
    with cols[2]:
        kpi_tile(t("bs_equity_ratio", lang), format_pct(equity / assets * 100 if assets else None), theme)
    with cols[3]:
        kpi_tile(t("bs_net_debt", lang), format_currency(net_debt), theme)
    as_of = latest["period"].strftime("%Y-%m")
    st.caption(f"ℹ️ {t('bs_as_of', lang).format(month=as_of)}. {t('bs_net_debt_note', lang)}")

    # ---- assets by type ----------------------------------------------------------
    st.write("")
    _section(t("bs_assets_chart", lang))
    fig = stacked_bars_colored(
        view, "period", _series(view, BALANCE_ASSET_SERIES, SEQUENTIAL[theme], lang), theme,
        partial_periods=open_months, partial_label=t("partial_month_label", lang), y_title=t("amount", lang),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- liabilities and equity: debt in the orchid ramp, equity in cobalt ---------
    _section(t("bs_liab_equity_chart", lang))
    liab = _series(view, BALANCE_LIABILITY_SERIES, SEQUENTIAL_WARM[theme], lang)
    eq = _series(view, BALANCE_EQUITY_SERIES, SEQUENTIAL[theme], lang)
    fig = stacked_bars_colored(
        view, "period", liab + eq, theme,
        partial_periods=open_months, partial_label=t("partial_month_label", lang), y_title=t("amount", lang),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if open_months:
        st.caption(f"ℹ️ {t('bs_open_note', lang)}")

    # ---- fixed assets: cost vs accumulated depreciation (accounts 1200 / 1209) --------
    _section(t("bs_fixed_assets_chart", lang))
    labels = {"cost": t("bs_fixed_cost", lang), "accumulated_depreciation": t("bs_fixed_acc_dep", lang), "net": t("bs_fixed_net", lang)}
    melted = fixed_view.melt(id_vars=["period"], value_vars=list(labels), var_name=t("measure_label", lang), value_name="value")
    melted[t("measure_label", lang)] = melted[t("measure_label", lang)].map(labels)
    fig = line_over_time(
        melted, "period", "value", t("measure_label", lang), "", theme, value_suffix=" kr",
        x_title=t("month", lang), y_title=t("amount", lang), granularity="month",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- balance check (all months, not just the view) ---------------------------------
    worst = balance_check_max(balance)
    check_text = t("bs_check_ok" if worst < 0.005 else "bs_check_bad", lang).format(value=f"{worst:,.2f}", n=len(balance))
    if worst < 0.005:
        st.caption(f"✓ {check_text}")
    else:
        st.warning(check_text)
    st.caption(t("bs_footnote", lang))
