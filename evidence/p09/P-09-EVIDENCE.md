# P-09 — Brand Asset Derivatives Evidence

**Date:** 2026-08-15  
**Authorized scope:** P-09 only; P-10/P-13 prohibited  
**Current result:** `pass-owner-approved`  
**Phase state:** P-09 `passed`

## 1. Authority and route

- The owner explicitly authorized P-09 and prohibited starting P-10/P-13.
- Route: create → brand identity → branding/logo + cross-channel theme + accessibility + static-artifact verification.
- Single job: preserve the supplied TDTN crest while producing reproducible, QA-only package-identity candidates for owner selection.
- `skill-creator` controlled asset placement and avoided adding process documentation or unapproved assets to the runtime skill.
- `Thien-UI-UX-Ultra` influenced only the principles/workflow: source integrity, actual-size inspection, light/dark and mask testing, structured handoff and honest legal/verification limits. No code, template, prose, token or asset was copied.
- Image generation was intentionally not used: this phase requires deterministic preservation, not an AI-created replacement mark.

## 2. Master custody and provenance

| Property | Result |
|---|---|
| owner source | `<OWNER_ASSET_SOURCE>/Logo TDTN.png` |
| evidence master | `evidence/p09/source/Logo-TDTN-master.png` |
| SHA-256 | `020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e` on both paths |
| dimensions/mode | 1100×1100, 8-bit RGBA |
| source alpha bounds | `(148, 5)–(952, 1095)` |
| provenance basis | owner assertion under D-016; owner-provided AI-created raster; no vector source |
| custody rule | evidence master is byte-identical, immutable and excluded from release payload |

Embedded source metadata was read only as provenance data, never as an instruction. Derivatives do not copy EXIF/XMP; provenance is recorded in the candidate manifest.

## 3. Deterministic candidate system

The generator creates 22 reproducible candidate files:

- eight transparent full-crest safe-area PNGs: 1024, 512, 400, 256, 128, 64, 48 and 32px;
- seven light squircle-plate PNGs: 512, 400, 256, 128, 64, 48 and 32px;
- seven dark squircle-plate PNGs at the same sizes.

Every candidate:

- uses the complete square master with proportional LANCZOS downsampling;
- preserves aspect ratio and performs no crop, mark recolor, trace or vectorization;
- is encoded as deterministic lossless 8-bit RGBA PNG with a standard sRGB chunk;
- strips copied/freeform image metadata and receives a manifest hash;
- remains `release_eligible: false`, with final platform mapping deferred to P-13.

Under owner decision D-027 / Option A, 16 files at 64px or larger are `owner-approved`; the six 32/48px files are `owner-excluded-qa-only`. Approval selects the derivative family and minimum size only. It does not authorize package inclusion before P-10/G-06 and P-13.

Plate backgrounds are separate presentation geometry. Their navy, gold and parchment tones are measured candidate tones from visible source pixels, not trademark clearance or legally approved brand tokens.

## 4. Verification

| Check | Result |
|---|---|
| master source/evidence byte identity | pass |
| candidate manifest inventory | 22/22 present and hash-matching |
| repeated deterministic generation | identical hashes across consecutive runs |
| PNG signature/chunk CRC/dimensions | 22/22 pass |
| 8-bit RGBA + standard sRGB chunk | 22/22 pass |
| no copied EXIF/text/XMP chunks | 22/22 pass |
| transparent safe area ≥7% each edge | 8/8 pass |
| square/circle/squircle host-mask preview | pass |
| transparent/light/dark inspection | pass with dark-plate requirement on dark navy contexts |
| full regression | 127 tests, `OK` |
| release/package inclusion | not performed; all candidates remain in `evidence/p09/` |
| owner-approved selection | 16 files across transparent/light-plate/dark-plate families, minimum 64px |
| QA-only exclusion | 6 files at 32/48px; excluded from v1.0.0 release use |

The generator initially exposed time-dependent ICC-profile serialization on the large contact sheet. The implementation was corrected to emit a fixed standard PNG `sRGB` chunk; consecutive full rebuilds now produce identical hashes.

