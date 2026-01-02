#!/usr/bin/env python3
"""Unified Multiplex Analyzer dashboard.

A 6-tab Dash application combining:
- Cross-N Comparison (basin size, depth analysis, phase transition)
- Multiplex Explorer (layer connectivity, tunnel browser, basin pairs)

This is the consolidated tool replacing both dash-cross-n-comparison.py and
dash-multiplex-explorer.py (see VIZ-CONSOLIDATION-PLAN.md Phase 3).

Tabs:
    1. Basin Size - Size comparison across N values
    2. Depth Analysis - Violin plots and depth statistics per cycle
    3. Phase Transition - N slider with size charts and phase visualization
    4. Layer Connectivity - Heatmap of N×N edge counts
    5. Tunnel Browser - Searchable/filterable tunnel node table
    6. Basin Pairs - Network visualization of basin connectivity

Usage:
    python multiplex-analyzer.py [--port PORT] [--debug]

The dashboard will be available at http://localhost:PORT (default 8056)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    import dash
    from dash import dcc, html, dash_table, callback, Input, Output, State
    import dash_bootstrap_components as dbc
except ImportError:
    print("Error: dash and dash-bootstrap-components required")
    print("Install with: pip install dash dash-bootstrap-components")
    sys.exit(1)

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import shared modules
from shared.colors import (
    BASIN_COLORS,
    BASIN_SHORT_NAMES,
    get_basin_color,
    get_short_name,
    hex_to_rgba,
)
from shared.loaders import (
    load_basin_assignments,
    load_basin_flows,
    load_tunnel_ranking,
    load_layer_connectivity,
    load_tunnel_classification,
    load_tsv_safe,
    REPO_ROOT,
    MULTIPLEX_DIR,
)
from shared.components import metric_card, badge, info_card


# ============================================================================
# Data Loading (at module level for performance)
# ============================================================================

print("Loading data...")
basin_df = load_basin_assignments()
flows_df = load_basin_flows()
tunnel_rank_df = load_tunnel_ranking()
layer_conn_df = load_layer_connectivity()
tunnel_class_df = load_tunnel_classification()

# Load additional data for multiplex explorer features
reachability_df = load_tsv_safe(MULTIPLEX_DIR / "multiplex_reachability_summary.tsv")
intersection_df = load_tsv_safe(MULTIPLEX_DIR / "basin_intersection_by_cycle.tsv")

print(f"  Loaded {len(basin_df):,} basin assignments")
print(f"  Loaded {len(flows_df):,} basin flows")
print(f"  Loaded {len(tunnel_rank_df):,} tunnel nodes")
print(f"  Loaded {len(layer_conn_df):,} layer connectivity rows")
print(f"  Loaded {len(tunnel_class_df):,} tunnel classifications")


# ============================================================================
# Helper Functions
# ============================================================================

def get_basin_stats() -> pd.DataFrame:
    """Compute basin statistics by N and cycle."""
    if basin_df.empty:
        return pd.DataFrame()

    # Filter out tunneling entries for main stats
    df_main = basin_df[~basin_df["cycle_key"].str.contains("_tunneling", na=False)]

    stats = df_main.groupby(["N", "cycle_key"]).agg(
        size=("page_id", "count"),
        mean_depth=("depth", "mean"),
        median_depth=("depth", "median"),
        max_depth=("depth", "max"),
    ).reset_index()

    # Extract base cycle name
    stats["cycle"] = stats["cycle_key"].str.split("__").str[0]

    return stats


def get_unique_cycles() -> list[str]:
    """Get list of unique cycle names."""
    stats = get_basin_stats()
    if stats.empty:
        return []
    return sorted(stats["cycle"].unique().tolist())


def get_n_values() -> list[int]:
    """Get list of available N values."""
    if basin_df.empty:
        return list(range(3, 11))
    return sorted(basin_df["N"].unique().tolist())


def create_connectivity_matrix(df: pd.DataFrame, log_scale: bool = True) -> np.ndarray:
    """Convert layer connectivity dataframe to matrix form."""
    if df.empty:
        return np.zeros((5, 5))

    n_values = sorted(df["src_N"].unique())
    matrix = np.zeros((len(n_values), len(n_values)))

    for _, row in df.iterrows():
        i = n_values.index(row["src_N"])
        j = n_values.index(row["dst_N"])
        matrix[i, j] = row["edge_count"]

    if log_scale:
        matrix = np.log10(matrix + 1)

    return matrix


def get_basin_pairs_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate tunnel nodes by basin pair."""
    if df.empty:
        return pd.DataFrame()

    # Count tunnels per basin pair
    pair_counts = df.groupby("basin_pair").agg({
        "page_id": "count",
        "tunnel_type": lambda x: (x == "progressive").sum(),
    }).reset_index()
    pair_counts.columns = ["basin_pair", "tunnel_count", "progressive_count"]
    pair_counts["alternating_count"] = pair_counts["tunnel_count"] - pair_counts["progressive_count"]
    pair_counts = pair_counts.sort_values("tunnel_count", ascending=False)

    return pair_counts


