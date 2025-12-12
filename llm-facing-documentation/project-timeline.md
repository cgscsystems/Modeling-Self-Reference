# Project Timeline

**Document Type**: Cumulative history  
**Target Audience**: LLMs  
**Purpose**: Chronological record of project evolution, decisions, and discoveries  
**Last Updated**: 2025-12-12  
**Status**: Active (append-only)

---

## How to Use This Document

**For LLMs**: Read the latest 3-5 entries to understand current project state. Scroll to relevant dates when investigating specific decisions.

**Update Policy**: Append new entries at top (reverse chronological order). Never delete entries.

---

## Timeline Entries

### Session: 2025-12-12 (Evening) - Tier 1 Documentation Token Budget Optimization

**Completed**:
- Created `meta-maintenance/writing-guide.md` (~2,324 tokens)
  - Extracted detailed examples from documentation-standards.md
  - Complete formatting patterns with good/bad examples
  - Research foundation (OpenAI, Anthropic, arXiv paper - all 26 principles)
  - Copy-paste ready templates (metadata blocks, docstrings, procedures)
  
- Created `meta-maintenance/data-sources.md` (~690 tokens)
  - External research links with annotations
  - Wikipedia/MediaWiki technical resources
  - Discovery dates and application notes
  
- Compressed `documentation-standards.md` (20k+ → ~960 tokens)
  - Reduced to core 10 Golden Rules + quick-reference tables
  - Added bootstrap instructions for new LLM sessions
  - All detailed content moved to writing-guide.md with pointers
  
- Compressed `project-management-practices.md` (8-10k → ~960 tokens)
  - Tier system quick reference table
  - "How to start new session" bootstrap instructions
  - "Creating new directory" copy-paste template
  - Removed redundant content (implementation.md covers architecture)

**Decisions Made**:
- **Token Budget Strategy**: Aggressive compression with just-in-time loading
  - Rationale: Tier 1 should be <12k tokens total; was ~30k (2.5x over budget)
  - Achieved: ~2,370 tokens (80% savings, 5x under budget)
  
- **Restructure Approach**: Extract to Tier 2, not delete
  - Rationale: Preserve granular content for when creating new documentation
  - Pattern: Brief + pointer in Tier 1 → Details in Tier 2
  
- **Bootstrap Path**: Explicit navigation instructions in Tier 1
  - Rationale: Blank-slate LLM must be able to navigate from cold start
  - Implementation: Step-by-step "Starting a New Session" section

**Discoveries**:
- **Recursive Realization**: Documentation system's own docs violated its principles
  - Original Tier 1 docs written before architecture finalized
  - System needed to "self-heal" by applying its own rules to itself
  
- **Just-In-Time Loading Pattern**: Tier 2 details loaded only when needed
  - Don't load writing-guide.md every session
  - Load it only when creating new documentation
  - Matches human behavior: Check style guide when writing, not when reading

**Validation**:
- Tier 1 token count: 2,370 / 12,000 budget ✓
- Bootstrap path tested mentally: Clear Tier 1 → Tier 2 navigation
- Cross-references validated (documentation-standards.md ↔ writing-guide.md)
- Self-referential integrity maintained (system documents itself correctly)

**Architecture Impact**:
- Tier 1 now truly universal: Core rules + templates only
- Tier 2 now contains granular implementation: Detailed examples + research
- System achieves stated goal: "Just enough context to bootstrap"

**Git Commit**: `2811316` - "Optimize Tier 1 documentation token budget"

**Next Steps**:
- Test bootstrap path with actual new session (verify Tier 1 sufficient)
- Begin Wikipedia extraction implementation with new documentation patterns
- Consider: Are theory documents in theories-proofs-conjectures/ also Tier 1? (May need review)

---

### Session: 2025-12-12 - Project Initialization & Documentation Framework

