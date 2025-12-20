# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

This project applies **formal graph theory to self-referential systems** (Wikipedia, databases, code) to discover hidden structure through deterministic traversal rules. The core insight: finite self-referential graphs partition into "basins of attraction" under deterministic rules, and switching between rules ("tunneling") reveals semantic relationships invisible to single-rule analysis.

**Current Focus**: Extracting and analyzing Wikipedia's link graph to validate N-Link Rule Theory empirically.

---

## Quick Start: New Session Bootstrap

**CRITICAL**: Follow this sequence to minimize token usage while maximizing context:

### Step 1: Universal Context (Tier 1, ~8-12k tokens)
Load these files every session:
1. [llm-facing-documentation/README.md](llm-facing-documentation/README.md) - Project overview
2. [llm-facing-documentation/project-timeline.md](llm-facing-documentation/project-timeline.md) - Latest 3-5 entries only
3. [llm-facing-documentation/llm-project-management-instructions/documentation-standards.md](llm-facing-documentation/llm-project-management-instructions/documentation-standards.md)
4. [llm-facing-documentation/llm-project-management-instructions/project-management-practices.md](llm-facing-documentation/llm-project-management-instructions/project-management-practices.md)

### Step 2: Work Context (Tier 2, ~10-20k tokens)
Navigate to the directory you're working in and load its INDEX.md:
- **Theory work**: Load [llm-facing-documentation/theories-proofs-conjectures/INDEX.md](llm-facing-documentation/theories-proofs-conjectures/INDEX.md)
- **Wikipedia pipeline**: Load [data-pipeline/wikipedia-decomposition/INDEX.md](data-pipeline/wikipedia-decomposition/INDEX.md)
- **Documentation system**: Load [meta-maintenance/INDEX.md](meta-maintenance/INDEX.md)

### Step 3: Deep Dive (Tier 3, as needed)
Load specific reference documents only when explicitly needed for your task.

---

## Development Commands

### Environment Setup

**Initial setup** (one-time after cloning):
```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Activate environment** (each session):
```bash
# Linux/macOS
source .venv/bin/activate
```

```powershell
# Windows
.venv\Scripts\Activate.ps1
```

**Verify installation**:
```bash
python --version  # Should be 3.8+
pip list          # Should show: mwparserfromhell, mwxml, requests
```

### VS Code Workspace

Open the workspace configuration to get system prompts and settings:
```bash
code self-reference-modeling.code-workspace
```

**Workspace settings include**:
- Python interpreter: `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS)
- Format on save: black (line length 88)
- Linting: flake8 enabled
- System prompts: End-of-session protocol trigger

### Python Development

**Code style**:
- Formatter: black (line length 88)
- Linter: flake8
- Tab size: 4 spaces

**Running Python scripts**:
```bash
python path/to/script.py
```

**Testing** (when tests exist):
```bash
pytest
```

---

## Repository Architecture

### Directory Structure

```
Modeling-Self-Reference/
├── llm-facing-documentation/          # Tier 1: Load every session
│   ├── README.md                      # Project overview
│   ├── project-timeline.md            # Cumulative history
│   ├── end-of-session-protocol.md     # Session wrap-up procedure
│   ├── llm-project-management-instructions/
│   │   ├── documentation-standards.md # How to write docs
│   │   └── project-management-practices.md # How to maintain project
│   └── theories-proofs-conjectures/   # Tier 2: Mathematical foundations
│       ├── INDEX.md
│       ├── unified-inference-theory.md
│       ├── n-link-rule-theory.md
│       └── database-inference-graph-theory.md
│
├── meta-maintenance/                   # Tier 2: Documentation system internals
│   ├── INDEX.md
│   ├── implementation.md              # System architecture
│   ├── session-log.md                 # Design history
│   ├── writing-guide.md               # Detailed templates
│   └── data-sources.md                # External research links
│
├── data-pipeline/                     # Tier 2: Implementation workspaces
│   └── wikipedia-decomposition/
│       ├── INDEX.md
│       ├── implementation-guide.md
│       └── data-sources.md
│
├── human-facing-documentation/        # Not for LLM loading
├── .vscode/                           # Workspace configuration
│   └── settings.json                  # System prompts (Tier 0)
├── initialization.md                  # One-time setup guide
├── requirements.txt                   # Python dependencies
└── self-reference-modeling.code-workspace
```

