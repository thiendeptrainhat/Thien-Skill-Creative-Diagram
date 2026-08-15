# Semantic grammar index

Load only the selected canonical type reference. The registry contains exactly 27 types; variants and patterns never add another type.

| Type | Capability | Family | Reference |
|---|---|---|---|
| `architecture` | `CAP-T01` | `topology` | [type-architecture.md](type-architecture.md) |
| `it-current-state` | `CAP-T02` | `landscape` | [type-it-current-state.md](type-it-current-state.md) |
| `flowchart` | `CAP-T03` | `decision-flow` | [type-flowchart.md](type-flowchart.md) |
| `sequence` | `CAP-T04` | `ordered-interaction` | [type-sequence.md](type-sequence.md) |
| `state-machine` | `CAP-T05` | `state-transition` | [type-state-machine.md](type-state-machine.md) |
| `er-data-model` | `CAP-T06` | `data-model` | [type-er-data-model.md](type-er-data-model.md) |
| `timeline` | `CAP-T07` | `temporal` | [type-timeline.md](type-timeline.md) |
| `swimlane` | `CAP-T08` | `owned-process` | [type-swimlane.md](type-swimlane.md) |
| `quadrant` | `CAP-T09` | `quantitative-position` | [type-quadrant.md](type-quadrant.md) |
| `radar` | `CAP-T10` | `multivariate-quantitative` | [type-radar.md](type-radar.md) |
| `loop-flywheel` | `CAP-T11` | `cycle` | [type-loop-flywheel.md](type-loop-flywheel.md) |
| `nested` | `CAP-T12` | `containment` | [type-nested.md](type-nested.md) |
| `tree` | `CAP-T13` | `hierarchy` | [type-tree.md](type-tree.md) |
| `org-chart` | `CAP-T14` | `organization` | [type-org-chart.md](type-org-chart.md) |
| `layer-stack` | `CAP-T15` | `ordered-layers` | [type-layer-stack.md](type-layer-stack.md) |
| `venn` | `CAP-T16` | `set-membership` | [type-venn.md](type-venn.md) |
| `pyramid-funnel` | `CAP-T17` | `ordered-quantitative` | [type-pyramid-funnel.md](type-pyramid-funnel.md) |
| `bar-chart` | `CAP-T18` | `categorical-quantitative` | [type-bar-chart.md](type-bar-chart.md) |
| `line-chart` | `CAP-T19` | `ordered-quantitative` | [type-line-chart.md](type-line-chart.md) |
| `gantt` | `CAP-T20` | `temporal-dependency` | [type-gantt.md](type-gantt.md) |
| `scatter-plot` | `CAP-T21` | `paired-quantitative` | [type-scatter-plot.md](type-scatter-plot.md) |
| `high-level` | `CAP-T22` | `platform-overview` | [type-high-level.md](type-high-level.md) |
| `process` | `CAP-T23` | `artifact-process` | [type-process.md](type-process.md) |
| `medallion` | `CAP-T24` | `tier-promotion` | [type-medallion.md](type-medallion.md) |
| `data-flow` | `CAP-T25` | `data-movement` | [type-data-flow.md](type-data-flow.md) |
| `dp-integration` | `CAP-T26` | `integration-topology` | [type-dp-integration.md](type-dp-integration.md) |
| `dp-security-matrix` | `CAP-T27` | `permission-matrix` | [type-dp-security-matrix.md](type-dp-security-matrix.md) |

Use `scripts/semantic_grammars.py` for deterministic validation and `scripts/semantic_patterns.py` for pattern transformation. Use `capability-map.json` to resolve phase ownership, selector, fallback, implementation mapping, and test ID for every locked capability.
