# Responses to WH's Feedback Questions

**Date**: 2026-01-01
**Context**: Addressing questions from [wh-mm_on-pr.md](../../human-facing-documentation/human-collaboration/wh-mm_on-pr.md)

---

## Q1: "Did you find the joined cycle for any start points?"

**Answer**: YES - we can now trace any page to its terminal cycle at each N value.

### Tool Created

`answer-wh-cycle-attachment.py` traces pages to their terminal cycles across N values.

### Example: Massachusetts

```
N | Type     | Steps | Cycle Len | Cycle
----------------------------------------------------------------------
3 | CYCLE    |     4 |         3 | Newfoundland_(island) + 2 others
4 | CYCLE    |     3 |         2 | Ethiopia ↔ Eritrea
5 | CYCLE    |     0 |         2 | Massachusetts ↔ Gulf_of_Maine
6 | CYCLE    |     3 |         3 | New_Jersey + 2 others
7 | CYCLE    |    59 |         2 | Paris ↔ List_of_cities_in_the_European_Union...
```

**Key Finding**: Massachusetts reaches ITSELF at N=5 (0 steps - it IS the cycle), but reaches completely different cycles at other N values.

### Example: Boston

```
N | Type     | Steps | Cycle Len | Cycle
----------------------------------------------------------------------
3 | CYCLE    |     5 |         3 | Newfoundland_(island) + 2 others
4 | CYCLE    |    28 |         2 | Ethiopia ↔ Eritrea
5 | CYCLE    |     2 |         2 | New_Hampshire ↔ Vermont
6 | CYCLE    |     6 |         2 | San_Luis_Potosí ↔ Tamaulipas
7 | HALT     |    13 |         0 | -
```

**Key Finding**: Boston does NOT reach the Massachusetts basin at N=5! It reaches New_Hampshire↔Vermont instead.

---

## Q2: "Is there an N=4 cycle attached to Massachusetts?"

**Answer**: NO - Massachusetts does NOT form a 2-cycle with Gulf_of_Maine at N=4.

### What Actually Happens at N=4

At N=4:
- Massachusetts → Atlantic_Ocean (4th link)
- Gulf_of_Maine → Cape_Cod (4th link)

Both eventually reach the **Ethiopia ↔ Eritrea** cycle (not Massachusetts).

### The Massachusetts ↔ Gulf_of_Maine Cycle

This 2-cycle exists **ONLY at N=5**:
- Massachusetts 5th link → Gulf_of_Maine
- Gulf_of_Maine 5th link → Massachusetts

This is why N=5 shows the massive Massachusetts basin (1M+ nodes) - Massachusetts forms a cycle at N=5 but flows elsewhere at N=4.

### Implication

The 62.6× amplification from N=4 → N=5 is partly explained by Massachusetts **becoming** a cycle at N=5. At N=4, pages that would flow to Massachusetts instead flow to Ethiopia↔Eritrea.

---

## Q3: Hyperstructure Coverage (~2/3 of Wikipedia estimate)

**Answer**: Based on available data, ~28% of Wikipedia is in the hyperstructure. But this is an underestimate due to incomplete data.

### Current Data

From assignment parquet files (cycles with full node lists):

| N | Unique Pages | Coverage |
|---|-------------|----------|
| 3 | 20,031 | 0.28% |
| 4 | 6,739 | 0.09% |
| 5 | 1,979,777 | 27.85% |
| 6 | 26,882 | 0.38% |
| 7 | 6,260 | 0.09% |
| **Union** | **2,017,790** | **28.38%** |

### Data Completeness Issue

Assignment parquet files only exist for cycles where `--write-membership-top-k` was used. From layer files, we know N=5 alone contains ~3.85M pages (21.5% of Wikipedia).

### True Hyperstructure Estimate

Given:
- N=5 alone: 3.85M pages (21.5%)
- Other N values add incrementally (~1-5% each based on layer totals)
- Cross-N overlap is significant (same pages in multiple basins)

**Estimated true hyperstructure**: 30-50% of Wikipedia

WH's estimate of 2/3 (~67%) seems high, but would require full enumeration across all N values to confirm or refute.

### To Get Exact Answer

Run basin mapping with `--write-membership-top-k=999999` for all cycles at all N∈{3-10}.

---

## Q4: MM Attribution

**Completed**: Added provenance sections to NLR-C-0001 and NLR-C-0003 in contract-registry.md.

```markdown
- **Provenance**:
  - Theory originator: WH (N-link rule concept, basin partition framework)
  - Implementation & empirical analysis: MM (2025-12-29 onwards)
```

---

## Summary of Discoveries

1. **Cycle attachment is N-dependent**: The same page reaches different terminal cycles at different N values.

2. **Massachusetts cycle only exists at N=5**: At N=4, both Massachusetts and Gulf_of_Maine flow to Ethiopia↔Eritrea instead.

3. **N=5 phase transition partly explained**: Massachusetts becoming a cycle at N=5 (vs flowing elsewhere at N=4) contributes to the 62.6× basin size amplification.

4. **Hyperstructure coverage ~28-50%**: Lower than WH's 2/3 estimate, but data is incomplete.

5. **Tunneling is real**: Pages demonstrably switch between different basins as N changes.

---

## Scripts Created

| Script | Purpose |
|--------|---------|
| `answer-wh-cycle-attachment.py` | Trace any page to terminal cycles at each N |
| `compute-hyperstructure-coverage.py` | Union all pages across N values |

## Data Files Created

| File | Description |
|------|-------------|
| `cycle_attachment_Massachusetts.tsv` | Massachusetts terminal cycles by N |
| `cycle_attachment_Boston.tsv` | Boston terminal cycles by N |
| `hyperstructure_coverage_summary.tsv` | Coverage statistics |

---

## Next Steps

1. **Full hyperstructure enumeration**: Run with `--write-membership-top-k=999999` for all cycles
2. **Build multiplex table**: Unified (page_id, N, cycle) structure for all basins
3. **Compute intersection matrix**: Quantify overlap between basins at different N
4. **Identify tunnel nodes**: Pages that switch basins when N changes
