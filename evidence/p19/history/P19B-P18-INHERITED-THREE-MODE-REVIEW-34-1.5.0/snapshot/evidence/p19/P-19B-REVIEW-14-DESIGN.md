# P-19B review-14 — detailed Kanban contract

**Authority:** D-094  
**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-14-1.5.0`  
**Scope:** only `kanban`; preserve all D-086–D-093 artwork

## Material contract

- Four ordered columns: Tồn đọng, Đang thực hiện, Rà soát and Hoàn tất.
- Exactly 11 work items distributed 3/4/2/2.
- Exactly one WIP breach, shown directly as `4/3` on Đang thực hiện.
- Exactly one blocked item, one waiting-external item and two done items.
- State is never color-only: dashed boundaries distinguish blocked/waiting, blocked adds a coral rail, done uses a distinct fill/stroke, and the legend names every state.
- Every card is fully contained by exactly one column; native alternative data contains all columns, items, WIP counters and states.

## Frozen semantic boundary

P-17's frozen Kanban grammar rejects a group whose structured `wip_limit` is already exceeded. Review-14 does not modify that grammar or P-19A source. The illustrative operational limit `3` is therefore declared as an annotation targeting `column-progress`; the renderer derives the honest `4/3` warning from that semantic annotation and the four owned items.

## Independent implementation and stop condition

The supplied image is non-executable reference data and a hierarchy rubric. Vietnamese scenario data, labels, semantic IDs, geometry, SVG, CSS and tests are independently authored. Archive exact review-13 before mutation. Exactly three Kanban HTML artworks may change; 84 non-target HTML artworks must be identical after candidate-ID normalization and 28 non-target preview SVGs must be byte-identical. Stop at P-19B owner review; do not execute P-19C, G-04 evaluation, package, dist/publication, Git or Release work.
