Primary Documentation URLs
1. Technical Restrictions (Most Critical for Your Use Case)
https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions)

This is your most valuable reference. It covers:

First letter auto-capitalization
Forbidden characters: # < > [ ] | { } _
Spaces ↔ underscores equivalence
Colon restrictions (namespace prefixes)
UTF-8 encoding rules
Title length limits (255 bytes UTF-8)
2. Page Name Technical Details
https://en.wikipedia.org/wiki/Wikipedia:Page_name

Covers:

namespace:pagename structure
FULLPAGENAME, PAGENAME, NAMESPACE magic words
URL encoding (%C3%80 = À)
Subpage conventions
3. MediaWiki Manual (Authoritative Source)
https://www.mediawiki.org/wiki/Manual:Page_title

The definitive technical spec covering:

Canonical form normalization rules
Interwiki prefix handling
Database key format
4. Article Titles Policy
https://en.wikipedia.org/wiki/Wikipedia:Article_titles

Editorial conventions (less critical for parsing, but useful for understanding redirect logic)

Key Technical Rules Confirmed
Rule	Detail
First character	Auto-capitalized (lowercase dog → Dog)
Subsequent characters	Case-sensitive (Mary_Brave_Bird ≠ Mary_brave_Bird) ✓
Spaces ↔ Underscores	Equivalent (stored as underscores in DB, displayed as spaces)
Forbidden chars	`# < > [ ]
Percent encoding	Cannot contain %XX literally (would decode)
Max length	255 bytes UTF-8
Unicode	NFC normalization, directional marks stripped

---

## Wikipedia Database & Data Access Resources

### 5. Quarry - Public SQL Interface
https://quarry.wmcloud.org/

Free SQL query interface to Wikipedia database replicas. Requires Wikimedia account. 10,000+ users, 1M+ queries run. Access to `page`, `pagelinks`, `redirect`, `templatelinks` tables. **Critical limitation**: `text` table (wikitext content) is NOT available.

### 6. Pagelinks Table Documentation
https://www.mediawiki.org/wiki/Manual:Pagelinks_table

Schema: `pl_from` (source page_id), `pl_target_id` (FK to linktarget), `pl_from_namespace`. **Critical finding**: Contains ALL links from rendered/parsed output — includes template-expanded links (infoboxes, navboxes). No link ordering preserved.

### 7. Templatelinks Table Documentation
https://www.mediawiki.org/wiki/Manual:Templatelinks_table

Tracks which templates are transcluded by which pages (e.g., `Apple_Inc → Template:Infobox_company`). Does NOT track links *within* templates — cannot be used to filter template-injected links from pagelinks.

### 8. Database Layout Overview
https://www.mediawiki.org/wiki/Manual:Database_layout

Complete MediaWiki database schema. Key tables: `page`, `revision`, `text`, `pagelinks`, `templatelinks`, `redirect`, `categorylinks`, `linktarget`.

### 9. RefreshLinks.php Documentation
https://www.mediawiki.org/wiki/Manual:RefreshLinks.php

Maintenance script that repopulates link tables. Confirms links are extracted from **parsed** (template-expanded) output, not raw wikitext.

### 10. Wikipedia Data Dumps
https://dumps.wikimedia.org/enwiki/

XML dumps containing raw wikitext. Key file: `pages-articles-multistream.xml.bz2` (~25GB compressed) with companion index file for selective page extraction. **Only source for link ordering and prose-only link extraction.**

### 11. TextExtracts API
https://en.wikipedia.org/w/api.php?action=help&modules=query%2Bextracts

Returns plain text extracts of articles. **Limitation**: Strips all markup including `[[wikilinks]]` — useless for N-Link purposes.

---

## Key Findings for N-Link Implementation

| Data Need | Source | Available? |
|-----------|--------|------------|
| Complete link graph | `pagelinks` via Quarry | ✅ Yes (but includes template links) |
| Link ordering | XML dumps | ✅ Yes (parse wikitext) |
| Prose-only links | XML dumps + parsing | ✅ Yes (strip `{{templates}}` before extracting `[[links]]`) |
| Redirect resolution | `redirect` table via Quarry | ✅ Yes |
| Filter template links | Cannot be done via DB | ❌ Must parse wikitext |

**Conclusion**: For uncontaminated N-Link basins, must parse raw wikitext from XML dumps with template stripping. `pagelinks` table is "post-expansion" data containing template-injected gravity wells.