# Next Session: Visualization Tool Consolidation Assessment

**Goal**: Assess current visualization tools and plan consolidation into a unified interface and deployment unit.

---

## Current State

### Separate Dashboard Applications (5 ports)

| Tool | Port | Script | Purpose |
|------|------|--------|---------|
| Basin Geometry Viewer | 8055 | `dash-basin-geometry-viewer.py` | 3D point clouds, interval layouts |
| Multiplex Explorer | 8056 | `dash-multiplex-explorer.py` | Cross-N connectivity, tunnel nodes |
| Tunneling Dashboard | 8060 | `tunneling/tunneling-dashboard.py` | 5-tab tunnel exploration |
| Path Tracer | 8061 | `tunneling/path-tracer-tool.py` | Per-page basin membership |
| Cross-N Comparison | 8062 | `dash-cross-n-comparison.py` | Phase transition visualization |

### Static Generators (no server)

| Tool | Script | Output |
|------|--------|--------|
| Sankey Diagram | `tunneling/sankey-basin-flows.py` | `report/assets/tunneling_sankey.html` |
| Node Explorer | `tunneling/tunnel-node-explorer.py` | `report/assets/tunnel_node_explorer.html` |
| Batch Render | `batch-render-basin-images.py` | PNG/SVG/PDF images |
| Multi-N Figures | `generate-multi-n-figures.py` | Report figures |

### Launcher Scripts

| Script | Purpose |
|--------|---------|
| `tunneling/launch-tunneling-viz.py` | Launch tunneling tools |

---

## Assessment Questions

### 1. Usage Patterns
- Which dashboards are used together most often?
- Which are used standalone?
- Are there redundant features across dashboards?

### 2. Shared Components
Identify components that could be shared:
- [ ] Page search/autocomplete
- [ ] Basin selector dropdown
- [ ] N-value slider
- [ ] Cycle/basin color schemes
- [ ] Data loading patterns

### 3. Data Dependencies
Map which tools load which data files:
- `multiplex_basin_assignments.parquet`
- `tunnel_frequency_ranking.tsv`
- `basin_flows.tsv`
- `semantic_model_wikipedia.json`
- Basin pointcloud parquet files
- Edge DuckDB databases

### 4. Architecture Options

**Option A: Single Mega-Dashboard**
- One Dash app with all tabs
- Pros: Single port, unified experience
- Cons: Large codebase, slower startup, memory usage

**Option B: Micro-frontends**
- Keep separate apps but serve via single proxy
- Pros: Isolation, independent scaling
- Cons: Deployment complexity

**Option C: Selective Consolidation**
- Merge related tools, keep specialized ones separate
- Example: Merge Tunneling Dashboard + Path Tracer
- Pros: Balanced complexity
- Cons: Still multiple processes

**Option D: Unified Launcher with Lazy Loading**
- Single entry point that spawns dashboards on demand
- Shared process for common data
- Pros: Resource efficient, single CLI
- Cons: Implementation complexity

---

## Proposed Investigation Steps

### Phase 1: Inventory (30 min)
1. List all Dash callbacks across tools
2. Identify duplicate/similar functionality
3. Map data loading patterns
4. Count lines of code per tool

### Phase 2: Component Analysis (30 min)
1. Extract common UI patterns
2. Identify shared business logic
3. Assess API client usage potential
4. Review styling consistency

### Phase 3: Architecture Decision (30 min)
1. Evaluate options A-D above
2. Consider deployment targets (local dev, demo server, publication)
3. Decide on consolidation strategy
4. Create implementation plan

---

## Success Criteria

A good consolidation would:
- [ ] Reduce number of ports from 5 to 1-2
- [ ] Share common components (search, selectors, colors)
- [ ] Single entry point for users
- [ ] Preserve all current functionality
- [ ] Improve maintainability
- [ ] Support both local and API modes

---

## Quick Start Commands

```bash
# Current: Start each dashboard separately
python n-link-analysis/viz/dash-basin-geometry-viewer.py --port 8055
python n-link-analysis/viz/dash-multiplex-explorer.py --port 8056
python n-link-analysis/viz/tunneling/tunneling-dashboard.py --port 8060
python n-link-analysis/viz/tunneling/path-tracer-tool.py --port 8061
python n-link-analysis/viz/dash-cross-n-comparison.py --port 8062

# Goal: Single command
python n-link-analysis/viz/unified-dashboard.py --port 8050
```

---

## Related Files

- [README.md](README.md) - Current tool documentation
- [api_client.py](api_client.py) - Shared API client (already extracted)
- [tunneling/README.md](tunneling/README.md) - Tunneling tool documentation
- [MULTIPLEX-EXPLORER-GUIDE.md](MULTIPLEX-EXPLORER-GUIDE.md) - Explorer usage guide

---

**Created**: 2026-01-02
