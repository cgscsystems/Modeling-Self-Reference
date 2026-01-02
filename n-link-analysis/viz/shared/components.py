"""Reusable Dash UI components.

Provides factory functions for common UI patterns used across multiple
dashboards, ensuring consistent styling and behavior.
"""

from __future__ import annotations

try:
    import dash_bootstrap_components as dbc
    from dash import html
except ImportError:
    raise ImportError(
        "dash and dash-bootstrap-components required. "
        "Install with: pip install dash dash-bootstrap-components"
    )


def metric_card(
    value: str,
    label: str,
    color: str = "#1f77b4",
    text_color: str | None = None,
) -> dbc.Card:
    """Create a metric display card.

    A card component showing a large value with a descriptive label below,
    commonly used for KPI displays in dashboard headers.

    Args:
        value: The metric value to display (formatted string)
        label: Descriptive label below the value
        color: Color for the value text (hex string)
        text_color: Optional text color class (e.g., "text-primary").
                   If provided, overrides color parameter.

    Returns:
        dbc.Card component ready for use in layout

    Example:
        >>> metric_card("1,234", "Total Pages", color="#1f77b4")
        >>> metric_card("99.3%", "Tunnel Rate", text_color="text-success")
    """
    value_style = {"color": color} if not text_color else {}
    value_class = f"card-title text-center {text_color}" if text_color else "card-title text-center"

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(value, className=value_class, style=value_style),
                    html.P(label, className="card-text text-center text-muted"),
                ]
            )
        ],
        className="mb-3",
    )


def filter_row(*children) -> dbc.Row:
    """Create a row of filter controls with consistent spacing.

    Wraps each child in a column with auto-width sizing, aligned at bottom
    for consistent input alignment.

    Args:
        *children: Filter control components (dropdowns, sliders, etc.)

    Returns:
        dbc.Row containing the filter controls

    Example:
        >>> filter_row(
        ...     dcc.Dropdown(id="type-filter", ...),
        ...     dcc.Slider(id="score-filter", ...),
        ... )
    """
    cols = [dbc.Col(child, width="auto") for child in children]
    return dbc.Row(cols, className="mb-3 align-items-end")


def badge(
    text: str,
    color: str = "primary",
    pill: bool = False,
) -> dbc.Badge:
    """Create a styled badge.

    Args:
        text: Badge text content
        color: Bootstrap color name (primary, secondary, success, danger, etc.)
        pill: If True, creates a pill-shaped badge

    Returns:
        dbc.Badge component

    Example:
        >>> badge("API Mode", color="success")
        >>> badge("41,234 nodes", color="secondary", pill=True)
    """
    return dbc.Badge(text, color=color, pill=pill, className="me-1")


def info_card(title: str, content: list | str) -> dbc.Card:
    """Create an information card with header.

    Args:
        title: Card header text
        content: Card body content (string or list of html elements)

    Returns:
        dbc.Card component with header and body

    Example:
        >>> info_card("Key Insights", [
        ...     html.Li("99.3% of tunneling is caused by degree_shift"),
        ...     html.Li("N=5 is the critical phase transition point"),
        ... ])
    """
    body_content = content if isinstance(content, list) else [html.P(content)]

    return dbc.Card(
        [
            dbc.CardHeader(title),
            dbc.CardBody(body_content),
        ]
    )


def stability_indicator(stability_class: str) -> html.Span:
    """Create a colored stability indicator.

    Args:
        stability_class: One of "stable", "moderate", "fragile", or "unknown"

    Returns:
        html.Span with colored square and text

    Example:
        >>> stability_indicator("stable")  # Green indicator
    """
    colors = {
        "stable": "#2ca02c",
        "moderate": "#ff7f0e",
        "fragile": "#d62728",
        "unknown": "#7f7f7f",
    }

    color = colors.get(stability_class.lower(), colors["unknown"])

    return html.Span(
        [
            html.Span(
                "\u25a0 ",  # Black square character
                style={"color": color, "fontSize": "16px"},
            ),
            html.Strong(stability_class.title()),
        ]
    )


def tunnel_type_badge(tunnel_type: str) -> dbc.Badge:
    """Create a badge for tunnel type.

    Args:
        tunnel_type: Either "progressive" or "alternating"

    Returns:
        Colored badge indicating tunnel type
    """
    color_map = {
        "progressive": "success",
        "alternating": "warning",
    }
    return dbc.Badge(
        tunnel_type.title(),
        color=color_map.get(tunnel_type.lower(), "secondary"),
        className="me-1",
    )


def loading_wrapper(component_id: str, children) -> dbc.Spinner:
    """Wrap a component with a loading spinner.

    Args:
        component_id: ID of the loading component
        children: Component(s) to wrap

    Returns:
        dbc.Spinner component containing the children
    """
    return dbc.Spinner(
        children,
        id=f"{component_id}-spinner",
        color="primary",
        type="border",
        size="sm",
    )
