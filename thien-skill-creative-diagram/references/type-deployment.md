# Deployment semantic grammar

**Canonical ID:** `deployment`  
**Capability:** `CAP-T35`  
**Family:** `runtime-topology`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for runtime artifacts placed on supplied zones and hosts with replicas, ports, and runtime relations.

## Required semantics

- Preserve every supplied placement field.
- Keep positive replica counts, port labels, and cross-zone relations exact.

## Allowed abstract roles

- `artifact`
- `host`
- `zone`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed edges that preserve action-specific kind and label; optional relation kind may be runtime, dependency, or flow.
- Keep logical architecture distinct from runtime placement.

## Label rules

- Use exact zone, host, artifact, replica, and port labels.
- Disclose unknown placement rather than guessing.

## Complexity behavior

- Split dense zones while retaining placement identity.
- Do not duplicate one runtime artifact for presentation.

## Semantic invariants

- `deployment-placement-valid`
- `directed-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not substitute a logical component map.
- Do not invent ports, hosts, or replicas.

## Coverage

- Positive semantic test: `T-TYPE-35-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-35-BOUND-01`, `T-TYPE-35-HARD-01`, and `T-TYPE-35-A11Y-01`.
- Boundary mutation: `remove-deployment-placement`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
