#!/usr/bin/env python3
"""
Fetch Wikipedia edit history for basin-critical pages.

Uses MediaWiki API to retrieve revision history for pages that define
basin cycles and high-fanin nodes. This helps predict which basins
might be unstable if we compare to a future Wikipedia dump.

Usage:
    python fetch-edit-history.py [--pages PAGE1,PAGE2] [--top-cycles] [--days 90]

Examples:
    python fetch-edit-history.py --top-cycles --days 90
    python fetch-edit-history.py --pages "Massachusetts,Gulf_of_Maine,Philosophy"
"""

import argparse
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time


# Wikipedia API endpoint
API_URL = "https://en.wikipedia.org/w/api.php"

# Required by Wikipedia API policy
HEADERS = {
    "User-Agent": "NLinkBasinAnalysis/1.0 (https://github.com/user/nlink; research@example.com) requests/2.x"
}

# Basin cycle pages from stability analysis (highest impact)
CYCLE_PAGES = [
    # From Gulf_of_Maine__Massachusetts (1M+ pages in basin)
    "Massachusetts",
    "Gulf_of_Maine",
    # From Hill__Mountain (189K pages)
    "Hill",
    "Mountain",
    # From Sea_salt__Seawater (266K pages)
    "Sea_salt",
    "Seawater",
    # From Autumn__Summer (163K pages)
    "Autumn",
    "Summer",
    # From Animal__Kingdom_(biology) (113K pages)
    "Animal",
    "Kingdom_(biology)",
    # From Latvia__Lithuania (82K pages)
    "Latvia",
    "Lithuania",
    # From Civil_law__Precedent (56K pages)
    "Civil_law_(legal_system)",
    "Precedent",
    # From Thermosetting_polymer__Curing_(chemistry) (61K pages)
    "Thermosetting_polymer",
    "Curing_(chemistry)",
    # From American_Revolutionary_War__Eastern_United_States (44K pages)
    "American_Revolutionary_War",
    "Eastern_United_States",
]


def fetch_revisions(title: str, days: int = 90, limit: int = 50) -> dict:
    """
    Fetch recent revisions for a Wikipedia page.

    Args:
        title: Page title (with underscores or spaces)
        days: Look back this many days
        limit: Max revisions to fetch

    Returns:
        dict with page info and revisions
    """
    # Calculate date cutoff
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "action": "query",
        "format": "json",
        "titles": title.replace("_", " "),
        "prop": "revisions",
        "rvprop": "ids|timestamp|user|size|comment",
        "rvlimit": limit,
        "rvstart": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rvend": cutoff_str,
        "rvdir": "older",  # Newest first
    }

    try:
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                return {"title": title, "error": "Page not found", "revisions": []}
            return {
                "title": page_data.get("title", title),
                "pageid": int(page_id),
                "revisions": page_data.get("revisions", []),
            }
        return {"title": title, "error": "No data", "revisions": []}

    except Exception as e:
        return {"title": title, "error": str(e), "revisions": []}


