#!/usr/bin/env python3
"""
Organize analysis data files into consolidated directory structure.

Creates copies organized by three views:
- by-date: Temporal organization (when the analysis ran)
- by-type: Analysis type (basin-layers, branches, dashboards, etc.)
- by-n-value: N-link rule value (n=2 through n=10, plus cross-n)

Usage:
    python n-link-analysis/scripts/organize-consolidated-data.py [--dry-run]

The script is idempotent - running it multiple times only copies new files.
"""

import argparse
import re
import shutil
from pathlib import Path
from collections import defaultdict

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "data/wikipedia/processed/analysis"
CONSOLIDATED_DIR = PROJECT_ROOT / "data/wikipedia/processed/consolidated"

# Date tag patterns (checked in order)
DATE_PATTERNS = {
    r'bootstrap_2025-12-30': '2025-12-30',
    r'reproduction_2025-12-31': '2025-12-31',
    r'cross_n_2025_12_31': '2025-12-31',
    r'full_analysis_2025_12_31': '2025-12-31',
    r'reproduction_2026-01-01': '2026-01-01',
    r'harness_2026-01-01': '2026-01-01',
    r'single_cycle_2026-01-01': '2026-01-01',
    r'multi_n_jan_2026': '2026-01-01',
    r'test_n\d+_\w+': 'test-runs',
    r'mechanism_\w+': 'mechanism',
}

# Type patterns (order matters - more specific patterns first)
TYPE_PATTERNS = [
    (r'basin_n=\d+.*_layers\.tsv$', 'basin-layers'),
    (r'basin_pointcloud_', 'basin-layers'),
    (r'branches_.*_branches_all\.tsv$', 'branches'),
    (r'branches_.*_branches_topk\.tsv$', 'branches'),
    (r'branches_.*_assignments\.parquet$', 'branches'),
    (r'path_characteristics_', 'path-characteristics'),
    (r'sample_traces_', 'traces'),
    (r'trace_n=', 'traces'),
    (r'entry_breadth_', 'entry-breadth'),
    (r'depth_', 'depth-exploration'),
    (r'dashboard', 'dashboards'),
    (r'dominant_upstream_chain_', 'dashboards'),
    (r'dominance_collapse_', 'dashboards'),
    (r'universal_cycles', 'dashboards'),
    (r'cycle_', 'other'),
    (r'hyperstructure_', 'other'),
    (r'preimages_', 'other'),
    (r'phase_transition_', 'other'),
]

# N-value patterns
N_PATTERN = re.compile(r'_n=(\d+)_')
CROSS_N_PATTERN = re.compile(r'(cross_n|n3_to_n\d+|over_n)')


def get_date_category(filename: str) -> str:
    """Determine date category from filename."""
    for pattern, date in DATE_PATTERNS.items():
        if re.search(pattern, filename):
            return date
    return 'other'


def get_type_category(filename: str) -> str:
    """Determine type category from filename."""
    for pattern, category in TYPE_PATTERNS:
        if re.search(pattern, filename):
            return category
    return 'other'


def get_n_category(filename: str) -> str | None:
    """Determine N-value category from filename."""
    if CROSS_N_PATTERN.search(filename):
        return 'cross-n'
    match = N_PATTERN.search(filename)
    if match:
        return f'n={match.group(1)}'
    return None


def ensure_directories():
    """Create the consolidated directory structure if it doesn't exist."""
    # Date directories
    for date in set(DATE_PATTERNS.values()) | {'other'}:
        (CONSOLIDATED_DIR / "by-date" / date).mkdir(parents=True, exist_ok=True)

    # Type directories
    for _, type_cat in TYPE_PATTERNS:
        (CONSOLIDATED_DIR / "by-type" / type_cat).mkdir(parents=True, exist_ok=True)
    (CONSOLIDATED_DIR / "by-type" / "other").mkdir(parents=True, exist_ok=True)

    # N-value directories
    for n in range(2, 11):
        (CONSOLIDATED_DIR / "by-n-value" / f"n={n}").mkdir(parents=True, exist_ok=True)
    (CONSOLIDATED_DIR / "by-n-value" / "cross-n").mkdir(parents=True, exist_ok=True)


def organize_files(dry_run: bool = False) -> dict:
    """
    Main organization logic.

    Args:
        dry_run: If True, don't actually copy files, just report what would happen.

    Returns:
        Dictionary of statistics about files processed.
    """
    stats = defaultdict(int)

    if not ANALYSIS_DIR.exists():
        print(f"ERROR: Analysis directory not found: {ANALYSIS_DIR}")
        return stats

    # Process TSV and parquet files
    for pattern in ["*.tsv", "*.parquet"]:
        for f in ANALYSIS_DIR.glob(pattern):
            filename = f.name
            is_parquet = filename.endswith('.parquet')
            suffix = '-parquet' if is_parquet else ''

            # Get categories
            date_cat = get_date_category(filename)
            type_cat = get_type_category(filename)
            n_cat = get_n_category(filename)

            # Copy to by-date
            date_dest = CONSOLIDATED_DIR / "by-date" / date_cat / filename
            if not date_dest.exists():
                if not dry_run:
                    shutil.copy2(f, date_dest)
                stats[f'by-date{suffix}'] += 1

            # Copy to by-type
            type_dest = CONSOLIDATED_DIR / "by-type" / type_cat / filename
            if not type_dest.exists():
                if not dry_run:
                    shutil.copy2(f, type_dest)
                stats[f'by-type{suffix}'] += 1

            # Copy to by-n-value (if applicable)
            if n_cat:
                n_dest = CONSOLIDATED_DIR / "by-n-value" / n_cat / filename
                if not n_dest.exists():
                    if not dry_run:
                        shutil.copy2(f, n_dest)
                    stats[f'by-n-value{suffix}'] += 1

    return stats


def print_summary():
    """Print organization summary."""
    print("\n=== Consolidated Directory Summary ===\n")

    for view in ['by-date', 'by-type', 'by-n-value']:
        view_path = CONSOLIDATED_DIR / view
        if not view_path.exists():
            continue
        print(f"\n{view}/")
        for subdir in sorted(view_path.iterdir()):
            if subdir.is_dir():
                count = len(list(subdir.glob("*")))
                if count > 0:
                    print(f"  {subdir.name}: {count} files")


def main():
    parser = argparse.ArgumentParser(
        description="Organize analysis data files into consolidated directory structure."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't copy files, just show what would be done"
    )
    args = parser.parse_args()

    print(f"Analysis directory: {ANALYSIS_DIR}")
    print(f"Consolidated directory: {CONSOLIDATED_DIR}")

    if args.dry_run:
        print("\n[DRY RUN - no files will be copied]\n")

    print("Ensuring directory structure...")
    if not args.dry_run:
        ensure_directories()

    print("Organizing analysis files...")
    stats = organize_files(dry_run=args.dry_run)

    if stats:
        action = "Would copy" if args.dry_run else "Files copied"
        print(f"\n{action}:")
        for key, count in sorted(stats.items()):
            print(f"  {key}: {count}")
    else:
        print("\nNo new files to organize.")

    if not args.dry_run:
        print_summary()


if __name__ == "__main__":
    main()
