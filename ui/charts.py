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

FONT_FAMILY = "Inter, 'IBM Plex Sans', system-ui, -apple-system, sans-serif"


def _base_layout(theme: str, title: str) -> dict:
    c = CHROME[theme]
    return dict(
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        paper_bgcolor=c["surface"],
        plot_bgcolor=c["surface"],
        font=dict(family=FONT_FAMILY, color=c["text_secondary"], size=12),
        # t=44 (not the tighter 32 used elsewhere): this chart's own title
        # sits inside this top margin, and when a legend is also present it
        # renders in the same band (legend y=1.02, just above the plot
        # area) — 32px was tight enough for the two to clip against the
        # container's top edge on charts with both a title and a legend.
        margin=dict(l=8, r=8, t=44, b=8),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
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


def _apply_granularity_ticks(fig: go.Figure, df: pd.DataFrame, x_col: str, granularity: str | None) -> None:
    """Explicit tick positions/labels keyed to the query granularity, instead
    of relying on Plotly's automatic date-tick formatter. That auto-formatter
    breaks down when the x-range collapses to a single point or a very
    narrow span (observed after switching a chart to quarterly granularity
    on a filtered date range with only one bucket): it falls back to
    microsecond-precision tick labels like "23:59:59.999 Dec 31, 2019"
    instead of a quarter label, because it has almost no range to infer a
    sensible format from. Pinning exact ticks sidesteps that fallback
    entirely, for one bucket or a hundred."""
    formatter = _GRANULARITY_TICK_FORMAT.get(granularity or "")
    if formatter is None or x_col not in df.columns:
        return
    xs = pd.to_datetime(df[x_col]).drop_duplicates().sort_values()
    if xs.empty:
        return
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
    granularity: str | None = None,
) -> go.Figure:
    """x_title/y_title: translated axis labels — pass these rather than
    relying on the raw column name (e.g. "period") ever reaching the UI.
    granularity: "day"/"week"/"month"/"quarter"/"year" — when given, pins
    explicit tick labels instead of Plotly's auto date formatter (see
    _apply_granularity_ticks)."""
    palette = CATEGORICAL[theme]
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=palette)
    fig.update_traces(line=dict(width=2))
    if fill and color is None:
        fig.update_traces(fill="tozeroy", fillcolor=palette[0] + "26")
    fig.update_layout(**_base_layout(theme, title))
    # "closest" hovermode (see _base_layout) means each series shows its own
    # clean "Name: value" tooltip only when the cursor is actually near that
    # line's point — no field-name prefixes, no repeated stats.
    if color is None:
        fig.update_traces(showlegend=False, line_color=palette[0])
        fig.update_traces(hovertemplate=f"{y_title or _pretty_label(y)}: %{{y:,.0f}}{value_suffix}<extra></extra>")
    else:
        fig.update_traces(hovertemplate=f"%{{fullData.name}}: %{{y:,.0f}}{value_suffix}<extra></extra>")
    _style_axes(fig, theme, x_title=x_title, y_title=y_title)
    _apply_granularity_ticks(fig, df, x, granularity)
    _stabilize_flat_yaxis(fig, df, y)
    return fig


def bar_breakdown(
    df: pd.DataFrame, x: str, y: str, color: str | None, title: str, theme: str, orientation: str = "v",
    value_suffix: str = "", color_scale: str | None = None, x_title: str | None = None, y_title: str | None = None,
) -> go.Figure:
    """color_scale: None (flat sage), "sage", or "warm" — when set (and
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
        map_style="dark" if theme == "dark" else "light",
        paper_bgcolor=c["surface"],
        margin=dict(l=0, r=0, t=32, b=0),
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        font=dict(family=FONT_FAMILY, color=c["text_secondary"]),
        coloraxis_showscale=show_colorbar,
        coloraxis_colorbar=dict(title=None, tickfont=dict(color=c["muted"]), len=0.7),
    )
    return fig


def coverage_map(df: pd.DataFrame, count_col: str, theme: str, title: str, names_col: str = "company_names") -> go.Figure:
    """City-level presence/density map for the Overview landing page — a
    coarser 'where do we operate' read, not per-company drill-down. Bubble
    size/color still encode company count (magnitude), but the hover shows
    the actual company names for that city, not just a repeat of the count."""
    c = CHROME[theme]
    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        size=count_col,
        color=count_col,
        color_continuous_scale=SEQUENTIAL[theme],
        size_max=28,
        zoom=3.6,
        center={"lat": 64.5, "lon": 13.0},
        hover_name="city",
        custom_data=[names_col],
    )
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<extra></extra>")
    fig.update_layout(
        map_style="dark" if theme == "dark" else "light",
        paper_bgcolor=c["surface"],
        margin=dict(l=0, r=0, t=32, b=0),
        title=dict(text=title, font=dict(size=13, color=c["text_secondary"], family=FONT_FAMILY)),
        font=dict(family=FONT_FAMILY, color=c["text_secondary"]),
        coloraxis_showscale=False,
        showlegend=False,
    )
    return fig
