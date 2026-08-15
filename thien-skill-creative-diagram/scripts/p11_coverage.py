"""Authoritative P-11 hard-failure-to-mutation coverage registry."""

from __future__ import annotations


def _row(category: str, test_id: str, detector: str, mutation_test: str) -> dict[str, str]:
    return {"category": category, "test_id": test_id, "detector": detector, "mutation_test": mutation_test, "status": "detected"}


P11_HARD_FAILURES = {
    "schema-json-invalid": _row("contract", "T-P11-SCHEMA-01", "validate_json_documents", "RepositoryQATests.test_invalid_json_mutation_is_detected"),
    "reference-link-missing": _row("contract", "T-P11-LINK-01", "validate_markdown_links", "RepositoryQATests.test_missing_and_escaping_link_mutations_are_detected"),
    "reference-link-escape": _row("contract", "T-P11-LINK-02", "validate_markdown_links", "RepositoryQATests.test_missing_and_escaping_link_mutations_are_detected"),
    "type-coverage-mismatch": _row("coverage", "T-P11-COVERAGE-01", "validate_type_coverage", "RepositoryQATests.test_type_coverage_mutation_is_detected"),
    "build-drift": _row("determinism", "T-P11-DET-01", "validate_determinism", "RepositoryQATests.test_determinism_mutation_is_detected"),
    "node-out-of-bounds": _row("geometry", "T-P11-GEO-01", "validate_geometry_contract", "GeometryMutationTests.test_bounds_clipping_overlap_and_endpoint_mutations_are_detected"),
    "graphic-out-of-bounds": _row("geometry", "T-P11-GEO-02", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_duplicate_id_name_external_and_bounds_mutations_are_detected"),
    "material-clipping-risk": _row("geometry", "T-P11-GEO-03", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_clipping_compression_ellipsis_and_unicode_mutations_are_detected"),
    "node-overlap": _row("geometry", "T-P11-GEO-04", "validate_geometry_contract", "GeometryMutationTests.test_bounds_clipping_overlap_and_endpoint_mutations_are_detected"),
    "route-endpoint-invalid": _row("geometry", "T-P11-GEO-05", "validate_geometry_contract", "GeometryMutationTests.test_bounds_clipping_overlap_and_endpoint_mutations_are_detected"),
    "route-endpoint-missing": _row("geometry", "T-P11-GEO-06", "validate_geometry_contract", "GeometryMutationTests.test_bounds_clipping_overlap_and_endpoint_mutations_are_detected"),
    "route-crosses-node": _row("geometry", "T-P11-GEO-07", "validate_geometry_contract", "GeometryMutationTests.test_unrelated_node_crossing_mutation_is_detected"),
    "route-crossing-unmarked": _row("geometry", "T-P11-GEO-08", "validate_geometry_contract", "GeometryMutationTests.test_connector_crossing_and_shared_attach_mutations_are_detected"),
    "shared-attach-point": _row("geometry", "T-P11-GEO-09", "validate_geometry_contract", "GeometryMutationTests.test_connector_crossing_and_shared_attach_mutations_are_detected"),
    "duplicate-svg-id": _row("geometry", "T-P11-GEO-10", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_duplicate_id_name_external_and_bounds_mutations_are_detected"),
    "accessible-name-missing": _row("accessibility", "T-P11-A11Y-01", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_duplicate_id_name_external_and_bounds_mutations_are_detected"),
    "reading-order-mismatch": _row("accessibility", "T-P11-A11Y-02", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_read_order_and_material_loss_mutations_are_detected"),
    "contrast-failure": _row("accessibility", "T-P11-A11Y-03", "validate_contrast_contract", "SVGAccessibilityTypographyTests.test_contrast_and_non_color_state_mutations_are_detected"),
    "color-only-state": _row("accessibility", "T-P11-A11Y-04", "validate_state_redundancy", "SVGAccessibilityTypographyTests.test_contrast_and_non_color_state_mutations_are_detected"),
    "typography-compressed": _row("vietnamese-typography", "T-P11-VI-01", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_clipping_compression_ellipsis_and_unicode_mutations_are_detected"),
    "material-ellipsis": _row("vietnamese-typography", "T-P11-VI-02", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_clipping_compression_ellipsis_and_unicode_mutations_are_detected"),
    "unicode-not-nfc": _row("vietnamese-typography", "T-P11-VI-03", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_clipping_compression_ellipsis_and_unicode_mutations_are_detected"),
    "material-label-missing": _row("vietnamese-typography", "T-P11-VI-04", "validate_svg_contract", "SVGAccessibilityTypographyTests.test_read_order_and_material_loss_mutations_are_detected"),
    "carrier-ir-mismatch": _row("quantitative", "T-P11-QUANT-01", "validate_carrier_equivalence", "QuantitativeIntegrityTests.test_three_carriers_normalize_equivalently_including_zero_negative_and_missing"),
    "quantitative-unit-missing": _row("quantitative", "T-P11-QUANT-02", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_numeric_unit_missingness_and_source_render_mutations_are_detected"),
    "missingness-implicit": _row("quantitative", "T-P11-QUANT-03", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_numeric_unit_missingness_and_source_render_mutations_are_detected"),
    "bar-zero-baseline": _row("quantitative", "T-P11-QUANT-04", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_numeric_unit_missingness_and_source_render_mutations_are_detected"),
    "source-render-value-mismatch": _row("quantitative", "T-P11-QUANT-05", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_numeric_unit_missingness_and_source_render_mutations_are_detected"),
    "scatter-coordinate-out-of-domain": _row("quantitative", "T-P11-QUANT-06", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_scatter_radar_quadrant_and_funnel_mutations_are_detected"),
    "radar-scale-incompatible": _row("quantitative", "T-P11-QUANT-07", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_scatter_radar_quadrant_and_funnel_mutations_are_detected"),
    "quadrant-coordinate-out-of-domain": _row("quantitative", "T-P11-QUANT-08", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_scatter_radar_quadrant_and_funnel_mutations_are_detected"),
    "funnel-order-invalid": _row("quantitative", "T-P11-QUANT-09", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_scatter_radar_quadrant_and_funnel_mutations_are_detected"),
    "timezone-missing": _row("quantitative", "T-P11-QUANT-10", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_temporal_date_timezone_duration_order_and_render_mutations_are_detected"),
    "temporal-duration-invalid": _row("quantitative", "T-P11-QUANT-11", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_temporal_date_timezone_duration_order_and_render_mutations_are_detected"),
    "temporal-order-invalid": _row("quantitative", "T-P11-QUANT-12", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_temporal_date_timezone_duration_order_and_render_mutations_are_detected"),
    "source-render-time-mismatch": _row("quantitative", "T-P11-QUANT-13", "validate_quantitative_ir", "QuantitativeIntegrityTests.test_temporal_date_timezone_duration_order_and_render_mutations_are_detected"),
    "fidelity-equation-invalid": _row("import-fidelity", "T-P11-FID-01", "validate_fidelity", "SecurityMotionPackageTests.test_fidelity_equation_and_invention_mutations_are_detected"),
    "invented-content": _row("import-fidelity", "T-P11-FID-02", "validate_fidelity", "SecurityMotionPackageTests.test_fidelity_equation_and_invention_mutations_are_detected"),
    "mermaid-executable-feature": _row("import-security", "T-P11-SEC-01", "safe_import.parse_mermaid", "MermaidTests.test_directives_links_html_and_click_actions_fail"),
    "xml-external-feature": _row("import-security", "T-P11-SEC-02", "safe_import.parse_drawio", "DrawioTests.test_dtd_entity_and_missing_png_model_fail_before_resolution"),
    "decompression-over-limit": _row("import-security", "T-P11-SEC-03", "safe_import.parse_drawio", "DrawioTests.test_decompression_ratio_abuse_is_rejected"),
    "json-depth-over-limit": _row("import-security", "T-P11-SEC-04", "safe_import.parse_json_text", "SafeTextCarrierTests.test_json_rejects_duplicate_nonfinite_and_deep_input"),
    "network-side-effect": _row("import-security", "T-P11-SEC-05", "safe import has no network path", "SecurityMotionPackageTests.test_import_security_codes_and_zero_network_side_effect"),
    "static-frame-incomplete": _row("motion", "T-P11-MOT-01", "validate_motion_html", "SecurityMotionPackageTests.test_motion_static_reduced_print_focus_and_controls_mutations_are_detected"),
    "reduced-motion-missing": _row("motion", "T-P11-MOT-02", "validate_motion_html", "SecurityMotionPackageTests.test_motion_static_reduced_print_focus_and_controls_mutations_are_detected"),
    "print-frame-missing": _row("motion", "T-P11-MOT-03", "validate_motion_html", "SecurityMotionPackageTests.test_motion_static_reduced_print_focus_and_controls_mutations_are_detected"),
    "focus-style-missing": _row("motion", "T-P11-MOT-04", "validate_motion_html", "SecurityMotionPackageTests.test_motion_static_reduced_print_focus_and_controls_mutations_are_detected"),
    "motion-controls-missing": _row("motion", "T-P11-MOT-05", "validate_motion_html", "SecurityMotionPackageTests.test_motion_static_reduced_print_focus_and_controls_mutations_are_detected"),
    "package-path-absolute": _row("package-hygiene", "T-P11-PKG-01", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "package-path-traversal": _row("package-hygiene", "T-P11-PKG-02", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "package-development-file": _row("package-hygiene", "T-P11-PKG-03", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "package-secret-file": _row("package-hygiene", "T-P11-PKG-03B", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "package-qa-only-file": _row("package-hygiene", "T-P11-PKG-04", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "package-duplicate-path": _row("package-hygiene", "T-P11-PKG-05", "validate_package_inventory", "SecurityMotionPackageTests.test_package_hygiene_mutations_are_detected"),
    "golden-drift": _row("golden", "T-P11-GOLD-01", "golden_review.compare_manifest", "ImmutableGoldenReviewTests.test_drift_missing_approval_and_path_escape_mutations_are_detected"),
    "golden-approval-missing": _row("golden", "T-P11-GOLD-02", "golden_review.load_manifest", "ImmutableGoldenReviewTests.test_drift_missing_approval_and_path_escape_mutations_are_detected"),
    "golden-path-escape": _row("golden", "T-P11-GOLD-03", "golden_review.compare_manifest", "ImmutableGoldenReviewTests.test_drift_missing_approval_and_path_escape_mutations_are_detected"),
    "golden-auto-update": _row("golden", "T-P11-GOLD-04", "golden_review CLI has no update operation", "ImmutableGoldenReviewTests.test_cli_exposes_compare_only_and_rejects_update"),
}


__all__ = ["P11_HARD_FAILURES"]
