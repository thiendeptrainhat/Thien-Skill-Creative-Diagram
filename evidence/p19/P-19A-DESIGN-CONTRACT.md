# P-19A — 39+4 visual-adapter design contract

**Candidate:** `P19A-THIRTY-NINE-PLUS-FOUR-ADAPTERS-1.5.0`  
**Authority:** owner instruction on 2026-08-27; D-078  
**Maturity:** implementation subphase; P-19B/P-19C remain unauthorized  
**Primary profile:** standalone executive artifact  
**Modules:** design system, data visualization, chart mechanics, localization, accessibility, browser-verification boundary

- **Outcome:** one canonical, deterministic adapter layer that maps each of 39 canonical types and four approved capabilities to the exact P-18R4 14-engine foundation without generic fallback.
- **Audience:** P-19B renderer implementation and QA reviewers.
- **Single job:** convert validated semantic IR into an engine-specific layout plan that preserves meaning, quantitative truth, reading order, typography constraints, geometry constraints, and accessible-alternative intent.
- **Success signal:** 39/39 type adapters, 4/4 capability adapters, 14/14 engine bindings, unique silhouette declarations, focused and full regression PASS, and zero HTML/SVG/gallery output.
- **Approved inputs and source authority:** `PROJECT-CONTRACT.md`; `PLAN.md`; exact P-18R4 foundation; exact owner-approved P-18R5 review-04 and P-18R6 review-17; P-17 semantic source and fixtures.
- **Constraints and risks:** clean-room-oriented independent reimplementation; exact P-18R5/R6 artifacts immutable; no font download/install; no `dist/`, publication mirror, package, Git, tag, or Release mutation; no P-19B mode derivation or 129-HTML gallery.
- **Existing-system decisions:** `preserve` P-18 typography/geometry/14-engine mapping and P-17 semantic validators; `extend` with adapter registry and engine-specific semantic projections; no `repair` or `retire` decision in P-19A.
- **Visual thesis:** each diagram family must remain recognizable from its semantic silhouette before styling, while quantitative and accessibility truth remain inspectable as structured data.
- **Signature element:** a unique, explicit silhouette declaration for every canonical type and capability under its locked engine.
- **Variance / motion / density:** 3 / 0 / 7. P-19A creates no motion or rendered composition.
- **Semantic palette:** inherited from the owner-approved kernel; not emitted or changed in this subphase.
- **Typography:** preserve Instrument Serif / Geist / Geist Mono direction, explicit-user-font precedence, real-font measurement before layout, Vietnamese glyph coverage, 16px material minimum, and no shrink-to-fit.
- **Geometry:** content-fit artboard; ports before routing; obstacle-aware routes; 8px minimum label/connector clearance; no global post-layout transform.
- **Accessibility:** preserve accessible name, description, reading order, data-alternative requirement, and declare a type-specific alternative representation.
- **Verification:** exact P-18R4 mapping comparison; deterministic adapter-plan comparison; all semantic fixtures; capability quantitative assertions; invalid-semantic fail-closed tests; canonical reference drift check; full regression; Python/JSON static checks; exact P-18R5/R6 manifest hash checks.
- **Rights and provenance:** all new code and prose are independently authored for this repository; no upstream code, prose, CSS, SVG, template, specimen, font, or asset is copied.
- **Approved exceptions:** browser rendering is not executed because P-19A emits no executable web artifact; this is `not run (out of scope)`, not a browser PASS.
- **Open questions:** none for P-19A. Starting P-19B requires a new explicit owner authorization.

