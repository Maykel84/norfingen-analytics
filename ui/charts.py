"""Chart builders on the Organic Business warm/sage/terracotta system.

Palette provenance: the categorical triple below (sage, terracotta,
slate-blue) was checked with the dataviz skill's validate_palette.js — all
six checks pass in both light and dark mode on the stricter *all-pairs*
pairlist (safe for scatter/map charts, not just bar/line/stack). Sage and
terracotta alone collapse under protanopia at business-appropriate
saturation, so a muted slate-blue fills the third categorical slot — see
ui/theme.py's module docstring for the full note. The sequential ramp is a
hand-built cream->sage->forest duotone (a brand choice, not the skill's
strict single-hue ramp) with monotonically decreasing lightness in light
mode (darker = bigger, the intuitive reading for a light surface) and the
anchor flipped in dark mode (brighter = bigger, since dark would recede into
a dark surface instead of standing out) — both directions are what the skill
actually checks for sequential encodings, not adjacency CVD.
"""

import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CATEGORICAL = {
    "light": ["#1f6b3a", "#c8661f", "#4f5aa8"],
    "dark": ["#57a366", "#c97830", "#5f6bbd"],
}

SEQUENTIAL = {
    "light": ["#c7dbc5", "#82b68b", "#4a9159", "#3a7547", "#2c5c38", "#21492c", "#1a3d24"],
    "dark": ["#30472f", "#4b8755", "#65ac72", "#7bbb86", "#8fc898", "#9ed2a5", "#a8d9ae"],
}

# Warm (terracotta) sequential twin of SEQUENTIAL — used to color cost-side
# breakdowns (suppliers, GL accounts) so cost reads visually distinct from
# revenue-side charts (sage), not just as decoration. Same monotonic-
# lightness construction as SEQUENTIAL, terracotta hue family instead.
SEQUENTIAL_WARM = {
    "light": ["#f0ddc7", "#e3bd93", "#d69b5f", "#c8661f", "#a8551a", "#864417", "#5c2f10"],
    "dark": ["#3d2c1c", "#6b4423", "#96592a", "#c97830", "#d99456", "#e6ac7a", "#f0c39c"],
}

STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

# Which CATEGORICAL slot each measure gets when a chart draws it as a lone
# series (color=None) — without this, every single-measure chart fell back
# to palette[0] (sage/green) regardless of which measure it was, so
# Revenue/Profit/Orders charts all rendered as same-colored green lines,
# visually indistinguishable from each other at a glance even though the
# underlying numbers were genuinely different (the "measures look
# identical" symptom traced to this, not a data bug). Matches the color
# each measure already gets for free when several are plotted together in
# one multi-series chart (e.g. Overview's History chart, where revenue/
# cost/profit are melted into one line_over_time call and Plotly assigns
# palette colors in first-appearance order: revenue=0, cost=1, profit=2).
MEASURE_COLOR_INDEX = {"revenue": 0, "order_count": 0, "cost": 1, "profit": 2, "margin_pct": 2}


def measure_color(measure: str, theme: str) -> str:
    """The categorical color a single-series chart should use for this
    measure, consistent with how it's colored when plotted alongside others."""
    return CATEGORICAL[theme][MEASURE_COLOR_INDEX.get(measure, 0)]

from ui.theme import (  # noqa: E402  (palette switch: Orchid & Cobalt by default, NORFINGEN_PALETTE=classic for the old one)
    PALETTE, PREVIEW_CATEGORICAL, PREVIEW_CHROME, PREVIEW_SEQUENTIAL, PREVIEW_SEQUENTIAL_WARM,
)

CHROME = {
    "light": {
        "surface": "#faf7f1",
        "text_primary": "#2a2318",
        "text_secondary": "#5c5140",
        "muted": "#93876f",
        "grid": "#ece3d3",
        "axis": "#d8cbb0",
    },
    "dark": {
        "surface": "#211d17",
        "text_primary": "#f5efe2",
        "text_secondary": "#cdc2ab",
        "muted": "#8f846f",
        "grid": "#332c22",
        "axis": "#4a4132",
    },
}

if PALETTE == "orchid-cobalt":
    CATEGORICAL = PREVIEW_CATEGORICAL
    SEQUENTIAL = PREVIEW_SEQUENTIAL
    SEQUENTIAL_WARM = PREVIEW_SEQUENTIAL_WARM
    CHROME = PREVIEW_CHROME