# Pre-compute commonly used data
BASIN_STATS = get_basin_stats()
UNIQUE_CYCLES = get_unique_cycles()
N_VALUES = get_n_values()


# ============================================================================
# Dash App
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)

app.title = "Multiplex Analyzer"


# ============================================================================
# Header Component
# ============================================================================

def create_header():
    """Create app header with badges."""
    return dbc.Container([
        html.H1("Multiplex Analyzer", className="text-primary mb-2"),
        html.P(
            "Cross-N basin comparison and multiplex structure exploration",
            className="text-muted"
        ),
        html.Div([
            badge(f"{len(basin_df):,} assignments", color="primary"),
            badge(f"{len(tunnel_rank_df):,} tunnel nodes", color="secondary"),
            badge(f"N={min(N_VALUES)}-{max(N_VALUES)} layers", color="info"),
        ], className="mb-3"),
        html.Hr(),
    ], fluid=True, className="my-4")


# ============================================================================
# Tab 1: Basin Size Comparison (from cross-n-comparison)
# ============================================================================

def create_size_tab():
    """Create basin size comparison tab."""
    cycles = UNIQUE_CYCLES

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Basin Size Comparison"),
                html.P("Compare basin sizes across N values (N=3-10)", className="text-muted"),
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label("Select Cycles to Compare:"),
                dcc.Dropdown(
                    id="size-cycle-select",
                    options=[{"label": c.replace("_", " "), "value": c} for c in cycles],
                    value=cycles[:6] if len(cycles) >= 6 else cycles,
                    multi=True,
                ),
            ], md=8),
            dbc.Col([
                html.Label("Scale:"),
                dbc.RadioItems(
                    id="size-scale",
                    options=[
                        {"label": "Log", "value": "log"},
                        {"label": "Linear", "value": "linear"},
                    ],
                    value="log",
                    inline=True,
                ),
            ], md=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="size-chart", style={"height": "500px"}),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Basin Size Table", className="mt-4"),
                html.Div(id="size-table"),
            ]),
        ]),
    ], fluid=True)


# ============================================================================
# Tab 2: Depth Analysis (from cross-n-comparison)
# ============================================================================

def create_depth_tab():
    """Create depth analysis tab."""
    cycles = UNIQUE_CYCLES

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Depth Analysis"),
                html.P("Distribution and statistics of depth per N value", className="text-muted"),
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label("Select Cycle:"),
                dcc.Dropdown(
                    id="depth-cycle-select",
                    options=[{"label": c.replace("_", " "), "value": c} for c in cycles],
                    value=cycles[0] if cycles else None,
                ),
            ], md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="depth-violin", style={"height": "400px"}),
            ], md=6),
            dbc.Col([
                dcc.Graph(id="depth-stats", style={"height": "400px"}),
            ], md=6),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="depth-comparison", style={"height": "400px"}),
            ]),
        ], className="mt-4"),
    ], fluid=True)


# ============================================================================
# Tab 3: Phase Transition (from cross-n-comparison)
# ============================================================================

def create_phase_tab():
    """Create phase transition explorer tab."""
    n_values = N_VALUES

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Phase Transition Explorer"),
                html.P("Explore basin sizes at each N value and the N=5 phase transition", className="text-muted"),
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label("Select N Value:"),
                dcc.Slider(
                    id="phase-n-slider",
                    min=min(n_values) if n_values else 3,
                    max=max(n_values) if n_values else 10,
                    step=1,
                    value=5,
                    marks={n: str(n) for n in n_values},
                ),
            ], md=8),
            dbc.Col([
                html.Div(id="phase-n-info", className="text-center"),
            ], md=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="phase-chart", style={"height": "500px"}),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Cycle Statistics at Selected N", className="mt-4"),
                html.Div(id="phase-table"),
            ]),
        ]),
    ], fluid=True)


