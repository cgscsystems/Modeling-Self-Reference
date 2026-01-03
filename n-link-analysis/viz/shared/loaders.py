"""Cached data loading utilities for visualization tools.

Provides centralized, cached data loading functions for common data files
used across multiple dashboards. Uses functools.lru_cache for in-memory
caching to avoid redundant file I/O.

Common Data Files:
    - multiplex_basin_assignments.parquet: Page-level basin assignments across N values
    - basin_flows.tsv: Cross-basin page flow data
    - tunnel_frequency_ranking.tsv: Ranked tunnel nodes with scores
    - basin_stability_scores.tsv: Per-basin stability metrics
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

# Resolve paths relative to this file
# Path: shared/loaders.py -> viz/ -> n-link-analysis/ -> REPO_ROOT
REPO_ROOT = Path(__file__).resolve().parents[3]
MULTIPLEX_DIR = REPO_ROOT / "data" / "wikipedia" / "processed" / "multiplex"
ANALYSIS_DIR = REPO_ROOT / "data" / "wikipedia" / "processed" / "analysis"


def load_tsv_safe(path: Path) -> pd.DataFrame:
    """Load TSV file with error handling.

    Args:
        path: Path to TSV file

    Returns:
        DataFrame with file contents, or empty DataFrame if file doesn't exist
        or cannot be read.
    """
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, sep="\t")
    except Exception:
        return pd.DataFrame()


def load_parquet_safe(path: Path) -> pd.DataFrame:
    """Load Parquet file with error handling.

    Args:
        path: Path to Parquet file

    Returns:
        DataFrame with file contents, or empty DataFrame if file doesn't exist
        or cannot be read.
    """
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def load_json_safe(path: Path) -> dict[str, Any]:
    """Load JSON file with error handling.

    Args:
        path: Path to JSON file

    Returns:
        Dict with file contents, or empty dict if file doesn't exist
        or cannot be read.
    """
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


@lru_cache(maxsize=1)
def load_basin_assignments(data_dir: Path | None = None) -> pd.DataFrame:
    """Load multiplex basin assignments parquet.

    This is the primary data file containing page-level basin assignments
    across all N values (3-10). Each row represents one page's assignment
    at one N value.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: page_id, N, cycle_key, depth, etc.
    """
    path = (data_dir or MULTIPLEX_DIR) / "multiplex_basin_assignments.parquet"
    return load_parquet_safe(path)


@lru_cache(maxsize=1)
def load_basin_flows(data_dir: Path | None = None) -> pd.DataFrame:
    """Load basin flows TSV.

    Contains cross-basin page flow data showing how pages move between
    basins as N changes.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: from_basin, to_basin, from_n, to_n, count
    """
    path = (data_dir or MULTIPLEX_DIR) / "basin_flows.tsv"
    return load_tsv_safe(path)


@lru_cache(maxsize=1)
def load_tunnel_ranking(data_dir: Path | None = None) -> pd.DataFrame:
    """Load tunnel frequency ranking TSV.

    Contains ranked list of tunnel nodes with scores, basin bridging info,
    and transition counts.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: page_id, page_title, tunnel_score, tunnel_type,
        n_basins_bridged, n_transitions, mean_depth, basin_list, stable_ranges
    """
    path = (data_dir or MULTIPLEX_DIR) / "tunnel_frequency_ranking.tsv"
    df = load_tsv_safe(path)
    if not df.empty and "page_title" in df.columns:
        # Fill NaN page titles with page_id
        df["page_title"] = df["page_title"].fillna(df["page_id"].astype(str))
    return df


@lru_cache(maxsize=1)
def load_basin_stability(data_dir: Path | None = None) -> pd.DataFrame:
    """Load basin stability scores TSV.

    Contains per-basin stability metrics computed from cross-N analysis.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: canonical_cycle_id, persistence_score,
        stability_class, total_pages, etc.
    """
    path = (data_dir or MULTIPLEX_DIR) / "basin_stability_scores.tsv"
    return load_tsv_safe(path)


@lru_cache(maxsize=1)
def load_tunnel_mechanisms(data_dir: Path | None = None) -> pd.DataFrame:
    """Load tunnel mechanism summary TSV.

    Contains aggregated tunnel mechanism counts (degree_shift vs boundary_shift).

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: mechanism, count
    """
    path = (data_dir or MULTIPLEX_DIR) / "tunnel_mechanism_summary.tsv"
    return load_tsv_safe(path)


@lru_cache(maxsize=1)
def load_validation_metrics(data_dir: Path | None = None) -> pd.DataFrame:
    """Load tunneling validation metrics TSV.

    Contains hypothesis validation results from tunneling analysis.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: hypothesis, expected, observed, statistic,
        p_value, result
    """
    path = (data_dir or MULTIPLEX_DIR) / "tunneling_validation_metrics.tsv"
    return load_tsv_safe(path)


@lru_cache(maxsize=1)
def load_semantic_model(data_dir: Path | None = None) -> dict[str, Any]:
    """Load semantic model JSON.

    Contains high-level summary statistics and semantic model information.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        Dict with keys: summary, basins, etc.
    """
    path = (data_dir or MULTIPLEX_DIR) / "semantic_model_wikipedia.json"
    return load_json_safe(path)


@lru_cache(maxsize=1)
def load_layer_connectivity(data_dir: Path | None = None) -> pd.DataFrame:
    """Load multiplex layer connectivity TSV.

    Contains N×N layer edge count matrix.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: src_N, dst_N, edge_count
    """
    path = (data_dir or MULTIPLEX_DIR) / "multiplex_layer_connectivity.tsv"
    return load_tsv_safe(path)


@lru_cache(maxsize=1)
def load_tunnel_classification(data_dir: Path | None = None) -> pd.DataFrame:
    """Load tunnel node classification TSV.

    Contains detailed classification of tunnel nodes by type and basin pair.

    Args:
        data_dir: Optional directory override. Defaults to MULTIPLEX_DIR.

    Returns:
        DataFrame with columns: page_id, tunnel_type, basin_pair, etc.
    """
    path = (data_dir or MULTIPLEX_DIR) / "tunnel_classification.tsv"
    return load_tsv_safe(path)


def clear_cache() -> None:
    """Clear all cached data loaders.

    Useful when underlying files have changed and need to be reloaded.
    """
    load_basin_assignments.cache_clear()
    load_basin_flows.cache_clear()
    load_tunnel_ranking.cache_clear()
    load_basin_stability.cache_clear()
    load_tunnel_mechanisms.cache_clear()
    load_validation_metrics.cache_clear()
    load_semantic_model.cache_clear()
    load_layer_connectivity.cache_clear()
    load_tunnel_classification.cache_clear()
