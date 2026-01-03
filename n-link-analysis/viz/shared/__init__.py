"""Shared visualization components for N-Link Analysis dashboards.

This module provides reusable components extracted from multiple dashboards
to reduce duplication and ensure consistency.

Modules:
    colors: Basin color schemes and display name mappings
    loaders: Cached data loading utilities
    components: Reusable Dash UI component factories
"""

from .colors import (
    BASIN_COLORS,
    BASIN_SHORT_NAMES,
    get_basin_color,
    get_short_name,
    hex_to_rgba,
)

from .loaders import (
    load_basin_assignments,
    load_basin_flows,
    load_tunnel_ranking,
    load_tsv_safe,
    MULTIPLEX_DIR,
    REPO_ROOT,
)

from .components import (
    metric_card,
    filter_row,
    badge,
    info_card,
)

__all__ = [
    # colors
    "BASIN_COLORS",
    "BASIN_SHORT_NAMES",
    "get_basin_color",
    "get_short_name",
    "hex_to_rgba",
    # loaders
    "load_basin_assignments",
    "load_basin_flows",
    "load_tunnel_ranking",
    "load_tsv_safe",
    "MULTIPLEX_DIR",
    "REPO_ROOT",
    # components
    "metric_card",
    "filter_row",
    "badge",
    "info_card",
]