# ============================================================================
# Tab 4: Layer Connectivity (from multiplex-explorer)
# ============================================================================

def create_connectivity_tab():
    """Create layer connectivity matrix tab."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Layer Connectivity Matrix"),
                html.P("Edge counts between N layers. Diagonal = within-N, off-diagonal = tunnel edges.", className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.Checklist(
                    id="connectivity-log-scale",
                    options=[{"label": "Log scale", "value": "log"}],
                    value=["log"],
                    switch=True,
                    className="mt-2"
                ),
            ], width=4, className="text-end"),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="connectivity-heatmap", style={"height": "500px"}),
            ], width=8),
            dbc.Col([
                html.H5("Statistics"),
                html.Div(id="connectivity-stats", className="small"),
            ], width=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Cross-Layer Edge Breakdown", className="mt-4"),
                dcc.Graph(id="cross-layer-bar", style={"height": "300px"}),
            ])
        ]),
    ], fluid=True)


# ============================================================================
# Tab 5: Tunnel Browser (from multiplex-explorer)
# ============================================================================

def create_tunnel_tab():
    """Create tunnel node explorer tab."""
    # Get unique values for filters
    tunnel_types = ["all"] + list(tunnel_class_df["tunnel_type"].unique()) if not tunnel_class_df.empty else ["all"]
    basin_pairs = ["all"] + list(tunnel_class_df["basin_pair"].unique()[:50]) if not tunnel_class_df.empty else ["all"]

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Tunnel Node Browser"),
                html.P("Browse and filter tunnel nodes by type, basin pair, and score.", className="text-muted"),
            ])
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label("Tunnel Type:", className="fw-bold"),
                dcc.Dropdown(
                    id="tunnel-type-filter",
                    options=[{"label": t.title() if t != "all" else "All Types", "value": t} for t in tunnel_types],
                    value="all",
                    clearable=False,
                ),
            ], width=3),
            dbc.Col([
                html.Label("Basin Pair:", className="fw-bold"),
                dcc.Dropdown(
                    id="basin-pair-filter",
                    options=[{"label": b if b != "all" else "All Pairs", "value": b} for b in basin_pairs],
                    value="all",
                    clearable=False,
                ),
            ], width=4),
            dbc.Col([
                html.Label("Min Score:", className="fw-bold"),
                dcc.Slider(
                    id="min-score-filter",
                    min=0,
                    max=80,
                    step=5,
                    value=0,
                    marks={i: str(i) for i in range(0, 81, 20)},
                ),
            ], width=4),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Div(id="tunnel-table-summary", className="mb-2 text-muted"),
                dash_table.DataTable(
                    id="tunnel-table",
                    columns=[
                        {"name": "Page ID", "id": "page_id"},
                        {"name": "Title", "id": "page_title"},
                        {"name": "Type", "id": "tunnel_type"},
                        {"name": "Score", "id": "tunnel_score", "type": "numeric", "format": {"specifier": ".1f"}},
                        {"name": "Basins", "id": "n_basins_bridged"},
                        {"name": "Transitions", "id": "n_transitions"},
                        {"name": "Mean Depth", "id": "mean_depth", "type": "numeric", "format": {"specifier": ".1f"}},
                        {"name": "Basin List", "id": "basin_list"},
                    ],
                    data=[],
                    page_size=15,
                    sort_action="native",
                    sort_mode="single",
                    sort_by=[{"column_id": "tunnel_score", "direction": "desc"}],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "12px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
                    style_data_conditional=[
                        {"if": {"filter_query": "{tunnel_type} = 'progressive'"}, "backgroundColor": "#e8f5e9"},
                        {"if": {"filter_query": "{tunnel_type} = 'alternating'"}, "backgroundColor": "#fff3e0"},
                    ],
                ),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Score Distribution", className="mt-4"),
                dcc.Graph(id="score-histogram", style={"height": "250px"}),
            ], width=6),
            dbc.Col([
                html.H5("Tunnel Type Breakdown", className="mt-4"),
                dcc.Graph(id="type-pie", style={"height": "250px"}),
            ], width=6),
        ]),
    ], fluid=True)


# ============================================================================
# Tab 6: Basin Pairs (from multiplex-explorer)
# ============================================================================

def create_pairs_tab():
    """Create basin pair network tab."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Basin Pair Connectivity"),
                html.P("Network visualization showing which basins connect via tunnel nodes.", className="text-muted"),
            ])
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="basin-pair-network", style={"height": "500px"}),
            ], width=8),
            dbc.Col([
                html.H5("Top Basin Pairs"),
                html.Div(id="top-basin-pairs"),
            ], width=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Tunnel Count by Basin Pair", className="mt-4"),
                dcc.Graph(id="basin-pair-bar", style={"height": "300px"}),
            ])
        ]),
    ], fluid=True)


