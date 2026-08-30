# D-084 — Replace P-19 Sankey with the approved P-18 Sankey

User instruction: “bỏ sankey P-19,lấy sankey P-18”. This is adoption, not redesign.
Primary profile: executive artifact. Preserve approved composition, typography,
labels, data, ribbon paths, node bars, focal annotation, canvas and paint order.
Retire the old three-node/two-ribbon hard-coded renderer from active use.

Use the exact project-authored P-18R6 review-17 Sankey SVG as a hash-pinned local
asset. Neutral-light SVG and preview must be byte-identical to that source.
Dark/editorial may change only explicit paint colors and the mode attribute;
all geometry, text, numeric values and line styles remain unchanged. No upstream
asset or new style candidate is needed. This is reuse of the project's own approved
work; it does not reclassify upstream expression as project-owned.

The gallery's Sankey data comes from the approved SVG's seven nodes/nine flows,
12,000 CI minutes. Preserve an exact flow/value alternative table and source hash.
Do not render different user data using this fixed approved artwork: reject a
non-matching input explicitly. General-purpose Sankey layout is not claimed by
this replacement. Frozen minimal P-19A fixtures and adapters are unchanged.

One self-contained inline SVG remains in each HTML. Its original internal CSS
is retained and protected; preview extraction must not insert P-19 CSS over it.
Other 126 HTML must remain identical modulo candidate ID, and 42 other previews
byte-identical, including Gantt and flywheel. Archive review-04 before mutation.
Check source-byte equality, color-only derivation, data conservation, hashes,
exact 129 coverage and three local raster renders. Browser checks remain blocked
under the known URL policy, with no bypass or inherited browser PASS.

Scope: P-19B review-05 only. P-18 remains frozen; no P-19C, package, dist,
publication, Git or Release. Owner approval of the new overall candidate pending.