### Key Architectural Patterns

**Three-Tier Documentation System**:
- **Tier 1** (Universal): Read every session (~8-12k tokens)
- **Tier 2** (Contextual): Load when working in functional area (~10-20k tokens)
- **Tier 3** (Reference): Deep-dive as-needed (no limit)

**Directory Semantics**:
- Directories WITH `implementation.md` = active workspace (Tier 2)
- Directories WITHOUT implementation files = organizational structure
- Every directory has an INDEX.md as a "relay node" for navigation

**Documentation Philosophy**:
- **Cumulative, not snapshot**: Append new entries, never delete history
- **LLM-first**: Structured over narrative, explicit over implicit
- **Self-referential**: System documents its own creation and evolution
- **Token-efficient**: Front-load critical information, cross-reference instead of duplicate

---

## Common Development Tasks

### Creating New Documentation

**Metadata template** (required at start of every doc):
```markdown
# [Document Title]

**Document Type**: [meta-documentation | theory | implementation | reference | procedure]
**Target Audience**: [LLMs | humans | both]
**Purpose**: [One-sentence description]
**Last Updated**: YYYY-MM-DD
**Status**: [draft | active | deprecated]
```

**Naming conventions**:
- Files: `kebab-case-descriptive-name.md`
- Directories: `kebab-case-plural-nouns/`
- Avoid spaces, underscores, CamelCase

### Creating New Directory

When creating a new subsystem or feature area:

1. Create directory with INDEX.md and implementation.md
2. Use templates from [llm-facing-documentation/llm-project-management-instructions/project-management-practices.md](llm-facing-documentation/llm-project-management-instructions/project-management-practices.md)
3. Optional files: data-sources.md, session-log.md, future.md

### Updating Project Timeline

**When to log** (priority-based):
- **High**: Architectural decisions, completed milestones, critical discoveries (always log)
- **Medium**: Non-obvious implementation details, research findings (log if significant)
- **Low**: Routine tasks, typo fixes (skip)

**Update pattern**: Append to top of [llm-facing-documentation/project-timeline.md](llm-facing-documentation/project-timeline.md) (reverse chronological)

### End-of-Session Protocol

When user says "wrap up session" or "execute end-of-session protocol":

1. Load [llm-facing-documentation/end-of-session-protocol.md](llm-facing-documentation/end-of-session-protocol.md) if not in context
2. Follow the 7-step procedure:
   - Session summary
   - Meta-update check (if modified system docs)
   - Dependency check
   - Project timeline update
   - Directory-specific documentation
   - Git status check
   - Final checklist

**Note**: VS Code workspace settings automatically trigger this protocol.

### Git Workflow

**Check status**:
```bash
git status
```

**View recent commits**:
```bash
git log --oneline -10
```

