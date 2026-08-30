# P-18R3 independent visual-craft review

**Candidate:** `P18-PILOT-1.5.0-VISUAL-CRAFT-REPLACEMENT`  
**Manifest SHA-256:** `4fb00b7f1b898a4a59b6fd4092b8f15f35ddd5b4a51c14124911b42a145ed5a7`  
**Date:** 2026-08-23  
**Reviewer boundary:** visual-craft judgment was performed as a gate independent from the semantic/quantitative/security validators; it is not owner approval

## Gate result

**PASS — 92/100; every scored dimension is at least 4/5; zero hard-condition failure.**

| Dimension | Score | Weight | Weighted | Review basis |
|---|---:|---:|---:|---|
| Semantic silhouette | 5/5 | 20 | 20 | Twelve families remain distinguishable from geometry at contact-sheet scale. |
| Hierarchy and focal path | 5/5 | 15 | 15 | Each frame has one declared intent, one entry point or focal mark, and a short reading path. |
| Typography and labels | 4/5 | 15 | 12 | Required size roles pass; direct labels and measured wrapping are clean across three viewports. |
| Geometry and routing | 5/5 | 15 | 15 | Browser geometry found no clipping, overlap, unrelated-node route, wrong endpoint or missing required bridge. |
| Composition and density | 4/5 | 15 | 12 | Field + legend occupancy is 91.33%; whitespace is intentional and the former evidence rail is absent. |
| Mode craft and contrast | 4/5 | 10 | 8 | Light, dark and editorial are coherent static systems; 36/36 contrast checks pass. |
| Legend and explanatory economy | 5/5 | 5 | 5 | Each family has a short type-specific legend and one intent sentence, with no QA prose inside the SVG. |
| Originality and provenance | 5/5 | 5 | 5 | Original fixtures/expression, one-to-one receipts and abstract-only upstream comparison. |
| **Total** |  | **100** | **92** | **PASS ≥85; minimum row = 4/5.** |

## Hard-condition audit

1. Field + type legend: 91.33% of artboard height; duplicate visible SVG titles = 0; SVG evidence rails = 0 — `PASS`.
2. Canonical roles: display 40–48px, node/stage 20–24px, material text ≥16px, mono metadata 14–16px — `PASS`.
3. Chrome measurement over 108 runs found zero clipped text, text overlap, route through unrelated node or endpoint failure — `PASS`.
4. Route labels use masks with `data-clearance=8`; the one unavoidable Swimlane crossing has an explicit bridge/hop — `PASS`.
5. Masked thumbnail recognition: 12/12 — `PASS`.
6. Five-second takeaway/focal-path review: 12/12 — `PASS`.
7. Independent visual-craft score: 92/100, no dimension below 4/5; inherited technical gates remain `PASS`.
8. Comparison was limited to the abstract rubric; no pixel comparison, overlay, tracing or reuse was performed.

## Blind silhouette review

Review input: `review/blind-neutral-light.jpg`, SHA-256 `a77b241679a0a715dd12851846c116083bfbe55799e41e13914197bf58badb84`. The sheet excludes the outer HTML header and family/title metadata, uses a fixed shuffled order and shows only the semantic field plus type legend. The reviewer did not use DOM, filenames or manifest paths while classifying the visible sheet.

| Slot | Selected family | Confidence | Correct |
|---:|---|---|---|
| 01 | Wardley map | High | Yes |
| 02 | Sankey | High | Yes |
| 03 | Bubble | High | Yes |
| 04 | Swimlane | High | Yes |
| 05 | Fishbone | High | Yes |
| 06 | Architecture | High | Yes |
| 07 | Ridgeline | High | Yes |
| 08 | User journey | High | Yes |
| 09 | Treemap | High | Yes |
| 10 | Slopegraph | High | Yes |
| 11 | Deployment | High | Yes |
| 12 | Dumbbell | High | Yes |
| **Aggregate** |  |  | **12/12 PASS** |

This is a recorded internal blind-silhouette review, not an owner or external-user study. The owner review remains the approval boundary.

## Five-second takeaway review

Protocol: each neutral-light artifact frame was viewed without the exact ledger/provenance section; the first perceived focal object/path and takeaway were compared with the renderer-declared intent.

| Family | First perceived focal object/path and takeaway | Result |
|---|---|---|
| Architecture | The approval route traverses four trust zones with no bypass. | PASS |
| Swimlane | Five numbered handoffs move evidence across six owners. | PASS |
| Sankey | 100 ML/day splits into delivery and loss while conserving the total. | PASS |
| Treemap | A total of 100 is partitioned by parent group and area. | PASS |
| Wardley map | The dependency chain moves from custom portal toward evolved hosting. | PASS |
| Deployment | Gateway enters the app cluster and fans out to two data stores. | PASS |
| User journey | Apply is the low point; sentiment recovers toward Activate. | PASS |
| Fishbone | Ten hypotheses in five groups converge on one observed effect. | PASS |
| Dumbbell | Every region improves; Central and Remote show the largest drops. | PASS |
| Slopegraph | Permits and Grants decline; Records rises slightly. | PASS |
| Ridgeline | Three distributions share bins and a global amplitude scale. | PASS |
| Bubble | Migration is the largest budget and sits in the high-effort region. | PASS |

## Approval boundary

This review makes the frozen replacement eligible for owner inspection. It does not approve `G-03@1.5.0`, close P-18 or authorize P-19.
