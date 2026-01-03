#!/usr/bin/env python3
"""Generate multi-N comparison figures for publication.

Creates:
1. Phase transition chart: Basin size vs N for all cycles
2. Basin collapse chart: Log-scale comparison N=5 vs N=10
3. Tunneling explosion chart: Tunnel nodes by N range
4. Summary statistics table

Run (repo root):
  python n-link-analysis/viz/generate-multi-n-figures.py --all
  python n-link-analysis/viz/generate-multi-n-figures.py --phase-transition
  python n-link-analysis/viz/generate-multi-n-figures.py --collapse-chart
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


REPO_ROOT = Path(__file__).resolve().parents[2]
MULTIPLEX_DIR = REPO_ROOT / "data" / "wikipedia" / "processed" / "multiplex"
REPORT_ASSETS_DIR = REPO_ROOT / "n-link-analysis" / "report" / "assets"

# Color palette for consistent styling
COLORS = {
    "Massachusetts": "#1f77b4",
    "Sea_salt": "#ff7f0e",
    "Mountain": "#2ca02c",
    "Autumn": "#d62728",
    "Kingdom_(biology)": "#9467bd",
    "Latvia": "#8c564b",
    "Precedent": "#e377c2",
    "American_Revolutionary_War": "#7f7f7f",
    "Thermosetting_polymer": "#bcbd22",
}


def load_basin_data() -> pd.DataFrame:
    """Load multiplex basin assignments."""
    path = MULTIPLEX_DIR / "multiplex_basin_assignments.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_parquet(path)


def load_tunnel_data() -> pd.DataFrame:
    """Load tunnel classification data."""
    path = MULTIPLEX_DIR / "tunnel_classification.tsv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path, sep="\t")


def get_basin_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """Compute basin sizes by N and cycle."""
    # Filter out tunneling entries (they're subsets)
    df_main = df[~df["cycle_key"].str.contains("_tunneling", na=False)]

    sizes = df_main.groupby(["N", "cycle_key"]).size().reset_index(name="size")

    # Extract base cycle name
    sizes["cycle"] = sizes["cycle_key"].str.split("__").str[0]

    return sizes


def create_phase_transition_chart(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create phase transition chart showing basin size vs N."""
    sizes = get_basin_sizes(df)

    # Get unique cycles and their max sizes for ordering
    cycle_max = sizes.groupby("cycle")["size"].max().sort_values(ascending=False)
    top_cycles = cycle_max.head(6).index.tolist()

    # Filter to top cycles
    sizes_top = sizes[sizes["cycle"].isin(top_cycles)]

    fig = go.Figure()

    for cycle in top_cycles:
        cycle_data = sizes_top[sizes_top["cycle"] == cycle].sort_values("N")
        if len(cycle_data) > 0:
            color = COLORS.get(cycle, "#666666")
            fig.add_trace(go.Scatter(
                x=cycle_data["N"],
                y=cycle_data["size"],
                mode="lines+markers",
                name=cycle.replace("_", " "),
                line=dict(color=color, width=2),
                marker=dict(size=8),
            ))

    fig.update_layout(
        title=dict(
            text="Basin Size Phase Transition (N=3-10)",
            font=dict(size=20),
            x=0.5,
        ),
        xaxis=dict(
            title="N (link position)",
            tickmode="linear",
            tick0=3,
            dtick=1,
            range=[2.5, 10.5],
        ),
        yaxis=dict(
            title="Basin Size (pages)",
            type="log",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        template="plotly_white",
        width=1000,
        height=600,
    )

    # Add N=5 peak annotation
    fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_annotation(
        x=5, y=1.05, yref="paper",
        text="N=5 Peak",
        showarrow=False,
        font=dict(size=12, color="gray"),
    )

    output_path = output_dir / "phase_transition_n3_n10.png"
    fig.write_image(str(output_path), width=1000, height=600, scale=2)
    print(f"✓ Saved: {output_path.name}")

    # Also save interactive HTML
    html_path = output_dir / "phase_transition_n3_n10.html"
    fig.write_html(str(html_path))
    print(f"✓ Saved: {html_path.name}")

    return output_path


def create_collapse_chart(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create basin collapse comparison chart (N=5 vs N=10)."""
    # For N=5: use main cycle keys (without _tunneling suffix)
    # For N=8-10: use _tunneling cycle keys which represent the same basins

    # Get N=5 sizes (main cycles)
    n5_data = df[(df["N"] == 5) & (~df["cycle_key"].str.contains("_tunneling", na=False))]
    n5_sizes = n5_data.groupby("cycle_key").size()

    # Get N=10 sizes (tunneling cycles - these are the same basins at N=10)
    n10_data = df[(df["N"] == 10) & (df["cycle_key"].str.contains("_tunneling", na=False))]
    n10_sizes = n10_data.groupby("cycle_key").size()

    # Map tunneling cycle keys back to base cycle names
    n10_mapped = {}
    for key, size in n10_sizes.items():
        base_key = key.replace("_tunneling", "")
        n10_mapped[base_key] = size

    # Build comparison DataFrame
    comparison_data = []
    for cycle_key in n5_sizes.index:
        if cycle_key in n10_mapped:
            comparison_data.append({
                "cycle": cycle_key.split("__")[0],
                "cycle_key": cycle_key,
                "N=5": n5_sizes[cycle_key],
                "N=10": n10_mapped[cycle_key],
            })

    if not comparison_data:
        print("⚠️  No cycles with both N=5 and N=10 data")
        return None

    comparison = pd.DataFrame(comparison_data).set_index("cycle")
    comparison["Collapse Factor"] = comparison["N=5"] / comparison["N=10"]
    comparison = comparison.sort_values("Collapse Factor", ascending=False)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Basin Size Comparison", "Collapse Factor"],
        column_widths=[0.6, 0.4],
    )

    cycles = comparison.index.tolist()
    x_labels = [c.replace("_", " ") for c in cycles]

    # Left: Grouped bar chart
    fig.add_trace(go.Bar(
        name="N=5",
        x=x_labels,
        y=comparison["N=5"],
        marker_color="#1f77b4",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name="N=10",
        x=x_labels,
        y=comparison["N=10"],
        marker_color="#ff7f0e",
    ), row=1, col=1)

    # Right: Collapse factor
    fig.add_trace(go.Bar(
        name="Collapse",
        x=x_labels,
        y=comparison["Collapse Factor"],
        marker_color="#2ca02c",
        showlegend=False,
    ), row=1, col=2)

    fig.update_layout(
        title=dict(
            text="Basin Collapse: N=5 → N=10",
            font=dict(size=20),
            x=0.5,
        ),
        barmode="group",
        template="plotly_white",
        width=1200,
        height=500,
    )

    fig.update_yaxes(type="log", title="Pages", row=1, col=1)
    fig.update_yaxes(title="Collapse Factor (×)", row=1, col=2)
    fig.update_xaxes(tickangle=45)

    output_path = output_dir / "basin_collapse_n5_vs_n10.png"
    fig.write_image(str(output_path), width=1200, height=500, scale=2)
    print(f"✓ Saved: {output_path.name}")

    return output_path


def create_tunnel_explosion_chart(output_dir: Path) -> Path:
    """Create chart showing tunnel node explosion from N=3-7 to N=3-10."""
    tunnel_df = load_tunnel_data()

    # Count by n_distinct_basins
    counts = tunnel_df["n_distinct_basins"].value_counts().sort_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[f"{n} basins" for n in counts.index],
        y=counts.values,
        marker_color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"][:len(counts)],
        text=counts.values,
        textposition="outside",
    ))

    fig.update_layout(
        title=dict(
            text=f"Tunnel Node Distribution (N=3-10)<br><sub>Total: {len(tunnel_df):,} tunnel nodes</sub>",
            font=dict(size=18),
            x=0.5,
        ),
        xaxis=dict(title="Number of Distinct Basins Bridged"),
        yaxis=dict(title="Count", type="log"),
        template="plotly_white",
        width=800,
        height=500,
        showlegend=False,
    )

    output_path = output_dir / "tunnel_node_distribution.png"
    fig.write_image(str(output_path), width=800, height=500, scale=2)
    print(f"✓ Saved: {output_path.name}")

    return output_path


def create_depth_distribution_chart(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create depth distribution comparison across N values."""
    # Filter to main basins
    df_main = df[~df["cycle_key"].str.contains("_tunneling", na=False)]

    # Get depth stats by N
    depth_stats = df_main.groupby("N").agg(
        mean_depth=("depth", "mean"),
        median_depth=("depth", "median"),
        max_depth=("depth", "max"),
        count=("depth", "count"),
    ).reset_index()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Mean/Median Depth by N", "Max Depth by N"],
    )

    # Left: Mean and median
    fig.add_trace(go.Scatter(
        x=depth_stats["N"],
        y=depth_stats["mean_depth"],
        mode="lines+markers",
        name="Mean",
        line=dict(color="#1f77b4", width=2),
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=depth_stats["N"],
        y=depth_stats["median_depth"],
        mode="lines+markers",
        name="Median",
        line=dict(color="#ff7f0e", width=2),
    ), row=1, col=1)

    # Right: Max depth
    fig.add_trace(go.Bar(
        x=depth_stats["N"],
        y=depth_stats["max_depth"],
        marker_color="#2ca02c",
        showlegend=False,
    ), row=1, col=2)

    fig.update_layout(
        title=dict(
            text="Depth Distribution Across N Values",
            font=dict(size=20),
            x=0.5,
        ),
        template="plotly_white",
        width=1000,
        height=450,
    )

    fig.update_xaxes(title="N", tickmode="linear", tick0=3, dtick=1)
    fig.update_yaxes(title="Depth", row=1, col=1)
    fig.update_yaxes(title="Max Depth", row=1, col=2)

    output_path = output_dir / "depth_distribution_by_n.png"
    fig.write_image(str(output_path), width=1000, height=450, scale=2)
    print(f"✓ Saved: {output_path.name}")

    return output_path


def create_summary_table(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create summary statistics table as HTML."""
    sizes = get_basin_sizes(df)
    tunnel_df = load_tunnel_data()

    # Summary by N
    summary = sizes.groupby("N").agg(
        total_pages=("size", "sum"),
        n_basins=("cycle", "nunique"),
        largest_basin=("size", "max"),
    ).reset_index()

    # Add tunnel info
    summary["tunnel_nodes"] = 0  # Placeholder - tunnels span N values

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Multi-N Summary Statistics</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 800px; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #ddd; }}
        .highlight {{ background-color: #fff3cd !important; font-weight: bold; }}
        .metric {{ font-size: 24px; color: #1f77b4; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .metrics-row {{ display: flex; gap: 40px; margin: 20px 0; }}
        .metric-box {{ text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>N-Link Basin Analysis: Multi-N Summary</h1>

    <div class="metrics-row">
        <div class="metric-box">
            <div class="metric">{len(tunnel_df):,}</div>
            <div class="metric-label">Tunnel Nodes (N=3-10)</div>
        </div>
        <div class="metric-box">
            <div class="metric">{sizes['size'].sum():,}</div>
            <div class="metric-label">Total Basin Assignments</div>
        </div>
        <div class="metric-box">
            <div class="metric">{sizes['N'].nunique()}</div>
            <div class="metric-label">N Values Analyzed</div>
        </div>
    </div>

    <h2>Basin Statistics by N</h2>
    <table>
        <tr>
            <th>N</th>
            <th>Total Pages</th>
            <th># Basins</th>
            <th>Largest Basin</th>
        </tr>
"""

    for _, row in summary.iterrows():
        highlight = ' class="highlight"' if row["N"] == 5 else ""
        html += f"""        <tr{highlight}>
            <td>{int(row['N'])}</td>
            <td>{int(row['total_pages']):,}</td>
            <td>{int(row['n_basins'])}</td>
            <td>{int(row['largest_basin']):,}</td>
        </tr>
"""

    html += """    </table>

    <h2>Key Findings</h2>
    <ul>
        <li><strong>N=5 Peak</strong>: Maximum basin coverage (highlighted row)</li>
        <li><strong>Basin Collapse</strong>: 10-1000× size reduction from N=5 to N=10</li>
        <li><strong>Tunnel Explosion</strong>: 4.6× more tunnel nodes with N=8-10 included</li>
    </ul>

    <p><em>Generated by generate-multi-n-figures.py</em></p>
</body>
</html>"""

    output_path = output_dir / "multi_n_summary_table.html"
    output_path.write_text(html)
    print(f"✓ Saved: {output_path.name}")

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate multi-N comparison figures")
    parser.add_argument("--all", action="store_true", help="Generate all figures")
    parser.add_argument("--phase-transition", action="store_true", help="Phase transition chart")
    parser.add_argument("--collapse-chart", action="store_true", help="Basin collapse comparison")
    parser.add_argument("--tunnel-chart", action="store_true", help="Tunnel node distribution")
    parser.add_argument("--depth-chart", action="store_true", help="Depth distribution by N")
    parser.add_argument("--summary-table", action="store_true", help="Summary statistics HTML")
    parser.add_argument("--output-dir", type=Path, help="Output directory")

    args = parser.parse_args()

    # Check for kaleido
    try:
        import kaleido  # noqa: F401
    except ImportError:
        print("Error: kaleido required for PNG export")
        print("Install: pip install kaleido")
        return 1

    output_dir = args.output_dir or REPORT_ASSETS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # If no specific flags, default to --all
    if not any([args.phase_transition, args.collapse_chart, args.tunnel_chart,
                args.depth_chart, args.summary_table]):
        args.all = True

    print(f"\nGenerating multi-N figures...")
    print(f"Output: {output_dir}\n")

    # Load data once
    df = load_basin_data()
    print(f"Loaded {len(df):,} basin assignments\n")

    generated = []

    if args.all or args.phase_transition:
        path = create_phase_transition_chart(df, output_dir)
        if path:
            generated.append(path)

    if args.all or args.collapse_chart:
        path = create_collapse_chart(df, output_dir)
        if path:
            generated.append(path)

    if args.all or args.tunnel_chart:
        path = create_tunnel_explosion_chart(output_dir)
        if path:
            generated.append(path)

    if args.all or args.depth_chart:
        path = create_depth_distribution_chart(df, output_dir)
        if path:
            generated.append(path)

    if args.all or args.summary_table:
        path = create_summary_table(df, output_dir)
        if path:
            generated.append(path)

    print(f"\n✓ Generated {len(generated)} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