**Committing changes** (when user requests):
```bash
git add <files>
git commit -m "type: brief description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**IMPORTANT Git Safety**:
- Only commit when user explicitly requests
- Never use `--no-verify` or skip hooks
- Never force push to main/master
- Never amend commits that have been pushed

---

## Theory Overview (Load When Working on Theory)

The mathematical foundation comprises three integrated theories:

1. **N-Link Rule Theory**: Deterministic traversal on finite directed graphs partitions nodes into basins of attraction
2. **Database Inference Graph Theory**: Extension to typed database graphs with multi-rule tunneling
3. **Unified Inference Theory**: Comprehensive integration showing how self-reference emerges from graph structure

**When to load**: Only when actively working on theory development. The project summary above provides sufficient context for implementation work.

**Location**: [llm-facing-documentation/theories-proofs-conjectures/](llm-facing-documentation/theories-proofs-conjectures/)

---

## Dependencies

Current Python dependencies (from requirements.txt):
- `mwparserfromhell` - MediaWiki wikitext parser
- `mwxml` - MediaWiki XML dump processor
- `requests` - HTTP library

**Adding new dependencies**:
1. Add to requirements.txt
2. Run `pip install -r requirements.txt`
3. Update this file and relevant implementation docs
4. Log to project timeline

---

## Documentation Standards (Quick Reference)

**Structure over prose**: Use hierarchy, not narrative
**Explicit over implicit**: State assumptions, no shared context
**Precise over fluent**: Accuracy beats readability
**Cross-reference over duplication**: Link, don't repeat
**Token-efficient**: Front-load critical information

**For complete guidelines**: See [llm-facing-documentation/llm-project-management-instructions/documentation-standards.md](llm-facing-documentation/llm-project-management-instructions/documentation-standards.md)

---

## Working with This System

### Finding Information

**Navigation pattern**:
1. Start at directory INDEX.md
2. Load core files (Tier 2)
3. Reference files as needed (Tier 3)

**Never load**:
- Files in `deprecated/` subdirectories
- Files in `human-facing-documentation/` (unless specifically needed)
- Multiple copies of the same logical document

### Maintaining Documentation

**Update triggers**:
- User-prompted: "update the timeline", "log this decision"
- End-of-session: Follow protocol in end-of-session-protocol.md
- Milestone-triggered: Completed feature or subsystem

**Update patterns**:
- **Static docs** (theory, standards): Rare, user-prompted only
- **Cumulative docs** (timeline): Append-only with timestamp
- **Active docs** (implementation): In-place edits with decision log

### Deprecation Policy

**When to deprecate** (vs git version):
- Theory documents undergoing major revision/merger
- Documents that would confuse if accidentally loaded

**Procedure**:
1. Create `deprecated/` subdirectory
2. Move old document(s)
3. Add deprecation notice with reason and replacement link
4. Update INDEX.md to warn against loading deprecated files

**For code and implementation docs**: Use git history, no deprecation needed

---

## Token Budget Guidelines

**Target loads per session**:
- Bootstrap (Tier 1): ~8-12k tokens
- Working context (Tier 2): ~10-20k tokens
- Deep dive (Tier 3): As needed (no limit)
- Total typical session: 18-32k tokens

**Optimization strategies**:
- Don't re-read files already in context
- Use INDEX files as navigation guides
- Follow tier system strictly
- Request only files you need to modify

---

## Key Principles

1. **This is a research project**: The documentation system itself is part of the research (self-referential systems)
2. **LLM-first design**: All documentation optimized for machine parsing, not human reading
3. **Cumulative growth**: Append and extend, never delete or rewrite history
4. **Directory-based discovery**: No central registry, docs co-located with code
5. **Self-healing**: Fix broken references on encounter, log corrections to timeline
6. **Version-controlled configuration**: Workspace settings and system prompts in git

---

## Troubleshooting

**Python not found**:
- Try `python3` instead of `python`
- Verify Python 3.8+ in PATH

**Virtual environment issues**:
- Windows: Set execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Ensure venv is activated (prompt shows `(.venv)`)

**Import errors**:
- Activate virtual environment first
- Run `pip install -r requirements.txt`
- Verify with `pip list`

**Broken documentation links**:
- Use git history: `git log --all --full-history -- '**/filename.md'`
- Update references and log correction to timeline

---

## Related Resources

- Project timeline (latest state): [llm-facing-documentation/project-timeline.md](llm-facing-documentation/project-timeline.md)
- Documentation system architecture: [meta-maintenance/implementation.md](meta-maintenance/implementation.md)
- Theory foundations: [llm-facing-documentation/theories-proofs-conjectures/INDEX.md](llm-facing-documentation/theories-proofs-conjectures/INDEX.md)
- Wikipedia pipeline design: [data-pipeline/wikipedia-decomposition/implementation-guide.md](data-pipeline/wikipedia-decomposition/implementation-guide.md)

---

**Last Updated**: 2025-12-17
**Status**: Active