FONT_FAMILY = "Inter, 'IBM Plex Sans', system-ui, -apple-system, sans-serif"



def _base_layout(theme: str, title: str) -> dict:
    c = CHROME[theme]
    return dict(
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        paper_bgcolor=c["surface"],
        plot_bgcolor=c["surface"],
        font=dict(family=FONT_FAMILY, color=c["text_secondary"], size=12),
        # Legend lives BELOW the plot (b=64 makes room), not stacked above
        # it alongside the title. Above-the-plot positioning (both title
        # and legend competing for the same narrow band via paper-fraction
        # y values) was fragile: the exact pixel gap needed between them
        # depends on the rendered figure height, which varies per chart
        # (some set an explicit height, most don't) — measured live, a
        # legend with its own title (e.g. "Typ zatrudnienia") wrapped onto
        # two lines and land almost exactly on top of the chart title
        # itself, both illegible, no matter how the y fractions were
        # tuned. Below the plot, the legend can't collide with the title
        # regardless of how many lines it wraps to or how tall the figure is.
        margin=dict(l=8, r=8, t=32, b=64),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="left",
            x=0,
            font=dict(color=c["text_secondary"]),
        ),
        hoverlabel=dict(bgcolor=c["surface"], font=dict(family=FONT_FAMILY, color=c["text_primary"])),
        # "closest" shows a tooltip only for the element actually under the
        # cursor — "x unified" (the previous setting) fired for anything at
        # that x-position even when the cursor wasn't near a mark, which
        # read as tooltips appearing from x-axis proximity rather than from
        # hovering the chart element itself.
        hovermode="closest",
    )


def _pretty_label(raw: str | None) -> str | None:
    """Raw column names (snake_case, all-lowercase) never reach the UI as
    axis titles or legend headers — normal capitalization only (first letter
    up, rest lowercase), never a raw field name like 'order_count'."""
    if not raw:
        return raw
    s = str(raw).replace("_", " ").strip()
    return s[:1].upper() + s[1:].lower() if s else s


def _style_axes(fig: go.Figure, theme: str, x_title: str | None = None, y_title: str | None = None) -> go.Figure:
    c = CHROME[theme]
    fig.update_xaxes(showgrid=False, showline=True, linecolor=c["grid"], color=c["muted"])
    fig.update_yaxes(showgrid=True, gridcolor=c["grid"], zeroline=False, color=c["muted"])
    # x_title/y_title (translated, passed by the caller) always win. Falling
    # back to a prettified raw column name only covers charts nobody has
    # wired up a translation for yet — it capitalizes "order_count" into
    # "Order count", which is still English, not the point of this fallback.
    if x_title is not None:
        fig.update_xaxes(title=x_title)
    elif fig.layout.xaxis.title.text:
        fig.update_xaxes(title=_pretty_label(fig.layout.xaxis.title.text))
    if y_title is not None:
        fig.update_yaxes(title=y_title)
    elif fig.layout.yaxis.title.text:
        fig.update_yaxes(title=_pretty_label(fig.layout.yaxis.title.text))
    if fig.layout.legend.title.text:
        fig.update_layout(legend_title_text=_pretty_label(fig.layout.legend.title.text))
    return fig


_GRANULARITY_TICK_FORMAT = {
    "day": lambda d: d.strftime("%d %b %Y"),
    "week": lambda d: d.strftime("%d %b %Y"),
    "month": lambda d: d.strftime("%b %Y"),
    "quarter": lambda d: f"Q{(d.month - 1) // 3 + 1} {d.year}",
    "year": lambda d: d.strftime("%Y"),
}


