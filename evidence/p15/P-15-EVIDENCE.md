# P-15 — Publication Patch Evidence

**Date:** 2026-08-16
**Authorization:** D-039
**Authorized scope:** root license discovery, README logo presentation, governance/evidence, commit and push directly to private `main`
**Phase disposition:** `passed` under D-040

## Scope boundary

This patch changes only repository presentation and audit records. It does not change runtime code, package contents, version, legal wording, approved brand bytes, tag `v1.0.0`, GitHub Release metadata or Release assets. No package was rebuilt.

## Exact source bindings

| Item | Path | SHA-256 | Result |
|---|---|---|---|
| Approved 400px logo derivative | `evidence/p09/candidates/full-crest-plate-light-400.png` | `69789949b4233d14a4010245a3a614b8e6fcfbd28cbae0e2f26e0a890faa1453` | PASS |
| Canonical approved license | `thien-skill-creative-diagram/LICENSE.md` | `64d88634fe7ad212049799d7febdbe574bd64574c1f75cfe065f2952a2906f31` | PASS |
| Repository-root license | `LICENSE.md` | `64d88634fe7ad212049799d7febdbe574bd64574c1f75cfe065f2952a2906f31` | PASS — byte-identical by `cmp` |
| Updated repository README | `README.md` | `c41e0588e276655b0abe13d8fb6b48bc4dcd0b9c67a2990729b098dc11d33d9e` | PASS |

The README uses the already-published, owner-approved 400px evidence asset through a repository-relative path and links the repository-root license. It does not introduce a new logo derivative or a new license text.

## Frozen v1.0.0 invariants

| Artifact | SHA-256 | Result |
|---|---|---|
| Claude plugin ZIP | `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9` | unchanged |
| OpenAI plugin ZIP | `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c` | unchanged |
| Universal raw skill ZIP | `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f` | unchanged |
| `SHA256SUMS.txt` | `af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596` | unchanged |

Pre-push GitHub verification confirmed the target is `thiendeptrainhat/Thien-Skill-Creative-Diagram`, visibility `PRIVATE`, default branch `main`; annotated tag object `c91194cb454e7e04eafd2636f98a87a6b32fe24f` and all four Release asset digests match the P-14 release record.

## Pre-push verification

- Full regression suite: 127/127 PASS.
- Package/parity/hygiene/smoke verifier: 23/23 PASS.
- Sanitized publication mirror verifier: 5/5 PASS.
- Root/canonical license byte comparison: PASS.
- README logo path, logo file and root-license link: PASS.
- Publication mirror Git diff whitespace/error check: PASS.
- GitHub CLI authentication: valid owner session with repository scope.

## Remote closure

- Publication commit `9fdf15a5e140b5a366a415b59195de23be77ea3a` was pushed directly to private `main`.
- GitHub contents API reports root `LICENSE.md`, 51,371 bytes, blob `081562e91716ccf34afac7eac3fe8e48d4af53d2`.
- GitHub license detection reports `key: other`, `name: Other`, `spdx_id: NOASSERTION` and points to root `LICENSE.md`. This is the expected classification for the approved custom commercial source-available license; no standard/open-source license was substituted.
- GitHub contents API reports the updated root `README.md`, blob `e03c3b14749bf8aff01037eebfede325bf061dc7`, and the referenced approved logo file, blob `407cb432ad437c3f2c58eb2b2070a863cbb72144`, 85,814 bytes.
- Annotated tag object remains `c91194cb454e7e04eafd2636f98a87a6b32fe24f`.
- GitHub Release `v1.0.0` remains non-draft and non-prerelease; the three ZIP digests and `SHA256SUMS.txt` digest remain exactly as listed above.
- The audit-closure commit updates only authoritative phase status, D-040 and this evidence record. It does not move the tag or mutate the Release.

No open finding remains within the authorized publication-patch scope.
