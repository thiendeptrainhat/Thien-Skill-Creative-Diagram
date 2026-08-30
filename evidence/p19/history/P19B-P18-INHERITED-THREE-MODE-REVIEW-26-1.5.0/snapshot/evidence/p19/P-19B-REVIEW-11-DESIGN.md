# P-19B review-11 — P-18 inline cardinality alignment

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-11-1.5.0`  
**Authority:** D-091  
**Visual parent:** exact P-18R6 review-17 database-schema contract  
**Boundary:** er-data-model cardinality placement only; no P-19C/package/dist/publication/Git/Release

## Design contract

- Preserve the complete D-090 four-entity model, fields, types, PK/FK marks, relationship paths, relationship names, legend and alternative table.
- Place every source `1` and target `N` directly on its connector axis near the corresponding entity boundary, matching the approved P-18 database-schema behavior.
- Paint one canvas-color, no-stroke knockout behind each cardinality after the continuous relationship path and before the glyph.
- Use P-18's 8px along-line and 4px perpendicular knockout padding; retain at least 8px knockout-to-node clearance.
- Apply the same endpoint rule to horizontal, rounded-orthogonal and vertical relationships.
- Preserve identical geometry across neutral-light, neutral-dark and editorial modes.
- Preserve 84 non-target HTML artworks after candidate-ID normalization and 28 non-target previews byte-for-byte.

## Acceptance

Technical PASS requires six inline cardinalities, six bound canvas knockouts, correct source/target values, axis metadata, endpoint proximity, P-18 padding contract, unchanged D-090 ER semantics, three-mode geometry equality, immutable review-10 archive and non-target preservation. Browser execution and owner approval remain separate.