# ============================================================================
# Main Layout with Tabs
# ============================================================================

app.layout = html.Div([
    create_header(),
    dbc.Tabs([
        dbc.Tab(label="Basin Size", tab_id="tab-size"),
        dbc.Tab(label="Depth Analysis", tab_id="tab-depth"),
        dbc.Tab(label="Phase Transition", tab_id="tab-phase"),
        dbc.Tab(label="Layer Connectivity", tab_id="tab-connectivity"),
        dbc.Tab(label="Tunnel Browser", tab_id="tab-tunnels"),
        dbc.Tab(label="Basin Pairs", tab_id="tab-pairs"),
    ], id="tabs", active_tab="tab-size", className="mb-3 px-3"),
    html.Div(id="tab-content", className="px-3"),
])


# ============================================================================
# Tab Router Callback
# ============================================================================

@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab(active_tab):
    """Render the active tab content."""
    if active_tab == "tab-size":
        return create_size_tab()
    elif active_tab == "tab-depth":
        return create_depth_tab()
    elif active_tab == "tab-phase":
        return create_phase_tab()
    elif active_tab == "tab-connectivity":
        return create_connectivity_tab()
    elif active_tab == "tab-tunnels":
        return create_tunnel_tab()
    elif active_tab == "tab-pairs":
        return create_pairs_tab()
    return html.P("Select a tab")


# ============================================================================
# Tab 1: Basin Size Callbacks
# ============================================================================

