# Operational Intelligence Dashboard

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

**Known limitation**: only ~35% of `postings` rows carry a `customer_id`, so
cost/profit broken down *by company* reflects that tagged subset only.
Company-wide totals (no company grouping) use the full postings data and are
accurate.

Location: the database has no lat/lon columns, only `city`/`postal_code`. A
static city→coordinates lookup for the ~39 Norwegian cities present in the
data lives in [`data/geocoding.py`](data/geocoding.py).

## Project structure

```
app.py                  # Streamlit entrypoint
semantic/
    schema.py            # discovered schema constants
    metrics.py           # semantic layer: dimensions, measures, query interface
data/
    db.py                 # connection handling, cached queries
    geocoding.py          # static city -> lat/lon lookup
ui/
    i18n.py               # translations (en/pl/no)
    charts.py             # chart builders (shared palette/layout)
    components.py         # KPI tiles, formatters
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
traffic. The sidebar footer shows the last-refreshed timestamp.

## Language

English, Polish, and Norwegian via the sidebar language switcher
(`ui/i18n.py`). Defaults to English.

## Theme

`.streamlit/config.toml` sets the default light theme. A runtime light/dark
toggle is available in the sidebar; it restyles all charts and KPI tiles
through the shared palette in `ui/charts.py`. Note: Streamlit's own native
widget chrome (buttons, inputs) does not fully re-theme at runtime in this
Streamlit version — for full native dark mode, viewers can also use
Streamlit's built-in theme switcher (⋮ menu → Settings → Theme).

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (you handle this — see the project's commit
   checkpoints).
2. On share.streamlit.io, create a new app pointing at this repo, `app.py`.
3. In the app's Settings → Secrets, paste the contents of your local
   `.streamlit/secrets.toml` (with the real password).
4. Deploy.
