# Gate decision record — target v2.0.0

This record began as the D-130 readiness packet. D-131 now records the owner's exact-candidate approvals. All v2.0.0 gates are `PASS`; external/repository execution remains on hold pending a separate explicit command.

| Gate | Result | Approved evidence | Approval/limit |
|---|---|---|---|
| `G-00@2.0.0` | `PASS` | Governance records D-130/D-131, P-20 scope, target 2.0.0, immutable lineage and execution hold. | Owner approved 2026-08-31. |
| `G-01@2.0.0` | `PASS` | P-16 exact upstream/provenance snapshot is preserved; v2 source manifest binds commit `648c2a5…eed3`. | Owner approved version-scoped provenance rebind. |
| `G-02@2.0.0` | `PASS` | Exact approved 39 canonical + four capability product/test contract is unchanged. | Owner approved version-scoped contract rebind. |
| `G-03@2.0.0` | `PASS` | Exact P-18 review-17 manifest `7925c1…a03a` is unchanged. | Owner approved version-scoped visual-foundation rebind. |
| `G-04@2.0.0` | `PASS` | Exact P-17/P-18/P-19 lineage unchanged; P-20 checks preserve `14 + 93 = 107` and D-128 flexibility. | Owner approved the exact source/gallery evidence for v2.0.0. |
| `G-05@2.0.0` | `PASS` | `TCD-PACKAGES-2.0.0-RC1`; 26/26 package checks, 414/414 regression and extracted smoke/manifest checks pass. | Owner approved the exact three ZIP hashes. |
| `G-06@2.0.0` | `PASS` | `TCD-LEGAL-2.0.0-RC1`, aggregate `93643da0…f29c0`; exact brand-byte carry-forward candidate. | Owner approved and explicitly waived independent Vietnamese-lawyer review. This is not a lawyer sign-off. |
| `G-07@2.0.0` | `PASS` | Exact `TCD-RELEASE-2.0.0-RC1`, manifest SHA-256 `2905d4d3945a75ba9b644aece005bcb6de5bb2278ca8f7e47a4247189c77be72`. | Exact release candidate approved; execution remains on hold. |

## Owner approval

Owner statement received on 2026-08-31:

> tôi duyệt hết, không cần luật sư

D-131 interprets this as approval of all exact v2.0.0 gate inputs and the exact release candidate. The owner waives independent lawyer review for `G-06@2.0.0` and accepts that risk. The approval does not claim that a lawyer reviewed the legal bytes.

## Execution hold

No approved byte was changed by this decision. The three v2 ZIPs remain under `evidence/p20/candidate-dist/`; historical `dist/` v1.0.0 and publication/remotes remain untouched. Copy/promotion to `dist`, commit, push, tag, publication, and creating or changing a Release require a separate explicit owner command.
