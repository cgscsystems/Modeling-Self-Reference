#!/usr/bin/env python3
"""Batch generate basin pointcloud parquets for all available N×cycle combinations.

This script generates the 3D pointcloud data files needed by the Basin Geometry Viewer
(dash-basin-geometry-viewer.py) for all N values with available data.

Run (repo root)
--------------
  python n-link-analysis/scripts/batch-render-basin-pointclouds.py

Options:
  --dry-run     Show what would be generated without running
  --skip-n5     Skip N=5 (already generated)
  --n VALUE     Generate only for specific N value
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[2]
MULTIPLEX_PATH = REPO_ROOT / "data" / "wikipedia" / "processed" / "multiplex" / "multiplex_basin_assignments.parquet"
ANALYSIS_DIR = REPO_ROOT / "data" / "wikipedia" / "processed" / "analysis"
RENDER_SCRIPT = REPO_ROOT / "n-link-analysis" / "viz" / "render-full-basin-geometry.py"


def get_available_cycles() -> dict[int, list[tuple[str, str, int]]]:
    """Get available cycles from multiplex data, grouped by N value.

    Returns dict: N -> [(cycle_key, cycle_a_title, cycle_b_title, count), ...]
    """
    if not MULTIPLEX_PATH.exists():
        raise FileNotFoundError(f"Missing: {MULTIPLEX_PATH}")

    df = pq.read_table(MULTIPLEX_PATH).to_pandas()

    # Group by N and cycle_key
    summary = df.groupby(["N", "cycle_key"]).size().reset_index(name="count")

    result: dict[int, list[tuple[str, str, str, int]]] = {}
    for _, row in summary.iterrows():
        n = int(row["N"])
        cycle_key = str(row["cycle_key"])
        count = int(row["count"])

        # Parse cycle_key: "Massachusetts__Gulf_of_Maine" -> ("Massachusetts", "Gulf_of_Maine")
        # Handle tunneling suffix if present
        clean_key = cycle_key.replace("_tunneling", "")
        if "__" in clean_key:
            parts = clean_key.split("__", 1)
            cycle_a, cycle_b = parts[0], parts[1]
        else:
            cycle_a = clean_key
            cycle_b = clean_key  # Self-loop

        if n not in result:
            result[n] = []
        result[n].append((cycle_key, cycle_a, cycle_b, count))

    return result


def get_existing_pointclouds() -> set[tuple[int, str]]:
    """Get set of (N, cycle_slug) for existing pointcloud parquets."""
    existing = set()
    for f in ANALYSIS_DIR.glob("basin_pointcloud_n=*_cycle=*.parquet"):
        # Parse: basin_pointcloud_n=5_cycle=Massachusetts.parquet
        name = f.stem
        try:
            n_part = name.split("_n=")[1].split("_")[0]
            cycle_part = name.split("_cycle=")[1]
            existing.add((int(n_part), cycle_part))
        except (IndexError, ValueError):
            continue
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch generate basin pointcloud parquets")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--skip-n5", action="store_true", help="Skip N=5 (already complete)")
    parser.add_argument("--n", type=int, help="Generate only for specific N value")
    parser.add_argument("--max-nodes", type=int, default=0, help="Limit nodes per basin (0=no limit)")
    args = parser.parse_args()

    print("Loading available cycles from multiplex data...")
    cycles_by_n = get_available_cycles()
    existing = get_existing_pointclouds()

    print(f"Found data for N values: {sorted(cycles_by_n.keys())}")
    print(f"Existing pointclouds: {len(existing)}")
    print()

    # Build list of jobs to run
    jobs: list[tuple[int, str, str, int]] = []

    for n in sorted(cycles_by_n.keys()):
        if args.n is not None and n != args.n:
            continue
        if args.skip_n5 and n == 5:
            continue

        for cycle_key, cycle_a, cycle_b, count in cycles_by_n[n]:
            # Use cycle_a as the slug (first part of the cycle pair)
            cycle_slug = cycle_a

            if (n, cycle_slug) in existing:
                print(f"  [skip] N={n} {cycle_slug} (already exists)")
                continue

            jobs.append((n, cycle_a, cycle_b, count))

    if not jobs:
        print("No new pointclouds to generate!")
        return 0

    print(f"\nWill generate {len(jobs)} pointcloud(s):")
    for n, cycle_a, cycle_b, count in jobs:
        print(f"  N={n} {cycle_a} <-> {cycle_b} ({count:,} nodes)")

    if args.dry_run:
        print("\n[DRY RUN] No files generated.")
        return 0

    print("\n" + "=" * 60)

    failed = []
    for i, (n, cycle_a, cycle_b, count) in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] Generating N={n} {cycle_a}...")

        cmd = [
            sys.executable,
            str(RENDER_SCRIPT),
            "--n", str(n),
            "--cycle-title", cycle_a,
            "--cycle-title", cycle_b,
            "--max-depth", "0",  # Exhaustive
        ]

        if args.max_nodes > 0:
            cmd.extend(["--max-nodes", str(args.max_nodes)])

        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            print(f"  ✓ Complete")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed: {e}")
            failed.append((n, cycle_a))

    print("\n" + "=" * 60)
    print(f"Generated: {len(jobs) - len(failed)}/{len(jobs)}")

    if failed:
        print(f"Failed: {failed}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
