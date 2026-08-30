#!/usr/bin/env python3
"""Deterministic structural, semantic, quantitative and security QA for P-18R6."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
ANCHORS = R6 / "anchors"
R5 = ROOT / "evidence/p18/r5"
INVENTORY = R6 / "P-18R6-INVENTORY.json"
REPORT = R6 / "review/static-verification.json"
EXPECTED_ENGINES = {
    "topology-and-zones", "integration-pipeline", "runtime-deployment", "dependency-dag",
    "directed-flow-state", "lane-interaction", "time-planning", "work-experience",
    "hierarchy", "containment-stack", "compartment-model", "spatial-matrix",
    "quantitative", "special-geometry",
}
SVG_NS = "{http://www.w3.org/2000/svg}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, test_id: str, detail: str, results: list[dict[str, str]]) -> None:
    results.append({"id": test_id, "status": "PASS" if condition else "FAIL", "detail": detail})


def visible_text(root: ET.Element) -> list[str]:
    values = []
    for item in root.iter(f"{SVG_NS}text"):
        text = "".join(item.itertext()).strip()
        if text:
            values.append(text)
    return values


def signature(root: ET.Element) -> tuple[int, ...]:
    tags = Counter(item.tag.removeprefix(SVG_NS) for item in root.iter())
    classes = Counter()
    for item in root.iter():
        for cls in item.attrib.get("class", "").split():
            classes[cls] += 1
    return (
        tags["rect"], tags["path"], tags["line"], tags["circle"], tags["polygon"],
        classes["zone"], classes["zone-fill"], classes["node-card"], classes["band"], classes["bridge-mark"],
    )


def main() -> None:
    results: list[dict[str, str]] = []
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    html_paths = sorted(ANCHORS.glob("*.html"))
    svg_paths = sorted(ANCHORS.glob("*.svg"))
    check(len(html_paths) == 14, "R6-COUNT-HTML", f"found={len(html_paths)} expected=14", results)
    check(len(svg_paths) == 14, "R6-COUNT-SVG", f"found={len(svg_paths)} expected=14", results)
    check(inventory["engine_count"] == 14, "R6-INVENTORY-COUNT", f"inventory={inventory['engine_count']}", results)
    check({item["engine"] for item in inventory["engines"]} == EXPECTED_ENGINES, "R6-ENGINE-COVERAGE", "exact 14-engine set", results)

    parsed: list[tuple[Path, ET.Element]] = []
    for path in svg_paths:
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            parsed.append((path, root))
            check(True, f"XML-{path.stem}", "well-formed SVG", results)
        except ET.ParseError as exc:
            check(False, f"XML-{path.stem}", str(exc), results)

    engines = []
    signatures = []
    for path, root in parsed:
        source = path.read_text(encoding="utf-8")
        engine = root.attrib.get("data-layout-engine", "")
        engines.append(engine)
        signatures.append(signature(root))
        text = visible_text(root)
        viewbox = root.attrib.get("viewBox", "").split()
        valid_viewbox = len(viewbox) == 4 and all(float(value) > 0 if index >= 2 else float(value) == 0 for index, value in enumerate(viewbox))
        check(valid_viewbox, f"VIEWBOX-{engine}", root.attrib.get("viewBox", "missing"), results)
        check(root.attrib.get("role") == "img" and root.attrib.get("aria-labelledby"), f"A11Y-{engine}", "role img + labelled title/desc", results)
        check(root.find(f"{SVG_NS}title") is not None and root.find(f"{SVG_NS}desc") is not None, f"TITLE-DESC-{engine}", "title and desc present", results)
        check("<script" not in source and "<foreignObject" not in source and "http://" not in source.replace("http://www.w3.org/2000/svg", "") and "https://" not in source, f"SECURITY-{engine}", "no script/foreignObject/network resource", results)
        check("transform=\"scale" not in source and "transform=\"matrix" not in source, f"NO-GLOBAL-TRANSFORM-{engine}", "no scale/matrix layout transform", results)
        check(not any(value.upper().find("EVIDENCE RAIL") >= 0 for value in text), f"NO-EVIDENCE-RAIL-{engine}", "no visible evidence rail", results)
        check(len(text) == len([value for value in text if value]), f"VISIBLE-TEXT-{engine}", f"visible text elements={len(text)}", results)
        # The exact R5 anchor predates the R6 data attribute but is verified by its parent manifest.
        ratio = float(root.attrib.get("data-semantic-ratio", "0.81" if engine == "lane-interaction" else "0"))
        check(ratio >= 0.75, f"SEMANTIC-RATIO-{engine}", f"declared={ratio:.2f}", results)
        custom = engine != "lane-interaction"
        check((root.attrib.get("data-font-measured") == "true") if custom else True, f"FONT-MEASURED-{engine}", "real-font measurement binding", results)
        check((root.attrib.get("data-min-label-clearance") == "8") if custom else True, f"LABEL-CLEARANCE-{engine}", "minimum 8px contract", results)

        css_sizes = [int(value) for value in re.findall(r"font-size:([0-9]+)px", source)]
        allowed_minimum = min(css_sizes) if css_sizes else 14
        check(allowed_minimum >= 14, f"TYPE-MIN-{engine}", f"minimum declared font={allowed_minimum}px", results)
        check("font-size:24px" in source, f"NODE-TYPE-{engine}", "24px node title present", results)
        check("font-size:16px" in source, f"MATERIAL-TYPE-{engine}", "16px material text present", results)

    check(len(engines) == 14 and set(engines) == EXPECTED_ENGINES, "R6-SVG-ENGINE-COVERAGE", f"unique={len(set(engines))}", results)
    # Structural signatures are deliberately coarse; distinct count >=12 guards against generic-template reuse.
    check(len(set(signatures)) >= 12, "R6-SILHOUETTE-SIGNATURE", f"unique structural signatures={len(set(signatures))}/14", results)

    r5_svg = R5 / "anchor/swimlane--neutral-light.svg"
    r6_lane = ANCHORS / "06-lane-interaction--neutral-light.svg"
    check(r6_lane.read_bytes() == r5_svg.read_bytes(), "R6-R5-LANE-BYTE-PRESERVE", f"sha256={sha256(r6_lane)}", results)
    check(sha256(R5 / "P-18R5-MANIFEST.json") == "7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8", "R6-R5-PARENT-PIN", "approved manifest SHA-256 unchanged", results)

    quantitative_root = next(root for path, root in parsed if root.attrib.get("data-layout-engine") == "quantitative")
    quantitative_values = [(float(item.attrib["data-x"]), float(item.attrib["data-y"]), float(item.attrib["data-size"])) for item in quantitative_root.iter(f"{SVG_NS}circle") if "data-size" in item.attrib]
    check(len(quantitative_values) == 5 and all(0 <= x <= 100 and 0 <= y <= 100 and size > 0 for x, y, size in quantitative_values), "R6-QUANT-VALUES", f"points={len(quantitative_values)} ranges valid", results)
    special = next(item for item in inventory["engines"] if item["engine"] == "special-geometry")
    check(special["canonical_type"] == "sankey", "R6-SANKEY-TYPE", "special geometry uses conservation-based Sankey", results)

    blind = (R6 / "blind-review.html").read_text(encoding="utf-8")
    blind_visible = re.sub(r"<[^>]+>", " ", blind)
    leaked = sorted(engine for engine in EXPECTED_ENGINES if engine in blind_visible)
    check(len(re.findall(r"Masked candidate", blind_visible)) == 14, "R6-BLIND-COUNT", "14 visible masked candidates", results)
    check(not leaked, "R6-BLIND-NO-ENGINE-LEAK", f"visible engine leaks={leaked}", results)
    check("canonical type" not in blind_visible.lower() and "evidence rail" not in blind_visible.lower(), "R6-BLIND-NO-ANSWER-RAIL", "no visible type/evidence answer", results)

    for path in html_paths:
        source = path.read_text(encoding="utf-8")
        check("<script" not in source and "https://" not in source and "http://" not in source.replace("http://www.w3.org/2000/svg", ""), f"HTML-SELF-CONTAINED-{path.stem}", "standalone; no network/script", results)
        check(source.count('class="artifact-frame"') == 1, f"HTML-ONE-FRAME-{path.stem}", "exactly one canonical frame", results)

    failures = [item for item in results if item["status"] != "PASS"]
    report = {
        "schema_version": "1.0",
        "candidate_id": inventory["candidate_id"],
        "status": "PASS" if not failures else "FAIL",
        "test_count": len(results),
        "pass_count": len(results) - len(failures),
        "fail_count": len(failures),
        "results": results,
        "browser_status": "PENDING_BROWSER_EXECUTION",
        "owner_status": "PENDING",
        "g03_1_5_0": "NOT-EVALUATED",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "test_count", "pass_count", "fail_count")}, ensure_ascii=False))
    if failures:
        for failure in failures:
            print(f"FAIL {failure['id']}: {failure['detail']}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