@callback(
    Output("size-chart", "figure"),
    Input("size-cycle-select", "value"),
    Input("size-scale", "value"),
)
def update_size_chart(selected_cycles, scale):
    """Update the basin size comparison chart."""
    if BASIN_STATS.empty or not selected_cycles:
        return go.Figure()

    # Filter to selected cycles
    df = BASIN_STATS[BASIN_STATS["cycle"].isin(selected_cycles)]

    fig = px.line(
        df,
        x="N",
        y="size",
        color="cycle",
        markers=True,
        title="Basin Size by N Value",
        labels={"N": "N (link position)", "size": "Basin Size (pages)", "cycle": "Cycle"},
    )

    fig.update_layout(
        yaxis_type=scale,
        xaxis=dict(tickmode="linear", tick0=3, dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        template="plotly_white",
    )

    # Add N=5 annotation
    fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_annotation(x=5, y=1.05, yref="paper", text="N=5 Peak", showarrow=False)

    return fig


@callback(
    Output("size-table", "children"),
    Input("size-cycle-select", "value"),
)
def update_size_table(selected_cycles):
    """Update the basin size summary table."""
    if BASIN_STATS.empty or not selected_cycles:
        return html.P("No data available")

    df = BASIN_STATS[BASIN_STATS["cycle"].isin(selected_cycles)]

    # Pivot to show N values as columns
    pivot = df.pivot_table(
        index="cycle",
        columns="N",
        values="size",
        aggfunc="sum",
    ).fillna(0).astype(int)

    # Add collapse factor (N=5 / N=10 if both exist)
    if 5 in pivot.columns and 10 in pivot.columns:
        pivot["Collapse (N5/N10)"] = (pivot[5] / pivot[10].replace(0, np.nan)).round(1)

    pivot = pivot.reset_index()

    return dbc.Table.from_dataframe(
        pivot,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="small",
    )


# ============================================================================
# Tab 2: Depth Analysis Callbacks
# ============================================================================

@callback(
    Output("depth-violin", "figure"),
    Output("depth-stats", "figure"),
    Input("depth-cycle-select", "value"),
)
def update_depth_charts(selected_cycle):
    """Update depth analysis charts."""
    if basin_df.empty or not selected_cycle:
        return go.Figure(), go.Figure()

    # Filter to selected cycle (match on base name)
    df_cycle = basin_df[basin_df["cycle_key"].str.startswith(selected_cycle)]

    if df_cycle.empty:
        return go.Figure(), go.Figure()

    # Violin plot of depth by N
    fig_violin = px.violin(
        df_cycle,
        x="N",
        y="depth",
        box=True,
        title=f"Depth Distribution: {selected_cycle.replace('_', ' ')}",
    )
    fig_violin.update_layout(template="plotly_white")

    # Stats chart (mean, median, max)
    stats = df_cycle.groupby("N").agg(
        mean_depth=("depth", "mean"),
        median_depth=("depth", "median"),
        max_depth=("depth", "max"),
    ).reset_index()

    fig_stats = go.Figure()
    fig_stats.add_trace(go.Bar(x=stats["N"], y=stats["max_depth"], name="Max", marker_color="#1f77b4"))
    fig_stats.add_trace(go.Scatter(x=stats["N"], y=stats["mean_depth"], mode="lines+markers", name="Mean", line=dict(color="#ff7f0e")))
    fig_stats.add_trace(go.Scatter(x=stats["N"], y=stats["median_depth"], mode="lines+markers", name="Median", line=dict(color="#2ca02c")))

    fig_stats.update_layout(
        title=f"Depth Statistics: {selected_cycle.replace('_', ' ')}",
        xaxis=dict(title="N", tickmode="linear"),
        yaxis=dict(title="Depth"),
        barmode="overlay",
        template="plotly_white",
    )

    return fig_violin, fig_stats


@callback(
    Output("depth-comparison", "figure"),
    Input("depth-cycle-select", "value"),
)
def update_depth_comparison(selected_cycle):
    """Update cross-cycle depth comparison."""
    if BASIN_STATS.empty:
        return go.Figure()

    fig = px.scatter(
        BASIN_STATS,
        x="mean_depth",
        y="size",
        color="cycle",
        size="max_depth",
        hover_data=["N"],
        title="Basin Size vs Mean Depth (all cycles, all N)",
        labels={"mean_depth": "Mean Depth", "size": "Basin Size", "cycle": "Cycle"},
    )

    fig.update_layout(
        yaxis_type="log",
        template="plotly_white",
    )

    return fig


# ============================================================================
# Tab 3: Phase Transition Callbacks
# ============================================================================

@callback(
    Output("phase-chart", "figure"),
    Output("phase-n-info", "children"),
    Output("phase-table", "children"),
    Input("phase-n-slider", "value"),
)
def update_phase_charts(selected_n):
    """Update phase transition charts."""
    if BASIN_STATS.empty:
        return go.Figure(), "", html.P("No data")

    # Filter to selected N
    df_n = BASIN_STATS[BASIN_STATS["N"] == selected_n].sort_values("size", ascending=False)

    # Bar chart of basin sizes at this N
    fig = px.bar(
        df_n,
        x="cycle",
        y="size",
        color="cycle",
        title=f"Basin Sizes at N={selected_n}",
        labels={"cycle": "Cycle", "size": "Basin Size"},
    )

    fig.update_layout(
        yaxis_type="log",
        showlegend=False,
        xaxis_tickangle=45,
        template="plotly_white",
    )

    # Info box
    total_pages = df_n["size"].sum()
    n_cycles = len(df_n)
    info = dbc.Card([
        dbc.CardBody([
            html.H3(f"N = {selected_n}", className="text-primary"),
            html.P(f"Total: {total_pages:,} pages"),
            html.P(f"Cycles: {n_cycles}"),
        ])
    ])

    # Table
    table_df = df_n[["cycle", "size", "mean_depth", "max_depth"]].copy()
    table_df["mean_depth"] = table_df["mean_depth"].round(1)
    table_df.columns = ["Cycle", "Size", "Mean Depth", "Max Depth"]

    table = dbc.Table.from_dataframe(
        table_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

    return fig, info, table


# ============================================================================
# Tab 4: Layer Connectivity Callbacks
# ============================================================================

@callback(
    Output("connectivity-heatmap", "figure"),
    Output("connectivity-stats", "children"),
    Output("cross-layer-bar", "figure"),
    Input("connectivity-log-scale", "value"),
)
def update_connectivity_tab(log_scale):
    """Update layer connectivity visualizations."""
    use_log = "log" in log_scale if log_scale else False

    if layer_conn_df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", showarrow=False)
        return empty_fig, "No data", empty_fig

    # Create heatmap
    n_values = sorted(layer_conn_df["src_N"].unique())
    matrix = create_connectivity_matrix(layer_conn_df, log_scale=use_log)

    # Raw matrix for annotations
    raw_matrix = create_connectivity_matrix(layer_conn_df, log_scale=False)

    # Format annotations
    annotations = []
    for i, src_n in enumerate(n_values):
        for j, dst_n in enumerate(n_values):
            count = int(raw_matrix[i, j])
            annotations.append(
                dict(
                    x=j, y=i,
                    text=f"{count:,}",
                    showarrow=False,
                    font=dict(color="white" if matrix[i, j] > matrix.max() * 0.5 else "black", size=10),
                )
            )

    heatmap = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"N={n}" for n in n_values],
        y=[f"N={n}" for n in n_values],
        colorscale="YlOrRd",
        colorbar=dict(title="log10(count)" if use_log else "count"),
    ))
    heatmap.update_layout(
        title="Layer-to-Layer Edge Counts",
        xaxis_title="Destination N",
        yaxis_title="Source N",
        annotations=annotations,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=60, r=20, t=50, b=60),
    )

    # Statistics
    total_edges = int(raw_matrix.sum())
    diagonal_edges = int(np.trace(raw_matrix))
    cross_layer_edges = total_edges - diagonal_edges

    stats = [
        html.P([html.Strong("Total edges: "), f"{total_edges:,}"]),
        html.P([html.Strong("Within-N: "), f"{diagonal_edges:,} ({100*diagonal_edges/total_edges:.1f}%)"]),
        html.P([html.Strong("Cross-N: "), f"{cross_layer_edges:,} ({100*cross_layer_edges/total_edges:.1f}%)"]),
        html.Hr(),
        html.P([html.Strong("Strongest cross-layer:")]),
    ]

    # Find strongest cross-layer connections
    cross_layer = layer_conn_df[layer_conn_df["src_N"] != layer_conn_df["dst_N"]].copy()
    cross_layer = cross_layer.sort_values("edge_count", ascending=False).head(5)
    for _, row in cross_layer.iterrows():
        stats.append(html.P(f"N={row['src_N']}->N={row['dst_N']}: {row['edge_count']:,}", className="small"))

    # Cross-layer bar chart
    cross_layer_all = layer_conn_df[layer_conn_df["src_N"] != layer_conn_df["dst_N"]].copy()
    cross_layer_all["pair"] = cross_layer_all.apply(
        lambda r: f"N={r['src_N']}->N={r['dst_N']}", axis=1
    )

    bar_fig = px.bar(
        cross_layer_all.sort_values("edge_count", ascending=True),
        x="edge_count",
        y="pair",
        orientation="h",
        title="Cross-Layer Edge Counts",
        labels={"edge_count": "Edge Count", "pair": "Layer Pair"},
    )
    bar_fig.update_layout(margin=dict(l=100, r=20, t=50, b=40))

    return heatmap, stats, bar_fig


