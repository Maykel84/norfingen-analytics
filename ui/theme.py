"""Design tokens for the Modernist visual system: steel/silver neutrals as
structural scaffolding, navy + teal as the two accent hues. Chart palettes in
ui/charts.py are derived from these same hues, not picked independently.

Categorical set (navy / teal / slate-violet) is validated with the dataviz
skill's validate_palette.js: all 6 checks pass in both light and dark for the
*adjacent* pairlist (bar/line/stack — everywhere this app uses >1 series).
The third slot leans slate-violet rather than a literal steel-blue because
three cool near-blue hues cannot clear normal-vision CVD separation at once
(validator-confirmed) — this is the documented trade-off, not an oversight.
"""

FONT_DISPLAY = "'IBM Plex Sans', 'Inter', system-ui, -apple-system, sans-serif"
FONT_BODY = "'Inter', 'IBM Plex Sans', system-ui, -apple-system, sans-serif"
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700&family=IBM+Plex+Sans:wght@500;600;700&display=swap"
)

TOKENS = {
    "light": {
        # steel/silver neutral scale — structural scaffolding only
        "surface": "#fcfcfb",
        "panel": "#f5f6f7",
        "page": "#eef0f2",
        "border": "#dde1e5",
        "divider": "#e3e6e9",
        "text_primary": "#0f1720",
        "text_secondary": "#4b5563",
        "text_muted": "#8a94a0",
        # accents
        "navy": "#1c4fae",
        "navy_soft": "#e8eefb",
        "teal": "#0c9b7e",
        "teal_soft": "#e1f5f0",
        "slate": "#8452c9",
        "good": "#0ca30c",
        "critical": "#d03b3b",
    },
    "dark": {
        "surface": "#171b20",
        "panel": "#1d2228",
        "page": "#12161a",
        "border": "#2b3138",
        "divider": "#262c33",
        "text_primary": "#f5f6f7",
        "text_secondary": "#c3c9d1",
        "text_muted": "#7d8792",
        "navy": "#4c7fd6",
        "navy_soft": "#1e2a44",
        "teal": "#12a98d",
        "teal_soft": "#123a33",
        "slate": "#9868d6",
        "good": "#0ca30c",
        "critical": "#e66767",
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

    div.block-container {{
        padding-top: 1rem;
        max-width: 1220px;
    }}

    /* Nav shell — present at the top of every page. (True scroll-pinned
       sticky was tried but collided with Streamlit's own fixed header bar;
       dropped in favor of a reliably-rendered top shell.) */
    .st-key-app_nav {{
        background: {t['surface']};
        border-bottom: 1px solid {t['border']};
        border-radius: 10px;
        padding: 10px 20px 14px 20px;
        margin-bottom: 20px;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button {{
        background: transparent;
        border: none !important;
        border-radius: 6px !important;
        color: {t['text_secondary']};
        font-weight: 600 !important;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button[kind="primary"] {{
        background: {t['navy']} !important;
        color: white !important;
    }}
    .st-key-app_nav div[data-testid="stButton"] > button:hover {{
        color: {t['navy']} !important;
        border-color: transparent !important;
    }}
    .brand {{
        font-family: {FONT_DISPLAY};
        font-weight: 700;
        font-size: 17px;
        color: {t['text_primary']};
        letter-spacing: -0.01em;
    }}

    .nav-pill {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 6px;
    }}
    .nav-pill-active {{
        background: {t['navy']};
        color: white;
    }}
    .nav-pill-inactive {{
        background: transparent;
        color: {t['text_secondary']};
    }}

    /* KPI tiles */
    .kpi-tile {{
        padding: 4px 0 4px 0;
        border-left: 2px solid {t['divider']};
        padding-left: 16px;
    }}
    .kpi-label {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {t['text_muted']};
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-family: {FONT_DISPLAY};
        font-size: 32px;
        font-weight: 700;
        color: {t['text_primary']};
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
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
       never bleeds into the nav bar's own button styling above. */
    [class*="st-key-pill_"] div[data-testid="stButton"] > button {{
        border-radius: 999px !important;
        border: 1px solid {t['border']} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    [class*="st-key-pill_"] div[data-testid="stButton"] > button:hover {{
        border-color: {t['navy']} !important;
        color: {t['navy']} !important;
    }}

    /* Client cards */
    .client-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
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
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        background: {t['teal_soft']};
        color: {t['teal']};
        margin-right: 6px;
    }}

    hr {{ border-color: {t['divider']}; }}

    [data-testid="stMetricValue"] {{ font-family: {FONT_DISPLAY}; }}
    </style>
    """