def _apply_granularity_ticks(
    fig: go.Figure, df: pd.DataFrame, x_col: str, granularity: str | None, max_ticks: int = 12,
) -> None:
    """Explicit tick positions/labels keyed to the query granularity, instead
    of relying on Plotly's automatic date-tick formatter. That auto-formatter
    breaks down when the x-range collapses to a single point or a very
    narrow span (observed after switching a chart to quarterly granularity
    on a filtered date range with only one bucket): it falls back to
    microsecond-precision tick labels like "23:59:59.999 Dec 31, 2019"
    instead of a quarter label, because it has almost no range to infer a
    sensible format from. Pinning exact ticks sidesteps that fallback
    entirely, for one bucket or a hundred.

    max_ticks thins WHICH points get a printed label when there are many
    (e.g. a client's full monthly history, 80-100+ months) — every point
    still plots on the line, only the tick labels are sampled down to an
    evenly-spaced subset, otherwise that many forced labels overlap into
    an unreadable scribble rather than the microsecond-fallback bug this
    was originally built to fix."""
    formatter = _GRANULARITY_TICK_FORMAT.get(granularity or "")
    if formatter is None or x_col not in df.columns:
        return
    xs = pd.to_datetime(df[x_col]).drop_duplicates().sort_values().reset_index(drop=True)
    if xs.empty:
        return
    if len(xs) > max_ticks:
        step = (len(xs) - 1) / (max_ticks - 1)
        positions = sorted({round(i * step) for i in range(max_ticks)})
        xs = xs.iloc[positions]
    fig.update_xaxes(tickmode="array", tickvals=xs, ticktext=[formatter(d) for d in xs])


def _stabilize_flat_yaxis(fig: go.Figure, df: pd.DataFrame, y_col: str) -> None:
    """Plotly autoscales the y-axis tightly around the data's own min/max by
    default — fine for genuinely volatile series, but for a near-flat one
    (e.g. one client's monthly revenue, which barely moves month to month)
    that zooms in so far that ordinary noise reads as a dramatic swing (an
    axis range like 118.6975k-118.699k for values that don't meaningfully
    vary). Below an 8% spread-to-mean threshold, anchor the range to zero
    instead so a stable series actually reads as stable."""
    if y_col not in df.columns:
        return
    values = pd.to_numeric(df[y_col], errors="coerce").dropna()
    if values.empty:
        return
    y_min, y_max, y_mean = float(values.min()), float(values.max()), float(values.mean())
    spread = y_max - y_min
    if abs(y_mean) == 0 or spread / abs(y_mean) >= 0.08:
        return
    lo = min(0.0, y_min)
    hi = max(y_max * 1.1, lo + abs(y_mean) * 0.1)
    if hi <= lo:
        hi = lo + 1.0
    fig.update_yaxes(range=[lo, hi])


def line_over_time(
    df: pd.DataFrame, x: str, y: str, color: str | None, title: str, theme: str,
    value_suffix: str = "", fill: bool = False, x_title: str | None = None, y_title: str | None = None,
    granularity: str | None = None, line_color: str | None = None,
    partial_periods: list | None = None, partial_label: str | None = None,
) -> go.Figure:
    """partial_periods: month-start dates still in progress — shaded band + label.
    x_title/y_title: translated axis labels — pass these rather than
    relying on the raw column name (e.g. "period") ever reaching the UI.
    granularity: "day"/"week"/"month"/"quarter"/"year" — when given, pins
    explicit tick labels instead of Plotly's auto date formatter (see
    _apply_granularity_ticks). line_color: explicit hex for a single-series
    chart (color=None) — pass measure_color(measure, theme) so e.g. a
    profit chart is colored the same as profit is everywhere else, instead
    of every lone-series chart defaulting to palette[0]."""
    palette = CATEGORICAL[theme]
    solo_color = line_color or palette[0]
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=palette)
    fig.update_traces(line=dict(width=2))
    if fill and color is None:
        fig.update_traces(fill="tozeroy", fillcolor=solo_color + "26")
    fig.update_layout(**_base_layout(theme, title))
    # "closest" hovermode (see _base_layout) means each series shows its own
    # clean "Name: value" tooltip only when the cursor is actually near that
    # line's point — no field-name prefixes, no repeated stats.
    if color is None:
        fig.update_traces(showlegend=False, line_color=solo_color)
        fig.update_traces(hovertemplate=f"{y_title or _pretty_label(y)}: %{{y:,.0f}}{value_suffix}<extra></extra>")
    else:
        fig.update_traces(hovertemplate=f"%{{fullData.name}}: %{{y:,.0f}}{value_suffix}<extra></extra>")
    _style_axes(fig, theme, x_title=x_title, y_title=y_title)
    _apply_granularity_ticks(fig, df, x, granularity)
    _stabilize_flat_yaxis(fig, df, y)
    if partial_periods:
        _mark_partial_periods(fig, df, x, partial_periods, partial_label, theme)
    return fig


