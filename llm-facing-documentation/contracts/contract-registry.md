# Contract Registry

**Purpose**: A registry of explicit theory–experiment–evidence contracts.

This is the *primary index* for contract objects, and should be treated as append-only (you can add new entries; avoid rewriting old ones except to mark them deprecated).

**Last Updated**: 2025-12-31

---

## Active Contracts

### NLR-C-0001 — Long-tail basin size under fixed-N traversal (Wikipedia proving ground)

- **Status**: supported (empirical; scope: Wikipedia namespace 0, non-redirect pages)
- **Theory**:
  - [n-link-rule-theory.md](../theories-proofs-conjectures/n-link-rule-theory.md) (basins, cycles, terminals)
  - [unified-inference-theory.md](../theories-proofs-conjectures/unified-inference-theory.md) (integration framing)
- **Experiment**:
  - [map-basin-from-cycle.py](../../n-link-analysis/scripts/map-basin-from-cycle.py) (reverse reachability / basin mapping)
  - [sample-nlink-traces.py](../../n-link-analysis/scripts/sample-nlink-traces.py) (cycle sampling)
- **Evidence**:
  - [long-tail-basin-size.md](../../n-link-analysis/empirical-investigations/long-tail-basin-size.md)
  - Outputs under `data/wikipedia/processed/analysis/`
- **Notes**:
  - This contract is intentionally "Wikipedia-first" to preserve cultural salience and reduce concerns of bespoke/system-fit bias.

---

### NLR-C-0003 — N-dependent phase transition in basin structure (Wikipedia)

- **Status**: supported (empirical; scope: Wikipedia namespace 0, non-redirect pages, N∈{3,4,5,6,7})
- **Theory**:
  - [n-link-rule-theory.md](../theories-proofs-conjectures/n-link-rule-theory.md) (N-link rule definition, basin partitioning)
  - Extends NLR-C-0001 to cross-N comparison
- **Experiment**:
  - [reproduce-main-findings.py](../../n-link-analysis/scripts/reproduce-main-findings.py) (parameterized by N)
  - [compare-across-n.py](../../n-link-analysis/scripts/compare-across-n.py) (cross-N analysis)
  - [map-basin-from-cycle.py](../../n-link-analysis/scripts/map-basin-from-cycle.py) (basin mapping)
  - [sample-nlink-traces.py](../../n-link-analysis/scripts/sample-nlink-traces.py) (cycle sampling)
- **Evidence**:
  - [REPRODUCTION-OVERVIEW.md](../../n-link-analysis/empirical-investigations/REPRODUCTION-OVERVIEW.md) (N∈{3,5,7} comprehensive summary)
  - [PHASE-TRANSITION-REFINED.md](../../n-link-analysis/empirical-investigations/PHASE-TRANSITION-REFINED.md) (N∈{3,4,5,6,7} refined analysis)
  - [CROSS-N-FINDINGS.md](../../CROSS-N-FINDINGS.md) (publication-quality discovery summary)
  - Phase transition visualizations: `n-link-analysis/report/assets/phase_transition_n3_to_n7.png`
  - Coverage analysis: `n-link-analysis/report/assets/coverage_vs_basin_mass.png`, `coverage_zones_analysis.png`
  - Cross-N visualizations: `n-link-analysis/report/assets/cross_n_*.png` (6 charts)
  - Data outputs: `data/wikipedia/processed/analysis/*_n={3,4,5,6,7}_*` (~72 files)
  - Link degree distribution: `data/wikipedia/processed/analysis/link_degree_distribution*.tsv`
- **Key Finding**:
  - **Refined**: N=5 is an isolated spike (65× amplification from N=4), not a plateau
  - N=4 is a local minimum (30k nodes) - smaller than N=3 (102k)! Asymmetric curve: sharp rise (65×), gradual fall (7-9×)
  - N=5 peak aligns precisely with 32.6% page coverage (5.9M pages with ≥5 links)
  - Coverage vs basin mass: near-zero correlation (r=-0.042) confirms non-monotonic relationship
  - **Mechanism identified**: Two competing effects (Path Existence vs Path Concentration) balanced optimally at N=5
  - Same 6 terminal cycles persist across N with radically different properties (up to 4289× size variation)
- **Theory Claim Evaluated**:
  - **Refuted**: "Basin structure is universal across N" → Structure is rule-dependent, not graph-intrinsic
  - **Supported**: "Finite self-referential graphs partition into basins under deterministic rules" → Holds for all N∈{3,4,5,6,7}
  - **New hypothesis**: Basin mass peaks occur at ~30-35% coverage threshold (potentially universal for scale-free networks)
- **Notes**:
  - Basin properties emerge from rule-graph coupling (deterministic rule selectivity × graph degree distribution)
  - Critical phenomena framework validated: N=5 exhibits phase transition-like behavior
  - Coverage Paradox documented: Basin mass is non-monotonic function of connectivity
  - Predictive framework: For any graph, measure degree distribution → find N where coverage ≈ 33% → predict basin peak
  - Next steps: Test N∈{8,9,10}, other language Wikipedias, citation networks, percolation modeling

---

### NLR-C-0002 — Citation & integration lineage for sqsd.html → N-Link theory

- **Status**: proposed
- **Goal**: Ensure every usage of `sqsd.html` is explicitly attributed, scoped, and linked into the theory–experiment–evidence chain without “stealth integration” into canonical theory.
- **External Artifact (source)**:
  - [sqsd.html](../theories-proofs-conjectures/sqsd.html) — Ryan Querin (external)
- **Theory (targets / touchpoints)**:
  - [n-link-rule-theory.md](../theories-proofs-conjectures/n-link-rule-theory.md) (if/when SQSD concepts are cited)
  - [database-inference-graph-theory.md](../theories-proofs-conjectures/database-inference-graph-theory.md) (if/when SQSD concepts are cited)
  - [unified-inference-theory.md](../theories-proofs-conjectures/unified-inference-theory.md) (if/when SQSD concepts are cited)
- **Evidence**:
  - Add a dedicated investigation doc when SQSD is first used for an empirical argument (e.g., under `n-link-analysis/empirical-investigations/`).
- **Operational rules**:
  - Do not quote or embed large portions of `sqsd.html` into canonical theory; prefer high-level references.
  - Any canonical-theory citation should be additive (append-only) and must include author credit.
  - Before broader redistribution, record explicit permission/license terms for `sqsd.html` under `EXT-A-0001`.

---

## External / Third-Party Artifacts (Referenced by Contracts)

### EXT-A-0001 — sqsd.html (Structural Query Semantics as a Deterministic Space)

- **Status**: referenced (not yet integrated into canonical theory)
- **Artifact**: [sqsd.html](../theories-proofs-conjectures/sqsd.html)
- **Author**: Ryan Querin
- **Relationship**: authored externally; explicitly based on (and extending) project work
- **Redistribution / License**: TODO — record explicit permission and license terms before wider distribution
- **Integration policy**:
  - Do not treat as canonical theory.
  - When used, reference via explicit contract entries (and cite author).