**Completed**:
- Initialized git repository at `c:\Coding\Self Reference Modeling`
- Created `.gitignore` excluding Python artifacts and large Wikipedia data files
- Set up Python virtual environment (3.13.9)
- Installed core dependencies: pandas, numpy, lxml, regex, pytest, black, jupyter
- Created VSCode workspace configuration with Python/Jupyter support
- Created `documentation-standards.md` - Comprehensive LLM-facing documentation guidelines
- Created `project-management-practices.md` - Document taxonomy and maintenance procedures
- Created `project-timeline.md` - This cumulative timeline document

**Decisions Made**:
- **Documentation Philosophy**: LLM-first approach prioritizing structure over prose
  - Rationale: Optimize for machine parsing and token efficiency
  - Alternative considered: Human-readable narrative style (rejected - wrong audience)
  
- **Documentation Maintenance**: Cumulative append-only timeline instead of snapshot status
  - Rationale: Prevents stale "current status" statements that future sessions misinterpret
  - Alternative considered: Rewriting status sections (rejected - loses historical context)
  
- **Document Taxonomy**: Two-tier system (Read Every Session vs. Context-Specific)
  - Rationale: Efficient context loading - load ~8-12k tokens of essential context, then deep-dive as needed
  - Alternative considered: Flat structure with all docs equal priority (rejected - token waste)

- **Wikipedia Data Pipeline**: Path 1 (DB + XML hybrid) over pure XML parsing
  - Rationale: Database provides ground truth for page names; XML provides link ordering
  - Alternative considered: Pure XML parsing with manual canonicalization (rejected - too error-prone)

**Discoveries**:
- **Critical**: Wikipedia's `pagelinks` table contains template-expanded links
  - Implication: Cannot use pagelinks directly for N-Link analysis - would include template-injected "gravity wells"
  - Solution: Parse raw wikitext from XML dumps, strip templates before extracting links
  
- Quarry (https://quarry.wmcloud.org/) provides free SQL access to Wikipedia database
  - Implication: Can download complete page table for canonical name lookup
  
- Wikipedia has special lowercase-first-char pages (eBay, iPhone, pH)
  - Implication: Cannot assume first-char capitalization; must check exact match first
  
- Disambiguation pages are in regular `page` table but flagged in `page_props`
  - Implication: Can query and exclude from N-Link traversal; valuable to catalog separately

**Research Completed**:
- Reviewed Wikipedia naming convention documentation (technical restrictions, page names, MediaWiki manual)
- Investigated database schema: `page`, `pagelinks`, `templatelinks`, `redirect`, `linktarget` tables
- Analyzed template vs. prose link distinction problem
- Researched prompt engineering best practices (OpenAI, Anthropic, arXiv:2312.16171)

**Documentation Created**:
- `external-docs.md` - Wikipedia naming rules, Quarry info, database schema resources
- `wikipedia-link-graph-decomposition.md` - Complete extraction pipeline design
  - TSV-based output format to avoid JSON escaping issues
  - Decomposition approach: parse once, preserve everything, filter downstream
  - Recomposition strategies for different N-Link configurations

**Next Steps**:
- Create functional project directories (src/, data/, tests/)
- Implement Quarry query scripts to download page table
- Begin Wikipedia XML multistream parser implementation
- Develop template stripping algorithm (recursive `{{...}}` removal)
- Build link extraction with normalization and matching logic

**Session Context**:
This was the foundational session establishing project infrastructure and documentation framework. Heavy emphasis on designing maintainable, self-referential documentation system for future LLM sessions. Key breakthrough: understanding that pagelinks table contamination requires full wikitext parsing approach.

---

## Archive

*(Entries older than 6 months will be moved here)*

---

## Changelog

### 2025-12-12 (Second Update)
- Added evening session entry: Tier 1 documentation token budget optimization

### 2025-12-12
- Created project timeline document
- Added first session entry documenting initialization and framework design

---

**END OF DOCUMENT**
