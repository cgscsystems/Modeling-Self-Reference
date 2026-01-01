# N-Link Analysis - Session Log

**Document Type**: Cumulative
**Target Audience**: LLMs + Developers
**Purpose**: Append-only record of analysis decisions, experiments, and outcomes
**Last Updated**: 2025-12-31
**Status**: Active

---

### 2025-12-31 (Third) - Mechanism Understanding and Massachusetts Case Study

**What was tried**:
- Built path characteristics analyzer (5,000 samples across N∈{3,4,5,6,7})
- Built cycle evolution tracker (6 universal cycles across N)
- Built link profile analyzer (investigated actual Wikipedia article structures)
- Deep-dive on Massachusetts basin (why 94× larger at N=5 than N=4)

**What worked**:
- Path analysis revealed N=4 premature convergence (11 steps median, fastest)
- N=5 has slowest rapid convergence rate (85.9% <50 steps) = broadest exploration
- Cycle evolution tracking identified all 6 universal cycles with size ranges 10× to 1,285×
- Massachusetts link profile: 1,120 outlinks, forms 2-cycle ONLY at N=5 (position 5 → Gulf_of_Maine)
- Mean depth strongly correlates with basin mass (51.3 steps at N=5 vs 3.2 at N=4)

**Key findings**:
- **Premature convergence mechanism**: N=4 converges too fast for broad exploration
- **Optimal exploration time**: N=5's 14% of paths taking >50 steps creates broad catchment
- **Cycle position effect**: Massachusetts forms cycle only at N=5; points to non-cycling articles at other N
- **Hub connectivity amplification**: 1,120 outlinks + cycle formation + optimal exploration = 94× amplification
- Refined basin mass formula: Entry_Breadth × Path_Survival × Convergence_Optimality

**Scripts created**:
- `scripts/analyze-path-characteristics.py` (400 lines)
- `scripts/visualize-mechanism-comparison.py` (200 lines)
- `scripts/compare-cycle-evolution.py` (350 lines)
- `scripts/analyze-cycle-link-profiles.py` (250 lines)

**Documentation created**:
- `empirical-investigations/MECHANISM-ANALYSIS.md` (~12k tokens)
- `empirical-investigations/MASSACHUSETTS-CASE-STUDY.md` (~10k tokens)
- Updated `empirical-investigations/INDEX.md` with 3 new completed investigations

**Visualizations**:
- `report/assets/mechanism_comparison_n3_to_n7.png` (4-panel path mechanisms)
- `report/assets/bottleneck_analysis_n3_to_n7.png` (2-panel concentration)
- `report/assets/cycle_evolution_basin_sizes.png` (universal cycles)
- `report/assets/cycle_dominance_evolution.png` (dominance trends)
- `report/assets/massachusetts_deep_dive.png` (4-panel case study)

**Commit**: (pending)

---

### 2025-12-31 (Second) - Link Degree Analysis and Coverage Threshold Discovery

**What was tried**:
- Extended cross-N analysis to N∈{3,4,5,6,7} (added N=4, N=6)
- Extracted Wikipedia link degree distribution (17.9M pages via DuckDB)
- Correlated coverage percentage with basin mass

**What worked**:
- N=4 and N=6 reproduction pipelines ran successfully (~25 min total)
- DuckDB query for link degrees succeeded (Parquet has corruption issues)
- Discovered N=4 is local minimum (30k nodes, smaller than N=3!)
- Found 32.6% coverage threshold aligns perfectly with N=5 peak
- Near-zero correlation (r=-0.042) confirms non-monotonic relationship

**Key findings**:
- N=5 is isolated spike (65× from N=4), not plateau
- Asymmetric curve: sharp rise (65×) vs gradual fall (7-9×)
- Coverage Paradox: Two competing mechanisms identified
- Predictive hypothesis: Basin peaks at ~30-35% coverage

**Files created**:
- `empirical-investigations/PHASE-TRANSITION-REFINED.md`
- `report/assets/phase_transition_n3_to_n7.png`
- `report/assets/coverage_vs_basin_mass.png`
- `report/assets/coverage_zones_analysis.png`
- `data/../analysis/link_degree_distribution*.tsv` (2 files)
- `data/../analysis/coverage_vs_basin_mass.tsv`

**Commit**: (pending)

---

### 2025-12-31 - Cross-N Reproduction and Phase Transition Discovery

**Completed**:
- Created comprehensive reproduction infrastructure:
  - `scripts/validate-data-dependencies.py` - Schema/integrity validation
  - `scripts/reproduce-main-findings.py` - Complete pipeline orchestration (parameterized by N)
  - `scripts/compare-across-n.py` - Cross-N comparison analysis
  - `scripts-reference.md` - Complete documentation for all 14 analysis scripts (~15k tokens)
- Executed full reproduction for N=5 (9 terminal cycles, 1.99M total basin mass)
- Expanded to N∈{3,5,7} to test universality hypothesis
- Generated 9 visualizations (3 interactive 3D HTML trees, 6 cross-N PNG comparison charts)
- Created publication-quality documentation:
  - `empirical-investigations/REPRODUCTION-OVERVIEW.md` - Comprehensive session summary
  - `CROSS-N-FINDINGS.md` (root) - Discovery summary
  - `VISUALIZATION-GUIDE.md` (root) - Visualization index

**Major Discovery**:
- **N=5 exhibits unique phase transition**: 20-60× larger basins than N∈{3,7}
- Same 6 cycles persist across all N but with radically different properties (up to 4289× size variation)
- Only N=5 shows extreme single-trunk structure (67% of basins >95% concentration)
- Hypothesis: N=5 sits at critical 33% page coverage threshold (percolation-like phenomenon)

