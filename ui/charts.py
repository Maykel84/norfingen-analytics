"""Chart builders on the Modernist navy/teal/steel system.

Palette provenance: the categorical triple below (navy, teal, slate-violet)
was checked with the dataviz skill's validate_palette.js — all six checks
pass in both light and dark mode on the *adjacent* pairlist (the only one
this app needs: every categorical chart here has <=3 series). The sequential
ramp is a hand-built teal->navy duotone (a brand choice, not the skill's
strict single-hue ramp) with monotonically decreasing lightness, which is
what the skill actually checks for sequential/diverging encodings.
"""

import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CATEGORICAL = {
    "light": ["#1c4fae", "#0c9b7e", "#8452c9"],
    "dark": ["#4c7fd6", "#12a98d", "#9868d6"],
}

SEQUENTIAL_TEAL_NAVY = {
    "light": ["#c7e8e0", "#8ccdbc", "#3cae97", "#0c887a", "#0c6973", "#0d4e6d", "#0d3a69", "#0d2c66"],
    "dark": ["#134a43", "#128c76", "#24a89e", "#40a8b9", "#5aa7d2", "#6da6e4", "#7aa6f0", "#7aa6f0"],
}

STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

CHROME = {
    "light": {
        "surface": "#fcfcfb",
        "text_primary": "#0f1720",
        "text_secondary": "#4b5563",
        "muted": "#8a94a0",
        "grid": "#e3e6e9",
        "axis": "#c3c2b7",
    },
    "dark": {
        "surface": "#171b20",
        "text_primary": "#f5f6f7",
        "text_secondary": "#c3c9d1",
        "muted": "#7d8792",
        "grid": "#262c33",
        "axis": "#383835",
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
        margin=dict(l=8, r=8, t=32, b=8),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color=c["text_secondary"]),
        ),
        hoverlabel=dict(bgcolor=c["surface"], font=dict(family=FONT_FAMILY, color=c["text_primary"])),
        hovermode="x unified",
    )


def _style_axes(fig: go.Figure, theme: str) -> go.Figure:
    c = CHROME[theme]
    fig.update_xaxes(showgrid=False, showline=True, linecolor=c["grid"], color=c["muted"])
    fig.update_yaxes(showgrid=True, gridcolor=c["grid"], zeroline=False, color=c["muted"])
    return fig


def line_over_time(df: pd.DataFrame, x: str, y: str, color: str | None, title: str, theme: str) -> go.Figure:
    palette = CATEGORICAL[theme]
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=palette)
    fig.update_traces(line=dict(width=2))
    fig.update_layout(**_base_layout(theme, title))
    if color is None:
        fig.update_traces(showlegend=False, line_color=palette[0])
    _style_axes(fig, theme)
    return fig


def bar_breakdown(
    df: pd.DataFrame, x: str, y: str, color: str | None, title: str, theme: str, orientation: str = "v"
) -> go.Figure:
    palette = CATEGORICAL[theme]
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
        fig.update_traces(showlegend=False, marker_color=palette[0])
    _style_axes(fig, theme)
    return fig


def grouped_bar_compare(df: pd.DataFrame, x: str, y: str, color: str, title: str, theme: str) -> go.Figure:
    """Grouped bars for client compare mode — color is entity identity (<=3), not magnitude."""
    palette = CATEGORICAL[theme]
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", color_discrete_sequence=palette)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**_base_layout(theme, title))
    _style_axes(fig, theme)
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
        color_continuous_scale=SEQUENTIAL_TEAL_NAVY[theme],
        hover_name=hover_name,
        custom_data=[hover_extra, color_col, secondary_col],
    )
    if len(jittered) == 1:
        fig.update_layout(map=dict(center={"lat": jittered["_lat_j"].iloc[0], "lon": jittered["_lon_j"].iloc[0]}, zoom=7))
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            + hover_extra.capitalize()
            + ": %{customdata[0]}<br>"
            + color_col.capitalize()
            + ": %{customdata[1]:,.0f}<br>"
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


def coverage_map(df: pd.DataFrame, count_col: str, theme: str, title: str) -> go.Figure:
    """City-level presence/density map for the Overview landing page — a
    coarser 'where do we operate' read, not per-company drill-down."""
    c = CHROME[theme]
    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        size=count_col,
        color=count_col,
        color_continuous_scale=SEQUENTIAL_TEAL_NAVY[theme],
        size_max=28,
        zoom=3.6,
        center={"lat": 64.5, "lon": 13.0},
        hover_name="city",
        custom_data=[count_col],
        hover_data={count_col: True, "lat": False, "lon": False},
    )
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