def _mark_partial_periods(fig: go.Figure, df: pd.DataFrame, x_col: str, partial_periods, label, theme: str) -> None:
    """Shade the open month so its (cost-less) point is not read as a result.
    A month point sits at the 1st of the month; the band spans the whole month
    but only when that bucket is actually on the chart (month granularity)."""
    present = set(pd.to_datetime(df[x_col]).dt.normalize())
    for p in partial_periods:
        start = pd.Timestamp(p)
        if start not in present:
            continue
        end = start + pd.offsets.MonthBegin(1)
        fig.add_vrect(
            x0=start - pd.Timedelta(days=4), x1=end - pd.Timedelta(days=4),
            fillcolor=CHROME[theme]["muted"], opacity=0.18, line_width=0, layer="below",
            annotation_text=label or "", annotation_position="top left",
            annotation_font=dict(size=11, color=CHROME[theme]["muted"]),
        )


def donut_chart(
    labels: list[str], values: list[float], colors: list[str], theme: str, center_text: str = "",
    customdata: list[str] | None = None,
) -> go.Figure:
    """Status donut. customdata (e.g. "1,862 invoices") is shown in the hover
    next to the amount; slices stay in the order given so colors stay stable."""
    c = CHROME[theme]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62, sort=False, direction="clockwise",
        marker=dict(colors=colors, line=dict(color=c["surface"], width=2)),
        customdata=customdata, textinfo="none",
        hovertemplate="%{label}<br>%{value:,.0f} kr<br>%{customdata}<extra></extra>" if customdata else None,
    ))
    fig.update_layout(**_base_layout(theme, ""))
    fig.update_layout(height=380, showlegend=True, margin=dict(l=10, r=10, t=10, b=10))
    if center_text:
        fig.add_annotation(text=center_text, x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=c["text_primary"]))
    return fig


def stacked_bar_over_time(
    df: pd.DataFrame, x: str, series: dict[str, str], theme: str, value_suffix: str = " kr",
    x_title: str | None = None, y_title: str | None = None, granularity: str | None = "month",
) -> go.Figure:
    """Stacked bars over time. series maps df column -> legend label, stacked
    in the order given, colored from the validated categorical palette."""
    # same overflow rule as stacked_area(): 3 validated hues, a 4th+ series is neutral gray
    palette = list(CATEGORICAL[theme]) + [CHROME[theme]["muted"]] * max(0, len(series) - len(CATEGORICAL[theme]))
    fig = go.Figure()
    for i, (col, label) in enumerate(series.items()):
        fig.add_bar(
            x=df[x], y=df[col], name=label, marker_color=palette[i], marker_line_width=0,
            hovertemplate=f"{label}: %{{y:,.0f}}{value_suffix}<extra></extra>",
        )
    fig.update_layout(**_base_layout(theme, ""), barmode="stack")
    _style_axes(fig, theme, x_title=x_title, y_title=y_title)
    _apply_granularity_ticks(fig, df, x, granularity)
    return fig


def ramp_colors(ramp: list[str], n: int) -> list[str]:
    """n evenly spread shades of a 7-step sequential ramp (skipping the palest, which
    vanishes on the card), so the series of one stack stay in one colour family."""
    if n <= 1:
        return [ramp[4]]
    return [ramp[round(1 + i * 5 / (n - 1))] for i in range(n)]


def stacked_bars_colored(
    df: pd.DataFrame, x: str, series: list[tuple[str, str, str]], theme: str, partial_periods: list | None = None,
    partial_label: str | None = None, x_title: str | None = None, y_title: str | None = None,
) -> go.Figure:
    """Monthly stacked bars with an explicit colour per series: series = [(column, label,
    hex)]. Negative values stack below zero. The month in progress gets a grey band."""
    fig = go.Figure()
    for col, label, color in series:
        fig.add_bar(
            x=df[x], y=df[col], name=label, marker_color=color, marker_line_width=0,
            hovertemplate=f"{label}: %{{y:,.0f}} kr<extra></extra>",
        )
    fig.update_layout(**_base_layout(theme, ""), barmode="relative", bargap=0.15)
    _style_axes(fig, theme, x_title=x_title, y_title=y_title)
    _apply_granularity_ticks(fig, df, x, "month")
    present = set(pd.to_datetime(df[x]).dt.normalize())
    for p in partial_periods or []:
        start = pd.Timestamp(p)
        if start in present:  # a bar is centred on the 1st, so the band is too
            fig.add_vrect(
                x0=start - pd.Timedelta(days=16), x1=start + pd.Timedelta(days=16),
                fillcolor=CHROME[theme]["muted"], opacity=0.18, line_width=0, layer="below",
                annotation_text=partial_label or "", annotation_position="top left",
                annotation_font=dict(size=11, color=CHROME[theme]["muted"]),
            )
    return fig


