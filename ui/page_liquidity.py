import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from semantic.metrics import (
    get_bank_balance_daily, get_cogs_payables, get_financing_structure, get_owner_loan_monthly,
    get_partial_months_in_range, get_vat_monthly, get_vat_settlements,
)
from ui.charts import CATEGORICAL, CHROME, line_over_time, stacked_bar_over_time
from ui.components import format_currency, format_pct, kpi_tile
from ui.i18n import t


def _in_year(series: pd.Series, year: int | None) -> pd.Series:
    return series.dt.year == year if year is not None else pd.Series(True, index=series.index)


def _date(s: pd.Series) -> pd.Series:
    return s.dt.strftime("%Y-%m-%d").fillna("—")


def _section(label: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


def render(lang: str, theme: str, selected_year: int | None) -> None:
    """Cash, financing and VAT. Balances are cumulative from the first posting
    (a year filter only slices the view, it never re-bases a balance)."""
    with st.spinner(t("loading_data", lang)):
        bank = get_bank_balance_daily()
        loan = get_owner_loan_monthly()
        financing = get_financing_structure()
        vat_m = get_vat_monthly()
        settlements = get_vat_settlements()
        cogs = get_cogs_payables()

    bank_view = bank[_in_year(bank["day"], selected_year)]
    loan_view = loan[_in_year(loan["period"], selected_year)]
    vat_view = vat_m[_in_year(vat_m["period"], selected_year)]
    settle_view = settlements[_in_year(settlements["period_end"], selected_year)]
    cogs_view = cogs[_in_year(cogs["accrual_date"], selected_year)]

    # ---- bank ------------------------------------------------------------
    unpaid_vat = settlements[settlements["status"] == "UNPAID"]
    next_due = unpaid_vat["payment_date"].min() if not unpaid_vat.empty else None
    cols = st.columns(4)
    if not bank_view.empty:
        low = bank_view.loc[bank_view["balance"].idxmin()]
        with cols[0]:
            kpi_tile(t("liq_bank_balance", lang), format_currency(bank_view["balance"].iloc[-1]), theme)
        with cols[1]:
            kpi_tile(t("liq_min_balance", lang), format_currency(low["balance"]), theme)
            st.caption(f"{t('liq_on', lang)} {low['day']:%Y-%m-%d}")
    with cols[2]:
        # Outstanding principal at the end of the viewed period (loan rows stop at the
        # last instalment, so a later year is judged by the final row, not shown as 0).
        view_end = pd.Timestamp(year=selected_year, month=12, day=1) if selected_year else loan["period"].max()
        upto = loan[loan["period"] <= view_end]
        outstanding = float(upto["outstanding"].iloc[-1]) if not upto.empty else 0.0
        if outstanding > 0:
            kpi_tile(t("liq_loan_outstanding", lang), format_currency(outstanding), theme)
        else:
            repaid = upto[upto["principal_repaid"] > 0]
            kpi_tile(t("liq_loan_outstanding", lang), t("liq_repaid", lang), theme)
            if not repaid.empty:
                st.caption(t("liq_last_instalment", lang).format(month=f"{repaid['period'].iloc[-1]:%Y-%m}"))
    with cols[3]:
        kpi_tile(t("liq_vat_to_pay", lang), format_currency(unpaid_vat["balance"].sum()), theme)
        if next_due is not None:
            st.caption(f"{', '.join(unpaid_vat['term'])} · {t('liq_due', lang)} {next_due:%Y-%m-%d}")

    st.write("")
    _section(t("liq_bank_title", lang))
    if not bank_view.empty:
        month_end = bank_view.assign(period=bank_view["day"].dt.to_period("M").dt.to_timestamp()).groupby(
            "period", as_index=False).last()[["period", "balance"]]
        fig = line_over_time(
            month_end, "period", "balance", None, "", theme, value_suffix=" kr",
            x_title=t("month", lang), y_title=t("amount", lang), granularity="month", line_color=CATEGORICAL[theme][0],
        )
        fig.add_trace(go.Scatter(
            x=[low["day"]], y=[low["balance"]], mode="markers+text", name=t("liq_min_marker", lang),
            marker=dict(size=13, color=CATEGORICAL[theme][1], line=dict(width=2, color=CHROME[theme]["surface"])),
            text=[f"{low['balance']:,.0f} kr".replace(",", " ")], textposition="top right",
            textfont=dict(color=CHROME[theme]["text_primary"]), showlegend=False,
            hovertemplate=f"{t('liq_min_marker', lang)} %{{x|%Y-%m-%d}}: %{{y:,.0f}} kr<extra></extra>",
        ))
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- owner loan + financing structure -----------------------------------
    st.write("")
    _section(t("liq_loan_section", lang))
    left, right = st.columns(2)
    with left:
        fig = line_over_time(
            loan_view, "period", "outstanding", None, t("liq_loan_outstanding", lang), theme, value_suffix=" kr",
            fill=True, x_title=t("month", lang), y_title=t("amount", lang), granularity="month",
            line_color=CATEGORICAL[theme][2],
        )
        fig.update_traces(line_shape="hv")
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        fig = stacked_bar_over_time(
            loan_view, "period",
            {"principal_repaid": t("liq_principal_repaid", lang), "interest": t("liq_interest", lang)}, theme,
            x_title=t("month", lang), y_title=t("amount", lang),
        )
        fig.update_layout(height=340, title=dict(text=t("liq_principal_vs_interest", lang)), legend=dict(y=-0.4))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if not loan.empty and loan["outstanding"].iloc[-1] == 0:
        st.caption(f"ℹ️ {t('liq_loan_repaid_note', lang)}")

    _section(t("liq_financing_structure", lang))
    total = financing["share_capital"] + financing["owner_loan"]
    cols = st.columns(3)
    with cols[0]:
        kpi_tile(t("liq_share_capital", lang), format_currency(financing["share_capital"]), theme)
    with cols[1]:
        kpi_tile(t("liq_owner_loan", lang), format_currency(financing["owner_loan"]), theme)
    with cols[2]:
        kpi_tile(t("liq_loan_share", lang), format_pct(financing["owner_loan"] / total * 100 if total else 0), theme)

    # ---- VAT ---------------------------------------------------------------
    st.write("")
    _section(t("liq_vat_section", lang))
    # term in progress = months after the last settled period
    last_end = settlements["period_end"].max()
    accruing = vat_m[vat_m["period"] > last_end]
    cols = st.columns(2)
    with cols[0]:
        kpi_tile(t("liq_vat_to_pay", lang), format_currency(unpaid_vat["balance"].sum()), theme)
        if next_due is not None:
            st.caption(f"{', '.join(unpaid_vat['term'])} · {t('liq_due', lang)} {next_due:%Y-%m-%d}")
    with cols[1]:
        kpi_tile(t("liq_vat_accruing", lang), format_currency((accruing["output_vat"] - accruing["input_vat"]).sum()), theme)
        st.caption(f"ℹ️ {t('liq_vat_accruing_note', lang)}")

    if not vat_view.empty:
        fig = line_over_time(
            vat_view.melt("period", ["output_vat", "input_vat"], var_name="series", value_name="value").assign(
                series=lambda d: d["series"].map({"output_vat": t("liq_output_vat", lang), "input_vat": t("liq_input_vat", lang)})
            ),
            "period", "value", "series", "", theme, value_suffix=" kr",
            x_title=t("month", lang), y_title=t("amount", lang), granularity="month",
            partial_periods=get_partial_months_in_range((vat_view["period"].min().date(), pd.Timestamp.max.date())),
            partial_label=t("partial_month_label", lang),
        )
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if get_partial_months_in_range((vat_view["period"].min().date(), pd.Timestamp.max.date())):
            st.caption(f"ℹ️ {t('liq_vat_partial_note', lang)}")

    _section(t("liq_vat_settlements", lang))
    if not settle_view.empty:
        tbl = pd.DataFrame({
            t("liq_term", lang): settle_view["term"],
            t("liq_period", lang): settle_view["period_start"].dt.strftime("%Y-%m-%d") + " – " + settle_view["period_end"].dt.strftime("%Y-%m-%d"),
            t("liq_output_vat", lang): settle_view["output_vat"].map(format_currency),
            t("liq_input_vat", lang): settle_view["input_vat"].map(format_currency),
            t("liq_balance", lang): settle_view["balance"].map(format_currency),
            t("liq_payment_date", lang): _date(settle_view["payment_date"]),
            t("status", lang): settle_view["status"].map({"PAID": t("paid", lang), "UNPAID": t("unpaid", lang)}),
        }).iloc[::-1]
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=300)

    # ---- COGS payables -------------------------------------------------------
    st.write("")
    _section(t("liq_cogs_section", lang))
    unpaid_cogs = cogs[cogs["status"] == "UNPAID"]
    cols = st.columns(2)
    with cols[0]:
        kpi_tile(t("liq_cogs_unpaid", lang), format_currency(unpaid_cogs["amount_gross"].sum()), theme)
    # three accruals per account and month (one per supplier): offer a supplier filter,
    # keep the table sorted by accrual date (newest first, as the query returns it)
    all_label = t("all_suppliers", lang)
    suppliers = [all_label] + sorted(cogs_view["supplier"].unique()) if not cogs_view.empty else [all_label]
    with cols[1]:
        chosen = st.selectbox(t("cogs_filter_label", lang), suppliers, key="cogs_supplier_filter")
    if chosen != all_label:
        cogs_view = cogs_view[cogs_view["supplier"] == chosen]
    cogs_view = cogs_view.sort_values(["accrual_date", "supplier"], ascending=[False, True])
    if not cogs_view.empty:
        tbl = pd.DataFrame({
            t("liq_accrual_date", lang): _date(cogs_view["accrual_date"]),
            t("supplier", lang): cogs_view["supplier"],
            t("liq_description", lang): cogs_view["description"],
            t("liq_net", lang): cogs_view["amount_net"].map(format_currency),
            t("liq_vat", lang): cogs_view["vat_amount"].map(format_currency),
            t("liq_gross", lang): cogs_view["amount_gross"].map(format_currency),
            t("liq_due_date", lang): _date(cogs_view["payment_due_date"]),
            t("status", lang): cogs_view["status"].map({"PAID": t("paid", lang), "UNPAID": t("unpaid", lang)}),
            t("liq_paid_date", lang): _date(cogs_view["paid_date"]),
        })
        st.write("")
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=420)
