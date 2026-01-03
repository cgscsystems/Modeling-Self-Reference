# Human Collaboration Data Protocol

**Purpose**: Standards for capturing, formatting, and archiving human communications
**Last Updated**: 2026-01-01

---

## Why Archive Communications?

1. **Attribution**: Establishes who contributed what ideas and when
2. **Context preservation**: Future sessions (human or LLM) can understand decision rationale
3. **IP documentation**: Creates paper trail for intellectual property claims
4. **Collaboration hygiene**: Prevents "he said / she said" disputes

---

## Intake Process

### Step 1: Identify Archivable Content

Ask: Does this communication contain any of the following?
- [ ] Novel ideas, conjectures, or hypotheses
- [ ] Strategic decisions (IP, collaboration, publication)
- [ ] Feedback that shaped project direction
- [ ] Attribution-relevant contributions

If yes → proceed to formatting. If no → skip archiving.

### Step 2: Create Document

**Filename**: `{from}-{to}_{topic}.md`

**Required metadata block**:
```markdown
# [Descriptive Title]

**Date**: YYYY-MM-DD
**From**: [Initials or name]
**To**: [Initials, name, or "Team"]
**Context**: [One-line description of what prompted this]

---
```

### Step 3: Format Content

**For email/chat paste**:
1. Add section headers to break up topics
2. Convert wall-of-text to paragraphs
3. Use markdown lists for enumerated points
4. Preserve voice/tone (don't sanitize casual language)
5. Fix obvious typos but keep informal spelling if intentional

**For Q&A exchanges**:
1. Clearly label who said what (`## WH's Question`, `## LLM Response`)
2. Use blockquotes for direct quotes if needed
3. Add markdown formatting to responses (headers, lists, tables)

**For meeting notes**:
1. List attendees
2. Use headers for agenda items
3. End with "Action Items" section

### Step 4: Update INDEX.md

Add entry to the table in [INDEX.md](INDEX.md) with:
- Filename (linked)
- Date
- Participants
- Brief topic summary

---

## Participant Registry

| Initials | Name | Role |
|----------|------|------|
| WH | Will Harding | Project lead, theory originator |
| MM | Matt (via LLM) | Implementation, empirical analysis |
| RQ | Ryan Querin | Theory contributor (see EXT-0001 in contracts) |

*Add new participants as they join the project.*

---

## LLM Assistance

LLMs can help with:
- Reformatting pasted content (fixing lost structure from copy-paste)
- Adding section headers and markdown formatting
- Suggesting which content is archivable
- Updating INDEX.md

LLMs should NOT:
- Editorialize or summarize content (preserve original voice)
- Redact content without explicit instruction
- Guess at participants or dates

---

## Linking to Contracts

If a communication establishes or modifies a theory claim:
1. Note the relevant contract ID in the document
2. Update `llm-facing-documentation/contracts/contract-registry.md` if needed
3. Use format: `**Related Contract**: NLR-C-XXXX`

Example: If WH proposes a new conjecture in an email, the archived email should reference the contract created for that conjecture.

---

## Privacy Considerations

- This is a private repository; communications are not public
- Participants have implicitly consented by sending project-related messages
- Redact personal information unrelated to the project (phone numbers, addresses)
- If in doubt, ask the author before archiving

---
