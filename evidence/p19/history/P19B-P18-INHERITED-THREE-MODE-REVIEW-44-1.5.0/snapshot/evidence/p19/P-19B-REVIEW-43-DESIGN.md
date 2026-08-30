# P-19B review-43 design contract — D-123 ridgeline

- Scope: replace only CAP-V19 presentation and display identity; preserve every non-target P-19 specimen after candidate-id normalization.
- Display identity: `ridgeline`; internal capability ID remains `CAP-V19`; canonical parent remains `line-chart`.
- Visual parent: P-18R6 review-17 template, including shell, typography roles, dot field, palette roles, framing, spacing rhythm and exact-alternative placement.
- Content: twelve independently authored service-latency distributions on one 0–120 ms linear domain.
- Distribution contract: Gaussian KDE, twenty shared evaluation positions, bandwidth 7 ms, global-maximum amplitude normalization.
- Statistical contract: each row includes nested 50%, 80% and 95% quantile bands plus one median dot; one shared median reference spans all rows.
- Emphasis: exactly one focal service uses the inherited coral role; other distributions use inherited blue/green roles.
- Geometry: arrow-free quantitative axis, consistent row spacing, thin 1–1.5 px strokes, identical geometry in all three modes.
- Accessibility: twelve-row exact alternative table with sample count and P2.5/P10/P25/median/P75/P90/P97.5 values.
- Reference boundary: the supplied screenshot was used only as a structural rubric. Labels, data, coordinates, SVG paths, prose and code are an independent reimplementation.
- Status: owner review pending; P-19C remains unauthorized and unperformed.
