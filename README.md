# NorFinGen Analytics

Self-service analytics dashboard over a Supabase Postgres instance, built with
Streamlit. Users pick measures, dimensions, granularity, and date range rather
than reading a fixed report — similar in spirit to a Power BI semantic-model
report.

## Data source

Connects (read-only) to Supabase Postgres. Key tables:

- `customers` — companies served (name, segment, city, postal_code, industry)
- `orders` / `order_lines` — revenue
- `vouchers` / `postings` — costs, bucketed by account-number range (COGS
  4000–4999, labor 5000–5999, opex 6000–7999)
- Pre-built views `v_sales_flat`, `v_pl_monthly`, `v_headcount_monthly` exist
  in the DB but the semantic layer queries the base tables directly for
  filterable, dimension-flexible aggregation.

**Cost attribution (structural limitation, not a data quality gap)**: cost
postings — `postings` rows with `account_number` in the 4000–7999 range
(COGS/labor/opex) — never carry a `customer_id`. This is 0% tagged across the
board, not a partial-tagging issue (an earlier version of this README quoted
a "~35% tagged" figure; that number came from counting `customer_id` across
*all* postings, including receivables/payables rows outside the cost range,
and doesn't apply to cost specifically). `employee_id` and `department_id`
are likewise unpopulated on cost postings, and while `supplier_id` is
populated on about half of them, a supplier (who we buy from) cannot
substitute as a customer link (who we sell to).

Net effect: cost, profit, and margin are only measurable **whole-company**,
or broken down by **time period** or **cost bucket** (COGS/labor/opex) — never
by client, location, segment, or industry. This is a real property of how
the source accounting data is structured (revenue is captured per
order/customer; cost is captured per voucher/account, independent of any
customer), not something to fix upstream. The app reflects this directly:
the Clients tab shows revenue and order count only (no cost/profit/margin
columns), and Time Analysis restricts the measure list to revenue/orders
whenever the breakdown is grouped by a customer-attribute dimension.

Location: the database has no lat/lon columns, only `city`/`postal_code`. A
static city→coordinates lookup for the ~39 Norwegian cities present in the
data lives in [`data/geocoding.py`](data/geocoding.py).

## Project structure

```
app.py                  # Streamlit entrypoint / nav router
semantic/
    schema.py            # discovered schema constants
    metrics.py           # semantic layer: dimensions, measures, query interface
data/
    db.py                 # connection handling, cached queries
    geocoding.py          # static city -> lat/lon lookup
ui/
    theme.py              # design tokens (navy/teal/steel) + global CSS
    i18n.py               # translations (en/pl/no)
    charts.py             # chart builders (shared palette/layout)
    components.py         # nav bar, KPI tiles, pill/segmented controls, formatters
    page_overview.py       # Overview tab: year switcher, KPIs, trend, coverage map
    page_time.py           # Time Analysis tab: period drill-down, breakdown, comparison
    page_clients.py        # Clients tab: search/filter, cards, detail, compare
tests/
    test_metrics.py       # semantic layer aggregation math tests
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in `DB_PASSWORD` (get it from your
Supabase project settings). Never commit `.env`.

```bash
cp .env.example .env
```

For Streamlit Cloud, instead copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml` locally, or paste its contents into the app's
"Secrets" panel in Streamlit Community Cloud settings (never commit the real
file — it's gitignored).

## Run

```bash
streamlit run app.py
```

## Tests

```bash
pytest tests/
```

## Data refresh

Query results are cached for 8 hours (`st.cache_data(ttl=...)` in
`data/db.py`), so the database is hit at most ~3 times/day regardless of
traffic. A footer caption shows the last-refreshed timestamp.

## Language

English, Polish, and Norwegian via the language switcher in the persistent
top nav bar (`ui/i18n.py`). Defaults to English.

## Theme

`.streamlit/config.toml` sets the default light theme. A runtime light/dark
toggle is available in the top nav bar; it restyles all charts, the nav
shell, and KPI tiles through the shared tokens in `ui/theme.py` and palette
in `ui/charts.py`. Note: Streamlit's own native widget chrome (buttons,
inputs, dataframes) does not fully re-theme at runtime in this Streamlit
version — for full native dark mode, viewers can also use Streamlit's
built-in theme switcher (⋮ menu → Settings → Theme).

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (you handle this — see the project's commit
   checkpoints).
2. On share.streamlit.io, create a new app pointing at this repo, `app.py`.
3. In the app's Settings → Secrets, paste the contents of your local
   `.streamlit/secrets.toml` (with the real password).
4. Deploy.
