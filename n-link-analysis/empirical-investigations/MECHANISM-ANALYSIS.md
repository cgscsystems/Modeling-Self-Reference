# Path Mechanism Analysis: Why N=4 is Minimum and N=5 is Maximum

**Date**: 2025-12-31 (updated 2026-01-01)
**Investigation**: Mechanism understanding for phase transition
**Dataset**: 1,000 random path samples per N for N∈{3,4,5,6,7}
**Theory Connection**: Coverage Paradox (Path Existence vs Path Concentration)

> **⚠️ Important Update (2026-01-01)**: This document was written before the entry breadth hypothesis was tested empirically. Subsequent analysis in [ENTRY-BREADTH-RESULTS.md](ENTRY-BREADTH-RESULTS.md) **refuted** the entry breadth hypothesis: entry breadth actually *decreases* from N=4 to N=5. The dominant factor is **depth**, not entry breadth. See [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md) for the validated formula: `Basin_Mass = Entry_Breadth × Depth^2.5`. The mechanism observations (premature convergence, optimal exploration time) remain valid, but the causal attribution to "entry breadth" should be read as "depth amplification."

---

## Executive Summary

We explain the **non-monotonic basin mass curve** (N=4 minimum → N=5 peak → gradual decline) through path-level analysis. The key discoveries:

1. **N=4 has shortest paths** (14 steps median) despite low HALT rate (1.3%)
2. **N=4 has fastest convergence** (11 steps) but smallest basins
3. **N=5 has longer paths** (15 steps) and MODERATE convergence (12 steps) but GIANT basins
4. **Mechanism identified**: Basin mass ≠ convergence speed. It depends on **depth amplification** (see [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md)), not just concentration rate.

---

## The N=4 Paradox: Fast Convergence, Small Basins

### Empirical Observations

| Metric | N=3 | N=4 | N=5 | Interpretation |
|--------|-----|-----|-----|----------------|
| **Median convergence depth** | 17 steps | **11 steps** | 12 steps | N=4 converges **fastest** |
| **Median path length** | 21 steps | **14 steps** | 15 steps | N=4 has **shortest** paths |
| **HALT rate** | 1.2% | 1.3% | 2.7% | N=4 doesn't fragment more |
| **Basin mass** | 102k | **31k** | 2.0M | N=4 has **smallest** basins |

### The Paradox

**If N=4 converges fastest (11 steps), why does it have the smallest basins (31k vs 102k at N=3)?**

### Resolution: Depth Amplification (Not Entry Breadth)

**Key insight**: Basin mass depends on **depth**, not entry breadth:

```
Basin Mass = Entry Breadth × Depth^α    (where α ≈ 2.5)
```

> **Note**: The original hypothesis here was that entry breadth was the key factor. This was **refuted** by [ENTRY-BREADTH-RESULTS.md](ENTRY-BREADTH-RESULTS.md), which showed entry breadth *decreases* from N=4 to N=5 (0.75×), while basin mass increases 59×. The correct explanation is **depth amplification**: N=5 achieves 7.2× deeper basins than N=4, and since mass scales as Depth^2.5, this produces 62× amplification. See [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md).

**N=4 converges TOO fast!**

1. **Rapid convergence** (11 steps) means paths "decide their fate" quickly
2. **Short paths** (14 steps total) mean shallow basin depth
3. **Low depth**: Paths converge before exploring deeply

**Think of it as a karst sinkhole** (not a drainage basin):
- N=4 is like a shallow depression - water collects but doesn't penetrate deep
- N=5 is like a deep sinkhole - narrow opening, but huge underground volume due to depth

---

## The N=5 Sweet Spot: Moderate Convergence, Maximum Depth

### Empirical Observations

