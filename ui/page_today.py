import datetime as dt

import streamlit as st

from semantic.metrics import (
    get_daily_snapshot,
    get_most_recent_activity_date,
    get_orders_invoice_payment_status,
    get_orders_window_stats,
)
from ui.components import format_currency, format_int, kpi_tile, segmented_control
from ui.i18n import t


def render(lang: str, theme: str) -> None:
    """Deliberately NOT scoped by the header's global year selector — this
    page is a live daily pulse-check, not a historical report; every other
    tab (Overview/Time Analysis/Clients/Operations) respects that selector,
    this one always looks at the real, current calendar."""
    today = dt.date.today()
    snapshot = get_daily_snapshot(today)
    shown_day = today
    if snapshot["order_count"] == 0:
        most_recent = get_most_recent_activity_date()
        if most_recent and most_recent < today:
            shown_day = most_recent
            st.caption(f"ℹ️ {t('most_recent_day', lang)} {shown_day.strftime('%Y-%m-%d')}")
            snapshot = get_daily_snapshot(shown_day)

    cols = st.columns(3)
    with cols[0]:
        kpi_tile(t("todays_revenue", lang), format_currency(snapshot["revenue"]), theme)
    with cols[1]:
        kpi_tile(t("todays_orders", lang), format_int(snapshot["order_count"]), theme)
    with cols[2]:
        kpi_tile(t("active_clients_today", lang), format_int(snapshot["client_count"]), theme)

    st.write("")
    st.markdown(f'<div class="section-label">{t("todays_activity", lang)}</div>', unsafe_allow_html=True)
    orders_df = snapshot["orders"]
    if orders_df.empty:
        st.caption(t("no_activity", lang))
    else:
        table = orders_df.rename(
            columns={"order_date": t("event_date", lang), "customer": t("company", lang), "amount": t("revenue", lang)}
        )
        table[t("revenue", lang)] = table[t("revenue", lang)].map(format_currency)
        table = table[[t("event_date", lang), t("company", lang), t("revenue", lang)]]
        st.dataframe(table, use_container_width=True, hide_index=True)

    st.write("")
    st.markdown(f'<div class="section-label">{t("recent_activity", lang)}</div>', unsafe_allow_html=True)
    # Two numbers of different units (a count and a currency amount) never
    # share one tile — "3 · 59,116 kr" reads as noise with no indication of
    # which number is which. Each gets its own clearly labeled tile instead.
    window_cols = st.columns(4)
    for i, days in enumerate((3, 7)):
        stats = get_orders_window_stats(shown_day, days)
        window_label = t("last_n_days", lang).format(n=days)
        with window_cols[i * 2]:
            kpi_tile(f"{window_label} — {t('revenue', lang)}", format_currency(stats["revenue"]), theme)
        with window_cols[i * 2 + 1]:
            kpi_tile(f"{window_label} — {t('order_count', lang)}", format_int(stats["order_count"]), theme)

    st.write("")
    # 🧾 matches the icon language already used elsewhere (the year
    # dropdown's 📅/🗓) — this section is the one place invoicing shows up,
    # so a recognizable glyph anchors it faster than text weight alone.
    st.markdown(
        f'<div class="section-label">🧾 {t("invoice_payment_status", lang)}</div>', unsafe_allow_html=True,
    )
    if "invoice_window" not in st.session_state:
        st.session_state.invoice_window = 14
    segmented_control(
        [(14, t("last_n_days", lang).format(n=14)), (21, t("last_n_days", lang).format(n=21))],
        st.session_state.invoice_window, "invoice_window", state_key="invoice_window",
    )
    status_df = get_orders_invoice_payment_status(shown_day, st.session_state.invoice_window)
    if status_df.empty:
        st.caption(t("no_activity", lang))
    else:
        status_df = status_df.copy()
        yes, no = t("yes", lang), t("no", lang)
        status_df["invoiced"] = status_df["invoiced"].map({True: yes, False: no})
        status_df["paid"] = status_df["paid"].map({True: yes, False: no})
        status_df["amount"] = status_df["amount"].map(format_currency)
        table = status_df.rename(
            columns={
                "order_date": t("event_date", lang), "customer": t("company", lang), "amount": t("revenue", lang),
                "invoiced": t("invoiced", lang), "paid": t("paid", lang),
            }
        )
        table = table[[t("event_date", lang), t("company", lang), t("revenue", lang), t("invoiced", lang), t("paid", lang)]]
        st.dataframe(table, use_container_width=True, hide_index=True)
