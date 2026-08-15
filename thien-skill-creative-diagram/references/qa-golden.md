# Automated QA and immutable golden review

Use this reference after semantic validation and before treating a rendered artifact as review-ready. The checks are deterministic, read-only, and dependency-free. They support technical QA; they do not replace browser, assistive-technology, owner-golden, benchmark, legal, or release approval.

## Run the quality layers

1. Run `scripts/qa_contract.py::audit_skill_tree` for JSON syntax, relative reference links, exact 27-type coverage, canonical-tree hygiene, and approved contrast pairs.
2. Run `validate_svg_contract` on SVG output. Pass the validated IR when material-label and narrative-order checks are required.
3. Run `validate_geometry_contract` with layout node boxes and connector routes. Declare a crossing or shared junction only when it is semantically intentional; absence of a declaration is a failure.
4. Run `validate_state_redundancy`, `validate_motion_html`, and `validate_contrast_contract` for the applicable artifact.
5. For quantitative inputs, run `validate_carrier_equivalence` before semantic mapping, then `validate_quantitative_ir` against the final SVG. This checks exact-data metadata for series charts and visible source dates for Gantt/Timeline.
6. Run `validate_fidelity` for imported data and `validate_package_inventory` on a proposed package file list. The latter validates an inventory only; it does not build an archive.

Every failure is stable and named. Treat a raised `QAFailure` as a hard failure; do not average it into a visual score or silently bypass the validator.

## Review approved goldens

Use `scripts/golden_review.py` only to compare approved artifacts:

```text
python3 scripts/golden_review.py --manifest <approved-manifest.json> --root <artifact-root> --json
```

The manifest must declare `immutable: true`, an approved status, relative paths, SHA-256 hashes, media types, and an approval reference. The command has no update option. A mismatch returns `golden-drift`, leaves all files unchanged, and requires a separately approved review workflow.

Do not put QA-only references, screenshots, contact sheets, previews, manifests, or evidence in a release package. Do not create or approve new goldens during ordinary rendering.

## Interpret evidence honestly

- Static validation is not a browser pass or WCAG conformance claim.
- A matching hash proves byte identity with the approved baseline, not visual correctness in every renderer.
- P-11 mutation coverage proves that each registered hard-failure family can be detected. P-12 owns benchmark execution and independent forward tests.
- If a compatible browser is unavailable, report browser verification as `blocked / not executable`; do not install or download a browser without authorization.

The complete registry is [p11-hard-failure-map.json](p11-hard-failure-map.json).