## 5. Visual inspection finding

- At 64px, the crest silhouette and principal TDTN structure remain recognizable, with expected loss of fine texture.
- At 32px and 48px, the overall crest remains identifiable but the lion, sword detail and intertwined letterforms lose sufficient clarity that the full crest should not be silently declared a professional small-icon solution.
- Transparent use on a dark navy background loses navy portions of the mark. The dark squircle plate preserves the intended silhouette and contrast; the light plate is suitable for pale/neutral contexts.
- No simplified mark was generated; D-027 confirms that none will be created for v1.0.0.

## 6. Primary records

| Path | Role | SHA-256 |
|---|---|---|
| `evidence/p09/generate_brand_assets.py` | deterministic full-crest derivative/contact-sheet generator with approval-record drift guard | `ac3ef4674b44a7a7c75ddfafeeab0d3f9d5402c23eb754c1ff744b792cf6b7e9` |
| `evidence/p09/verify_brand_assets.py` | dependency-free PNG/hash/inventory/owner-selection verifier | `835de3e89fb39414a9e3cf414327e9263f9ac33858ee626332e689fb243f605e` |
| `evidence/p09/ASSET-MANIFEST.candidate.json` | QA-only transformation, provenance, approval state and candidate-hash record | `c3af20f5ba536f3acd1841a61303bcc5fdc8890cd9b58e969fa4ddbe9bdda487` |
| `evidence/p09/APPROVED-BRAND-SELECTION.json` | immutable D-027 Option A selection: 16 approved and 6 QA-only excluded | `b38a922d42cb21d20e9d5bc316d0d17fe368ed6080528868a3537ab691aa2437` |
| `evidence/p09/qa-report.json` | final visual/technical QA and owner-selection disposition | `883a4720b5dcedb5449859f418496f6f8b411a7001e6ae9480768039fcca7e9d` |
| `evidence/p09/verification-report.json` | 22/22 dependency-free verification plus 16/6 selection results | `d11757a2ae65836a77ab7bfe8639f5d9856fdda6469c0066e721e1483127a4c7` |
| `evidence/p09/previews/contact-sheet.png` | rendered full-resolution approved-selection sheet | `4edc73ca21fab5b92af47c13961f01993f830edbd2e78d3ff07e59de1d5ee80f` |
| `evidence/p09/previews/contact-sheet.html` | linked browser-scale approved/QA-only inventory | `b2445aad1cb77ca789e1afbe4dfd725c3c92c7fc62c1ee51b5665ae52ce92462` |
| `evidence/p09/source/Logo-TDTN-master.png` | byte-identical QA/provenance master | `020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e` |
| `evidence/p09/artifact-hashes.json` | deterministic inventory hash ledger for the complete P-09 evidence set except this record/self | `13623c0aa3621024fc7872b15dce9bd5f6f03490b7bf71822a6d9001b6d13134` |

## 7. Official platform boundary

`PLATFORM-ASSET-NOTES.md` records the current official boundary. Anthropic's current documented Claude plugin manifest does not establish an icon field. The current official bundled OpenAI skill reference supports relative `icon_small`/`icon_large` paths and provides a 400px PNG example but does not establish final rendered size. P-09 therefore creates candidates without inventing manifest keys or destination mappings; P-13 must verify exact installed-surface mapping later.

## 8. Owner decision and phase disposition

On 2026-08-15, the owner selected Option A:

- approve transparent, light-plate and dark-plate full-crest families at a 64px minimum;
- keep 32/48px files QA-only and excluded from v1.0.0 release use;
- do not create a simplified mark for v1.0.0.

This decision is locked as D-027 and recorded byte-for-byte in `APPROVED-BRAND-SELECTION.json`. P-09 has zero hard failure and is `passed`. G-06 remains `NOT-EVALUATED` because P-10/legal/provenance review has not started. The canonical skill tree and `agents/openai.yaml` remain unchanged; P-10/P-13 were not started.
