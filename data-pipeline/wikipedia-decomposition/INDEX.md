# Wikipedia Decomposition Pipeline Index

**Purpose**: Design documents and scripts for Wikipedia parsing and link graph extraction  
**Last Updated**: 2025-12-29

---

## Core Files (Load when entering directory)

| File | Tier | Purpose | Tokens |
|------|------|---------|--------|
| [implementation-guide.md](implementation-guide.md) | 2 | Pipeline architecture and design | ~5k |

**Load these when**: Working on Wikipedia data extraction pipeline

---

## Reference Files (Available as-needed)

| File | Tier | Purpose | Tokens |
|------|------|---------|--------|
| [data-sources.md](data-sources.md) | 3 | Wikipedia/MediaWiki technical resources | ~3k |

**Load these when**: Adding new data sources or citing Wikipedia technical details (historical reproducibility)

---

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| [scripts/parse-sql-to-parquet.py](scripts/parse-sql-to-parquet.py) | Parse SQL dumps → pages, redirects, disambig parquet | ✅ Complete |
| [scripts/parse-xml-links.py](scripts/parse-xml-links.py) | Extract wikilinks from XML → links parquet | ✅ Complete |
| [scripts/resolve-links.py](scripts/resolve-links.py) | Resolve link titles to page IDs | ✅ Complete |
| [scripts/quick-stats.py](scripts/quick-stats.py) | DuckDB queries for data verification | ✅ Complete |

---

## Output Files

All in `data/wikipedia/processed/` (gitignored):

| File | Rows | Size | Description |
|------|------|------|-------------|
| `pages.parquet` | 64.7M | 985 MB | All pages with namespace, redirect flag |
| `redirects.parquet` | 15.0M | 189 MB | Redirect mappings (from_id → to_title) |
| `disambig_pages.parquet` | 376K | 1.8 MB | Disambiguation page IDs |
| `links.parquet` | 353.4M | 2.84 GB | Raw links (from_id → to_title) |
| `links_resolved.parquet` | 237.6M | 1.39 GB | Resolved edges (from_id → to_id) |

**Total processed data**: ~5.4 GB

---

## Status

- **Phase**: Complete
- **Implementation**: All extraction scripts complete
- **Dump Date**: 2025-12-20
- **Dependencies**: Python 3.13, pyarrow 22.0.0, duckdb 1.4.3

---

## Usage

**First time in wikipedia-decomposition/**: Load implementation-guide.md for complete pipeline context

**Working on specific tasks**:
- Re-running extraction → Use scripts in order: parse-sql → parse-xml-links → resolve-links
- Adding data sources → Update data-sources.md
- Querying data → Use DuckDB on parquet files directly

---
