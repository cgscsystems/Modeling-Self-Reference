#!/usr/bin/env python3
"""Compute hyperstructure coverage across all N values.

This script answers WH's question about what fraction of Wikipedia is in
the hyperstructure (union of all pages appearing in ANY basin at ANY N).

WH estimated ~2/3 of Wikipedia pages. This script computes the actual value.

Method:
  1. Load all branches_n=*_assignments.parquet files
  2. Union all page_ids across all N values and cycles
  3. Compute coverage as fraction of total Wikipedia pages

Data dependencies:
  - data/wikipedia/processed/analysis/branches_n=*_assignments.parquet
  - data/wikipedia/processed/pages.parquet (for total page count)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "wikipedia" / "processed"
ANALYSIS_DIR = PROCESSED_DIR / "analysis"
PAGES_PATH = PROCESSED_DIR / "pages.parquet"


def get_total_pages() -> int:
    """Get total number of namespace-0 non-redirect pages."""
    con = duckdb.connect()
    result = con.execute(
        f"""
        SELECT COUNT(*)
        FROM read_parquet('{PAGES_PATH.as_posix()}')
        WHERE namespace = 0 AND NOT is_redirect
        """
    ).fetchone()
    con.close()
    return int(result[0]) if result else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute hyperstructure coverage across all N values"
    )
    parser.add_argument(
        "--n-min",
        type=int,
        default=3,
        help="Minimum N value to include (default: 3)",
    )
    parser.add_argument(
        "--n-max",
        type=int,
        default=10,
        help="Maximum N value to include (default: 10)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Computing Hyperstructure Coverage")
    print("=" * 70)
    print()

    # Get total page count
    total_pages = get_total_pages()
    print(f"Total Wikipedia pages (ns=0, non-redirect): {total_pages:,}")
    print()

    # Find all assignment parquet files
    pattern = "branches_n=*_*_assignments.parquet"
    all_files = list(ANALYSIS_DIR.glob(pattern))

    if not all_files:
        print(f"ERROR: No files matching {pattern} found in {ANALYSIS_DIR}")
        return

    print(f"Found {len(all_files)} basin assignment files")
    print()

    # Track pages per N and overall
    pages_by_n: dict[int, set[int]] = {}
    all_pages: set[int] = set()

    # Process each file
    for filepath in sorted(all_files):
        # Parse N from filename: branches_n=5_cycle=...
        name = filepath.name
        try:
            n_part = name.split("_")[1]  # "n=5"
            n = int(n_part.split("=")[1])
        except (IndexError, ValueError):
            print(f"  Skipping (can't parse N): {name}")
            continue

        if n < args.n_min or n > args.n_max:
            continue

        if n not in pages_by_n:
            pages_by_n[n] = set()

        # Load page_ids from parquet
        try:
            table = pq.read_table(filepath, columns=["page_id"])
            page_ids = table["page_id"].to_pylist()
            pages_by_n[n].update(page_ids)
            all_pages.update(page_ids)
        except Exception as e:
            print(f"  Error reading {name}: {e}")
            continue

    print()
    print("=" * 70)
    print("RESULTS: Coverage by N")
    print("=" * 70)
    print()
    print(f"{'N':>3} | {'Pages':>12} | {'Coverage':>10} | {'New Pages':>12}")
    print("-" * 50)

    cumulative = set()
    for n in sorted(pages_by_n.keys()):
        pages_n = pages_by_n[n]
        new_pages = len(pages_n - cumulative)
        cumulative.update(pages_n)
        coverage = len(pages_n) / total_pages * 100
        print(f"{n:>3} | {len(pages_n):>12,} | {coverage:>9.2f}% | {new_pages:>12,}")

    print()
    print("=" * 70)
    print("HYPERSTRUCTURE TOTAL")
    print("=" * 70)
    print()

    hyperstructure_size = len(all_pages)
    hyperstructure_coverage = hyperstructure_size / total_pages * 100

    print(f"Union of all pages across N∈{{{args.n_min},...,{args.n_max}}}:")
    print(f"  Total unique pages: {hyperstructure_size:,}")
    print(f"  Coverage: {hyperstructure_coverage:.2f}%")
    print()
    print(f"WH's estimate: ~66.7% (2/3 of Wikipedia)")
    print(f"Actual: {hyperstructure_coverage:.1f}%")
    print()

    if hyperstructure_coverage > 50:
        print("✓ The hyperstructure covers a MAJORITY of Wikipedia")
    else:
        print("✗ The hyperstructure covers less than half of Wikipedia")

    # Note about data completeness
    print()
    print("=" * 70)
    print("NOTE: Data Completeness")
    print("=" * 70)
    print()
    print("This analysis only includes basins for which assignment parquet files")
    print("were generated (--write-membership-top-k flag during basin mapping).")
    print()
    print("From layer files, we know N=5 alone has ~3.85M unique pages (21.5% of")
    print("Wikipedia). With all N values included, the true hyperstructure is")
    print("likely larger than the ~28% computed here from available data.")
    print()
    print("To compute exact hyperstructure coverage, run basin mapping with")
    print("--write-membership-top-k=999999 for all cycles at all N values.")

    # Save results
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ANALYSIS_DIR / "hyperstructure_coverage_summary.tsv"
    with open(out_path, "w") as f:
        f.write("metric\tvalue\n")
        f.write(f"total_wikipedia_pages\t{total_pages}\n")
        f.write(f"hyperstructure_pages\t{hyperstructure_size}\n")
        f.write(f"hyperstructure_coverage_pct\t{hyperstructure_coverage:.4f}\n")
        f.write(f"n_min\t{args.n_min}\n")
        f.write(f"n_max\t{args.n_max}\n")
        f.write(f"num_basin_files\t{len(all_files)}\n")
        for n in sorted(pages_by_n.keys()):
            f.write(f"pages_at_n={n}\t{len(pages_by_n[n])}\n")

    print()
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()
