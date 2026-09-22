"""Design tokens for the Organic Business visual system: warm cream/parchment
neutrals as structural scaffolding (not cold steel-gray), sage green + warm
terracotta as the two primary accent hues, softened with rounded corners and
gentle shadows instead of hard 1px dividers. Chart palettes in ui/charts.py
are derived from these same hues, not picked independently.

Categorical set (sage / terracotta / slate-blue) is validated with the
dataviz skill's validate_palette.js: all 6 checks pass in both light and dark
for the *all-pairs* pairlist (stricter than the adjacent-only check the prior
Modernist palette used — this set is safe even for scatter/map/small-multiple
charts, not just bar/line/stack). The third slot is a muted slate-blue rather
than a third warm hue because sage-green and terracotta alone collapse under
protanopia at business-appropriate saturation (validator-confirmed) — the
same structural trade-off as before, just re-verified against the new hues.

Button contrast note (section 5 audit): plain terracotta (#c8661f / #c97830)
with white text measures ~3.1-3.9:1 — under the 4.5:1 AA threshold for normal
text. Terracotta is therefore used only as a chart color / text-on-soft-badge
color, never as a filled button background; `terracotta_button` is a darker
step reserved for that one case. Dark-mode sage buttons use dark ink text
(not white) since white-on-bright-sage was only 3.07:1 — see `on_sage_dark`.
"""

FONT_DISPLAY = "'IBM Plex Sans', 'Inter', system-ui, -apple-system, sans-serif"
FONT_BODY = "'Inter', 'IBM Plex Sans', system-ui, -apple-system, sans-serif"
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700&family=IBM+Plex+Sans:wght@500;600;700&display=swap"
)

TOKENS = {
    "light": {
        # warm neutral scale — structural scaffolding only, never a chart color
        "surface": "#faf7f1",
        "panel": "#f2ece0",
        "page": "#ede4d4",
        "border": "#e0d5c0",
        "divider": "#ece3d3",
        "text_primary": "#2a2318",
        "text_secondary": "#5c5140",
        "text_muted": "#93876f",
        # accents
        "sage": "#1f6b3a",
        "sage_soft": "#e3ede2",
        "terracotta": "#c8661f",
        "terracotta_button": "#9c4f19",
        "terracotta_soft": "#f7e6d5",
        "slate": "#4f5aa8",
        "slate_soft": "#e6e8f5",
        "on_accent": "#ffffff",
        "good": "#0ca30c",
        "critical": "#d03b3b",
        "shadow": "rgba(42, 35, 24, 0.08)",
    },
    "dark": {
        "surface": "#211d17",
        "panel": "#2a251d",
        "page": "#1a1712",
        "border": "#3c3427",
        "divider": "#332c22",
        "text_primary": "#f5efe2",
        "text_secondary": "#cdc2ab",
        "text_muted": "#8f846f",
        "sage": "#57a366",
        "sage_soft": "#23392a",
        "terracotta": "#c97830",
        "terracotta_button": "#c97830",
        "terracotta_soft": "#3d2c1c",
        "slate": "#5f6bbd",
        "slate_soft": "#232a44",
        "on_accent": "#15251a",
        "good": "#0ca30c",
        "critical": "#e66767",
        "shadow": "rgba(0, 0, 0, 0.35)",
    },
}


def tokens(theme: str) -> dict:
    return TOKENS[theme]


