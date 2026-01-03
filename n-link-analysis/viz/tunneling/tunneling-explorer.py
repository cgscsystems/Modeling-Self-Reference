#!/usr/bin/env python3
"""Unified Tunneling Explorer dashboard.

A 6-tab Dash application combining:
- Tunneling Dashboard (overview, flows, nodes, stability, validation)
- Path Tracer (search + trace per-page basin membership)

This is the consolidated tool replacing both tunneling-dashboard.py and
path-tracer-tool.py (see VIZ-CONSOLIDATION-PLAN.md Phase 2).

Tabs:
    1. Overview - Metric cards, mechanism pie, scatter plot
    2. Basin Flows - Sankey diagram of cross-basin flows
    3. Tunnel Nodes - Filterable table of tunnel nodes
    4. Path Tracer - Search and trace individual pages
    5. Stability - Basin stability analysis
    6. Validation - Theory validation results

Usage:
    # Local file mode (default)
    python tunneling-explorer.py [--port PORT]

    # API mode (connects to N-Link API server for live tracing)
    python tunneling-explorer.py --use-api [--api-url http://localhost:8000]

The dashboard will be available at http://localhost:PORT (default 8060)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

try:
    import dash
    from dash import dcc, html, dash_table, callback, Input, Output, State
    import dash_bootstrap_components as dbc
except ImportError:
    print("Error: dash and dash-bootstrap-components required")
    print("Install with: pip install dash dash-bootstrap-components")
    sys.exit(1)

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
    load_basin_stability,
    load_tunnel_mechanisms,
    load_validation_metrics,
    load_semantic_model,
    REPO_ROOT,
    MULTIPLEX_DIR,
)
from shared.components import metric_card, badge, info_card

# Import API client for path tracer functionality
try:
    from api_client import NLinkAPIClient, HTTPX_AVAILABLE
except ImportError:
    HTTPX_AVAILABLE = False
    NLinkAPIClient = None

# Global configuration (set by CLI args)
USE_API = False
API_URL = "http://localhost:8000"
api_client: Optional[NLinkAPIClient] = None


# ============================================================================
# Data Loading (at module level for performance)
# ============================================================================

print("Loading data...")
semantic_model = load_semantic_model()
flows_df = load_basin_flows()
tunnel_df = load_tunnel_ranking()
stability_df = load_basin_stability()
mechanisms_df = load_tunnel_mechanisms()
validation_df = load_validation_metrics()
multiplex_df = load_basin_assignments()

# Build lookup dictionaries for path tracer search
title_to_id: dict[str, int] = {}
id_to_title: dict[int, str] = {}
if not tunnel_df.empty:
    for _, row in tunnel_df.iterrows():
        page_id = row["page_id"]
        title = row.get("page_title", "")
        if pd.notna(title) and title != "":
            title_to_id[title.lower()] = page_id
            id_to_title[page_id] = title

print(f"  Loaded semantic model: {bool(semantic_model)}")
print(f"  Loaded {len(flows_df):,} basin flows")
print(f"  Loaded {len(tunnel_df):,} tunnel nodes")
print(f"  Loaded {len(multiplex_df):,} multiplex assignments")


# ============================================================================
# Overview Tab Components
# ============================================================================

def create_overview_charts(
    semantic_model: dict,
    mechanisms_df: pd.DataFrame,
    tunnel_df: pd.DataFrame,
) -> tuple[go.Figure, go.Figure, go.Figure]:
    """Create overview tab charts: mechanism pie, scatter, type bar."""

    # Mechanism pie chart
    if not mechanisms_df.empty:
        mech_fig = px.pie(
            mechanisms_df,
            values="count",
            names="mechanism",
            title="Tunnel Mechanism Distribution",
            color_discrete_sequence=["#2ca02c", "#ff7f0e"],
            hole=0.4,
        )
        mech_fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    else:
        mech_fig = go.Figure()
        mech_fig.add_annotation(text="No mechanism data", showarrow=False)

    # Tunnel score vs depth scatter
    if not tunnel_df.empty:
        scatter_fig = px.scatter(
            tunnel_df.head(500),  # Limit for performance
            x="mean_depth",
            y="tunnel_score",
            color="tunnel_type",
            hover_data=["page_title"],
            title="Tunnel Score vs Mean Depth",
            labels={"mean_depth": "Mean Depth", "tunnel_score": "Tunnel Score"},
            color_discrete_map={"progressive": "#2ca02c", "alternating": "#ff7f0e"},
        )
        scatter_fig.update_layout(margin=dict(t=50, b=50, l=50, r=20))
    else:
        scatter_fig = go.Figure()
        scatter_fig.add_annotation(text="No tunnel data", showarrow=False)

    # Type distribution bar
    if not tunnel_df.empty:
        type_counts = tunnel_df["tunnel_type"].value_counts()
        type_fig = go.Figure(
            data=[
                go.Bar(
                    x=type_counts.index.tolist(),
                    y=type_counts.values.tolist(),
                    marker_color=["#2ca02c", "#ff7f0e"],
                )
            ]
        )
        type_fig.update_layout(
            title="Tunnel Type Distribution",
            xaxis_title="Type",
            yaxis_title="Count",
            margin=dict(t=50, b=50, l=50, r=20),
        )
    else:
        type_fig = go.Figure()

    return mech_fig, scatter_fig, type_fig


# ============================================================================
# Basin Flows Tab Components
# ============================================================================

def create_sankey_figure(flows_df: pd.DataFrame) -> go.Figure:
    """Create Sankey diagram from flows data."""
    if flows_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No flow data available", showarrow=False)
        return fig

    n_values = sorted(set(flows_df["from_n"].unique()) | set(flows_df["to_n"].unique()))
    all_basins = sorted(
        set(flows_df["from_basin"].unique()) | set(flows_df["to_basin"].unique())
    )

    nodes = []
    node_indices = {}

    for n in n_values:
        for basin in all_basins:
            node_key = f"{basin}@N{n}"
            node_indices[node_key] = len(nodes)
            nodes.append(
                {
                    "label": f"{get_short_name(basin)} (N={n})",
                    "color": get_basin_color(basin),
                }
            )

    sources, targets, values, colors = [], [], [], []

    for _, row in flows_df.iterrows():
        from_key = f"{row['from_basin']}@N{row['from_n']}"
        to_key = f"{row['to_basin']}@N{row['to_n']}"

        if from_key in node_indices and to_key in node_indices:
            sources.append(node_indices[from_key])
            targets.append(node_indices[to_key])
            values.append(row["count"])
            colors.append(hex_to_rgba(get_basin_color(row["from_basin"]), 0.5))

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20,
                    thickness=25,
                    line=dict(color="black", width=0.5),
                    label=[n["label"] for n in nodes],
                    color=[n["color"] for n in nodes],
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=colors,
                ),
            )
        ]
    )

    fig.update_layout(
        title="Cross-Basin Page Flows",
        height=500,
        margin=dict(t=50, b=20, l=20, r=20),
    )

    return fig


# ============================================================================
# Stability Tab Components
# ============================================================================

def create_stability_chart(stability_df: pd.DataFrame) -> go.Figure:
    """Create basin stability horizontal bar chart."""
    if stability_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No stability data", showarrow=False)
        return fig

    df = stability_df.copy()
    df["short_name"] = df["canonical_cycle_id"].apply(get_short_name)

    colors = []
    for _, row in df.iterrows():
        stability = row.get("stability_class", "unknown")
        if stability == "fragile":
            colors.append("#d62728")
        elif stability == "moderate":
            colors.append("#ff7f0e")
        elif stability == "stable":
            colors.append("#2ca02c")
        else:
            colors.append("#7f7f7f")

    fig = go.Figure(
        data=[
            go.Bar(
                y=df["short_name"],
                x=df["persistence_score"],
                orientation="h",
                marker_color=colors,
                text=[f"{row.get('total_pages', 0):,} pages" for _, row in df.iterrows()],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title="Basin Stability Scores",
        xaxis_title="Persistence Score",
        yaxis_title="Basin",
        height=400,
        margin=dict(t=50, b=50, l=120, r=80),
    )

    return fig


# ============================================================================
# Validation Tab Components
# ============================================================================

def create_validation_table(validation_df: pd.DataFrame) -> dash_table.DataTable | html.P:
    """Create validation results table."""
    if validation_df.empty:
        return html.P("No validation data available")

    return dash_table.DataTable(
        id="validation-table",
        columns=[
            {"name": "Hypothesis", "id": "hypothesis"},
            {"name": "Expected", "id": "expected"},
            {"name": "Observed", "id": "observed"},
            {"name": "Statistic", "id": "statistic"},
            {"name": "P-Value", "id": "p_value"},
            {"name": "Result", "id": "result"},
        ],
        data=validation_df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "fontSize": "14px",
        },
        style_header={
            "backgroundColor": "#1a1a2e",
            "color": "white",
            "fontWeight": "bold",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": '{result} = "validated"'},
                "backgroundColor": "#d4edda",
                "color": "#155724",
            },
            {
                "if": {"filter_query": '{result} = "refuted"'},
                "backgroundColor": "#f8d7da",
                "color": "#721c24",
            },
        ],
    )


# ============================================================================
# Path Tracer Components
# ============================================================================

def search_pages(query: str, limit: int = 20) -> list[dict]:
    """Search for pages by title or ID.

    When USE_API is True, uses the API for search (searches all pages).
    Otherwise, uses local tunnel node data (only searches known tunnel nodes).
    """
    if USE_API and api_client is not None:
        return api_client.search_pages(query, limit=limit)

    results = []
    query_lower = query.lower().strip()

    if not query_lower:
        return results

    # Try as page ID first
    try:
        page_id = int(query_lower)
        if page_id in id_to_title:
            results.append({"page_id": page_id, "title": id_to_title[page_id]})
    except ValueError:
        pass

    # Search by title prefix
    for title, page_id in title_to_id.items():
        if query_lower in title:
            results.append(
                {"page_id": page_id, "title": id_to_title.get(page_id, f"page_{page_id}")}
            )
            if len(results) >= limit:
                break

    return results


def trace_page_live(page_id: int, title: str) -> Optional[dict]:
    """Trace a page live across all N values using the API."""
    if not USE_API or api_client is None:
        return None

    trace = {
        "page_id": page_id,
        "title": title,
        "tunnel_score": 0,
        "tunnel_type": "live_trace",
        "n_basins_bridged": 0,
        "n_transitions": 0,
        "mean_depth": 0,
        "basin_list": "",
        "stable_ranges": "",
        "n_values": {},
        "live_traces": {},
    }

    seen_basins = set()
    depths = []
    prev_cycle = None
    transitions = 0

    for n in range(3, 11):
        result = api_client.trace_single(n=n, start_page_id=page_id)
        if result is None:
            trace["n_values"][n] = {
                "basin": "",
                "basin_short": "N/A",
                "depth": None,
                "color": "#cccccc",
                "terminal_type": "ERROR",
            }
            continue

        terminal_type = result.get("terminal_type", "UNKNOWN")
        steps = result.get("steps", 0)
        cycle_titles = result.get("cycle_titles", [])

        if terminal_type == "CYCLE" and cycle_titles:
            basin_key = "__".join(sorted(cycle_titles[:2]))
        else:
            basin_key = f"_{terminal_type}_"

        seen_basins.add(basin_key)
        depths.append(steps)

        if prev_cycle is not None and basin_key != prev_cycle:
            transitions += 1
        prev_cycle = basin_key

        trace["n_values"][n] = {
            "basin": basin_key,
            "basin_short": get_short_name(basin_key) if terminal_type == "CYCLE" else terminal_type,
            "depth": steps,
            "color": get_basin_color(basin_key) if terminal_type == "CYCLE" else "#cccccc",
            "terminal_type": terminal_type,
        }

        trace["live_traces"][n] = {
            "path": result.get("path", []),
            "path_titles": result.get("path_titles", []),
            "cycle_start_index": result.get("cycle_start_index"),
            "cycle_len": result.get("cycle_len"),
        }

    trace["n_basins_bridged"] = len(seen_basins)
    trace["n_transitions"] = transitions
    trace["mean_depth"] = sum(depths) / len(depths) if depths else 0
    trace["tunnel_score"] = transitions / 7.0
    trace["basin_list"] = ", ".join(sorted(seen_basins))

    return trace


def get_page_trace(page_id: int) -> Optional[dict]:
    """Get basin membership trace for a page across all N values."""
    tunnel_row = tunnel_df[tunnel_df["page_id"] == page_id]

    if tunnel_row.empty:
        return None

    row = tunnel_row.iloc[0]

    page_multiplex = multiplex_df[multiplex_df["page_id"] == page_id]

    n_basins = {}
    n_depths = {}

    if not page_multiplex.empty:
        for _, mrow in page_multiplex.iterrows():
            n = mrow["N"]
            n_basins[n] = mrow.get("cycle_key", "")
            n_depths[n] = mrow.get("depth", 0)

    trace = {
        "page_id": page_id,
        "title": row.get("page_title", f"page_{page_id}"),
        "tunnel_score": row.get("tunnel_score", 0),
        "tunnel_type": row.get("tunnel_type", ""),
        "n_basins_bridged": row.get("n_basins_bridged", 0),
        "n_transitions": row.get("n_transitions", 0),
        "mean_depth": row.get("mean_depth", 0),
        "basin_list": row.get("basin_list", ""),
        "stable_ranges": row.get("stable_ranges", ""),
        "n_values": {},
    }

    for n in range(3, 11):
        basin = n_basins.get(n, "")
        depth = n_depths.get(n, None)
        trace["n_values"][n] = {
            "basin": basin,
            "basin_short": get_short_name(basin),
            "depth": depth,
            "color": get_basin_color(basin),
        }

    return trace


def create_timeline_figure(trace: dict) -> go.Figure:
    """Create timeline visualization of basin membership."""
    if not trace:
        fig = go.Figure()
        fig.add_annotation(text="No trace data", showarrow=False)
        return fig

    n_values = list(range(3, 11))
    basins = [trace["n_values"][n]["basin_short"] for n in n_values]
    colors = [trace["n_values"][n]["color"] for n in n_values]
    depths = [trace["n_values"][n]["depth"] for n in n_values]

    fig = go.Figure()

    for i, n in enumerate(n_values):
        fig.add_trace(
            go.Bar(
                y=[f"N={n}"],
                x=[1],
                orientation="h",
                marker_color=colors[i],
                text=[basins[i]],
                textposition="inside",
                textfont=dict(color="white", size=14),
                hovertemplate=(
                    f"<b>N={n}</b><br>"
                    f"Basin: {basins[i]}<br>"
                    f"Depth: {depths[i]}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    for i in range(len(n_values) - 1):
        if basins[i] != basins[i + 1]:
            fig.add_annotation(
                x=1.05,
                y=i + 0.5,
                text="↓ TUNNEL",
                showarrow=False,
                font=dict(color="#d62728", size=12, weight="bold"),
                xanchor="left",
            )

    fig.update_layout(
        title=f"Basin Membership Timeline: {trace['title']}",
        xaxis=dict(visible=False, range=[0, 1.3]),
        yaxis=dict(autorange="reversed"),
        height=400,
        margin=dict(t=60, b=20, l=60, r=80),
        bargap=0.3,
    )

    return fig


def create_depth_figure(trace: dict) -> go.Figure:
    """Create depth visualization across N values."""
    if not trace:
        fig = go.Figure()
        fig.add_annotation(text="No trace data", showarrow=False)
        return fig

    n_values = list(range(3, 11))
    depths = [trace["n_values"][n]["depth"] for n in n_values]
    colors = [trace["n_values"][n]["color"] for n in n_values]

    valid_data = [(n, d, c) for n, d, c in zip(n_values, depths, colors) if d is not None]

    if not valid_data:
        fig = go.Figure()
        fig.add_annotation(text="No depth data available", showarrow=False)
        return fig

    ns, ds, cs = zip(*valid_data)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[f"N={n}" for n in ns],
                y=ds,
                mode="lines+markers",
                marker=dict(size=12, color=list(cs)),
                line=dict(color="#666", width=2),
                hovertemplate="N=%{x}<br>Depth: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Depth Across N Values",
        xaxis_title="N Value",
        yaxis_title="Depth from Cycle",
        height=250,
        margin=dict(t=60, b=50, l=60, r=20),
    )

    return fig


# ============================================================================
# Dashboard Layout
# ============================================================================

def get_mode_badge():
    """Return badge component showing current mode."""
    if USE_API:
        return badge("API Mode", color="success")
    return badge("Local Files", color="secondary")


def create_layout() -> dbc.Container:
    """Create the main dashboard layout."""

    summary = semantic_model.get("summary", {})

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                [
                                    "Tunneling Explorer",
                                    html.Span(" ", style={"marginLeft": "10px"}),
                                    get_mode_badge(),
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                "Wikipedia N-Link Rule Analysis - Cross-Basin Tunneling Exploration",
                                className="text-muted",
                            ),
                        ]
                    )
                ],
                className="mb-4",
            ),
            # Tabs
            dbc.Tabs(
                [
                    # ========== Tab 1: Overview ==========
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        metric_card(
                                            f"{summary.get('total_pages_in_hyperstructure', 0):,}",
                                            "Total Pages",
                                            "#1f77b4",
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        metric_card(
                                            f"{summary.get('tunnel_nodes', 0):,}",
                                            "Tunnel Nodes",
                                            "#2ca02c",
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        metric_card(
                                            f"{summary.get('tunnel_percentage', 0):.2f}%",
                                            "Tunnel Rate",
                                            "#ff7f0e",
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        metric_card(
                                            f"{summary.get('n_basins', 0)}",
                                            "Basins",
                                            "#9467bd",
                                        ),
                                        md=3,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col([dcc.Graph(id="mechanism-pie")], md=4),
                                    dbc.Col([dcc.Graph(id="scatter-plot")], md=4),
                                    dbc.Col([dcc.Graph(id="type-bar")], md=4),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            info_card(
                                                "Key Insights",
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                "99.3% of tunneling is caused by degree_shift (different Nth link)"
                                                            ),
                                                            html.Li(
                                                                "N=5 is the critical phase transition point"
                                                            ),
                                                            html.Li(
                                                                "Shallow nodes (low depth) tunnel more than deep nodes"
                                                            ),
                                                            html.Li(
                                                                "Gulf of Maine acts as a 'sink' basin at higher N values"
                                                            ),
                                                        ]
                                                    )
                                                ],
                                            )
                                        ]
                                    )
                                ],
                                className="mt-3",
                            ),
                        ],
                        label="Overview",
                        tab_id="tab-overview",
                    ),
                    # ========== Tab 2: Basin Flows ==========
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dcc.Graph(
                                                id="sankey-diagram", style={"height": "600px"}
                                            )
                                        ]
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            info_card(
                                                "Flow Pattern",
                                                [
                                                    html.P(
                                                        [
                                                            "At the N=5→N=6 transition, pages flow ",
                                                            html.Strong("into"),
                                                            " Gulf of Maine from all other basins. This unidirectional flow ",
                                                            "explains the phase transition behavior observed in the basin structure.",
                                                        ]
                                                    )
                                                ],
                                            )
                                        ]
                                    )
                                ],
                                className="mt-3",
                            ),
                        ],
                        label="Basin Flows",
                        tab_id="tab-flows",
                    ),
                    # ========== Tab 3: Tunnel Nodes ==========
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4("Filter Options", className="mb-3"),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Tunnel Type"),
                                                            dcc.Dropdown(
                                                                id="type-filter",
                                                                options=[
                                                                    {"label": "All", "value": "all"},
                                                                    {
                                                                        "label": "Progressive",
                                                                        "value": "progressive",
                                                                    },
                                                                    {
                                                                        "label": "Alternating",
                                                                        "value": "alternating",
                                                                    },
                                                                ],
                                                                value="all",
                                                                clearable=False,
                                                            ),
                                                        ],
                                                        md=4,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Minimum Score"),
                                                            dcc.Slider(
                                                                id="score-slider",
                                                                min=0,
                                                                max=75,
                                                                step=5,
                                                                value=0,
                                                                marks={
                                                                    i: str(i)
                                                                    for i in range(0, 80, 10)
                                                                },
                                                            ),
                                                        ],
                                                        md=6,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dash_table.DataTable(
                                                id="tunnel-table",
                                                columns=[
                                                    {"name": "Rank", "id": "rank"},
                                                    {"name": "Page Title", "id": "page_title"},
                                                    {
                                                        "name": "Score",
                                                        "id": "tunnel_score",
                                                        "type": "numeric",
                                                        "format": {"specifier": ".2f"},
                                                    },
                                                    {"name": "Basins", "id": "n_basins_bridged"},
                                                    {
                                                        "name": "Depth",
                                                        "id": "mean_depth",
                                                        "type": "numeric",
                                                        "format": {"specifier": ".1f"},
                                                    },
                                                    {"name": "Type", "id": "tunnel_type"},
                                                ],
                                                page_size=20,
                                                sort_action="native",
                                                filter_action="native",
                                                style_table={"overflowX": "auto"},
                                                style_cell={
                                                    "textAlign": "left",
                                                    "padding": "8px",
                                                    "fontSize": "13px",
                                                },
                                                style_header={
                                                    "backgroundColor": "#1a1a2e",
                                                    "color": "white",
                                                    "fontWeight": "bold",
                                                },
                                                style_data_conditional=[
                                                    {
                                                        "if": {
                                                            "filter_query": '{tunnel_type} = "progressive"'
                                                        },
                                                        "backgroundColor": "#d4edda",
                                                    },
                                                    {
                                                        "if": {
                                                            "filter_query": '{tunnel_type} = "alternating"'
                                                        },
                                                        "backgroundColor": "#fff3cd",
                                                    },
                                                ],
                                            )
                                        ]
                                    )
                                ]
                            ),
                        ],
                        label="Tunnel Nodes",
                        tab_id="tab-nodes",
                    ),
                    # ========== Tab 4: Path Tracer ==========
                    dbc.Tab(
                        [
                            # Search row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Search for a Wikipedia page:"
                                                                            ),
                                                                            dbc.InputGroup(
                                                                                [
                                                                                    dbc.Input(
                                                                                        id="search-input",
                                                                                        type="text",
                                                                                        placeholder="Enter page title or ID...",
                                                                                        debounce=True,
                                                                                    ),
                                                                                    dbc.Button(
                                                                                        "Trace",
                                                                                        id="trace-btn",
                                                                                        color="primary",
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                        ],
                                                                        md=8,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label("Quick examples:"),
                                                                            dbc.ButtonGroup(
                                                                                [
                                                                                    dbc.Button(
                                                                                        "Kidder_family",
                                                                                        id="ex1-btn",
                                                                                        color="secondary",
                                                                                        size="sm",
                                                                                        className="me-1",
                                                                                    ),
                                                                                    dbc.Button(
                                                                                        "Massachusetts",
                                                                                        id="ex2-btn",
                                                                                        color="secondary",
                                                                                        size="sm",
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                        ],
                                                                        md=4,
                                                                    ),
                                                                ]
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4",
                            ),
                            # Search results
                            dbc.Row(
                                [dbc.Col([html.Div(id="search-results")])],
                                className="mb-4",
                            ),
                            # Trace display
                            dbc.Row([dbc.Col([html.Div(id="trace-display")])]),
                        ],
                        label="Path Tracer",
                        tab_id="tab-tracer",
                    ),
                    # ========== Tab 5: Stability ==========
                    dbc.Tab(
                        [
                            dbc.Row([dbc.Col([dcc.Graph(id="stability-chart")])]),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader("Stability Classes"),
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Span(
                                                                                        "■ ",
                                                                                        style={
                                                                                            "color": "#2ca02c",
                                                                                            "fontSize": "20px",
                                                                                        },
                                                                                    ),
                                                                                    html.Strong("Stable"),
                                                                                    html.P(
                                                                                        "Basin core persists across all N values",
                                                                                        className="mb-0",
                                                                                    ),
                                                                                ]
                                                                            )
                                                                        ],
                                                                        md=4,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Span(
                                                                                        "■ ",
                                                                                        style={
                                                                                            "color": "#ff7f0e",
                                                                                            "fontSize": "20px",
                                                                                        },
                                                                                    ),
                                                                                    html.Strong(
                                                                                        "Moderate"
                                                                                    ),
                                                                                    html.P(
                                                                                        "Some fluctuation in membership",
                                                                                        className="mb-0",
                                                                                    ),
                                                                                ]
                                                                            )
                                                                        ],
                                                                        md=4,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Span(
                                                                                        "■ ",
                                                                                        style={
                                                                                            "color": "#d62728",
                                                                                            "fontSize": "20px",
                                                                                        },
                                                                                    ),
                                                                                    html.Strong("Fragile"),
                                                                                    html.P(
                                                                                        "Major restructuring across N",
                                                                                        className="mb-0",
                                                                                    ),
                                                                                ]
                                                                            )
                                                                        ],
                                                                        md=4,
                                                                    ),
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className="mt-3",
                            ),
                        ],
                        label="Stability",
                        tab_id="tab-stability",
                    ),
                    # ========== Tab 6: Validation ==========
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(
                                                "Theory Validation Results", className="mb-3"
                                            ),
                                            html.Div(id="validation-container"),
                                        ]
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            info_card(
                                                "Summary",
                                                [
                                                    html.P(
                                                        [
                                                            "The tunneling analysis validated 3 of 4 theoretical predictions. ",
                                                            "The ",
                                                            html.Strong(
                                                                "hub hypothesis was refuted"
                                                            ),
                                                            " - tunnel nodes actually have slightly ",
                                                            html.Em("lower"),
                                                            " out-degree than average. ",
                                                            "This suggests tunneling is about ",
                                                            html.Strong("position (depth)"),
                                                            " rather than ",
                                                            html.Strong("connectivity (degree)"),
                                                            ".",
                                                        ]
                                                    )
                                                ],
                                            )
                                        ]
                                    )
                                ],
                                className="mt-3",
                            ),
                        ],
                        label="Validation",
                        tab_id="tab-validation",
                    ),
                ],
                id="tabs",
                active_tab="tab-overview",
            ),
            # Footer
            html.Hr(),
            html.Footer(
                [
                    html.P(
                        [
                            "Data: Wikipedia English (enwiki-20251220) | ",
                            "Analysis: N-Link Rule Theory",
                        ],
                        className="text-muted text-center",
                    )
                ]
            ),
        ],
        fluid=True,
        className="p-4",
    )


# ============================================================================
# App Initialization
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Tunneling Explorer",
)


# ============================================================================
# Callbacks
# ============================================================================

@callback(
    Output("mechanism-pie", "figure"),
    Output("scatter-plot", "figure"),
    Output("type-bar", "figure"),
    Input("tabs", "active_tab"),
)
def update_overview_charts(active_tab):
    """Update overview charts."""
    return create_overview_charts(semantic_model, mechanisms_df, tunnel_df)


@callback(
    Output("sankey-diagram", "figure"),
    Input("tabs", "active_tab"),
)
def update_sankey(active_tab):
    """Update Sankey diagram."""
    return create_sankey_figure(flows_df)


@callback(
    Output("tunnel-table", "data"),
    Input("type-filter", "value"),
    Input("score-slider", "value"),
)
def update_tunnel_table(type_filter, min_score):
    """Filter tunnel nodes table."""
    df = tunnel_df.copy()

    if type_filter != "all":
        df = df[df["tunnel_type"] == type_filter]

    if min_score > 0:
        df = df[df["tunnel_score"] >= min_score]

    df = df.reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)

    return df[
        ["rank", "page_title", "tunnel_score", "n_basins_bridged", "mean_depth", "tunnel_type"]
    ].to_dict("records")


@callback(
    Output("stability-chart", "figure"),
    Input("tabs", "active_tab"),
)
def update_stability(active_tab):
    """Update stability chart."""
    return create_stability_chart(stability_df)


@callback(
    Output("validation-container", "children"),
    Input("tabs", "active_tab"),
)
def update_validation(active_tab):
    """Update validation table."""
    return create_validation_table(validation_df)


# Path Tracer callbacks
@callback(
    Output("search-results", "children"),
    Input("search-input", "value"),
)
def update_search_results(query):
    """Show matching pages."""
    if not query or len(query) < 2:
        return ""

    results = search_pages(query)

    if not results:
        return dbc.Alert("No matching pages found", color="warning")

    buttons = []
    for r in results[:10]:
        buttons.append(
            dbc.Button(
                f"{r['title']} (ID: {r['page_id']})",
                id={"type": "result-btn", "page_id": r["page_id"]},
                color="light",
                className="me-2 mb-2",
                size="sm",
            )
        )

    return html.Div(
        [
            html.P(f"Found {len(results)} matching pages:", className="mb-2"),
            html.Div(buttons),
        ]
    )


@callback(
    Output("trace-display", "children"),
    Input("trace-btn", "n_clicks"),
    Input("ex1-btn", "n_clicks"),
    Input("ex2-btn", "n_clicks"),
    State("search-input", "value"),
    prevent_initial_call=True,
)
def show_trace(trace_clicks, ex1_clicks, ex2_clicks, search_value):
    """Display trace for selected page."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "ex1-btn":
        page_id = 14758846  # Kidder_family
        title = "Kidder_family"
    elif trigger_id == "ex2-btn":
        results = search_pages("massachusetts")
        if results:
            page_id = results[0]["page_id"]
            title = results[0].get("title", f"page_{page_id}")
        else:
            return dbc.Alert("Massachusetts not found", color="warning")
    else:
        if not search_value:
            return dbc.Alert("Please enter a search term", color="info")

        results = search_pages(search_value)
        if not results:
            return dbc.Alert("No matching page found", color="warning")
        page_id = results[0]["page_id"]
        title = results[0].get("title", f"page_{page_id}")

    # Get trace - try local data first, then API live trace
    trace = get_page_trace(page_id)

    if not trace and USE_API:
        trace = trace_page_live(page_id, title)

    if not trace:
        msg = f"Page ID {page_id} not found"
        if not USE_API:
            msg += " in tunnel nodes. Enable --use-api for live tracing of any page."
        return dbc.Alert(msg, color="warning")

    # Build display
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H4(
                        [
                            html.A(
                                trace["title"],
                                href=f"https://en.wikipedia.org/wiki/{trace['title'].replace(' ', '_')}",
                                target="_blank",
                            ),
                            html.Small(
                                f" (ID: {trace['page_id']})", className="text-muted"
                            ),
                        ]
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    # Stats row
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Strong("Tunnel Score: "),
                                            html.Span(f"{trace['tunnel_score']:.2f}"),
                                        ]
                                    )
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Strong("Type: "),
                                            html.Span(
                                                trace["tunnel_type"],
                                                className=f"badge bg-{'success' if trace['tunnel_type'] == 'progressive' else 'warning'}",
                                            ),
                                        ]
                                    )
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Strong("Basins Bridged: "),
                                            html.Span(str(trace["n_basins_bridged"])),
                                        ]
                                    )
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Strong("Mean Depth: "),
                                            html.Span(f"{trace['mean_depth']:.1f}"),
                                        ]
                                    )
                                ],
                                md=3,
                            ),
                        ],
                        className="mb-4",
                    ),
                    # Timeline chart
                    dcc.Graph(figure=create_timeline_figure(trace)),
                    # Depth chart
                    dcc.Graph(figure=create_depth_figure(trace)),
                    # Details table
                    html.H5("Basin Details by N", className="mt-4 mb-3"),
                    dbc.Table(
                        [
                            html.Thead(
                                [
                                    html.Tr(
                                        [
                                            html.Th("N Value"),
                                            html.Th("Basin"),
                                            html.Th("Depth"),
                                        ]
                                    )
                                ]
                            ),
                            html.Tbody(
                                [
                                    html.Tr(
                                        [
                                            html.Td(f"N={n}"),
                                            html.Td(
                                                [
                                                    html.Span(
                                                        "■ ",
                                                        style={
                                                            "color": trace["n_values"][n][
                                                                "color"
                                                            ]
                                                        },
                                                    ),
                                                    trace["n_values"][n]["basin_short"],
                                                ]
                                            ),
                                            html.Td(
                                                str(trace["n_values"][n]["depth"])
                                                if trace["n_values"][n]["depth"]
                                                else "N/A"
                                            ),
                                        ]
                                    )
                                    for n in range(3, 11)
                                ]
                            ),
                        ],
                        bordered=True,
                        hover=True,
                    ),
                ]
            ),
        ]
    )


# ============================================================================
# Main
# ============================================================================

def main():
    global USE_API, API_URL, api_client

    parser = argparse.ArgumentParser(description="Run Tunneling Explorer dashboard")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8060, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Use N-Link API for page search and live tracing",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="N-Link API base URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Tunneling Explorer")
    print("=" * 70)
    print()

    # Configure API mode
    if args.use_api:
        if not HTTPX_AVAILABLE:
            print("Error: httpx library required for API mode")
            print("Install with: pip install httpx")
            return 1

        USE_API = True
        API_URL = args.api_url
        api_client = NLinkAPIClient(API_URL)

        print(f"Mode: API (connecting to {API_URL})")

        if api_client.health_check():
            print("  API connection: OK")
        else:
            print("  API connection: FAILED - is the server running?")
            print("  Start with: uvicorn nlink_api.main:app --port 8000")
            return 1
    else:
        print("Mode: Local files")
        print(f"  Tunnel nodes: {len(tunnel_df):,}")
        print(f"  Multiplex assignments: {len(multiplex_df):,}")

    print()
    print(f"Starting server on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    print()

    # Set layout after globals are configured
    app.layout = create_layout()

    app.run(host=args.host, debug=args.debug, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
