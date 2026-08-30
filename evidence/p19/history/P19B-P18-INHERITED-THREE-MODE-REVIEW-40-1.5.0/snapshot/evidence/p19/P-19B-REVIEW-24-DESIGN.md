# P-19B review-24 — detailed typed UML class model

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-24-1.5.0`  
**Authority:** D-104, retaining D-084–D-103  
**Status:** implementation evidence; owner approval pending

## Design contract

- **Outcome:** replace the generic two-card UML specimen with a readable class model whose interface, members and relationship semantics can be inspected directly.
- **Independent content:** seven original payment/invoice-domain containers and seventeen independently written attributes/operations; the owner screenshot is used only as a structural QA rubric.
- **Containers:** one service class, one explicitly stereotyped focal interface, two implementing classes and three domain classes.
- **Relationships:** exactly one dependency, two realizations, one composition and one association. Every semantic relationship is a single uninterrupted SVG path.
- **Connector grammar:** dependency/realization are dashed and use open-arrow/hollow-triangle markers; composition uses a filled source diamond; association uses an open arrow and the P-18 default rounded 90-degree route.
- **Cardinality:** composition exposes `1` and `1..*`; association exposes `0..*` and `1`, placed inline with canvas knockout so the relation remains legible.
- **Legend:** inheritance, realization, composition, aggregation, association and dependency are all represented with line/marker semantics, not color alone.
- **Accessibility:** interface stereotype, member visibility, typed signatures, relationship-kind metadata, direct cardinalities and a complete alternative table provide redundant non-color meaning.
- **Preservation:** exact review-23 is archived; only three UML-class HTML files and one preview change. The other 87 HTML artworks and 29 previews remain preserved.

The reference image is not copied or traced. No source prose, names, CSS, SVG geometry, coordinates, template or asset is reused.
