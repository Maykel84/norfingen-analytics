import pandas as pd
import streamlit as st

from semantic.metrics import get_receivables, get_write_offs_by_month
from ui.charts import CATEGORICAL, CHROME, bar_breakdown, donut_chart, line_over_time
from ui.components import format_currency, format_int, kpi_tile
from ui.i18n import t
from ui.theme import PALETTE, tokens

STATUS_ORDER = ["PAID", "OPEN", "OVERDUE", "WRITTEN_OFF"]
STATUS_KEY = {
    "PAID": "inv_paid", "OPEN": "inv_open", "OVERDUE": "inv_overdue", "WRITTEN_OFF": "inv_written_off",
}
# (label key, lower bound exclusive, upper bound inclusive) in days past due
AGEING_BUCKETS = [
    ("rcv_not_due", None, 0), ("1–30", 0, 30), ("31–60", 30, 60), ("61–90", 60, 90), ("90+", 90, None),
]


def _bucket(days: float) -> int:
    for i, (_, lo, hi) in enumerate(AGEING_BUCKETS):
        if (lo is None or days > lo) and (hi is None or days <= hi):
            return i
    return len(AGEING_BUCKETS) - 1


def _status_colors(theme: str) -> dict[str, str]:
    p = CATEGORICAL[theme]
    # overdue is a warning state: in the Orchid & Cobalt preview the 2nd categorical
    # slot is pink (not alarming), so it uses the shared critical red instead
    overdue = tokens(theme)["critical"] if PALETTE == "orchid-cobalt" else p[1]
    return {"PAID": p[0], "OPEN": p[2], "OVERDUE": overdue, "WRITTEN_OFF": CHROME[theme]["muted"]}


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """Receivables snapshot. Scoped by the global year selector on invoice date
    (ageing is always measured at the newest generated date, not the clock)."""
    with st.spinner(t("loading_data", lang)):
        df = get_receivables(selected_year)
        write_offs = get_write_offs_by_month(selected_year)

    if df.empty:
        st.caption(t("no_activity", lang))
        return

    unpaid = df[df["invoice_status"].isin(["OPEN", "OVERDUE"])]
    by_status = df.groupby("invoice_status").agg(amount=("amount", "sum"), n=("order_id", "count"))
    by_status = by_status.reindex(STATUS_ORDER).fillna(0)

    # Write-off tiles come from the same ledger query as the chart below (account 7830),
    # so tile == last point of the running total by construction.
    wo_net = float(write_offs["written_off"].sum()) if not write_offs.empty else 0.0
    wo_gross = float(write_offs["written_off_gross"].sum()) if not write_offs.empty else 0.0
    cols = st.columns(5)
    with cols[0]:
        kpi_tile(t("rcv_outstanding", lang), format_currency(unpaid["amount"].sum()), theme)
    with cols[1]:
        kpi_tile(t("rcv_overdue_amount", lang), format_currency(by_status.loc["OVERDUE", "amount"]), theme)
    with cols[2]:
        kpi_tile(t("rcv_written_off_net", lang), format_currency(wo_net), theme)
    with cols[3]:
        kpi_tile(t("rcv_written_off_gross", lang), format_currency(wo_gross), theme)
    with cols[4]:
        kpi_tile(t("rcv_paid_late_count", lang), format_int(int(df["paid_late"].sum())), theme)
    st.caption(f"ℹ️ {t('rcv_gross_note', lang)}")

    st.write("")
    left, right = st.columns(2)
    with left:
        st.markdown(f'<div class="section-label">{t("rcv_status_split", lang)}</div>', unsafe_allow_html=True)
        colors = _status_colors(theme)
        fig = donut_chart(
            # legend carries count + amount: the tiny slices are unreadable as in-chart labels
            [f"{t(STATUS_KEY[s], lang)} · {int(by_status.loc[s, 'n']):,} · {format_currency(by_status.loc[s, 'amount'])}"
             for s in STATUS_ORDER],
            [float(by_status.loc[s, "amount"]) for s in STATUS_ORDER],
            [colors[s] for s in STATUS_ORDER], theme,
            center_text=f"{int(by_status['n'].sum()):,} {t('rcv_invoices', lang)}",
            customdata=[f"{int(by_status.loc[s, 'n']):,} {t('rcv_invoices', lang)}" for s in STATUS_ORDER],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right:
        st.markdown(f'<div class="section-label">{t("rcv_ageing", lang)}</div>', unsafe_allow_html=True)
        labels = [t(k, lang) if k.startswith("rcv_") else k for k, _, _ in AGEING_BUCKETS]
        ageing = pd.DataFrame({"bucket": labels, "amount": 0.0})
        for idx, amount in unpaid.groupby(unpaid["days_past_due"].map(_bucket))["amount"].sum().items():
            ageing.loc[idx, "amount"] = amount
        fig = bar_breakdown(
            ageing, "bucket", "amount", None, "", theme, value_suffix=" kr", color_scale="sage" if PALETTE == "orchid-cobalt" else "warm",
            x_title=t("rcv_days_past_due", lang), y_title=t("amount", lang),
        )
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.write("")
    tl, tr = st.columns(2)
    with tl:
        st.markdown(f'<div class="section-label">{t("rcv_top_late", lang)}</div>', unsafe_allow_html=True)
        late = (
            df[df["invoice_status"] == "PAID"].groupby("customer")
            .agg(late=("paid_late", "sum"), paid=("order_id", "count")).reset_index()
        )
        late = late[late["late"] > 0].sort_values(["late", "paid"], ascending=[False, False]).head(10)
        table = late.rename(columns={
            "customer": t("company", lang), "late": t("rcv_late_payments", lang), "paid": t("rcv_paid_invoices", lang),
        })
        st.dataframe(table, use_container_width=True, hide_index=True)
    with tr:
        st.markdown(f'<div class="section-label">{t("rcv_top_outstanding", lang)}</div>', unsafe_allow_html=True)
        out = (
            unpaid.assign(overdue_amount=unpaid["amount"].where(unpaid["invoice_status"] == "OVERDUE", 0.0))
            .groupby("customer")
            .agg(amount=("amount", "sum"), overdue_amount=("overdue_amount", "sum"), n=("order_id", "count"))
            .reset_index().sort_values("amount", ascending=False).head(10)
        )
        out["amount"] = out["amount"].map(format_currency)
        out["overdue_amount"] = out["overdue_amount"].map(format_currency)
        table = out.rename(columns={
            "customer": t("company", lang), "amount": t("rcv_outstanding", lang),
            "overdue_amount": t("rcv_overdue_amount", lang), "n": t("rcv_unpaid_invoices", lang),
        })
        st.dataframe(table, use_container_width=True, hide_index=True)

    st.write("")
    st.markdown(f'<div class="section-label">{t("rcv_write_offs", lang)}</div>', unsafe_allow_html=True)
    if write_offs.empty:
        st.caption(t("rcv_no_write_offs", lang))
        return
    # continuous monthly axis (zero months included) so the running total reads as a staircase
    end = max(write_offs["period"].max(), df["invoice_date"].max().to_period("M").to_timestamp())
    months = pd.date_range(write_offs["period"].min(), end, freq="MS")
    series = write_offs.set_index("period")["written_off"].reindex(months, fill_value=0.0)
    monthly_label, total_label = t("rcv_monthly", lang), t("rcv_running_total", lang)
    long = pd.concat([
        pd.DataFrame({"period": months, "value": series.values, "series": monthly_label}),
        pd.DataFrame({"period": months, "value": series.cumsum().values, "series": total_label}),
    ])
    fig = line_over_time(
        long, "period", "value", "series", "", theme, value_suffix=" kr",
        x_title=t("month", lang), y_title=t("amount", lang), granularity="month",
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