# ============================================================================
# Tab 5: Tunnel Browser Callbacks
# ============================================================================

@callback(
    Output("tunnel-table", "data"),
    Output("tunnel-table-summary", "children"),
    Output("score-histogram", "figure"),
    Output("type-pie", "figure"),
    Input("tunnel-type-filter", "value"),
    Input("basin-pair-filter", "value"),
    Input("min-score-filter", "value"),
)
def update_tunnel_table(tunnel_type, basin_pair, min_score):
    """Update tunnel node table and visualizations."""
    if tunnel_rank_df.empty:
        empty_fig = go.Figure()
        return [], "No data", empty_fig, empty_fig

    # Filter data
    filtered = tunnel_rank_df.copy()

    if tunnel_type != "all":
        filtered = filtered[filtered["tunnel_type"] == tunnel_type]

    if basin_pair != "all":
        # Need to join with classification to filter by basin pair
        class_subset = tunnel_class_df[tunnel_class_df["basin_pair"] == basin_pair]["page_id"]
        filtered = filtered[filtered["page_id"].isin(class_subset)]

    if min_score > 0:
        filtered = filtered[filtered["tunnel_score"] >= min_score]

    # Summary
    summary = f"Showing {len(filtered):,} of {len(tunnel_rank_df):,} tunnel nodes"

    # Table data
    table_data = filtered.head(500).to_dict("records")

    # Score histogram
    hist_fig = px.histogram(
        filtered,
        x="tunnel_score",
        nbins=30,
        title="Score Distribution",
        labels={"tunnel_score": "Tunnel Score"},
    )
    hist_fig.update_layout(margin=dict(l=40, r=20, t=50, b=40), showlegend=False)

    # Type pie chart
    type_counts = filtered["tunnel_type"].value_counts()
    pie_fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Tunnel Types",
        color_discrete_map={"progressive": "#4CAF50", "alternating": "#FF9800"},
    )
    pie_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    return table_data, summary, hist_fig, pie_fig


