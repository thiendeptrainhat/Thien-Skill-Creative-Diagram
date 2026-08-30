# P-18R3 verification and replacement freeze

**Date:** 2026-08-23  
**Authority:** D-050  
**Candidate:** `P18-PILOT-1.5.0-VISUAL-CRAFT-REPLACEMENT`

## Result

P-18R3 is complete. The replacement candidate is frozen for owner review at manifest SHA-256 `4fb00b7f1b898a4a59b6fd4092b8f15f35ddd5b4a51c14124911b42a145ed5a7` and source-bundle SHA-256 `30fc0ce7c5721a21fbe42cf5dd742ef3b23895e6f45070069cfa7dc34c3388c2`.

| Gate/check | Result |
|---|---|
| Generator drift | PASS |
| Focused P-18 tests | PASS — 10/10 |
| Per-artifact semantic, quantitative, geometry, accessibility, contrast, security/standalone, visual contract | PASS — 36/36 |
| Chrome browser QA | PASS — 108/108 at desktop/tablet/mobile |
| Visual-craft gate | PASS — 92/100; minimum dimension 4/5 |
| Blind silhouette | PASS — 12/12 |
| Five-second takeaway/focal path | PASS — 12/12 |
| Full canonical regression | PASS — 148/148 |
| `quick_validate.py` | DEFERRED — both available Python runtimes lack PyYAML; no dependency installation authorized |

`quick_validate.py` did not execute because its own undeclared runtime dependency is unavailable. This is recorded as environment-deferred, not converted to `PASS`. The canonical 148-test repository audit, including schema, links, type hygiene, contrast and package inventory policies, passed after removing generated `__pycache__` files and rerunning with bytecode writes disabled.

## Browser bindings

- `browser-runs/browser-batch-00.json`: 54/54 `PASS`, SHA-256 `d332a3bcab8eff068e0bdc913c1db46ec5479438eb6b2e937767155ed5b53bfa`.
- `browser-runs/browser-batch-18.json`: 54/54 `PASS`, SHA-256 `a186003e2903485149e2adadf54db1ed06ae0e5caf247463bb76f67505f0c8c2`.
- Across 108 runs: zero external request, console/page error, horizontal overflow, clipped text, text overlap, route-through-unrelated-node or wrong endpoint.

## Boundary

No canonical runtime integration, package build/rebuild, `dist/` mutation, publication-mirror refresh, commit, push, tag, Release change or P-19 work was performed. P-18 remains `in-progress` and `G-03@1.5.0` remains `NOT-EVALUATED` until the owner approves or rejects this exact frozen candidate.
