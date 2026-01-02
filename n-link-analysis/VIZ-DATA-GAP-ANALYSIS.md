# Visualization & Reporting Data Gap Analysis

**Date**: 2026-01-01
**Purpose**: Identify gaps between latest data (N=3-10) and visualization/reporting tools

---

## Summary

The data has been extended to N=3-10, but several visualization tools are hardcoded for N=3-7. The `tunnel_nodes.parquet` file only has columns for N3-N7, which is the root cause of the gap.

### Data State

| Data Source | N Range | Status |
|------------|---------|--------|
| `multiplex_basin_assignments.parquet` | N=3-10 | **Complete** |
| `tunnel_nodes.parquet` | N=3-7 only | **Missing N8-10 columns** |
| `branches_n=*_assignments.parquet` | N=3-10 | Complete (18 files for N8-10) |

### Scripts with Hardcoded N=3-7

| Script | Location | Issue | Fix Priority |
|--------|----------|-------|--------------|
| `path-tracer-tool.py` | `viz/tunneling/` | Line 8, 194, 214, 271, 533: `range(3, 8)` | High |
| `dash-multiplex-explorer.py` | `viz/` | Line 193: `N=3-7 layers` badge | Medium |
| `generate-tunneling-report.py` | `scripts/tunneling/` | Line 49: `N Range: 3-7` | Medium |

---

## Detailed Analysis

### 1. `path-tracer-tool.py` (High Priority)

**File**: [viz/tunneling/path-tracer-tool.py](viz/tunneling/path-tracer-tool.py)

**Issues**:
```python
# Line 8: Docstring says N=3-7
# 2. View its basin membership across all N values (3-7)

# Line 194: Hardcoded N range
for n in range(3, 8):

# Line 214: Chart creation
n_values = list(range(3, 8))

# Line 271: Depth chart
n_values = list(range(3, 8))

# Line 533: Details table
for n in range(3, 8)
```

**Required Changes**:
1. Update docstring to N=3-10
2. Change all `range(3, 8)` to `range(3, 11)`
3. Depends on: `tunnel_nodes.parquet` having N8-10 columns

**Blocker**: The `tunnel_nodes.parquet` only has `basin_at_N{3-7}` columns. Need to regenerate this file with N8-10 columns first.

---

### 2. `tunnel_nodes.parquet` Schema Gap (Root Cause)

**Current columns**:
```
page_id, basin_at_N3, basin_at_N4, basin_at_N5, basin_at_N6, basin_at_N7,
n_distinct_basins, is_tunnel_node
```

**Missing columns**:
```
basin_at_N8, basin_at_N9, basin_at_N10
```

**Script to regenerate**: `scripts/tunneling/find-tunnel-nodes.py`

The issue is that `find-tunnel-nodes.py` likely needs to be re-run with the extended N range to add the missing columns.

---

### 3. `dash-multiplex-explorer.py` (Medium Priority)

**File**: [viz/dash-multiplex-explorer.py](viz/dash-multiplex-explorer.py)

**Issue**:
```python
# Line 193
dbc.Badge(f"N=3-7 layers", color="secondary", className="me-2"),
```

**Fix**: Update to `N=3-10 layers` (cosmetic, but should match data)

---

### 4. `generate-tunneling-report.py` (Medium Priority)

**File**: [scripts/tunneling/generate-tunneling-report.py](scripts/tunneling/generate-tunneling-report.py)

**Issue**:
```python
# Line 49
**N Range**: 3-7
```

**Fix**: Update to `3-10` (report metadata)

---

### 5. `tunneling-dashboard.py` (No Changes Needed)

**File**: [viz/tunneling/tunneling-dashboard.py](viz/tunneling/tunneling-dashboard.py)

This script loads from TSV files which are dynamically generated. It does not hardcode N ranges. **No changes needed**.

---

## Recommended Action Plan

### Phase 1: Regenerate Tunnel Nodes with N8-10 (Required First)

```bash
# Re-run find-tunnel-nodes.py to add N8-10 columns
python n-link-analysis/scripts/tunneling/find-tunnel-nodes.py
```

This should automatically pick up the N=8-10 data from `multiplex_basin_assignments.parquet`.

### Phase 2: Update Visualization Scripts

1. **path-tracer-tool.py**: Change `range(3, 8)` → `range(3, 11)` in 4 locations
2. **dash-multiplex-explorer.py**: Update badge text
3. **generate-tunneling-report.py**: Update N Range metadata

### Phase 3: Regenerate Reports

```bash
# Regenerate tunneling report
python n-link-analysis/scripts/tunneling/generate-tunneling-report.py

# Regenerate human report (if needed)
python n-link-analysis/scripts/render-human-report.py --tag reproduction_2026-01-01
```

---

## Scripts Not Needing Updates

| Script | Reason |
|--------|--------|
| `tunneling-dashboard.py` | Loads from dynamic TSV files |
| `sankey-basin-flows.py` | Reads from `basin_flows.tsv` (dynamic) |
| `tunnel-node-explorer.py` | Reads from `tunnel_frequency_ranking.tsv` (dynamic) |
| `batch-render-basin-images.py` | Takes N as parameter |
| `render-full-basin-geometry.py` | Takes N as parameter |
| `dash-basin-geometry-viewer.py` | Takes N as parameter |
| `render-human-report.py` | Only handles N=5 basin structure |

---

## Quick Validation After Fixes

```bash
# 1. Check tunnel_nodes has N8-10 columns
python -c "import pandas as pd; print(pd.read_parquet('data/wikipedia/processed/multiplex/tunnel_nodes.parquet').columns.tolist())"

# 2. Start path tracer and verify N=8-10 appear
python n-link-analysis/viz/tunneling/path-tracer-tool.py --port 8061

# 3. Verify dashboard shows N=3-10
python n-link-analysis/viz/tunneling/tunneling-dashboard.py --port 8060
```

---

**Status**: Gap analysis complete. Waiting for decision on whether to proceed with fixes.
