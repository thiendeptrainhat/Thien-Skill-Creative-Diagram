# P-17 quantitative capability variants

These are capabilities, not canonical types 40–43. Validate the canonical parent first, then the named variant handler. Unit comparison uses Unicode NFC plus outer trimming, is case-sensitive, and performs no implicit conversion.

| Capability | Name | Parent | Semantic contract | Stable tests |
|---|---|---|---|---|
| `CAP-V17` | Dumbbell | `bar-chart` | Exactly two finite values per category on one shared linear domain; signed gap is second minus first. | `T-VAR-CAP-V17-POS-01`, `T-VAR-CAP-V17-BOUND-01`, `T-VAR-CAP-V17-HARD-01`, `T-VAR-CAP-V17-HARD-PARENT-01`, `T-VAR-CAP-V17-A11Y-01` |
| `CAP-V18` | Slopegraph | `line-chart` | Every series has the same two distinct states; direction, rank, ties, and crossings derive from source values. | `T-VAR-CAP-V18-POS-01`, `T-VAR-CAP-V18-BOUND-01`, `T-VAR-CAP-V18-HARD-01`, `T-VAR-CAP-V18-HARD-PARENT-01`, `T-VAR-CAP-V18-A11Y-01` |
| `CAP-V19` | Ridgeline | `line-chart` | Every series supplies finite samples plus one shared histogram or explicit-bandwidth Gaussian KDE contract with global-max amplitude normalization. | `T-VAR-CAP-V19-POS-01`, `T-VAR-CAP-V19-BOUND-01`, `T-VAR-CAP-V19-HARD-01`, `T-VAR-CAP-V19-HARD-PARENT-01`, `T-VAR-CAP-V19-A11Y-01` |
| `CAP-V20` | Bubble | `scatter-plot` | Every observation has finite x, y, and non-negative size; data-bearing area, not radius, represents size. | `T-VAR-CAP-V20-POS-01`, `T-VAR-CAP-V20-BOUND-01`, `T-VAR-CAP-V20-HARD-01`, `T-VAR-CAP-V20-HARD-PARENT-01`, `T-VAR-CAP-V20-A11Y-01` |

Quantitative checks use `T-QUANT-DUMBBELL-*`, `T-QUANT-SLOPE-*`, `T-QUANT-RIDGE-*`, and `T-QUANT-BUBBLE-*`. Render tests remain deferred to the authorized visual phases.
