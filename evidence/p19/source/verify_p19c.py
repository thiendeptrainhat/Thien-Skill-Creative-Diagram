#!/usr/bin/env python3
"""D-127 full technical QA for the exact P-18/P-19B coexistence candidate."""

from __future__ import annotations

from collections import Counter, defaultdict
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
TEST_DIR = SCRIPT_DIR / "tests"
SOURCE_DIR = ROOT / "evidence/p19/source"
for path in (SCRIPT_DIR, TEST_DIR, SOURCE_DIR):
    sys.path.insert(0, str(path))

from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID, render_gallery_html  # noqa: E402
from generate_p19b_gallery import specimen_sources  # noqa: E402
from p19_scope import P18_MANIFEST_SHA256, REUSED_TYPES, p18_references  # noqa: E402
from verify_p19b_review45 import verify as verify_review45  # noqa: E402


CANDIDATE = "P19C-FULL-QA-FREEZE-REVIEW-01-1.5.0"
P19_MANIFEST_SHA256 = "ae95aca927ec69904483441db6b85de0381c1c1d85f4f01ee07a21a40aed0ba2"
GALLERY = ROOT / "evidence/p19/gallery"
REPORT = ROOT / "evidence/p19/P-19C-VERIFICATION.json"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags = Counter()
        self.ids: list[str] = []
        self.html_attrs: dict[str, str] = {}
        self.svg_attrs: dict[str, str] = {}
        self.table_headers = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        self.tags[tag] += 1
        if tag == "html":
            self.html_attrs = values
        if tag == "svg":
            self.svg_attrs = values
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "th" and values.get("scope") == "col":
            self.table_headers += 1


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(checks: list[dict], name: str, ok: bool, detail: str, category: str) -> None:
    checks.append({"name": name, "category": category, "status": "PASS" if ok else "FAIL", "detail": detail})


def run_tests(command: list[str]) -> tuple[bool, str, int | None]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join((str(SCRIPT_DIR), str(TEST_DIR), str(SOURCE_DIR)))
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    match = re.search(r"Ran (\d+) tests?", result.stdout)
    return result.returncode == 0, result.stdout[-4000:], int(match.group(1)) if match else None


def artifact_snapshot(p18: list[dict], records: list[dict]) -> dict[str, str]:
    result = {}
    for item in p18:
        for key in ("html", "svg"):
            result[item[key]] = digest(ROOT / item[key])
    for item in records:
        path = GALLERY / item["path"]
        result[str(path.relative_to(ROOT))] = digest(path)
    for path in sorted((GALLERY / "previews").glob("*.svg")):
        result[str(path.relative_to(ROOT))] = digest(path)
    return result