**Theory Claim Evaluated**:
- **REFUTED**: "Basin structure is universal across N" → Structure is rule-dependent, emerges from rule-graph coupling
- **SUPPORTED**: "Finite self-referential graphs partition into basins" → Holds for all N∈{3,5,7}

**Data Generated** (~60 files in `data/wikipedia/processed/analysis/`):
- Sample traces: N∈{3,5,7}, 500 random starts each
- Basin layers: depth-stratified basin sizes for all cycles
- Branch analysis: tributary structure for all basins
- Dashboards: trunkiness metrics, dominance collapse (N=5 only)
- Dominant chains: upstream trunk paths (N=5 only)

**Contract Update**:
- Added NLR-C-0003 to contract registry (N-dependent phase transition, status: supported)

**Next Steps**:
- Finer N resolution (N∈{4,6,8,9,10}) to map transition curve
- Link degree distribution correlation analysis
- Test on other graphs (different language Wikipedias, citation networks)

Commit: (pending)

---

### 2025-12-31 - Basin Geometry Viewer Reclassified as Visualization

**Completed**:
- Split human-facing visualization tooling out of `scripts/` into `viz/`.
- Added:
	- `viz/dash-basin-geometry-viewer.py`
	- `viz/render-full-basin-geometry.py`
- Updated `INDEX.md` to document the new layout.

**Decision**:
- Treat the Dash basin viewer as a visualization workbench that consumes precomputed Parquet artifacts (no live reverse-expansion).

Commit: 722e63d

---

### 2025-12-29 - Directory Initialized

**Completed**:
- Created new Tier 2 analysis directory with standard docs and script placeholders

**Decisions**:
- Keep analysis scripts out of initial scaffolding; start with placeholders and crystallize algorithms after first benchmarks

**Next Steps**:
- Implement Phase 1 fixed-N basin statistics computation

---

### 2025-12-30 - Empirical Investigation Streams Introduced

**Decision**:
- Empirical findings are recorded in distinct, question-scoped documents under `empirical-investigations/`.
- `session-log.md` references those documents rather than duplicating results.

**New Investigation**:
- [Long-tail basin size (N=5)](empirical-investigations/long-tail-basin-size.md)

**Reproducibility Artifacts (generated outputs)**:
- Output directory: `data/wikipedia/processed/analysis/` (gitignored)
- Edge DB materialized for N=5 reverse expansions: `data/wikipedia/processed/analysis/edges_n=5.duckdb`

---

### 2025-12-30 - Empirical Session Bootstrap (Fixed N=5 sampling)

**Executed**:
- Ran a minimal sanity sampling run for fixed $N=5$ to confirm the analysis scripts work end-to-end and to create a fresh reproducibility artifact.

**Command**:
- `python n-link-analysis/scripts/sample-nlink-traces.py --n 5 --num 50 --seed0 0 --min-outdegree 50 --max-steps 5000 --top-cycles 10 --resolve-titles --out "data/wikipedia/processed/analysis/sample_traces_n=5_num=50_seed0=0_bootstrap_2025-12-30.tsv"`

**Observed Summary (high level)**:
- Terminal counts: `CYCLE = 49`, `HALT = 1` (with `min_outdegree=50`)
- Most frequent cycle in this run: `Gulf_of_Maine ↔ Massachusetts` (11 / 50)

**Primary Investigation Stream**:
- Results are consistent with and recorded under: [Long-tail basin size (N=5)](empirical-investigations/long-tail-basin-size.md)

---

### 2025-12-30 - Branch / Trunk Structure + Dominance Collapse (N=5)

**Executed**:
- Implemented and ran “branch analysis” on multiple $f_5$ basins (partitioning each basin by depth-1 entry subtree size).
- Implemented and ran “dominant-upstream chase” (“source of the Nile”) from multiple seeds.
- Aggregated cross-basin summaries into a trunkiness dashboard and a dominance-collapse dashboard.

**New Scripts**:
- `n-link-analysis/scripts/branch-basin-analysis.py`
- `n-link-analysis/scripts/chase-dominant-upstream.py`
- `n-link-analysis/scripts/compute-trunkiness-dashboard.py`
- `n-link-analysis/scripts/batch-chase-collapse-metrics.py`

**Key Artifacts** (under `data/wikipedia/processed/analysis/`):
- `branch_trunkiness_dashboard_n=5_bootstrap_2025-12-30.tsv`
- `dominance_collapse_dashboard_n=5_bootstrap_2025-12-30_seed=dominant_enters_cycle_title_thr=0.5.tsv`
- `dominant_upstream_chain_n=5_from=Animal_leasttrunk_bootstrap_2025-12-30.tsv`
- `dominant_upstream_chain_n=5_from=American_Revolutionary_War_leasttrunk_bootstrap_2025-12-30.tsv`
- `dominant_upstream_chain_n=5_from=Eastern_United_States_control_bootstrap_2025-12-30.tsv`

**Findings (high-level)**:
- Many tested $f_5$ basins exhibit extreme depth-1 entry concentration (“single-trunk” behavior), but not all.
- Even for a comparatively “non-trunk-like” basin at hop 0 (e.g., `Animal`), the dominant-upstream chase can rapidly enter highly trunk-like regimes upstream.
- The `Eastern_United_States` control chase immediately steps into `American_Revolutionary_War` with ~99% dominance, then matches the prior `American_Revolutionary_War` chain.

**Primary Investigation Stream**:
- Details (commands, outputs, and numeric summaries) are recorded under: [Long-tail basin size (N=5)](empirical-investigations/long-tail-basin-size.md)