| Metric | N=4 | N=5 | N=6 | Interpretation |
|--------|-----|-----|-----|----------------|
| **Median convergence depth** | 11 steps | 12 steps | 10 steps | N=5 is NOT fastest |
| **Rapid convergence rate (<50 steps)** | 97.5% | **85.9%** | 89.3% | N=5 has **slowest** rapid convergence |
| **Median path length** | 14 steps | 15 steps | 14 steps | N=5 has slightly longer paths |
| **HALT rate** | 1.3% | 2.7% | 10.2% | N=5 has moderate fragmentation |
| **Basin mass** | 31k | **2.0M** | 290k | N=5 has **65× larger** basins than N=4 |

### The Key Discovery

**N=5 does NOT converge fastest. It achieves the DEEPEST basins.**

Looking at **rapid convergence rate** (<50 steps):
- N=3: 98.6% converge quickly (shallow basins)
- N=4: 97.5% converge quickly (shallow basins)
- N=5: **85.9%** converge quickly (deepest exploration!)
- N=6: 89.3% converge quickly (moderate depth)
- N=7: 78.0% converge quickly (diffuse, high HALT)

**Interpretation**:
- N=5 has **14% of paths taking >50 steps** to converge
- These are the **deep exploratory paths** that penetrate far into the graph
- Depth^2.5 scaling = giant basins (see [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md))

---

## Mechanism Explanation: Three Regimes

### Regime 1: N=3 (High Coverage, Moderate Basins)

- **Coverage**: 37% of pages can continue
- **Convergence**: Slower (17 steps median)
- **Path length**: Longer (21 steps)
- **Problem**: TOO DIFFUSE - many competing paths, no strong concentration
- **Result**: Moderate basins (102k)

**Analogy**: A delta with many small channels - water spreads but doesn't concentrate

---

### Regime 2: N=4 (Medium Coverage, MINIMUM Basins)

- **Coverage**: 35% of pages can continue
- **Convergence**: **Fastest** (11 steps median)
- **Path length**: **Shortest** (14 steps)
- **Problem**: TOO FAST - paths converge before exploring broadly
- **Result**: Smallest basins (31k)

**Mechanism discovered**: **Premature Convergence**
- Coverage dropped just enough (37% → 35%) to create selective pressure
- But convergence happens SO FAST that catchment area never builds
- Paths "commit" to their cycle too early, missing potential tributaries

**This is the "worst of both worlds"**:
- Selective enough to fragment (vs N=3)
- But NOT selective enough to create long exploratory paths (vs N=5)

---

### Regime 3: N=5 (Goldilocks Zone, MAXIMUM Basins)

- **Coverage**: 33% of pages can continue
- **Convergence**: Moderate (12 steps median)
- **Path length**: Moderate (15 steps)
- **Magic**: **Slowest rapid convergence** (85.9% <50 steps) = deepest exploration
- **Result**: Giant basins (2.0M)

**Mechanism discovered**: **Optimal Exploration Depth**
- Coverage is selective enough (33%) to force concentration
- But convergence is SLOW enough (12 steps median, 14% take >50 steps) to explore deeply
- Paths penetrate far into the graph before committing to a cycle

**Why does this work?**
1. **Sufficient survival** (low HALT rate: 2.7%)
2. **Delayed commitment** (14% of paths take >50 steps)
3. **Deep penetration** (max depth 168 steps at N=5 vs 13 steps at N=4)

**The 32.6% coverage threshold is the tipping point** where:
- Enough pages exist to sustain long paths (Path Existence)
- Few enough exist to force eventual concentration (Path Concentration)
- Balance creates maximum exploratory depth

---

### Regime 4: N≥6 (Low Coverage, Fragmentation)

- **Coverage**: ≤30% of pages can continue
- **Convergence**: Fast again (10 steps at N=6, then slower at N=7)
- **Path length**: Variable (14 steps at N=6, 20 steps at N=7)
- **Problem**: High HALT rate kills paths (10.2% at N=6, 12.6% at N=7)
- **Result**: Smaller basins (290k at N=6, 34k at N=7)

**Mechanism**: **Fragmentation Dominates**
- Coverage too low → many paths HALT before reaching cycle
- Even surviving paths converge to smaller basins (less catchment area)
- N=7 shows longest median convergence (20 steps) but HIGHEST HALT rate (12.6%)
  - This is **wasteful exploration**: paths wander before HALTing

