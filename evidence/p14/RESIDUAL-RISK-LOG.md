# P-14 Residual Risk and Release Preconditions

**Date:** 2026-08-16  
**Candidate:** `TCD-RELEASE-1.0.0-RC1`  
**Current state:** v1.0.0 released; P-14 closure evidence recorded

## Residual risks requiring explicit owner acceptance

| ID | Severity | Residual condition | Existing control | Required decision |
|---|---|---|---|---|
| `P14-R01` | Medium | Browser/cross-browser execution was not completed because the in-app browser rejected the local `file://` QA surface. | Deterministic HTML/SVG, geometry/accessibility checks, immutable goldens and manual contact sheets passed; no browser claim is made. | Accepted by owner under D-035 on 2026-08-16. |
| `P14-R02` | Medium | The approved surface matrix has 0 `supported`, 13 `conditional` and 2 `unsupported` rows because live account/marketplace/fresh-session conditions were unavailable. | Package structure, Claude manifest and extracted runtime smoke passed; conditional/unsupported statuses remain explicit and cannot be advertised as supported. | Accepted by owner under D-035 on 2026-08-16. |
| `P14-R03` | Low | PNG output depends on an already available approved rasterizer; the canonical environment exercised transparent PNG→SVG/HTML fallback. | No dependency was installed and no PNG pass was claimed. | Keep the limitation in release notes. |
| `P14-R04` | Low | The bundled OpenAI validator could not run because PyYAML was unavailable; no dependency was installed. | Dependency-free manifest/path/asset validation passed against current official fields; G-05 passed with this disclosure. | Keep the tooling disclosure in release evidence. |

No open Critical or High product/quality/legal finding is recorded. The two High findings discovered in P-12 were corrected and closed before G-04.

## Blocking release preconditions

| ID | Condition | State | Resolution required before G-07 |
|---|---|---|---|
| `P14-B01` | Exact three ZIP files and the overall release candidate need owner approval. | resolved by D-035 | Owner approved `TCD-RELEASE-1.0.0-RC1` and all three frozen hashes. |
| `P14-B02` | Repository publication scope is not defined. | resolved by D-035/D-036 | Scope A is materialized as a deterministic sanitized mirror. Five files with actual owner-machine paths use stable placeholders; two generic security-pattern files remain unchanged; the original local corpus is preserved. |
| `P14-B03` | Local workspace is not a Git repository and has no remote. | resolved by D-038 | Only the sanitized mirror was initialized and pushed; the unsanitized audit source remains non-Git. |
| `P14-B04` | Private target repository cannot currently be verified. | resolved by read-only authenticated inspection | The exact owner-provided URL exists, displays the `Private` badge and an empty repository quick-setup surface. Connector/CLI limitations remain recorded but do not negate the direct authenticated observation. |
| `P14-B05` | G-07 and release authorization are absent. | resolved by D-037 | G-07 is `PASS`; exact init/commit/tag/push/release actions and README/license requirement are authorized. |

Generated `.pyc` cache directories observed during local verification were removed from `evidence/p10/` and `evidence/p12/`; no product, legal, brand, package or approval byte was changed.