# One distinct color per absence type (hour_entries.activity_type), the same in every
# absence chart and legend. Six hues spread over hue AND lightness so no two merge, in
# the active palette family; dark-mode values are light enough to stand off the card.
ABSENCE_COLORS = {
    "orchid-cobalt": {
        "light": {"VACATION": "#2f2fe4", "SICK": "#d552a3", "PARENTAL_LEAVE": "#0f6e64",
                  "CHILD_CARE_LEAVE": "#d49a1f", "FLEX_LEAVE": "#8e1ea2", "WELFARE_LEAVE": "#6b7280"},
        "dark": {"VACATION": "#8c8cff", "SICK": "#d552a3", "PARENTAL_LEAVE": "#98e8de",
                 "CHILD_CARE_LEAVE": "#e8b84a", "FLEX_LEAVE": "#b86bd6", "WELFARE_LEAVE": "#a3a6b5"},
    },
    "classic": {
        "light": {"VACATION": "#1f6b3a", "SICK": "#c8661f", "PARENTAL_LEAVE": "#4f5aa8",
                  "CHILD_CARE_LEAVE": "#b7791f", "FLEX_LEAVE": "#8e1ea2", "WELFARE_LEAVE": "#6b7280"},
        "dark": {"VACATION": "#57a366", "SICK": "#c97830", "PARENTAL_LEAVE": "#5f6bbd",
                 "CHILD_CARE_LEAVE": "#e0b04a", "FLEX_LEAVE": "#b86bd6", "WELFARE_LEAVE": "#a3a6b5"},
    },
}


def absence_colors(theme: str) -> dict[str, str]:
    """activity_type code -> hex for the absence charts, in the active palette."""
    family = "orchid-cobalt" if PALETTE == "orchid-cobalt" else "classic"
    return ABSENCE_COLORS[family][theme]


def bar_breakdown(
    df: pd.DataFrame, x: str, y: str, color: str | None, title: str, theme: str, orientation: str = "v",
    value_suffix: str = "", color_scale: str | None = None, x_title: str | None = None, y_title: str | None = None,
    color_map: dict[str, str] | None = None,
) -> go.Figure:
    """color_map: series name -> hex, for charts with more series than the 3-hue
    categorical palette can separate (without it the 4th+ series all fall back to
    one neutral gray and become indistinguishable). color_scale: None (flat sage), "sage", or "warm" — when set (and
    color is None), each bar is tinted by its own value on that sequential
    ramp instead of one flat color, so a ranked breakdown reads with some
    visual life rather than as identical same-color bars. x_title/y_title:
    translated labels for the x/y params as passed (mapped onto the correct
    physical axis below regardless of `orientation`) — pass these rather
    than letting the raw column name reach the UI untranslated."""
    palette = list(CATEGORICAL[theme])
    value_axis = "x" if orientation == "h" else "y"
    category_axis = "y" if orientation == "h" else "x"

    # Same "Other" overflow rule as stacked_area(): our validated categorical
    # set has exactly 3 hues, so a 4th+ identity series gets a neutral gray
    # rather than an invented, unvalidated 4th hue.
    if color and color in df.columns:
        n_series = df[color].nunique()
        if n_series > len(palette):
            palette += [CHROME[theme]["muted"]] * (n_series - len(palette))

    if color_scale and color is None:
        ramp = SEQUENTIAL_WARM[theme] if color_scale == "warm" else SEQUENTIAL[theme]
        fig = px.bar(
            df,
            x=x if orientation == "v" else y,
            y=y if orientation == "v" else x,
            orientation=orientation,
            color=y,
            color_continuous_scale=ramp,
        )
        fig.update_coloraxes(showscale=False)
    else:
        fig = px.bar(
            df,
            x=x if orientation == "v" else y,
            y=y if orientation == "v" else x,
            color=color,
            orientation=orientation,
            color_discrete_sequence=palette,
            color_discrete_map=color_map,
        )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**_base_layout(theme, title))
    if color is None:
        fig.update_traces(showlegend=False)
        if not color_scale:
            fig.update_traces(marker_color=palette[0])
        fig.update_traces(hovertemplate=f"%{{{category_axis}}}: %{{{value_axis}:,.0f}}{value_suffix}<extra></extra>")
    else:
        fig.update_traces(hovertemplate=f"%{{fullData.name}}: %{{{value_axis}:,.0f}}{value_suffix}<extra></extra>")
    # x_title/y_title are given in terms of the x/y params as the caller
    # passed them; map onto the axis they actually land on once orientation
    # flips category/value between the two physical axes.
    axes_kwargs = (
        dict(x_title=x_title, y_title=y_title) if orientation == "v" else dict(x_title=y_title, y_title=x_title)
    )
    _style_axes(fig, theme, **axes_kwargs)
    return fig


