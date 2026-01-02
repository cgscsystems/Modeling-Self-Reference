#!/usr/bin/env python3
"""Trace pages to their terminal cycles across N values.

This script answers WH's questions:
  - "Did you find the joined cycle for any start points?"
  - "Is there an N=4 cycle attached to Massachusetts?"

For any page, shows which terminal cycle it reaches at each N value.

Method:
  1. Look up page_id for the given title
  2. Trace f_N for each N∈{3,4,5,6,7,...} to find terminal cycles
  3. Report which cycles the page reaches at each N

Data dependencies:
  - data/wikipedia/processed/nlink_sequences.parquet
  - data/wikipedia/processed/pages.parquet
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import duckdb
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "wikipedia" / "processed"
NLINK_PATH = PROCESSED_DIR / "nlink_sequences.parquet"
PAGES_PATH = PROCESSED_DIR / "pages.parquet"
ANALYSIS_DIR = PROCESSED_DIR / "analysis"


def get_page_id(title: str) -> int | None:
    """Look up page_id for a given title."""
    con = duckdb.connect()
    result = con.execute(
        f"""
        SELECT page_id
        FROM read_parquet('{PAGES_PATH.as_posix()}')
        WHERE title = ? AND namespace = 0 AND NOT is_redirect
        LIMIT 1
        """,
        [title],
    ).fetchone()
    con.close()
    return int(result[0]) if result else None


def get_title(page_id: int) -> str:
    """Look up title for a page_id."""
    con = duckdb.connect()
    result = con.execute(
        f"""
        SELECT title
        FROM read_parquet('{PAGES_PATH.as_posix()}')
        WHERE page_id = ?
        LIMIT 1
        """,
        [page_id],
    ).fetchone()
    con.close()
    return str(result[0]) if result else "<unknown>"


def load_successor_arrays(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Load (page_id, next_id) arrays for fixed N."""
    query = f"""
        SELECT
            page_id::BIGINT AS page_id,
            list_extract(link_sequence, {n})::BIGINT AS next_id
        FROM read_parquet('{NLINK_PATH.as_posix()}')
    """
    con = duckdb.connect()
    tbl = con.execute(query).fetch_arrow_table()
    con.close()

    page_ids = tbl["page_id"].combine_chunks().to_numpy(zero_copy_only=False).astype(np.int64)
    next_ids_raw = tbl["next_id"].combine_chunks().to_numpy(zero_copy_only=False)

    if isinstance(next_ids_raw, np.ma.MaskedArray):
        next_ids = next_ids_raw.filled(-1).astype(np.int64)
    elif np.issubdtype(next_ids_raw.dtype, np.floating):
        next_ids = np.where(np.isnan(next_ids_raw), -1, next_ids_raw).astype(np.int64)
    else:
        next_ids = next_ids_raw.astype(np.int64)

    order = np.argsort(page_ids, kind="mergesort")
    return page_ids[order], next_ids[order]


def trace_to_cycle(
    start_page_id: int,
    sorted_page_ids: np.ndarray,
    next_ids: np.ndarray,
    max_steps: int = 500,
) -> tuple[str, list[int], int]:
    """Trace from start_page_id until cycle or HALT.

    Returns: (terminal_type, cycle_members, steps_to_cycle)
    """
    visited = {}
    path = []
    current = start_page_id

    for step in range(max_steps):
        if current in visited:
            # Found cycle
            cycle_start = visited[current]
            cycle_members = path[cycle_start:]
            return "CYCLE", cycle_members, cycle_start

        visited[current] = len(path)
        path.append(current)

        idx = int(np.searchsorted(sorted_page_ids, current))
        if idx >= len(sorted_page_ids) or int(sorted_page_ids[idx]) != current:
            return "HALT", [], len(path)

        nxt = int(next_ids[idx])
        if nxt == -1:
            return "HALT", [], len(path)

        current = nxt

    return "MAX_STEPS", [], max_steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Investigate which cycles Massachusetts reaches at each N value"
    )
    parser.add_argument(
        "--n-values",
        type=int,
        nargs="+",
        default=[3, 4, 5, 6, 7],
        help="N values to test (default: 3 4 5 6 7)",
    )
    parser.add_argument(
        "--page",
        type=str,
        default="Massachusetts",
        help="Page title to trace (default: Massachusetts)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"Tracing '{args.page}' to Terminal Cycles Across N Values")
    print("=" * 70)
    print()

    page_id = get_page_id(args.page)
    if page_id is None:
        print(f"ERROR: Could not find page_id for '{args.page}'")
        return

    print(f"Page: {args.page} (page_id: {page_id})")
    print()

    results = []

    for n in args.n_values:
        print(f"Loading N={n} successor data...", end=" ", flush=True)
        t0 = time.time()
        page_ids, next_ids = load_successor_arrays(n)
        print(f"done ({time.time() - t0:.1f}s)")

        terminal_type, cycle_members, steps = trace_to_cycle(page_id, page_ids, next_ids)

        if terminal_type == "CYCLE":
            cycle_titles = [get_title(pid) for pid in cycle_members]
            cycle_key = " ↔ ".join(cycle_titles[:2]) if len(cycle_titles) <= 2 else f"{cycle_titles[0]} + {len(cycle_titles)-1} others"
            results.append((n, "CYCLE", steps, len(cycle_members), cycle_key, cycle_members))
        else:
            results.append((n, terminal_type, steps, 0, "-", []))

    print()
    print("=" * 70)
    print("RESULTS: Terminal Cycles by N")
    print("=" * 70)
    print()
    print(f"{'N':>3} | {'Type':<8} | {'Steps':>5} | {'Cycle Len':>9} | Cycle")
    print("-" * 70)

    for n, ttype, steps, clen, ckey, _ in results:
        print(f"{n:>3} | {ttype:<8} | {steps:>5} | {clen:>9} | {ckey}")

    print()
    print("=" * 70)
    print("ANSWER TO WH's QUESTION:")
    print("=" * 70)
    print()

    # Check N=4 specifically
    n4_result = next((r for r in results if r[0] == 4), None)
    n5_result = next((r for r in results if r[0] == 5), None)

    if n4_result and n4_result[1] == "CYCLE":
        n4_cycle = n4_result[4]
        if "Massachusetts" in n4_cycle or "Gulf_of_Maine" in n4_cycle:
            print(f"YES: At N=4, {args.page} reaches the {n4_cycle} cycle.")
        else:
            print(f"NO: At N=4, {args.page} reaches a DIFFERENT cycle: {n4_cycle}")
            print()
            print("The Massachusetts ↔ Gulf_of_Maine cycle exists at N=5, but NOT at N=4.")
            print(f"At N=4, {args.page} instead flows to: {n4_cycle}")
    elif n4_result:
        print(f"At N=4, {args.page} reaches {n4_result[1]} (no cycle)")

    # Write results to TSV
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ANALYSIS_DIR / f"cycle_attachment_{args.page.replace(' ', '_')}.tsv"
    with open(out_path, "w") as f:
        f.write("N\tterminal_type\tsteps_to_cycle\tcycle_length\tcycle_key\n")
        for n, ttype, steps, clen, ckey, _ in results:
            f.write(f"{n}\t{ttype}\t{steps}\t{clen}\t{ckey}\n")

    print()
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()
