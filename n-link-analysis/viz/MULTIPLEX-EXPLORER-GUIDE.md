# Multiplex Tunnel Explorer Guide

**Tool**: `dash-multiplex-explorer.py`
**Port**: 8056 (default)
**Purpose**: Interactive exploration of cross-N basin connectivity, tunnel nodes, and multiplex graph structure

---

## Quick Start

```bash
# From repository root
python n-link-analysis/viz/dash-multiplex-explorer.py

# Custom port
python n-link-analysis/viz/dash-multiplex-explorer.py --port 8080

# Debug mode
python n-link-analysis/viz/dash-multiplex-explorer.py --debug
```

Open http://127.0.0.1:8056 in your browser.

---

## Data Requirements

The explorer loads data from `data/wikipedia/processed/multiplex/`:

| File | Description | Source |
|------|-------------|--------|
| `multiplex_layer_connectivity.tsv` | N×N edge count matrix | `compute-multiplex-reachability.py` |
| `tunnel_classification.tsv` | Tunnel node types and basin pairs | `classify-tunnel-types.py` |
| `tunnel_frequency_ranking.tsv` | Ranked tunnel nodes with scores | `compute-tunnel-frequency.py` |
| `multiplex_reachability_summary.tsv` | Per-cycle BFS reachability | `compute-multiplex-reachability.py` |
| `basin_intersection_by_cycle.tsv` | Jaccard similarity across N | `compute-intersection-matrix.py` |

Run Phase 1-3 scripts from `TUNNELING-ROADMAP.md` before using this explorer.

---

## Tabs Overview

### Tab 1: Layer Connectivity

**Purpose**: Visualize how N layers connect via within-N and tunnel edges.

**Features**:
- Interactive heatmap showing N×N edge counts
- Toggle between log and linear scale
- Statistics panel showing:
  - Total edges (9.7M)
  - Within-N percentage (99.2%)
  - Cross-N percentage (0.8%)
  - Strongest cross-layer connections
- Bar chart of cross-layer edge counts

**Key Insights**:
- Diagonal dominance confirms layers are mostly independent
- N=5↔N=6 has strongest cross-layer connectivity (4,845 edges each direction)
- Adjacent N layers connect more than distant ones

---

### Tab 2: Tunnel Nodes

**Purpose**: Browse and filter the 9,018 identified tunnel nodes.

**Filters**:
- **Tunnel Type**: Progressive (98.7%) vs Alternating (1.3%)
- **Basin Pair**: Filter by specific basin connections
- **Min Score**: Filter by tunnel importance score

**Table Columns**:
| Column | Description |
|--------|-------------|
| Page ID | Wikipedia page identifier |
| Title | Page title (if resolved) |
| Type | Progressive or alternating |
| Score | Importance score (higher = more central) |
| Basins | Number of basins bridged |
| Transitions | N-value transition count |
| Mean Depth | Average depth in basins |
| Basins | List of basins this node connects |

**Visualizations**:
- Score distribution histogram
- Tunnel type pie chart

**Scoring Formula**:
```
tunnel_score = n_basins_bridged × log(1 + n_transitions) × (100 / mean_depth)
```

---

### Tab 3: Basin Pairs

**Purpose**: Explore which basins connect via tunnel nodes.

**Features**:
- Network visualization showing basin connectivity
- Top basin pairs list with tunnel counts
- Bar chart of top 20 basin pairs

**Key Insights**:
- Gulf_of_Maine appears in 61% of basin pairs (tunnel hub)
- Sea_salt↔Gulf_of_Maine is the most common pair (1,959 tunnels)
- Progressive tunneling dominates all major pairs

---

### Tab 4: Reachability

**Purpose**: Analyze BFS reachability from each cycle across N layers.

**Visualizations**:
- Stacked bar chart: Reachable nodes per cycle, colored by N layer
- Jaccard intersection heatmap: Basin overlap across N pairs
- Intersection bar chart: Similarity by N pair

**Table**: Per-cycle reachability statistics
- Cycle members
- Total reachable nodes
- Tunnel-reachable nodes
- Max BFS depth reached

**Key Insights**:
- Gulf_of_Maine reaches 637 nodes (5× more than other cycles)
- Only Gulf_of_Maine reaches tunnel nodes (29 of 637)
- Jaccard similarity is very low (~0.001-0.01) between N values

---

## Usage Scenarios

### Scenario 1: Find High-Importance Tunnel Nodes

1. Go to **Tab 2: Tunnel Nodes**
2. Set **Min Score** slider to 50+
3. Sort by **Score** column (descending)
4. Examine top tunnel nodes - these are structurally central

### Scenario 2: Explore N=5↔N=6 Connectivity

1. Go to **Tab 1: Layer Connectivity**
2. Look at N=5→N=6 and N=6→N=5 cells in heatmap
3. Check bar chart for cross-layer breakdown
4. Go to **Tab 2**, filter by basin pairs that span N=5 and N=6

### Scenario 3: Understand Gulf_of_Maine Dominance

1. Go to **Tab 3: Basin Pairs**
2. Observe Gulf_of_Maine in top pairs list
3. Go to **Tab 4: Reachability**
4. Compare Gulf_of_Maine row to other cycles
5. Note tunnel_reachable = 29 (others = 0)

### Scenario 4: Compare Basin Stability

1. Go to **Tab 4: Reachability**
2. Examine Jaccard intersection heatmap
3. Low values indicate basins have different members at different N
4. N=5→N=6 typically has highest overlap

---

## Technical Notes

### Performance

- Loads ~20MB of data at startup
- Renders up to 500 rows in tunnel table (full data available via sorting)
- Network visualization limited to top 30 basin pairs for clarity

### Browser Compatibility

- Tested on Chrome, Firefox, Safari
- Responsive layout works on desktop and tablet
- Interactive Plotly charts require JavaScript

### Extending

To add new visualizations:
1. Add data loading function
2. Create layout component function
3. Add callback with `@callback` decorator
4. Include in appropriate tab

---

## Related Tools

| Tool | Purpose | Port |
|------|---------|------|
| `dash-basin-geometry-viewer.py` | 3D basin point clouds | 8054 |
| `interactive-depth-explorer-enhanced.py` | Depth distributions | 8051 |
| `interactive-depth-explorer.py` | Mass vs depth analysis | 8050 |
| **`dash-multiplex-explorer.py`** | **Tunnel/multiplex analysis** | **8056** |

---

## Data Sources

All data from Phase 1-3 of the tunneling roadmap:

```
TUNNELING-ROADMAP.md
├── Phase 1: Multiplex Data Layer (complete)
├── Phase 2: Tunnel Node Identification (complete)
├── Phase 3: Multiplex Connectivity (complete) ← This explorer
├── Phase 4: Mechanism Classification (pending)
└── Phase 5: Applications (pending)
```

---

**Last Updated**: 2026-01-01
**Author**: Claude Code Session