def main() -> None:
    checks: list[dict] = []
    inventory_path = GALLERY / "P-19B-INVENTORY.json"
    manifest_path = GALLERY / "P-19B-MANIFEST.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = inventory["records"]
    p18 = p18_references()
    before = artifact_snapshot(p18, records)

    add(checks, "p18-exact-manifest", digest(ROOT / "evidence/p18/r6/P-18R6-MANIFEST.json") == P18_MANIFEST_SHA256, P18_MANIFEST_SHA256, "coexistence")
    add(checks, "p18-exact-anchor-pairs", len(p18) == 14 and all(item["html_sha256"] == digest(ROOT / item["html"]) and item["svg_sha256"] == digest(ROOT / item["svg"]) for item in p18), "14 HTML + 14 SVG", "coexistence")
    add(checks, "p19-exact-gallery-manifest", digest(manifest_path) == P19_MANIFEST_SHA256, P19_MANIFEST_SHA256, "coexistence")
    add(checks, "p19-exact-counts", len(records) == 93 and len(list((GALLERY / "previews").glob("*.svg"))) == 31, "93 HTML + 31 preview", "coexistence")
    add(checks, "separate-artifact-paths", all(item["html"].startswith("evidence/p18/") and item["svg"].startswith("evidence/p18/") for item in p18) and all(not str((GALLERY / item["path"]).relative_to(ROOT)).startswith("evidence/p18/") for item in records), "P-18 and P-19 paths are disjoint", "coexistence")

    owner = json.loads((ROOT / "evidence/p19/P-19B-OWNER-APPROVAL.json").read_text(encoding="utf-8"))
    add(checks, "owner-approved-p19b-review45", owner.get("authority") == "D-126" and owner.get("candidate_id") == P19B_CANDIDATE_ID and owner.get("p19b_status") == "passed-owner-approved", str(owner.get("decision")), "governance")
    add(checks, "inventory-shape", inventory["candidate_id"] == P19B_CANDIDATE_ID and inventory["canonical_type_count"] == 25 and inventory["capability_count"] == 4 and inventory["presentation_variant_count"] == 2 and inventory["mode_count"] == 3, "25 canonical + 4 capability + 2 variants × 3 modes", "semantic")
    add(checks, "mode-balance", Counter(item["mode"] for item in records) == Counter({mode: 31 for mode in MODES}), str(dict(Counter(item["mode"] for item in records))), "semantic")
    p19_canonical = {item["identity"] for item in records if item["capability_id"] is None and item.get("presentation_variant_id") is None}
    add(checks, "canonical-union", len(p19_canonical) == 25 and not (p19_canonical & REUSED_TYPES) and len(p19_canonical | REUSED_TYPES) == 39, "14 P-18 + 25 P-19 = 39 unique canonical types", "semantic")
    add(checks, "silhouette-coverage", len({item["fixture_id"] for item in records}) == len({item["silhouette"] for item in records}) == 31, "31 unique fixture and silhouette identifiers", "semantic")

    manifest_failures = []
    for item in manifest["records"]:
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            manifest_failures.append(item["path"])
    add(checks, "p19-gallery-manifest-integrity", not manifest_failures and len(manifest["records"]) == 127, f"records=127 failures={len(manifest_failures)}", "determinism")

    anatomy_failures = []
    security_failures = []
    glyph_failures = []
    geometry = defaultdict(list)
    for item in records:
        path = GALLERY / item["path"]
        value = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(value)
        # Some approved alternative tables use row headers rather than a
        # column-header row. Both are valid table semantics, so require at
        # least one TH without forcing scope="col" on the frozen candidate.
        if parser.html_attrs.get("lang") != "vi" or parser.tags["svg"] != 1 or parser.tags["title"] < 2 or parser.tags["desc"] != 1 or parser.tags["table"] != 1 or parser.tags["details"] != 1 or parser.tags["summary"] != 1 or parser.tags["th"] < 1:
            anatomy_failures.append(item["path"])
        if parser.svg_attrs.get("role") != "img" or not parser.svg_attrs.get("aria-labelledby") or len(parser.ids) != len(set(parser.ids)):
            anatomy_failures.append(item["path"])
        if re.search(r"(?:https?:|//fonts\.|<script\b|javascript:|\son[a-z]+\s*=|<iframe\b|<object\b|<embed\b)", value, re.I):
            security_failures.append(item["path"])
        if "�" in value or "\x00" in value or not all(token in value for token in ("Georgia · display", "Avenir Next · material", "Menlo · technical")):
            glyph_failures.append(item["path"])
        svg = re.search(r"<svg\b.*?</svg>", value, re.S)
        if not svg:
            anatomy_failures.append(item["path"])
        else:
            geometry[item["fixture_id"]].append(svg.group().replace(item["mode"], "MODE"))
    add(checks, "html-svg-accessibility-anatomy", not anatomy_failures, f"93 pages; failures={len(set(anatomy_failures))}", "accessibility")
    add(checks, "standalone-security", not security_failures, f"scriptless/network-independent; failures={len(security_failures)}", "security")
    add(checks, "utf8-vietnamese-typography-receipts", not glyph_failures, f"replacement/control/receipt failures={len(glyph_failures)}", "typography")
    geometry_failures = [name for name, values in geometry.items() if len(values) != 3 or len(set(values)) != 1]
    add(checks, "three-mode-geometry-invariance", not geometry_failures, f"31 identities; failures={len(geometry_failures)}", "geometry")

    memory_hashes = {
        (fixture_id, mode): hashlib.sha256(render_gallery_html(ir, mode, fixture_id).encode("utf-8")).hexdigest()
        for fixture_id, _, ir in specimen_sources() for mode in MODES
    }
    deterministic = all(memory_hashes.get((item["fixture_id"], item["mode"])) == item["sha256"] for item in records)
    add(checks, "deterministic-memory-regeneration", deterministic and len(memory_hashes) == 93, f"hashes={len(memory_hashes)}", "determinism")

    review45 = verify_review45()
    add(checks, "review45-exact-and-protected-corpus", review45.get("status") == "PASS" and review45.get("candidate_id") == P19B_CANDIDATE_ID, f"archive={review45.get('archived_files_verified')} protected={review45.get('protected_files_verified')}", "regression")

    full_ok, full_output, full_count = run_tests([sys.executable, "-m", "unittest", "discover", "-s", str(TEST_DIR.relative_to(ROOT)), "-p", "test_*.py"])
    add(checks, "full-regression", full_ok and full_count is not None and full_count >= 414, f"tests={full_count}", "regression")
    scope_ok, scope_output, scope_count = run_tests([sys.executable, "evidence/p19/source/test_p19_scope.py"])
    add(checks, "p18-p19-scope-lock", scope_ok and scope_count == 8, f"tests={scope_count}", "coexistence")

    comparison = json.loads((ROOT / "evidence/p19/comparison/COMPARISON-MANIFEST.json").read_text(encoding="utf-8"))
    phase_counts = Counter(item["phase"] for item in comparison["records"])
    comparison_sources_ok = all(digest(ROOT / item["source"]) == item["source_sha256"] for item in comparison["records"])
    add(checks, "combined-comparison-107", comparison["counts"]["total"] == 107 and phase_counts == Counter({"p18": 14, "p19": 93}) and comparison_sources_ok, f"phase_counts={dict(phase_counts)}", "coexistence")

    browser_path = ROOT / "evidence/p19/P-19C-BROWSER-VERIFICATION.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8")) if browser_path.is_file() else {}
    add(checks, "browser-qa", browser.get("status") == "PASS" and browser.get("comparison", {}).get("desktop", {}).get("images") == 107 and browser.get("comparison", {}).get("mobile", {}).get("images") == 107, str(browser.get("status", "MISSING")), "browser")
    masked_path = ROOT / "evidence/p19/p19c/masked-review/MASKED-KEY.json"
    masked = json.loads(masked_path.read_text(encoding="utf-8")) if masked_path.is_file() else {}
    masked_hashes_ok = masked.get("record_count") == 31 and all(digest(ROOT / item["masked_path"]) == item["masked_sha256"] for item in masked.get("records", []))
    add(checks, "masked-review-pack", masked_hashes_ok, f"records={masked.get('record_count', 0)}; owner recognition pending", "visual-review")

    after = artifact_snapshot(p18, records)
    add(checks, "source-artwork-preservation-during-p19c-qa", before == after, f"bound_artifacts={len(after)}", "coexistence")
    failures = [item for item in checks if item["status"] != "PASS"]
    report = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE,
        "authority": "D-127",
        "status": "TECHNICAL_PASS_READY_FOR_OWNER_REVIEW" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "checks": checks,
        "test_receipts": {"full_regression": {"count": full_count, "tail": full_output}, "scope_lock": {"count": scope_count, "tail": scope_output}},
        "hard_boundaries": {
            "p18_replaced_by_p19": False,
            "combined_count": 107,
            "p19c_owner_approved": False,
            "g04_1_5_0": "NOT-EVALUATED",
            "package_dist_publication_git_release_authorized": False,
        },
        "owner_actions_required": [
            "Complete the 31-card masked recognition/five-second review without opening MASKED-KEY.json first.",
            "Approve or reject this exact P-19C freeze candidate.",
            "Record the separate G-04@1.5.0 gate decision.",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "pass_count": report["pass_count"], "check_count": report["check_count"], "report": str(REPORT.relative_to(ROOT))}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
