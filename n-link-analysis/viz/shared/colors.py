"""Basin color schemes and display name mappings.

Provides consistent color schemes and short names for basin visualization
across all dashboard tools. Colors are chosen to be colorblind-friendly
and visually distinct.
"""

from __future__ import annotations

import pandas as pd

# Basin color scheme (consistent across all visualizations)
BASIN_COLORS: dict[str, str] = {
    "Gulf_of_Maine__Massachusetts": "#1f77b4",
    "Sea_salt__Seawater": "#2ca02c",
    "Autumn__Summer": "#ff7f0e",
    "Hill__Mountain": "#8c564b",
    "Animal__Kingdom_(biology)": "#9467bd",
    "American_Revolutionary_War__Eastern_United_States": "#d62728",
    "Latvia__Lithuania": "#17becf",
    "Civil_law__Precedent": "#bcbd22",
    "Curing_(chemistry)__Thermosetting_polymer": "#e377c2",
}

# Short display names for UI (space-constrained contexts)
BASIN_SHORT_NAMES: dict[str, str] = {
    "Gulf_of_Maine__Massachusetts": "Gulf of Maine",
    "Sea_salt__Seawater": "Sea Salt",
    "Autumn__Summer": "Autumn",
    "Hill__Mountain": "Hill/Mountain",
    "Animal__Kingdom_(biology)": "Animal Kingdom",
    "American_Revolutionary_War__Eastern_United_States": "Am. Revolution",
    "Latvia__Lithuania": "Latvia/Lithuania",
    "Civil_law__Precedent": "Civil Law",
    "Curing_(chemistry)__Thermosetting_polymer": "Curing/Polymer",
}

# Default colors for unknown basins and special states
DEFAULT_BASIN_COLOR = "#7f7f7f"  # Gray for unknown basins
MISSING_DATA_COLOR = "#cccccc"  # Light gray for missing/N/A


def get_basin_color(basin: str) -> str:
    """Get color for a basin, with fallback to gray for unknown basins.

    Args:
        basin: Basin identifier (cycle_key format, e.g., "Gulf_of_Maine__Massachusetts")

    Returns:
        Hex color string. Returns MISSING_DATA_COLOR for empty/NaN values,
        DEFAULT_BASIN_COLOR for unknown basins, or the mapped color if found.

    Examples:
        >>> get_basin_color("Gulf_of_Maine__Massachusetts")
        '#1f77b4'
        >>> get_basin_color("Unknown_Basin")
        '#7f7f7f'
        >>> get_basin_color("")
        '#cccccc'
    """
    # Handle empty/NaN values
    if pd.isna(basin) or basin == "":
        return MISSING_DATA_COLOR

    # Direct lookup first
    if basin in BASIN_COLORS:
        return BASIN_COLORS[basin]

    # Fuzzy match: check if basin contains or is contained by known keys
    for key, color in BASIN_COLORS.items():
        if key in basin or basin in key:
            return color

    return DEFAULT_BASIN_COLOR


def get_short_name(basin: str) -> str:
    """Get display-friendly short name for a basin.

    Args:
        basin: Basin identifier (cycle_key format)

    Returns:
        Short display name. Returns "N/A" for empty values, the mapped short
        name if found, or a truncated version of the first part of the basin key.

    Examples:
        >>> get_short_name("Gulf_of_Maine__Massachusetts")
        'Gulf of Maine'
        >>> get_short_name("Unknown_Basin__Other")
        'Unknown_Basin'
        >>> get_short_name("")
        'N/A'
    """
    # Handle empty/NaN values
    if pd.isna(basin) or basin == "":
        return "N/A"

    # Direct lookup first
    if basin in BASIN_SHORT_NAMES:
        return BASIN_SHORT_NAMES[basin]

    # Fuzzy match: check if basin contains or is contained by known keys
    for key, name in BASIN_SHORT_NAMES.items():
        if key in basin or basin in key:
            return name

    # Fallback: extract first part of cycle key, truncated
    if "__" in basin:
        return basin.split("__")[0][:15]
    return basin[:15]


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to RGBA string for Plotly.

    Args:
        hex_color: Hex color string (e.g., "#1f77b4")
        alpha: Opacity value (0.0 to 1.0)

    Returns:
        RGBA color string (e.g., "rgba(31, 119, 180, 0.5)")
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"
