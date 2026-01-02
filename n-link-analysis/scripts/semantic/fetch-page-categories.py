#!/usr/bin/env python3
"""
Fetch Wikipedia categories for tunnel nodes to analyze semantic patterns.

Uses MediaWiki API to retrieve categories for pages, enabling semantic
analysis of what makes tunnel nodes special.

Usage:
    python fetch-page-categories.py --top 100 --output categories.json
"""

import argparse
import json
import requests
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
import time
from collections import Counter


API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "NLinkBasinAnalysis/1.0 (research project) requests/2.x"
}


def fetch_categories(titles: list, batch_size: int = 50) -> dict:
    """
    Fetch categories for multiple pages in batches.

    Args:
        titles: List of page titles
        batch_size: Number of pages per API call (max 50)

    Returns:
        dict mapping title -> list of categories
    """
    results = {}

    for i in range(0, len(titles), batch_size):
        batch = titles[i:i + batch_size]
        titles_param = "|".join(batch)

        params = {
            "action": "query",
            "format": "json",
            "titles": titles_param,
            "prop": "categories",
            "cllimit": "max",  # Get all categories
            "clshow": "!hidden",  # Exclude hidden categories
        }

        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    continue
                title = page_data.get("title", "")
                categories = page_data.get("categories", [])
                cat_names = [c["title"].replace("Category:", "") for c in categories]
                results[title] = cat_names

        except Exception as e:
            print(f"  Error fetching batch {i//batch_size + 1}: {e}")

        time.sleep(0.2)  # Rate limiting

    return results


def analyze_categories(cat_data: dict) -> dict:
    """
    Analyze category distribution.

    Returns:
        dict with category statistics
    """
    all_categories = []
    for title, cats in cat_data.items():
        all_categories.extend(cats)

    category_counts = Counter(all_categories)

    # Identify high-level semantic patterns
    semantic_patterns = {
        "geography": [],
        "biology": [],
        "history": [],
        "politics": [],
        "science": [],
        "culture": [],
        "people": [],
    }

    for cat, count in category_counts.most_common():
        cat_lower = cat.lower()
        if any(x in cat_lower for x in ["geography", "places", "cities", "counties", "states"]):
            semantic_patterns["geography"].append((cat, count))
        elif any(x in cat_lower for x in ["species", "genus", "family", "animals", "plants", "organisms"]):
            semantic_patterns["biology"].append((cat, count))
        elif any(x in cat_lower for x in ["history", "century", "wars", "battles"]):
            semantic_patterns["history"].append((cat, count))
        elif any(x in cat_lower for x in ["politics", "government", "elections", "politicians"]):
            semantic_patterns["politics"].append((cat, count))
        elif any(x in cat_lower for x in ["science", "physics", "chemistry", "mathematics"]):
            semantic_patterns["science"].append((cat, count))
        elif any(x in cat_lower for x in ["culture", "art", "music", "film", "literature"]):
            semantic_patterns["culture"].append((cat, count))
        elif any(x in cat_lower for x in ["people", "births", "deaths", "living"]):
            semantic_patterns["people"].append((cat, count))

    return {
        "total_pages": len(cat_data),
        "total_category_assignments": len(all_categories),
        "unique_categories": len(category_counts),
        "top_categories": category_counts.most_common(50),
        "semantic_patterns": {k: v[:10] for k, v in semantic_patterns.items()},
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Wikipedia categories for tunnel nodes")
    parser.add_argument("--top", type=int, default=100, help="Number of top tunnel nodes to analyze")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--sample", type=int, help="Random sample size instead of top N")
    args = parser.parse_args()

    # Load tunnel nodes with titles
    print("Loading tunnel node data...")
    tunnel_df = pd.read_csv("data/wikipedia/processed/multiplex/tunnel_frequency_ranking.tsv", sep="\t")
    pages = pq.read_table("data/wikipedia/processed/pages.parquet").to_pandas()
    tunnel_with_titles = tunnel_df.merge(pages[["page_id", "title"]], on="page_id", how="left")

    # Select nodes to analyze
    if args.sample:
        nodes = tunnel_with_titles.sample(n=min(args.sample, len(tunnel_with_titles)))
        print(f"Selected random sample of {len(nodes)} tunnel nodes")
    else:
        nodes = tunnel_with_titles.nlargest(args.top, "tunnel_score")
        print(f"Selected top {len(nodes)} tunnel nodes by score")

    titles = nodes["title"].dropna().tolist()
    print(f"Fetching categories for {len(titles)} pages...")

    # Fetch categories
    cat_data = fetch_categories(titles)
    print(f"Got categories for {len(cat_data)} pages")

    # Analyze
    analysis = analyze_categories(cat_data)

    # Display results
    print("\n=== CATEGORY ANALYSIS ===")
    print(f"Pages analyzed: {analysis['total_pages']}")
    print(f"Total category assignments: {analysis['total_category_assignments']}")
    print(f"Unique categories: {analysis['unique_categories']}")
    print(f"Avg categories per page: {analysis['total_category_assignments'] / max(1, analysis['total_pages']):.1f}")

    print("\n=== TOP 30 CATEGORIES ===")
    for cat, count in analysis["top_categories"][:30]:
        print(f"  {count:4d} | {cat}")

    print("\n=== SEMANTIC PATTERN SUMMARY ===")
    for pattern, cats in analysis["semantic_patterns"].items():
        if cats:
            total = sum(c[1] for c in cats)
            print(f"\n{pattern.upper()} ({total} total assignments):")
            for cat, count in cats[:5]:
                print(f"  {count:4d} | {cat}")

    # Save if requested
    if args.output:
        output_data = {
            "metadata": {
                "top_n": args.top if not args.sample else None,
                "sample_n": args.sample,
                "pages_analyzed": len(titles),
            },
            "category_data": cat_data,
            "analysis": analysis,
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(output_data, indent=2, default=str))
        print(f"\nResults saved to {args.output}")

    return analysis


if __name__ == "__main__":
    main()