---

## Quantitative Evidence

### Critical Metrics Across N

| N | Coverage % | HALT % | Med Conv | Basin Mass | Max Depth (measured) |
|---|------------|--------|----------|------------|----------------------|
| 3 | 37.4% | 1.2% | 17 steps | 102k | ~14 steps |
| 4 | 35.0% | 1.3% | **11 steps** | **31k** | **~10 steps (shallow)** |
| 5 | 32.6% | 2.7% | 12 steps | **2.0M** | **~74 steps (deep)** |
| 6 | 30.4% | 10.2% | 10 steps | 290k | ~27 steps |
| 7 | 28.2% | 12.6% | 20 steps | 34k | ~15 steps |

### The N=4→5 Amplification

**Why 65× basin size increase?**

> **Updated (2026-01-01)**: The original hypothesis here attributed amplification to entry breadth. This was **refuted**. See [ENTRY-BREADTH-RESULTS.md](ENTRY-BREADTH-RESULTS.md) for the empirical data showing entry breadth *decreases* from N=4 to N=5.

```
Basin Mass ≈ Entry Breadth × Depth^2.5

N=5 / N=4: 0.75 × (74/10)^2.5 ≈ 0.75 × 62 ≈ 47× (close to observed 65×)
```

Breaking down:
1. **Entry Breadth**: N=5 has 0.75× the entry breadth of N=4 (DOWN, not up!)
2. **Depth**: N=5 is 7.2× deeper than N=4 (the dominant factor)
3. **Net Effect**: Depth^2.5 dominates → 65× amplification

**Key insight**: The small coverage drop (35% → 33%, only 2 percentage points) creates HUGE depth difference because:
- Coverage is **nonlinear** in its effect on depth
- 33% is the critical threshold where paths explore maximally deep before converging
- Below 35% (N=4): converge too fast (shallow)
- Above 33% (N=3): too diffuse (moderate depth)

---

## Theoretical Implications

### 1. Basin Mass ≠ Convergence Speed

**Refuted intuition**: "Faster convergence → larger basins"

**Correct model**: Basin mass = Entry_Breadth × Depth^α × Path_Survival (see [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md))
- **Depth DOMINATES** (α ≈ 2.5, r = 0.943 correlation)
- Entry breadth provides baseline scaling (r = 0.127, negligible)
- Convergence speed has OPTIMUM (not monotonic)
- Too fast (N=4) → shallow basins → small mass
- Optimal (N=5) → deep basins → giant mass
- Too slow + high HALT (N=7) → paths die before depth

### 2. Coverage Paradox Validated

**Path Existence** (favors high coverage):
- More pages can continue → longer paths → more exploration

**Path Concentration** (favors low coverage):
- Fewer viable pages → forced convergence → concentrated basins

**The paradox**: N=5 balances these by having:
- Enough coverage (33%) for path existence
- Low enough coverage for eventual concentration
- But crucially: **SLOW ENOUGH convergence** to explore deeply before committing

### 3. Premature Convergence Mechanism

**New discovery**: N=4 is a **premature convergence regime**

- Paths decide their fate TOO QUICKLY (11 steps)
- Before they can explore broadly
- This creates small basins despite low fragmentation

**Why does this happen?**
- Hypothesis: 35% coverage creates a "convergence cascade"
- Once a few paths converge, they create attractors
- Remaining paths converge to those attractors quickly
- Not enough "exploration time" to build broad catchment

**Testable prediction**:
- N=4 basins should have **fewer unique entry branches** than N=5
- Next analysis: entry point breadth comparison

---

## Visualizations

**Main Charts**:
- [mechanism_comparison_n3_to_n7.png](../report/assets/mechanism_comparison_n3_to_n7.png)
- [bottleneck_analysis_n3_to_n7.png](../report/assets/bottleneck_analysis_n3_to_n7.png)

