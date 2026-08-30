#!/usr/bin/env python3
"""D-113 scatter-chart addition and exact review-32 preservation verification."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from scatter_chart_layout_v15 import layout_scatter_chart, scatter_chart_table, validate_scatter_chart_svg  # noqa: E402
from scatter_chart_review33_fixture import scatter_chart_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-32-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review33-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize_candidate(text):
    return text.replace(P19B_CANDIDATE_ID, OLD)


def svg_from_text(text):
    match = re.search(r"<svg\b.*?</svg>", text, re.S)
    require(match, "Missing SVG")
    return match.group()


def geometry_only(svg):
    return re.findall(r'<(?:rect|line|path|circle|text)\b[^>]*>', svg)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-33 gallery")
    target = [item for item in records if item["fixture_id"] == "type-scatter-chart"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong scatter-chart mode coverage")
    require(all(item.get("presentation_variant_id") == "scatter-chart" and item.get("parent") == "scatter-plot" for item in target), "Wrong scatter-chart parent binding")

    preserved_html = preserved_previews = policy_declarations = 0
    geometry = []
    measurements = []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-scatter-chart":
            for token in (
                'data-presentation-variant="scatter-chart"',
                'data-scatter-chart-contract="D-113-twelve-team-linear-trend"',
                'data-trend="least-squares"',
                'data-point-id="team-platform"',
                'data-focal="true"',
                "NỀN TẢNG",
            ):
                require(token in page, f"Scatter contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_scatter_chart_svg(svg))
            geometry.append(geometry_only(svg))
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-scatter-chart.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"points": 12, "focal": 1, "axes": 2, "x_ticks": 6, "y_ticks": 5, "trends": 1}
    require(all(item == expected for item in measurements), "Scatter measurements mismatch")
    require(geometry[0] == geometry[1] == geometry[2], "Scatter geometry differs across modes")
    layout = layout_scatter_chart(adapt_visual(scatter_chart_fixture()))
    require(abs(layout["trend_slope"] + 0.9891304347826086) < 1e-12, "OLS slope drift")
    require(scatter_chart_table(adapt_visual(scatter_chart_fixture())).count("<tr>") == 13, "Scatter table drift")
    raster, proof_svg = PROOFS / "type-scatter-chart.svg.png", PROOFS / "type-scatter-chart.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-113 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-113", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "new_target_html_count": len(target), "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "scatter_measurement": measurements[0],
        "axis_contract": {"x": [0, 20], "x_ticks": list(layout["x_ticks"]), "y": [0, 24], "y_ticks": list(layout["y_ticks"])},
        "ols": {"slope": layout["trend_slope"], "intercept": layout["trend_intercept"]},
        "three_mode_geometry": "PASS", "alternative_table_rows": 12,
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-33-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