def analyze_edit_pattern(revisions: list) -> dict:
    """
    Analyze edit patterns from revision list.

    Returns:
        dict with edit statistics
    """
    if not revisions:
        return {
            "edit_count": 0,
            "days_since_last_edit": None,
            "size_changes": [],
            "major_edits": 0,
        }

    # Parse timestamps
    timestamps = []
    size_changes = []
    prev_size = None

    for rev in revisions:
        ts = datetime.strptime(rev["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        timestamps.append(ts)

        size = rev.get("size", 0)
        if prev_size is not None:
            delta = size - prev_size
            size_changes.append({
                "timestamp": rev["timestamp"],
                "delta": delta,
                "user": rev.get("user", "unknown"),
                "comment": rev.get("comment", "")[:100],
            })
        prev_size = size

    # Calculate statistics
    now = datetime.now(timezone.utc)
    days_since_last = (now - timestamps[0].replace(tzinfo=timezone.utc)).days if timestamps else None

    # Major edits: size change > 500 bytes
    major_edits = [c for c in size_changes if abs(c["delta"]) > 500]

    return {
        "edit_count": len(revisions),
        "days_since_last_edit": days_since_last,
        "size_changes": size_changes[:10],  # Top 10
        "major_edits": len(major_edits),
        "largest_change": max((abs(c["delta"]) for c in size_changes), default=0),
    }


def format_report(results: list, days: int) -> str:
    """Format results as markdown report."""
    lines = [
        "# Wikipedia Edit History Analysis",
        "",
        f"**Analysis Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Lookback Period**: {days} days",
        f"**Pages Analyzed**: {len(results)}",
        "",
        "## Summary",
        "",
        "| Page | Edits | Days Since Last | Major Edits | Largest Δ |",
        "|------|-------|-----------------|-------------|-----------|",
    ]

    # Sort by edit count descending
    sorted_results = sorted(results, key=lambda x: x.get("stats", {}).get("edit_count", 0), reverse=True)

    for r in sorted_results:
        title = r.get("title", "Unknown")
        stats = r.get("stats", {})
        edits = stats.get("edit_count", 0)
        days_since = stats.get("days_since_last_edit")
        days_str = str(days_since) if days_since is not None else "N/A"
        major = stats.get("major_edits", 0)
        largest = stats.get("largest_change", 0)

        lines.append(f"| {title} | {edits} | {days_str} | {major} | {largest:+d} |")

    lines.extend([
        "",
        "## Stability Assessment",
        "",
    ])

    # Flag high-activity pages
    high_activity = [r for r in sorted_results if r.get("stats", {}).get("edit_count", 0) > 10]
    if high_activity:
        lines.append("### ⚠️ High Activity Pages (>10 edits)")
        lines.append("")
        for r in high_activity:
            title = r["title"]
            stats = r["stats"]
            lines.append(f"- **{title}**: {stats['edit_count']} edits, {stats['major_edits']} major")
        lines.append("")

    # Flag recently edited pages
    recent = [r for r in sorted_results
              if r.get("stats", {}).get("days_since_last_edit") is not None
              and r["stats"]["days_since_last_edit"] < 7]
    if recent:
        lines.append("### 🔄 Recently Edited (<7 days)")
        lines.append("")
        for r in recent:
            title = r["title"]
            days = r["stats"]["days_since_last_edit"]
            lines.append(f"- **{title}**: edited {days} days ago")
        lines.append("")

    # Stable pages
    stable = [r for r in sorted_results if r.get("stats", {}).get("edit_count", 0) == 0]
    if stable:
        lines.append(f"### ✅ Stable Pages (no edits in {days} days)")
        lines.append("")
        lines.append(", ".join(r["title"] for r in stable))
        lines.append("")

    lines.extend([
        "## Implications for Basin Stability",
        "",
        "Pages with high edit activity may cause basin reorganization if:",
        "1. The N-th link position changes (link inserted/deleted before position N)",
        "2. Link target changes (text replacement affects anchor)",
        "3. Paragraph restructuring moves links across positions",
        "",
        "**Recommendation**: Re-extract affected pages after major edits to track basin drift.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch Wikipedia edit history for basin-critical pages")
    parser.add_argument("--pages", type=str, help="Comma-separated page titles")
    parser.add_argument("--top-cycles", action="store_true", help="Analyze all tracked cycle pages")
    parser.add_argument("--days", type=int, default=90, help="Lookback period in days (default: 90)")
    parser.add_argument("--output", type=str, help="Output file path (markdown)")
    parser.add_argument("--json", type=str, help="Output raw JSON to file")
    args = parser.parse_args()

    # Determine pages to analyze
    if args.pages:
        pages = [p.strip() for p in args.pages.split(",")]
    elif args.top_cycles:
        pages = CYCLE_PAGES
    else:
        # Default: just the Massachusetts cycle
        pages = ["Massachusetts", "Gulf_of_Maine"]

    print(f"Fetching edit history for {len(pages)} pages (last {args.days} days)...")

    results = []
    for i, page in enumerate(pages):
        print(f"  [{i+1}/{len(pages)}] {page}...", end=" ", flush=True)
        data = fetch_revisions(page, days=args.days)
        stats = analyze_edit_pattern(data.get("revisions", []))
        data["stats"] = stats
        results.append(data)
        print(f"{stats['edit_count']} edits")
        time.sleep(0.5)  # Rate limiting

    # Generate report
    report = format_report(results, args.days)

    # Output
    if args.output:
        Path(args.output).write_text(report)
        print(f"\nReport written to {args.output}")
    else:
        print("\n" + report)

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2, default=str))
        print(f"Raw JSON written to {args.json}")

    return results


if __name__ == "__main__":
    main()
