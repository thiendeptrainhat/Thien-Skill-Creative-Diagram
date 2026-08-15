# Org chart semantic grammar

**Canonical ID:** `org-chart`  
**Capability:** `CAP-T14`  
**Family:** `organization`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for primary reporting, ownership, routing, and separately identified escalation relationships.

## Required semantics

- Preserve the primary manager relation.
- Keep escalation or dotted-line relations distinct.

## Allowed abstract roles

- `person`
- `role`
- `team`
- `vacancy`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Primary reporting edges form a forest or tree.
- Label non-primary relationships by kind.

## Label rules

- Use supplied person, role, and team labels.
- Do not infer seniority from order alone.

## Complexity behavior

- Split by department while retaining cross-department escalation.
- Do not omit vacancies or shared roles.

## Semantic invariants

- `requires-primary-reporting`
- `primary-reporting-acyclic`
- `distinguish-nonprimary-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not turn escalation into primary reporting.
- Do not assign an unprovided manager.

## Coverage

- Positive semantic test: `T-TYPE-14-SEM`.
- Boundary mutation: `remove-primary-reporting`.
- Later render smoke evidence remains required in each approved visual mode.