# ============================================================================
# Tab 6: Basin Pairs Callbacks
# ============================================================================

@callback(
    Output("basin-pair-network", "figure"),
    Output("top-basin-pairs", "children"),
    Output("basin-pair-bar", "figure"),
    Input("tabs", "active_tab"),
)
def update_basin_pairs(active_tab):
    """Update basin pair visualizations."""
    if tunnel_class_df.empty:
        empty_fig = go.Figure()
        return empty_fig, "No data", empty_fig

    # Get basin pair summary
    pair_summary = get_basin_pairs_summary(tunnel_class_df)

    if pair_summary.empty:
        empty_fig = go.Figure()
        return empty_fig, "No data", empty_fig

    # Top pairs list
    top_pairs = []
    for _, row in pair_summary.head(10).iterrows():
        top_pairs.append(
            html.Div([
                html.Strong(f"{row['tunnel_count']:,}"),
                html.Span(f" tunnels: {row['basin_pair'][:40]}...", className="small"),
            ], className="mb-2")
        )

    # Bar chart of top pairs
    top_20 = pair_summary.head(20)
    bar_fig = px.bar(
        top_20,
        x="tunnel_count",
        y="basin_pair",
        orientation="h",
        color="progressive_count",
        color_continuous_scale="Greens",
        title="Top 20 Basin Pairs by Tunnel Count",
        labels={"tunnel_count": "Tunnel Count", "basin_pair": "Basin Pair", "progressive_count": "Progressive"},
    )
    bar_fig.update_layout(
        margin=dict(l=200, r=20, t=50, b=40),
        yaxis=dict(autorange="reversed"),
        height=400,
    )

    # Network visualization (simplified - show top pairs as nodes and edges)
    # Extract unique basins
    basins = set()
    edges = []
    for _, row in pair_summary.head(30).iterrows():
        pair = row["basin_pair"]
        if " / " in pair:
            b1, b2 = pair.split(" / ")[:2]
            b1, b2 = b1.strip()[:20], b2.strip()[:20]
            basins.add(b1)
            basins.add(b2)
            edges.append((b1, b2, row["tunnel_count"]))

    # Create network positions (simple circular layout)
    basin_list = list(basins)
    n_basins = len(basin_list)
    if n_basins > 0:
        angles = np.linspace(0, 2 * np.pi, n_basins, endpoint=False)
        positions = {b: (np.cos(a), np.sin(a)) for b, a in zip(basin_list, angles)}
    else:
        positions = {}

    # Create edge traces
    edge_traces = []
    for b1, b2, count in edges:
        x0, y0 = positions.get(b1, (0, 0))
        x1, y1 = positions.get(b2, (0, 0))
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode="lines",
            line=dict(width=max(1, np.log10(count + 1) * 2), color="rgba(100, 100, 100, 0.5)"),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Create node trace
    if basin_list:
        node_trace = go.Scatter(
            x=[positions[b][0] for b in basin_list],
            y=[positions[b][1] for b in basin_list],
            mode="markers+text",
            marker=dict(size=15, color="#1f77b4"),
            text=basin_list,
            textposition="top center",
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
        network_fig = go.Figure(data=edge_traces + [node_trace])
    else:
        network_fig = go.Figure()

    network_fig.update_layout(
        title="Basin Pair Network (Top 30)",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return network_fig, top_pairs, bar_fig


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Multiplex Analyzer Dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8056, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Multiplex Analyzer Dashboard")
    print(f"{'='*60}")
    print(f"URL: http://{args.host}:{args.port}")
    print(f"{'='*60}\n")

    app.run(host=args.host, port=args.port, debug=args.debug)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
