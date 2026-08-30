# P-19B review-19 — D-099 Wardley-map remediation

Status: `implemented; automated verification PASS; owner review pending`

## Owner direction

Replace only the P-19 `wardley-map` with a detailed visibility/evolution map comparable in hierarchy and information density to the supplied image. The image is a visual rubric, not an implementation source.

## Reference analysis

- A plain vertical visibility axis and horizontal evolution axis establish the strategic frame.
- Four evolution regions are separated by restrained dashed guides.
- Open-circle components and thin, arrow-free dependency lines keep the value chain legible.
- Exactly one component carries the coral evolving signal; dashed arrow, outline and direct state text make the meaning independent of color.
- Labels sit directly by nodes; a compact legend explains only the essential mark types.

## Independent design contract

- Eight original illustrative components and nine dependency relations.
- Two linear normalized `0–1` axes: visibility on `y`, evolution on `x`.
- Four ordered stages: `Khởi nguyên`, `Tự xây dựng`, `Sản phẩm`, `Hàng hóa`, with three dashed boundaries.
- All dependency lines and both axes are plain and arrow-free.
- `Điều phối tác vụ` is the only evolving component and receives one dashed coral evolution arrow.
- Every component has a direct Vietnamese label; the accessible alternative is one exact table containing all eight components and nine dependencies.
- Neutral-light, neutral-dark and editorial reuse the same semantic material and exact geometry; only inherited P-18 semantic color roles vary.

## Design judgment

- **Preserve:** P-18 warm-paper/navy/coral grammar, type roles, fine dot field, restrained legend and direct evidence labels.
- **Repair:** replace the generic Wardley rendering with normalized strategic coordinates, explicit phase boundaries and a real dependency graph.
- **Extend:** add non-color evolving-state redundancy and a complete machine-checkable alternative table.
- **Retire:** remove the prior Wardley artwork only; no non-target visual, adapter registry or frozen artifact changes.

## Scope lock

The exact review-18 candidate was archived before mutation. Only three `wardley-map` HTML specimens and one neutral-light preview may change. The other 87 HTML specimens and 29 previews must remain identical after candidate-ID normalization. P-18, P-19A, package, `dist`, publication mirrors, Release and P-19C remain outside this change.

## Provenance

All fixture values, Vietnamese prose, IDs, normalized coordinates, layout, CSS and SVG are original to this repository. No code, coordinates, prose, CSS, SVG or template was copied from the attached image.
