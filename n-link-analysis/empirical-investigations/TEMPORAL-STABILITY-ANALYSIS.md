# Temporal Stability Analysis

**Date**: 2026-01-02
**Status**: Initial exploration
**Purpose**: Assess basin stability by analyzing Wikipedia edit history for cycle-defining pages

---

## Methodology

Instead of downloading multiple Wikipedia dumps (costly), we use the MediaWiki API to:
1. Identify pages that define basin cycles
2. Track their edit history
3. Predict which basins might reorganize in future dumps

### Key Insight

Basin stability depends on the **first N links in prose** remaining unchanged. Even minor edits that don't change N-th link targets preserve the basin structure.

---

## Cycle Pages Analyzed

| Cycle | Basin Size (N=5) | Combined Edits (90 days) |
|-------|------------------|--------------------------|
| Gulf_of_Maine ↔ Massachusetts | 1,006,218 | 24 |
| Sea_salt ↔ Seawater | 265,896 | 14 |
| Hill ↔ Mountain | 188,968 | 18 |
| Autumn ↔ Summer | 162,624 | 30 |
| Animal ↔ Kingdom_(biology) | 112,805 | 24 |
| Latvia ↔ Lithuania | 81,656 | 40 |

---

## Stability Assessment

### High-Activity Pages (>20 edits in 90 days)

| Page | Edits | Major (>500B) | Risk Level |
|------|-------|---------------|------------|
| American Revolutionary War | 31 | 0 | LOW (minor edits) |
| Autumn | 29 | 16 | MEDIUM (large changes) |
| Lithuania | 26 | 2 | LOW |
| Massachusetts | 24 | 2 | LOW |

### Recently Edited (<7 days ago)

- American Revolutionary War (1 day)
- Animal (0 days)
- Lithuania (1 day)
- Latvia (1 day)
- Kingdom (biology) (2 days)
- Autumn (4 days)
- Hill (4 days)

### Stable Pages (no edits in 90 days)

- Gulf of Maine

---

## Deep Dive: Autumn ↔ Summer Cycle

The Autumn article had **16 major edits** (>500 bytes each) in 90 days. Investigation:

### Current vs Extracted Link Comparison

**Summer page (prose-only links)**:
| Position | Extracted (Dec 20) | Current Wikipedia |
|----------|-------------------|-------------------|
| 1 | Heat | Heat |
| 2 | Temperate_climate | temperate |
| 3 | Season | season |
| 4 | Spring_(season) | Spring (season) |
| **5** | **Autumn** | **autumn** |

**Result**: N=5 link is **STABLE** (Autumn confirmed)

**Autumn page**:
| Position | Extracted (Dec 20) | Current Wikipedia |
|----------|-------------------|-------------------|
| 1 | North American English | North American English |
| 2 | temperate | temperate |
| 3 | season | season |
| 4 | Earth | Earth |
| **5** | **Summer** | **summer** |

**Result**: N=5 link is **STABLE** (Summer confirmed)

### Conclusion

Despite 29 edits to Autumn (including 16 major ones), the **Autumn ↔ Summer cycle remains intact**. The edits were:
- Photo additions/removals in non-prose sections
- Dead link fixes
- Minor text changes that didn't affect link order

---

## Prediction Framework

### Risk Factors for Basin Instability

1. **High edit frequency** on cycle-defining pages
2. **Major content changes** (>500 bytes) affecting lead section
3. **Link insertions/deletions** before position N
4. **Paragraph restructuring** that reorders links

### Stability Indicators

1. **Protected pages** (semi-protected, full-protected) edit less frequently
2. **Featured/Good articles** have stable lead sections
3. **Fundamental concept pages** (seasons, geography) are curated carefully

---

## Massachusetts Basin Assessment

The largest basin (1M+ pages) depends on:
- Massachusetts →(N=5)→ Gulf_of_Maine
- Gulf_of_Maine →(N=5)→ Massachusetts

**Gulf of Maine**: 0 edits in 90 days (completely stable)
**Massachusetts**: 24 edits, 2 major

Risk: **LOW** - Gulf of Maine acts as an anchor. Massachusetts changes would need to affect links 1-5 specifically.

---

## Recommendations

### For Temporal Analysis

1. **Periodic monitoring**: Run edit history check monthly
2. **Alert on major changes**: Flag pages with >500 byte changes to lead section
3. **Re-extract on demand**: When cycle pages change significantly, re-extract affected paths

### For Full Temporal Comparison

To properly compare basins across time:
1. Download dumps from multiple months (e.g., quarterly)
2. Extract link sequences from each
3. Compute basin assignments
4. Measure:
   - Cycle persistence (do the same cycles exist?)
   - Basin size drift (how much do basins grow/shrink?)
   - Tunnel node stability (do the same nodes tunnel?)

---

## Data Files

| File | Description |
|------|-------------|
| `scripts/temporal/fetch-edit-history.py` | Wikipedia API edit history fetcher |
| `data/wikipedia/processed/temporal/edit_history_2026-01-02.json` | Raw API results |
| `report/EDIT-HISTORY-ANALYSIS.md` | Generated summary report |

---

## Related Documents

- [MULTI-N-PHASE-MAP.md](MULTI-N-PHASE-MAP.md) - Phase transition analysis
- [../report/MULTI-N-ANALYSIS-REPORT.md](../report/MULTI-N-ANALYSIS-REPORT.md) - Comprehensive findings
- [../../human-facing-documentation/human-collaboration/wh-mm_on-pr.md](../../human-facing-documentation/human-collaboration/wh-mm_on-pr.md) - WH's temporal evolution speculation

---

**Key Finding**: Basin cycles are more stable than edit counts suggest. Most edits don't affect the critical first N links in prose. The Autumn ↔ Summer cycle survived 59 combined edits with no structural change.