def grouped_bar_compare(
    df: pd.DataFrame, x: str, y: str, color: str, title: str, theme: str, value_suffix: str = "",
    x_title: str | None = None, y_title: str | None = None,
) -> go.Figure:
    """Grouped (not stacked) bars for comparing independent totals side by
    side — e.g. client compare mode (color is entity identity) or two
    totals that shouldn't be summed together, like gross pay vs. total
    employer cost (the latter already includes the former)."""
    palette = CATEGORICAL[theme]
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", color_discrete_sequence=palette)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**_base_layout(theme, title))
    fig.update_traces(hovertemplate=f"%{{fullData.name}}: %{{y:,.0f}}{value_suffix}<extra></extra>")
    _style_axes(fig, theme, x_title=x_title, y_title=y_title)
    # This function is always used to compare identities (client names,
    # amount-type labels) that are already self-explanatory from their
    # legend entries — a legend title here is always a redundant repeat of
    # the color column's raw name (e.g. a bare "Name" heading), never
    # genuinely new information, so it's suppressed unconditionally.
    fig.update_layout(legend_title_text=None)
    return fig


def sparkline(values: pd.Series, theme: str, positive: bool = True) -> go.Figure:
    c = CHROME[theme]
    color = CATEGORICAL[theme][1] if positive else STATUS["critical"]
    fig = go.Figure(
        go.Scatter(
            y=values,
            mode="lines",
            line=dict(width=2, color=color),
            fill="tozeroy",
            fillcolor=color + "1f",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def _jitter(df: pd.DataFrame, lat_col: str, lon_col: str, group_cols: list[str]) -> pd.DataFrame:
    """Spread overlapping points at the same city in a small ring so dense
    cities (Oslo) don't collapse into a single overlapping blob."""
    out = df.copy()
    out["_lat_j"] = out[lat_col].astype(float)
    out["_lon_j"] = out[lon_col].astype(float)
    for _, idx in out.groupby(group_cols).groups.items():
        n = len(idx)
        if n <= 1:
            continue
        radius = 0.06 + 0.01 * n
        for i, row_idx in enumerate(idx):
            angle = 2 * math.pi * i / n
            out.loc[row_idx, "_lat_j"] += radius * math.sin(angle)
            out.loc[row_idx, "_lon_j"] += radius * math.cos(angle) / math.cos(math.radians(out.loc[row_idx, lat_col]))
    return out


def company_scatter_map(
    df: pd.DataFrame,
    size_col: str,
    color_col: str,
    secondary_col: str,
    secondary_label: str,
    title: str,
    theme: str,
    hover_name: str = "name",
    hover_extra: str = "city",
    hover_extra_label: str | None = None,
    color_label: str | None = None,
) -> go.Figure:
    """Proportionally-sized (area-proportional) point markers, sequential
    teal->navy fill, jittered so overlapping cities separate visually."""
    c = CHROME[theme]
    jittered = _jitter(df, "lat", "lon", ["city"])

    max_val = max(float(jittered[size_col].abs().max()), 1.0)
    # area-proportional: marker area ~ value, so radius ~ sqrt(value)
    jittered["_marker_size"] = 8 + 32 * (jittered[size_col].abs() / max_val).pow(0.5)

    # No fixed center/zoom: a hardcoded Norway-wide view (fine for the
    # coverage map) pushes west-coast cities off-screen entirely in a
    # narrow column (e.g. the Clients tab's single-client map) — letting
    # Plotly auto-fit bounds to the actual points keeps every marker visible
    # regardless of how many points or how narrow the container is.
    fig = px.scatter_map(
        jittered,
        lat="_lat_j",
        lon="_lon_j",
        size="_marker_size",
        size_max=40,
        color=color_col,
        color_continuous_scale=SEQUENTIAL[theme],
        hover_name=hover_name,
        custom_data=[hover_extra, color_col, secondary_col],
    )
    if len(jittered) == 1:
        fig.update_layout(map=dict(center={"lat": jittered["_lat_j"].iloc[0], "lon": jittered["_lon_j"].iloc[0]}, zoom=7))
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            + (hover_extra_label or _pretty_label(hover_extra))
            + ": %{customdata[0]}<br>"
            + (color_label or _pretty_label(color_col))
            + ": %{customdata[1]:,.0f} kr<br>"
            + secondary_label
            + ": %{customdata[2]:,.1f}<extra></extra>"
        )
    )
    # A colorbar is meaningless for a single point (min == max) and, worse,
    # squeezes the actual map into a sliver in a narrow column (e.g. the
    # Clients tab's single-client detail map) — only show it once there's
    # an actual range of values to read.
    show_colorbar = jittered[color_col].nunique() > 1
    fig.update_layout(
        # carto-positron/darkmatter: a muted, near-neutral basemap (soft
        # cream/gray land, pale water) instead of the "light"/"dark" built-
        # ins' more saturated blue-gray water — the map still has its own
        # fixed color (a real basemap can't literally be cream), but this
        # is far closer to the app's warm neutral scale, so the map reads
        # as "framed in the same design system" rather than a jarring
        # mismatched rectangle dropped onto a cream page.
        map_style="carto-darkmatter" if theme == "dark" else "carto-positron",
        paper_bgcolor=c["surface"],
        # t=4, not the 32 every other chart's title band needs: every call
        # site passes title="" for a map (labeled instead by the page's own
        # section-label above it), so that 32px was reserved for a title
        # that never actually renders — a bare empty cream strip on top of
        # the map. l/r/b stay at 0 (unchanged) so the map still bleeds to
        # its card's edges on those sides.
        margin=dict(l=0, r=0, t=4, b=0),
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        font=dict(family=FONT_FAMILY, color=c["text_secondary"]),
        coloraxis_showscale=show_colorbar,
        coloraxis_colorbar=dict(title=None, tickfont=dict(color=c["muted"]), len=0.7),
    )
    return fig