def inject_global_css(theme: str) -> str:
    t = tokens(theme)
    return f"""
    <style>
    @import url('{GOOGLE_FONTS_URL}');

    html, body, [class*="css"] {{
        font-family: {FONT_BODY};
    }}

    .stApp {{
        background-color: {t['page']};
        color: {t['text_primary']};
    }}

    section[data-testid="stSidebar"] {{ display: none; }}

    /* padding-top clears Streamlit's own fixed top toolbar (the Deploy /
       Share / GitHub icon bar) — on Streamlit Community Cloud this bar is
       taller/wider than in local dev (adds Share/Star/Fork/GitHub icons),
       so this needs more headroom than a bare local run suggests. */
    div.block-container {{
        padding-top: 4.5rem;
        max-width: 1220px;
    }}

    /* Identity strip — wordmark + language/theme controls, sitting directly
       on the page (no card, no background panel) so it reads as page
       chrome, not another boxed section. */
    .st-key-identity_bar {{
        padding: 4px 4px 0 4px;
        margin-top: 0.5rem;
    }}
    .st-key-identity_bar > div {{
        display: flex;
        align-items: center;
    }}

    /* Language/theme segmented toggles — small, discreet capsules (not a
       prominent control) so they read as secondary chrome next to the
       wordmark rather than competing with the main nav below. */
    .st-key-toggle_lang, .st-key-toggle_theme {{
        background: {t['panel']};
        border-radius: 999px;
        padding: 2px;
        display: flex;
        justify-content: flex-end;
    }}
    .st-key-toggle_lang div[data-testid="stButton"] > button,
    .st-key-toggle_theme div[data-testid="stButton"] > button {{
        background: transparent !important;
        border: none !important;
        border-radius: 999px !important;
        color: {t['text_muted']} !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        min-height: 1.8rem !important;
        padding: 0 8px !important;
    }}
    .st-key-toggle_lang div[data-testid="stButton"] > button[kind="primary"],
    .st-key-toggle_theme div[data-testid="stButton"] > button[kind="primary"] {{
        background: {t['terracotta_button']} !important;
        color: {t['on_accent']} !important;
    }}
    .st-key-toggle_lang div[data-testid="stButton"] > button:hover,
    .st-key-toggle_theme div[data-testid="stButton"] > button:hover {{
        color: {t['terracotta_button']} !important;
    }}
    /* CRITICAL fix: the plain :hover rule above (meant for the resting/
       secondary state) ties in CSS specificity with the [kind="primary"]
       rule above it and wins on source order — so hovering the ALREADY-
       ACTIVE pill (which happens automatically right after clicking it,
       since the cursor is still sitting on it) left the background at
       terracotta_button from the primary rule while :hover repainted the
       text to that exact same terracotta_button color: text and
       background identical, i.e. invisible until the mouse moved away.
       An explicit primary+hover rule (same colors as resting primary)
       closes that gap in both themes. */
    .st-key-toggle_lang div[data-testid="stButton"] > button[kind="primary"]:hover,
    .st-key-toggle_theme div[data-testid="stButton"] > button[kind="primary"]:hover {{
        background: {t['terracotta_button']} !important;
        color: {t['on_accent']} !important;
    }}

    /* Main nav row — the one card in the header, symmetric padding and
       fully rounded (it no longer visually docks under the identity strip,
       which has no background of its own now). */
    .st-key-app_nav {{
        background: {t['surface']};
        box-shadow: 0 4px 16px {t['shadow']};
        border-radius: 18px;
        padding: 14px 20px;
        margin-bottom: 24px;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button {{
        background: transparent;
        border: none !important;
        border-radius: 12px !important;
        color: {t['text_secondary']};
        font-weight: 600 !important;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button[kind="primary"] {{
        background: {t['sage']} !important;
        color: {t['on_accent']} !important;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button:hover {{
        color: {t['sage']} !important;
        background: {t['sage_soft']} !important;
    }}
    /* Same fix as toggle_lang/toggle_theme above: without this, hovering
       the already-active nav tab (the cursor sits on it right after the
       click that activated it) repaints it pale-green-on-pale-green via
       the plain :hover rule, instead of staying solid-green-on-white. */
    .st-key-app_nav div[data-testid="stButton"] > button[kind="primary"]:hover {{
        color: {t['on_accent']} !important;
        background: {t['sage']} !important;
    }}
    .brand {{
        font-family: {FONT_DISPLAY};
        font-weight: 700;
        font-size: 14px;
        color: {t['text_primary']};
        letter-spacing: -0.01em;
    }}

    /* KPI tiles — soft rounded card with a gentle shadow, not a hard left
       border rule. Streamlit's column content wrapper is a flex container
       with align-items normalizing to flex-start, so a plain injected div
       shrink-wraps to its own content width instead of filling the column
       — explicit width:100%/box-sizing here is what makes every tile in a
       row the same size regardless of how long its number is (the bug:
       short values like "5.3%" got a wide tile with empty space while long
       currency values got a narrow tile and wrapped to two lines). */
    div[data-testid="stMarkdownContainer"]:has(> .kpi-tile) {{
        width: 100%;
    }}
    .kpi-tile {{
        background: {t['surface']};
        border-radius: 16px;
        box-shadow: 0 2px 10px {t['shadow']};
        padding: 14px 14px;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }}
    .kpi-label {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {t['text_muted']};
        margin-bottom: 4px;
        white-space: nowrap;
    }}
    .kpi-value {{
        font-family: {FONT_DISPLAY};
        font-size: 20px;
        font-weight: 600;
        color: {t['text_primary']};
        line-height: 1.15;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .kpi-delta-up {{ color: {t['good']}; font-size: 13px; font-weight: 600; }}
    .kpi-delta-down {{ color: {t['critical']}; font-size: 13px; font-weight: 600; }}

    /* Section headers */
    .section-label {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {t['text_muted']};
        margin: 4px 0 10px 0;
    }}

    /* Pill controls (year switcher, segmented controls) — scoped to
       containers whose st.container(key=...) starts with "pill_", so this
       never bleeds into the nav bar's own button styling above. Resting
       state carries a visible fill (not just a border) so it reads as
       clickable before hover. */
    [class*="st-key-pill_"] div[data-testid="stButton"] > button {{
        border-radius: 999px !important;
        border: 1px solid {t['border']} !important;
        background: {t['panel']} !important;
        color: {t['text_secondary']} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    [class*="st-key-pill_"] div[data-testid="stButton"] > button[kind="primary"] {{
        background: {t['sage']} !important;
        border-color: {t['sage']} !important;
        color: {t['on_accent']} !important;
    }}
    [class*="st-key-pill_"] div[data-testid="stButton"] > button:hover {{
        border-color: {t['sage']} !important;
        color: {t['sage']} !important;
    }}
    /* CRITICAL fix — the actual root cause of "pill text disappears in its
       active state": the plain :hover rule above ties in specificity with
       the [kind="primary"] rule and wins on source order, so hovering an
       ALREADY-ACTIVE pill (the cursor is still over it right after the
       click that selected it) left the background sage (from the primary
       rule, untouched by :hover) while :hover repainted the text to that
       same sage green — identical text/background color, genuinely
       invisible, exactly the "blank colored shape" behavior reported.
       Restoring on_accent text (white in light mode, dark ink in dark —
       see ui/theme.py's module docstring) on hover keeps it legible. */
    [class*="st-key-pill_"] div[data-testid="stButton"] > button[kind="primary"]:hover {{
        border-color: {t['sage']} !important;
        color: {t['on_accent']} !important;
        background: {t['sage']} !important;
    }}

    /* Year dropdown — restyled BaseWeb select to match the app's controls
       rather than Streamlit's default select chrome. */
    .st-key-select_years div[data-baseweb="select"] > div {{
        border-radius: 12px !important;
        border: 1px solid {t['border']} !important;
        background: {t['surface']} !important;
        box-shadow: 0 2px 8px {t['shadow']};
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    .st-key-select_years div[data-baseweb="select"] > div:hover {{
        border-color: {t['sage']} !important;
    }}

    /* Client cards */
    .client-card {{
        background: {t['surface']};
        border-radius: 16px;
        box-shadow: 0 2px 10px {t['shadow']};
        padding: 14px 18px;
        margin-bottom: 10px;
    }}
    .client-card .name {{
        font-weight: 700;
        font-size: 15px;
        color: {t['text_primary']};
    }}
    .client-card .meta {{
        font-size: 12px;
        color: {t['text_muted']};
        margin-top: 2px;
    }}

    .tag-pill {{
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        background: {t['sage_soft']};
        color: {t['sage']};
        margin-right: 6px;
    }}

    /* st.tabs (Operations page sub-sections) — Streamlit's own tab widget
       defaults to a resting-state text color baked in from config.toml's
       (light-locked) textColor, which is unreadable on our warm-dark
       surface in dark mode (a real contrast bug caught in testing, not a
       hypothetical). This Streamlit version renders tabs as
       [data-testid="stTab"], not the older [data-baseweb="tab"] — verified
       via computed-style inspection, not assumed. */
    [data-testid="stTab"] p {{
        color: {t['text_secondary']} !important;
        font-weight: 600 !important;
    }}
    [data-testid="stTab"][aria-selected="true"] p {{
        color: {t['sage']} !important;
    }}
    [data-testid="stTabsHighlight"] {{
        background-color: {t['sage']} !important;
    }}
    [data-testid="stTabsBorder"] {{
        background-color: {t['divider']} !important;
    }}
    /* Sub-tab panels (Operations page) render their first chart's title/
       legend right under the tab row with only Streamlit's default 16px —
       not enough clearance once a Plotly legend row is present above the
       chart title, so it visually overlaps the tab labels. */
    [data-testid="stTabPanel"] {{
        padding-top: 36px !important;
    }}

    hr {{ border-color: {t['divider']}; }}

    [data-testid="stMetricValue"] {{ font-family: {FONT_DISPLAY}; }}

    /* Fallback theming for plain st.button()s outside the nav/pill/toggle
       containers above (e.g. Clients tab's "Client profile" button). Without
       this, the button keeps Streamlit's native light-locked background
       while its text inherits our dark-mode .stApp color override —
       light-on-light, invisible (the exact bug reported: readable in light
       mode purely by accident, unreadable in dark). Lower specificity than
       every scoped rule above, so those keep taking precedence. */
    div[data-testid="stButton"] > button {{
        background: {t['surface']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        font-weight: 600;
    }}
    div[data-testid="stButton"] > button:hover {{
        border-color: {t['sage']};
        color: {t['sage']};
    }}
    div[data-testid="stButton"] > button:disabled {{
        color: {t['text_muted']};
        border-color: {t['divider']};
    }}

    /* Multiselect tag row (Measures/Group by/Sector/Size, etc.) — Streamlit
       locks this to a single fixed-height row with horizontal scroll-and-
       truncate by default, so once more tags are selected than fit that one
       row, some are hidden with no visual hint, making it look like fewer
       things are selected than actually are. Letting it wrap keeps every
       selected tag visible without opening the dropdown. */
    [data-testid="stMultiSelectTagsContainer"] {{
        flex-wrap: wrap !important;
        height: auto !important;
        overflow: visible !important;
        row-gap: 4px;
    }}

    /* Widget labels (text_input/multiselect/selectbox/date_input captions
       like "Search clients", "Sector", "Size") — Streamlit gives these a
       fixed, low-contrast gray regardless of theme, which reads as barely-
       there ghost text against our dark surface. */
    [data-testid="stWidgetLabel"] p {{
        color: {t['text_secondary']} !important;
        font-weight: 600 !important;
    }}
    </style>
    """
