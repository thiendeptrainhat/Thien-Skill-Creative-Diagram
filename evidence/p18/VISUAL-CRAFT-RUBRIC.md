# P-18R visual-craft rubric

**Authority:** D-050  
**Applies to:** exact P-18 replacement candidate only  
**Relationship to existing gates:** additive; it cannot compensate for a semantic, quantitative, geometry, accessibility, security, standalone or provenance failure

## Hard acceptance conditions

1. Semantic field and type legend occupy at least 75% of artboard height, including intentional whitespace inside the field. No visible duplicate title or evidence rail exists in the SVG.
2. At canonical render, material text is at least 16px; node/stage titles are 20–24px; HTML display title is 40–48px; mono metadata/values/ticks are 14–16px.
3. There is no clipping, text overlap, connector through an unrelated node or wrong endpoint.
4. Label–connector clearance is at least 8px. An unavoidable crossing has a bridge/hop.
5. All 12 families have distinct silhouettes; aggregate blind thumbnail recognition is at least 10/12.
6. A reviewer can identify the intended takeaway or focal path in approximately five seconds.
7. Visual-craft score is at least 85/100 and no scored dimension is below 4/5. All inherited technical gates remain `PASS`.
8. Upstream comparison uses only the abstract rubric below. Pixel similarity, tracing or reuse of upstream code/CSS/SVG/template/asset is forbidden.

Any hard-condition failure makes the visual-craft result `FAIL` regardless of total score.

## Scored dimensions

Each dimension is scored 1–5. Weighted score is `score / 5 × weight`.

| Dimension | Weight | A 5/5 specimen demonstrates |
|---|---:|---|
| Semantic silhouette | 20 | Family is identifiable from geometry alone; visual roles match the locked grammar. |
| Hierarchy and focal path | 15 | One clear entry point/takeaway; accent and reading order resolve within about five seconds. |
| Typography and labels | 15 | Required sizes, confident hierarchy, measured wrapping, direct labels and clean whitespace. |
| Geometry and routing | 15 | Exact endpoints, clear ports, ≥8px label clearance, no unrelated-node crossing, bridge/hop where required. |
| Composition and density | 15 | ≥75% useful artboard height, deliberate negative space, balanced field, no ornamental rail. |
| Mode craft and contrast | 10 | Mode feels intentional rather than recolored; all opaque text/mark pairs pass recorded contrast checks. |
| Legend and explanatory economy | 5 | Type legend decodes only marks needed to read the diagram; no QA prose inside the artboard. |
| Originality and provenance | 5 | Original expression with complete receipt and abstract-only upstream comparison. |
| **Total** | **100** | **Pass ≥85 and every row ≥4/5.** |

## Blind silhouette protocol

- Create a mode-consistent thumbnail for each of the 12 families with outer HTML title, case ID, capability ID and evidence section excluded.
- Remove or mask family-name text while preserving data labels needed for meaning.
- Present thumbnails in a shuffled order against the fixed list of 12 allowed family names.
- Record selected name, confidence and correctness. Aggregate pass is at least 10 correct of 12.
- A reviewer may use no file name, DOM metadata, manifest path or source code.

An automated geometry-signature proxy may run before review but does not replace the recorded blind judgment.

## Five-second takeaway protocol

- Show the artifact frame at canonical review size for approximately five seconds.
- Hide the exact ledger and provenance section.
- Record the first perceived focal object/path and a one-sentence takeaway.
- Pass when focal object/path matches the renderer’s declared visual intent and the takeaway does not contradict locked semantics.
- Report the result per family; modes may be sampled only after geometry identity across modes is verified.

## Abstract upstream-comparison checklist

Permitted comparison questions:

- Is semantic geometry the primary signal?
- Is typography large enough and hierarchically disciplined?
- Is negative space intentional rather than unused canvas?
- Is one focal path/outcome visually dominant?
- Are type-specific marks, legends and quantitative encodings immediately legible?
- Are connectors quiet, exact and free from visual collisions?

Forbidden comparison methods:

- overlay, pixel-distance or image-similarity scoring;
- tracing layout coordinates or reproducing a screenshot composition;
- copying or adapting upstream CSS, SVG, HTML, templates, icons, prose or gallery assets;
- claiming equivalence from matching colors, fonts or decorative effects.
