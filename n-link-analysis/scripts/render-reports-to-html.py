#!/usr/bin/env python3
"""Convert markdown reports to styled HTML for the Docker gallery.

Converts core research reports from Markdown to self-contained HTML files
with styling that matches the gallery.html aesthetic.

Outputs are placed in n-link-analysis/report/assets/ for serving via Docker.

Usage:
    python n-link-analysis/scripts/render-reports-to-html.py
    python n-link-analysis/scripts/render-reports-to-html.py --dry-run
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import NamedTuple


class ReportConfig(NamedTuple):
    """Configuration for a report to convert."""
    source: str  # Source markdown filename
    output: str  # Output HTML filename
    title: str   # Page title


REPORTS = [
    ReportConfig(
        source="overview.md",
        output="overview.html",
        title="N=5 Basin Structure Overview",
    ),
    ReportConfig(
        source="MULTI-N-ANALYSIS-REPORT.md",
        output="multi-n-analysis.html",
        title="Multi-N Analysis Report (N=3-10)",
    ),
    ReportConfig(
        source="TUNNELING-FINDINGS.md",
        output="tunneling-findings.html",
        title="Tunneling Analysis Findings",
    ),
    ReportConfig(
        source="EDIT-HISTORY-ANALYSIS.md",
        output="edit-history.html",
        title="Wikipedia Edit History Analysis",
    ),
]


# CSS matching gallery.html aesthetic
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        header p {{
            font-size: 1rem;
            opacity: 0.9;
        }}

        .nav-link {{
            color: white;
            text-decoration: none;
            opacity: 0.9;
            font-size: 0.9rem;
        }}

        .nav-link:hover {{
            opacity: 1;
            text-decoration: underline;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .content {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        h1 {{ font-size: 1.8rem; }}
        h2 {{ font-size: 1.5rem; border-bottom: 2px solid #667eea; padding-bottom: 0.3rem; }}
        h3 {{ font-size: 1.25rem; }}
        h4 {{ font-size: 1.1rem; }}

        p {{
            margin-bottom: 1rem;
        }}

        a {{
            color: #667eea;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        ul, ol {{
            margin-bottom: 1rem;
            padding-left: 2rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.95rem;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }}

        th {{
            background: #667eea;
            color: white;
            font-weight: 500;
        }}

        tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        tr:hover {{
            background: #f0f0f0;
        }}

        code {{
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 0.9em;
        }}

        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1rem 0;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin: 1rem 0;
        }}

        blockquote {{
            border-left: 4px solid #667eea;
            margin: 1rem 0;
            padding-left: 1rem;
            color: #666;
            font-style: italic;
        }}

        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 2rem 0;
        }}

        .badge {{
            display: inline-block;
            background: #e8f4f8;
            color: #2980b9;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .content {{
                padding: 1rem;
            }}

            header h1 {{
                font-size: 1.5rem;
            }}

            table {{
                font-size: 0.85rem;
            }}

            th, td {{
                padding: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <p><a href="gallery.html" class="nav-link">Back to Gallery</a></p>
        <h1>{title}</h1>
        <p>N-Link Basin Analysis Project</p>
    </header>

    <div class="container">
        <div class="content">
{body}
        </div>
    </div>

    <footer>
        <p>Part of the Self-Reference Modeling Project</p>
        <p><a href="gallery.html">Return to Gallery</a></p>
    </footer>
</body>
</html>
"""