def _fit_map_view(df: pd.DataFrame, width_px: int = 340, height_px: int = 320) -> tuple[dict, float]:
    """Center and zoom that fit every point of df into a width x height viewport
    (Web-Mercator maths: 512 px world at zoom 0, 360 deg across). plotly's
    scatter_map has no fit-bounds, and a fixed zoom/center framed only the
    north: most customers sit in the south and fell outside the panel, leaving
    the basemap looking empty. width/height are deliberately conservative
    (panel minus padding) so it also fits the narrowest column."""
    lat_min, lat_max = float(df["lat"].min()), float(df["lat"].max())
    lon_min, lon_max = float(df["lon"].min()), float(df["lon"].max())
    center = {"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2}
    lat_span = max(lat_max - lat_min, 0.5)
    lon_span = max(lon_max - lon_min, 0.5)
    z_lon = math.log2(360 * width_px / (512 * lon_span))
    z_lat = math.log2(360 * height_px * math.cos(math.radians(center["lat"])) / (512 * lat_span))
    return center, max(3.0, min(z_lon, z_lat, 6.0))


def coverage_map(df: pd.DataFrame, count_col: str, theme: str, title: str, names_col: str = "company_names") -> go.Figure:
    """City-level presence/density map for the Overview landing page — a
    coarser 'where do we operate' read, not per-company drill-down. Bubble
    size/color still encode company count (magnitude), but the hover shows
    the actual company names for that city, not just a repeat of the count.
    The view is fitted to the cities shown; the colorscale skips the palest
    steps, which vanish against the light basemap."""
    c = CHROME[theme]
    center, zoom = _fit_map_view(df)
    ramp = SEQUENTIAL[theme][2:] if theme == "light" else SEQUENTIAL[theme][1:]
    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        size=count_col,
        color=count_col,
        color_continuous_scale=ramp,
        size_max=28,
        zoom=zoom,
        center=center,
        hover_name="city",
        custom_data=[names_col],
    )
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<extra></extra>", marker=dict(opacity=0.85))
    fig.update_layout(
        map_style="carto-darkmatter" if theme == "dark" else "carto-positron",
        paper_bgcolor=c["surface"],
        margin=dict(l=0, r=0, t=4, b=0),
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        font=dict(family=FONT_FAMILY, color=c["text_secondary"]),
        coloraxis_showscale=False,
        showlegend=False,
    )
    return fig
