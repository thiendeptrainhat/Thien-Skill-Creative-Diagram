# P-19B review-10 — detailed ER data model remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-10-1.5.0`  
**Authority:** D-090  
**Visual parent:** exact P-18R6 review-17  
**Boundary:** er-data-model only; no P-19C/package/dist/publication/Git/Release

## Design contract

- Render exactly four semantic entities: Author, Article, Tag and ArticleTag.
- Distinguish Article as the single aggregate root and ArticleTag as the single associative entity.
- Show all 19 declared members with names and types; mark primary keys with `#` and foreign keys with `→`.
- Show three explicit one-to-many relationships with direct `1`/`N` cardinalities and relationship labels.
- Keep Article as the restrained coral focal surface, ArticleTag dashed, and the other entities neutral navy.
- Provide a legend and a native alternative table containing every entity member and relationship.
- Preserve identical SVG geometry across neutral-light, neutral-dark and editorial modes.
- Preserve 84 non-target HTML artworks after candidate-ID normalization and 28 non-target previews byte-for-byte.

## Visual judgment

The model inherits P-18's warm paper, navy structure, coral focal signal, typography roles and restrained rounding. Technical density is organized by clear card headers, aligned field/type columns, continuous relationship lines and explicit PK/FK/cardinality text rather than color alone. The reference image is treated only as a non-executable hierarchy/rubric; Vietnamese scenario data, geometry, CSS, SVG and table are independently authored.

## Acceptance

Technical PASS requires exact 4/19/3/1/1 serialized counts, one aggregate root, one associative entity, explicit PK/FK/cardinality encoding, exact alternative table, three-mode geometry equality, immutable review-09 archive, protected-corpus integrity and non-target preservation. Browser execution and owner approval remain separate.