def markdown_to_html(text: str) -> str:
    """Convert markdown to HTML.

    Handles: headers, bold, italic, code, links, images, tables, lists, blockquotes.
    """
    lines = text.split("\n")
    result = []
    in_code_block = False
    in_table = False
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                result.append("</code></pre>")
                in_code_block = False
            else:
                lang = line.strip()[3:].strip()
                result.append(f"<pre><code>")
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            result.append(html.escape(line))
            i += 1
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                result.append("<table>")
                in_table = True

            # Check if this is a separator line
            if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
                i += 1
                continue

            cells = [c.strip() for c in line.strip().split("|")[1:-1]]

            # First row after table start is header
            if result[-1] == "<table>":
                result.append("<thead><tr>")
                for cell in cells:
                    result.append(f"<th>{inline_markdown(cell)}</th>")
                result.append("</tr></thead><tbody>")
            else:
                result.append("<tr>")
                for cell in cells:
                    result.append(f"<td>{inline_markdown(cell)}</td>")
                result.append("</tr>")
            i += 1
            continue
        elif in_table:
            result.append("</tbody></table>")
            in_table = False

        # Lists
        ul_match = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        ol_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

        if ul_match or ol_match:
            if ul_match:
                content = ul_match.group(2)
                new_list_type = "ul"
            else:
                content = ol_match.group(2)
                new_list_type = "ol"

            if not in_list:
                result.append(f"<{new_list_type}>")
                in_list = True
                list_type = new_list_type

            result.append(f"<li>{inline_markdown(content)}</li>")
            i += 1
            continue
        elif in_list:
            result.append(f"</{list_type}>")
            in_list = False
            list_type = None

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^[\-*_]{3,}$", line.strip()):
            result.append("<hr>")
            i += 1
            continue

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            result.append(f"<h{level}>{inline_markdown(content)}</h{level}>")
            i += 1
            continue

        # Blockquotes
        if line.strip().startswith(">"):
            content = line.strip()[1:].strip()
            result.append(f"<blockquote>{inline_markdown(content)}</blockquote>")
            i += 1
            continue

        # Regular paragraph
        result.append(f"<p>{inline_markdown(line)}</p>")
        i += 1

    # Close any open elements
    if in_code_block:
        result.append("</code></pre>")
    if in_table:
        result.append("</tbody></table>")
    if in_list:
        result.append(f"</{list_type}>")

    return "\n".join(result)


def inline_markdown(text: str) -> str:
    """Convert inline markdown elements."""
    # Images - fix relative paths (assets/ -> current dir since we're in assets/)
    text = re.sub(
        r"!\[([^\]]*)\]\(assets/([^)]+)\)",
        r'<img src="\2" alt="\1">',
        text
    )
    # Images with other paths
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1">',
        text
    )

    # Links - fix relative paths
    text = re.sub(
        r"\[([^\]]+)\]\(assets/([^)]+)\)",
        r'<a href="\2">\1</a>',
        text
    )
    # Other links
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text
    )

    # Bold and italic
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    return text


def convert_report(config: ReportConfig, report_dir: Path, assets_dir: Path, dry_run: bool = False) -> bool:
    """Convert a single report from markdown to HTML."""
    source_path = report_dir / config.source
    output_path = assets_dir / config.output

    if not source_path.exists():
        print(f"  Source not found: {source_path}")
        return False

    content = source_path.read_text(encoding="utf-8")

    # Convert markdown to HTML
    body_html = markdown_to_html(content)

    # Apply template
    full_html = HTML_TEMPLATE.format(
        title=config.title,
        body=body_html,
    )

    if dry_run:
        print(f"  Would write: {output_path}")
        print(f"    Size: {len(full_html):,} bytes")
    else:
        output_path.write_text(full_html, encoding="utf-8")
        print(f"  Written: {output_path}")
        print(f"    Size: {len(full_html):,} bytes")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report_dir = repo_root / "n-link-analysis" / "report"
    assets_dir = report_dir / "assets"

    print(f"Report directory: {report_dir}")
    print(f"Assets directory: {assets_dir}")
    print()

    success_count = 0
    for config in REPORTS:
        print(f"Converting: {config.source} -> {config.output}")
        if convert_report(config, report_dir, assets_dir, args.dry_run):
            success_count += 1
        print()

    print(f"Converted {success_count}/{len(REPORTS)} reports")

    if not args.dry_run:
        print("\nReports are now available in the Docker gallery at http://localhost:8070/")

    return 0 if success_count == len(REPORTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
