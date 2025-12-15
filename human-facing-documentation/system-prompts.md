# VS Code System Prompts for Self Reference Modeling Project

**Document Type**: Configuration  
**Target Audience**: Human developers/researchers  
**Purpose**: Critical system-level prompts for reproducible LLM behavior in this project  
**Last Updated**: 2025-12-15  
**Status**: Active

---

## Why System Prompts Matter

This project applies graph theory to self-referential systems (Wikipedia, databases, documentation). The LLM assistant acts as an **inference engine** navigating this documentation structure using different "traversal rules."

**Critical insight**: System prompts define which inference rules the LLM uses. Different prompts = different navigation patterns = different experimental results.

For reproducibility, all collaborators must use the same system prompts.

---

## How to Configure

**Location**: VS Code Settings (JSON)
- Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
- Search: "Preferences: Open User Settings (JSON)"
- Add the configuration below to your settings.json

**Alternatively**: Workspace settings
- `.vscode/settings.json` in project root (recommended for project-specific config)

---

## Required System Prompts

### End-of-Session Protocol Trigger

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "When user says 'execute end-of-session protocol', 'wrap up session', 'end of session', 'close session', or 'summarize session': (1) Request llm-facing-documentation/end-of-session-protocol.md if not in context, (2) Request llm-facing-documentation/llm-project-management-instructions/project-management-practices.md and documentation-standards.md if not in context, (3) Follow the 7-step protocol documented in end-of-session-protocol.md sequentially"
    }
  ]
}
```

**Purpose**: Ensures LLM can execute systematic session closing even after long sessions where initial context is truncated.

**What it triggers**: 7-step protocol including session summary, meta-update check, dependency verification, timeline update, directory documentation, git status, and final checklist.

**Token cost**: ~150 tokens injected per turn (minimal overhead)

**Full protocol**: See [end-of-session-protocol.md](../llm-facing-documentation/end-of-session-protocol.md) for complete procedure.

---

## Optional Enhancements

### Bootstrap New Session Reminder

```json
{
  "text": "At session start, if user has not loaded context, suggest loading: llm-facing-documentation/README.md (project overview), project-timeline.md (recent 3-5 entries), and documentation-standards.md (writing guidelines)"
}
```

**Purpose**: Helps LLM orient itself in new sessions

**Trade-off**: Adds ~100 tokens per turn; may be unnecessary if user always bootstraps manually

---

## Validation

To verify prompts are active:
1. Start new chat session
2. Say "execute end-of-session protocol"
3. LLM should request end-of-session-protocol.md first, then project-management-practices.md and documentation-standards.md if not already loaded
4. LLM should execute the 7-step protocol sequentially
5. If LLM doesn't know what to do → prompts not configured correctly

---

## Future Considerations

As the project grows, additional triggers may be needed for:
- Theory document navigation
- Code generation patterns
- Data pipeline orchestration

These will be documented here as they emerge.

---

## Meta-Note

These system prompts are **experimental apparatus**, not just configuration. They define the inference rules the LLM uses to navigate the project's self-referential documentation structure. This is the project's theory applied to itself.

---
