# P-18R1 anchor proof evidence

**Date:** 2026-08-23  
**Authority:** D-050  
**Scope:** non-counted `neutral-light` proof for Architecture, Swimlane and Sankey

## Result

P-18R1 established the shared QA-only visual foundation and rendered three anchor HTML files outside the exact `gallery/` specimen count:

| Anchor | SHA-256 | Result |
|---|---|---|
| `anchor-proof/architecture--neutral-light.html` | `dbcf8226964395f13e758a15ecbdfad03b5ac60ef549e34b57fb20a4ed491721` | PASS |
| `anchor-proof/swimlane--neutral-light.html` | `79fc21ad950a1d4031ae6d03156e7a3657ebc01f98c406191ab0082ce860753d` | PASS |
| `anchor-proof/sankey--neutral-light.html` | `002c00fb9fa5f07d975e047816e7c63ebcc9752cc952e0d364cf7cbf43c591aa` | PASS |

The exact files and hashes are also bound in `PILOT-MANIFEST.json.anchor_proof` with `counted_as_specimen=false`.

## Foundation demonstrated

- one visible HTML display title; SVG retains accessible metadata only and has no duplicate visible title or evidence rail;
- 40–48px display role, 20–24px node/stage titles, 16px material text and 15–16px mono metadata/value roles;
- measured-width line reservation through `source/p18_visual_foundation.py` rather than character-count-only wrapping;
- flat original zones/cards/bands, subtle offline dot field, single declared focal intent and case-specific type legend;
- source/target metadata on semantic routes and explicit node/zone boundaries;
- Architecture proves trust-boundary topology and reciprocal identity exchange;
- Swimlane proves six owners, grouped ownership, artifact roles, numbered handoffs and a visible bridge/hop where e08 crosses e06;
- Sankey proves exact band-width encoding, masked route labels and conservation statement without an evidence rail.

## Verification

- generation and per-artifact semantic/quantitative/geometry/accessibility/security/contrast/visual-contract checks: `PASS`;
- Chrome headless at desktop/tablet/mobile for the three anchor files: 9/9 `PASS`, zero external request, console error or horizontal overflow;
- direct visual inspection at canonical artifact-frame size: `PASS` for title separation, semantic-field occupancy, type hierarchy, focal path and family silhouette;
- no network access, dependency installation, package build, `dist/`, Git, tag, Release or P-19 mutation.

This record authorizes no gate transition. P-18R2 must regenerate the exact 36 replacement specimens; owner approval remains pending after P-18R3.
