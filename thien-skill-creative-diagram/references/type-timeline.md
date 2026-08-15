# Timeline semantic grammar

**Canonical ID:** `timeline`  
**Capability:** `CAP-T07`  
**Family:** `temporal`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for events or milestones ordered by supplied dates or timestamps.

## Required semantics

- Retain every timestamp and timezone or an explicit unknown marker.
- Preserve duplicate local times as distinct events.

## Allowed abstract roles

- `event`
- `milestone`
- `period`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use optional chronology edges only when source order is semantic.
- Never imply causality from chronology alone.

## Label rules

- Use supplied event labels and exact temporal values.
- Disclose timezone uncertainty.

## Complexity behavior

- Split by era or track without changing chronological order.
- Never drop close-together events for legibility.

## Semantic invariants

- `requires-temporal-node`
- `chronological-node-order`
- `timezone-required`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not fabricate dates.
- Do not silently sort contradictory source order without a ledger entry.

## Coverage

- Positive semantic test: `T-TYPE-07-SEM`.
- Boundary mutation: `reverse-temporal-order`.
- Later render smoke evidence remains required in each approved visual mode.