**Key Panels**:
1. **Convergence Depth**: Shows N=4 has fastest convergence (11 steps)
2. **HALT Rate**: Shows monotonic increase (fragmentation grows with N)
3. **Path Length**: Shows N=4 has shortest paths (14 steps)
4. **Rapid Convergence Rate**: Shows N=5 has LOWEST rate (85.9%) = broadest exploration

---

## Next Steps

### ~~Immediate: Validate Entry Breadth Hypothesis~~ ✓ COMPLETED

> **Status (2026-01-01)**: This investigation was completed. The hypothesis was **refuted**. See [ENTRY-BREADTH-RESULTS.md](ENTRY-BREADTH-RESULTS.md).

**Result**: Entry breadth DECREASES from N=4 to N=5 (0.75×), not increases as predicted. The dominant factor is **depth**, not entry breadth.

**Actual findings**:
- N=4: Entry breadth 571.8
- N=5: Entry breadth 429.2 (0.75× of N=4)
- But N=5 has 7.2× deeper basins → explains the 65× mass amplification

### Medium-term: Percolation Model

**Goal**: Build mathematical model predicting basin mass

**Components** (updated based on [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md)):
1. **Entry breadth** → baseline scaling (minor factor)
2. **Max depth** → dominant factor (Depth^2.5 scaling)
3. **Path survival** → implicit in depth (paths that HALT don't reach max depth)

**Validated equation**:
```
Basin Mass ≈ Entry_Breadth × Max_Depth^α

where:
  α = 2.50 ± 0.48 (measured across 6 cycles)
  R² = 0.878 (excellent fit)
  Log correlation r = 0.922
```

### Long-term: Test on Other Graphs

**Hypothesis**: ~30-35% coverage is universal threshold for scale-free networks

**Experiments**:
1. Other language Wikipedias (es, de, fr)
2. Citation networks (arXiv, papers)
3. Web graphs (Common Crawl subsets)

**Prediction**: All will show basin peaks at ~30-35% coverage

---

## Conclusion

**The N=4 minimum and N=5 peak are explained by the interplay of three factors**:

1. **Coverage** (drops from 37% → 28% as N increases)
2. **Convergence speed** (non-monotonic: fast at N=4, moderate at N=5)
3. **Basin depth** (the dominant factor - see [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md))

**N=4 is minimum** because:
- Converges TOO FAST (11 steps)
- Paths commit to cycles before exploring deeply
- Result: shallow basins, small mass

**N=5 is maximum** because:
- Converges at OPTIMAL speed (12 steps median, but 14% take >50 steps)
- Paths explore deeply before committing (max depth 168 vs 13 at N=4)
- 32.6% coverage threshold enables maximum exploration depth
- Result: deep basins, giant mass

**This refutes the simple fragmentation model** and establishes a new framework:

**Basin Mass = Entry Breadth × Depth^2.5** (validated in [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md))

Not just "low HALT rate = big basins" but "optimal exploration depth before convergence = big basins"

---

## Files Generated

**Scripts**:
- [analyze-path-characteristics.py](../scripts/analyze-path-characteristics.py)
- [visualize-mechanism-comparison.py](../scripts/visualize-mechanism-comparison.py)

**Data** (15 files):
- `path_characteristics_n={3,4,5,6,7}_mechanism_details.tsv`
- `path_characteristics_n={3,4,5,6,7}_mechanism_summary.tsv`
- `path_characteristics_n={3,4,5,6,7}_mechanism_depth_distributions.tsv`

**Visualizations**:
- `mechanism_comparison_n3_to_n7.png`
- `bottleneck_analysis_n3_to_n7.png`

---

**Last Updated**: 2026-01-01
**Status**: Mechanism identified; entry breadth hypothesis refuted, depth dominance validated
**Contract**: NLR-C-0003 (evidence supports depth-based basin mass formula)
**Related**: [ENTRY-BREADTH-RESULTS.md](ENTRY-BREADTH-RESULTS.md), [DEPTH-SCALING-ANALYSIS.md](DEPTH-SCALING-ANALYSIS.md)
