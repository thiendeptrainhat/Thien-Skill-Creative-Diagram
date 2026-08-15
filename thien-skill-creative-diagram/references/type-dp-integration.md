# DP integration semantic grammar

**Canonical ID:** `dp-integration`  
**Capability:** `CAP-T26`  
**Family:** `integration-topology`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for source systems and partner feeds connected through a platform boundary to consumers.

## Required semantics

- Retain sources, platform services, consumers, boundaries, and direction.
- Preserve bidirectional integrations as two explicit directions or one declared bidirectional edge.

## Allowed abstract roles

- `source`
- `partner`
- `platform-service`
- `store`
- `consumer`
- `boundary`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed integration edges.
- Every source-to-consumer path must cross the declared platform boundary when that is the supplied story.

## Label rules

- Use supplied system and interface labels.
- Keep platform boundary labels separate from component labels.

## Complexity behavior

- Split by source or consumer domain while retaining shared platform services.
- Do not duplicate the platform core.

## Semantic invariants

- `requires-source-platform-consumer`
- `requires-boundary`
- `directed-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not treat tier promotion as integration topology.
- Do not infer consumers from unused outputs.

## Coverage

- Positive semantic test: `T-TYPE-26-SEM`.
- Boundary mutation: `remove-platform-consumer`.
- Later render smoke evidence remains required in each approved visual mode.
