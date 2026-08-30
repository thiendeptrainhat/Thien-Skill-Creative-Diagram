"""Build and verify the exact P-19A adapter candidate."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
TEST_DIR = SCRIPT_DIR / "tests"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semantic_fixtures import fixtures, variant_fixtures  # noqa: E402
from visual_adapters_v15 import adapt_visual, adapter_inventory  # noqa: E402


CANDIDATE_ID = "P19A-THIRTY-NINE-PLUS-FOUR-ADAPTERS-1.5.0"
P19 = ROOT / "evidence/p19"
REFERENCE = ROOT / "thien-skill-creative-diagram/references/visual-adapters-v15.json"
PLAN_MANIFEST = P19 / "P-19A-PLAN-MANIFEST.json"
SOURCE_MANIFEST = P19 / "P-19A-SOURCE-MANIFEST.json"
VERIFICATION = P19 / "P-19A-VERIFICATION.json"

R5_EXPECTED = "7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8"
R6_EXPECTED = "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a"
DIST_EXPECTED = {
    "dist/SHA256SUMS.txt": "af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596",
    "dist/thien-skill-creative-diagram-1.0.0-claude-plugin.zip": "bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9",
    "dist/thien-skill-creative-diagram-1.0.0-openai-plugin.zip": "7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c",
    "dist/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip": "4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_tests(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    match = re.search(r"Ran (\d+) tests?", output)
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "test_count": int(match.group(1)) if match else None,
        "returncode": completed.returncode,
        "summary": "OK" if completed.returncode == 0 and "OK" in output else output[-2000:],
    }


def build_reference() -> str:
    write_json(REFERENCE, adapter_inventory())
    first = sha256(REFERENCE)
    write_json(REFERENCE, adapter_inventory())
    second = sha256(REFERENCE)
    if first != second:
        raise RuntimeError("P-19A reference regeneration is not deterministic.")
    return second


def build_plan_manifest() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    cases: list[tuple[str, dict[str, Any]]] = [(f"type:{key}", value) for key, value in fixtures().items()]
    cases += [(f"capability:{key}", value) for key, value in variant_fixtures().items()]
    for fixture_id, ir in cases:
        plan = adapt_visual(ir)
        encoded = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        entries.append({
            "fixture_id": fixture_id,
            "adapter_id": plan["adapter"]["adapter_id"],
            "canonical_type": plan["adapter"]["canonical_type"],
            "capability_id": plan["adapter"]["capability_id"],
            "layout_engine": plan["adapter"]["layout_engine"],
            "silhouette": plan["adapter"]["silhouette"],
            "material_count": plan["material_inventory"]["material_count"],
            "plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "emission_status": plan["phase_boundary"]["html_svg_emission"],
        })
    manifest = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-27",
        "plan_count": len(entries),
        "canonical_plan_count": sum(1 for item in entries if item["capability_id"] is None),
        "capability_plan_count": sum(1 for item in entries if item["capability_id"] is not None),
        "entries": sorted(entries, key=lambda item: item["adapter_id"]),
        "boundary": "adapter plans only; no HTML/SVG/mode/gallery emission",
    }
    write_json(PLAN_MANIFEST, manifest)
    return manifest


def static_checks() -> dict[str, Any]:
    python_paths = [
        ROOT / "thien-skill-creative-diagram/scripts/visual_adapters_v15.py",
        ROOT / "thien-skill-creative-diagram/scripts/tests/test_visual_adapters_v15.py",
        ROOT / "evidence/p19/source/build_p19a_reference.py",
        ROOT / "evidence/p19/source/verify_p19a.py",
    ]
    for path in python_paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    json_paths = [REFERENCE, PLAN_MANIFEST, P19 / "P-19A-PROVENANCE.json"]
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))
    emitted = [
        path for path in P19.rglob("*")
        if path.is_file() and path.suffix.lower() in {".html", ".svg", ".css"}
    ]
    return {
        "python_ast": {"status": "PASS", "count": len(python_paths)},
        "json_parse": {"status": "PASS", "count": len(json_paths)},
        "p19a_emitted_html_svg_css": {"status": "PASS" if not emitted else "FAIL", "count": len(emitted)},
        "browser": {"status": "not run (out of scope)", "reason": "P-19A emits no executable web artifact; this is not a browser PASS."},
    }


def integrity_checks() -> dict[str, Any]:
    values = {
        "p18r5_review04_manifest": sha256(ROOT / "evidence/p18/r5/P-18R5-MANIFEST.json"),
        "p18r6_review17_manifest": sha256(ROOT / "evidence/p18/r6/P-18R6-MANIFEST.json"),
        **{path: sha256(ROOT / path) for path in DIST_EXPECTED},
    }
    expected = {
        "p18r5_review04_manifest": R5_EXPECTED,
        "p18r6_review17_manifest": R6_EXPECTED,
        **DIST_EXPECTED,
    }
    return {
        "status": "PASS" if values == expected else "FAIL",
        "actual": values,
        "expected": expected,
    }


def build_source_manifest() -> dict[str, Any]:
    relative_paths = [
        "PROJECT-CONTRACT.md",
        "PLAN.md",
        "PHASE-GATES.md",
        "HANDOFF-CURRENT.md",
        "thien-skill-creative-diagram/SKILL.md",
        "thien-skill-creative-diagram/scripts/visual_adapters_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_visual_adapters_v15.py",
        "thien-skill-creative-diagram/references/visual-adapters-v15.json",
        "thien-skill-creative-diagram/references/visual-coverage.md",
        "evidence/p19/P-19A-DESIGN-CONTRACT.md",
        "evidence/p19/P-19A-EVIDENCE.md",
        "evidence/p19/P-19A-PROVENANCE.json",
        "evidence/p19/P-19A-PLAN-MANIFEST.json",
        "evidence/p19/source/build_p19a_reference.py",
        "evidence/p19/source/verify_p19a.py",
    ]
    manifest = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-27",
        "file_count": len(relative_paths),
        "files": [
            {"path": path, "sha256": sha256(ROOT / path), "size": (ROOT / path).stat().st_size}
            for path in relative_paths
        ],
        "excluded_immutable_artifacts": ["evidence/p18/r5/", "evidence/p18/r6/", "dist/", ".release-staging/"],
    }
    write_json(SOURCE_MANIFEST, manifest)
    return manifest


def main() -> None:
    reference_hash = build_reference()
    plan_manifest = build_plan_manifest()
    focused = run_tests(["thien-skill-creative-diagram/scripts/tests/test_visual_adapters_v15.py"])
    full = run_tests(["discover", "-s", "thien-skill-creative-diagram/scripts/tests", "-p", "test_*.py"])
    static = static_checks()
    integrity = integrity_checks()
    source_manifest = build_source_manifest()
    source_manifest_hash = sha256(SOURCE_MANIFEST)

    statuses = [
        focused["status"],
        full["status"],
        static["python_ast"]["status"],
        static["json_parse"]["status"],
        static["p19a_emitted_html_svg_css"]["status"],
        integrity["status"],
    ]
    candidate_binding = {
        "reference_sha256": reference_hash,
        "plan_manifest_sha256": sha256(PLAN_MANIFEST),
        "source_manifest_sha256": source_manifest_hash,
    }
    candidate_binding["aggregate_sha256"] = hashlib.sha256(
        json.dumps(candidate_binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    verification = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-27",
        "status": "PASS" if set(statuses) == {"PASS"} else "FAIL",
        "registry": {
            "canonical_adapters": adapter_inventory()["canonical_type_count"],
            "capability_adapters": adapter_inventory()["capability_count"],
            "layout_engines": adapter_inventory()["layout_engine_count"],
            "unique_silhouettes": len({item["silhouette"] for item in adapter_inventory()["adapters"] + adapter_inventory()["capability_adapters"]}),
        },
        "plan_manifest": {
            "plan_count": plan_manifest["plan_count"],
            "canonical_plan_count": plan_manifest["canonical_plan_count"],
            "capability_plan_count": plan_manifest["capability_plan_count"],
        },
        "tests": {"focused": focused, "full_regression": full},
        "static_checks": static,
        "immutable_integrity": integrity,
        "candidate_binding": candidate_binding,
        "source_file_count": source_manifest["file_count"],
        "phase_boundary": {
            "p19a": "passed" if set(statuses) == {"PASS"} else "failed",
            "p19b": "not-started / unauthorized",
            "p19c": "not-started / unauthorized",
            "package_git_release": "not authorized and not performed",
        },
    }
    write_json(VERIFICATION, verification)
    print(json.dumps({"candidate_id": CANDIDATE_ID, "status": verification["status"], "focused": focused["test_count"], "full": full["test_count"], "aggregate_sha256": candidate_binding["aggregate_sha256"]}, sort_keys=True))
    if verification["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
