#!/usr/bin/env python3
"""Focused static verification for the P-19B three-mode gallery."""

from __future__ import annotations

from collections import Counter
from html import unescape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
TEST_DIR = SCRIPT_DIR / "tests"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from gallery_renderer_v15 import (  # noqa: E402
    MODES,
    P18_PARENT_CANDIDATE_ID,
    P18_PARENT_MANIFEST_SHA256,
    P18_VISUAL_MODES,
    P19B_CANDIDATE_ID,
    render_gallery_html,
)
from semantic_fixtures import fixtures, variant_fixtures  # noqa: E402
from generate_p19b_gallery import specimen_sources
from p19_scope import REUSED_TYPES, p18_references


GALLERY = ROOT / "evidence/p19/gallery"
SPECIMENS = GALLERY / "specimens"
INVENTORY_PATH = GALLERY / "P-19B-INVENTORY.json"
MANIFEST_PATH = GALLERY / "P-19B-MANIFEST.json"
REPORT_PATH = ROOT / "evidence/p19/P-19B-STATIC-VERIFICATION.json"
HISTORY = ROOT / "evidence/p19/history/P19B-THREE-MODE-EXACT-129-HTML-1.5.0"


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_attrs: dict[str, str] = {}
        self.ids: list[str] = []
        self.tags: Counter[str] = Counter()
        self.hrefs: list[str] = []
        self.metadata_text = ""
        self._in_metadata = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attrs = values
        if values.get("id"):
            self.ids.append(values["id"])
            self._in_metadata = values["id"] == "p19b-metadata"
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre":
            self._in_metadata = False

    def handle_data(self, data: str) -> None:
        if self._in_metadata:
            self.metadata_text += data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(checks: list[dict], name: str, condition: bool, detail: str) -> None:
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def main() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = inventory["records"]
    files = sorted(SPECIMENS.glob("*.html"))
    checks: list[dict] = []

    check(checks, "candidate-id", inventory["candidate_id"] == P19B_CANDIDATE_ID, inventory["candidate_id"])
    check(checks, "exact-specimen-count", len(files) == len(records) == 87, f"files={len(files)} records={len(records)}")
    check(checks, "canonical-count", inventory["canonical_type_count"] == 25, str(inventory["canonical_type_count"]))
    check(checks, "capability-count", inventory["capability_count"] == 4, str(inventory["capability_count"]))
    check(checks, "mode-count", inventory["mode_count"] == 3, str(inventory["mode_count"]))
    check(checks, "engine-count", inventory["layout_engine_count"] == len({r["layout_engine"] for r in records}), str(inventory["layout_engine_count"]))
    mode_counts = Counter(item["mode"] for item in records)
    check(checks, "mode-balance", mode_counts == Counter({mode: 29 for mode in MODES}), str(dict(mode_counts)))
    canonical_records = [item for item in records if item["capability_id"] is None]
    capability_records = [item for item in records if item["capability_id"] is not None]
    check(checks, "canonical-three-mode-count", len(canonical_records) == 75, str(len(canonical_records)))
    check(checks, "capability-three-mode-count", len(capability_records) == 12, str(len(capability_records)))
    check(checks, "unique-fixture-count", len({item["fixture_id"] for item in records}) == 29, str(len({item["fixture_id"] for item in records})))
    check(checks, "unique-silhouette-count", len({item["silhouette"] for item in records}) == 29, str(len({item["silhouette"] for item in records})))
    check(checks, "visual-parent-candidate", inventory.get("visual_parent_candidate_id") == P18_PARENT_CANDIDATE_ID, str(inventory.get("visual_parent_candidate_id")))
    check(checks, "visual-parent-manifest", inventory.get("visual_parent_manifest_sha256") == P18_PARENT_MANIFEST_SHA256, str(inventory.get("visual_parent_manifest_sha256")))
    expected_light = {"paper": "#eeece7", "canvas": "#f7f6f2", "surface": "#ffffff", "text": "#252b3c", "connector": "#4f5e76", "grid": "#d9d7d2", "accent": "#f26a32", "accent_soft": "#f8e7dd", "accent_text": "#df5522"}
    check(checks, "p18-neutral-light-role-lock", all(P18_VISUAL_MODES["neutral-light"].get(key) == value for key, value in expected_light.items()), str(expected_light))

    document_failures: list[str] = []
    security_failures: list[str] = []
    hash_failures: list[str] = []
    geometry_groups: dict[str, list[str]] = {}
    for record in records:
        path = GALLERY / record["path"]
        value = path.read_text(encoding="utf-8")
        parser = DocumentParser()
        parser.feed(value)
        required = {
            "data-candidate-id": P19B_CANDIDATE_ID,
            "data-fixture-id": record["fixture_id"],
            "data-diagram-type": record["canonical_type"],
            "data-capability-id": record["capability_id"] or "none",
            "data-parent-type": record["parent"] or "none",
            "data-mode": record["mode"],
            "data-layout-engine": record["layout_engine"],
            "data-silhouette": record["silhouette"],
            "data-visual-parent-candidate": P18_PARENT_CANDIDATE_ID,
            "data-visual-parent-manifest-sha256": P18_PARENT_MANIFEST_SHA256,
            "data-check-disposition": record["automated_check_disposition"],
        }
        if not value.startswith("<!doctype html>") or any(parser.html_attrs.get(key) != expected for key, expected in required.items()):
            document_failures.append(f"metadata:{record['path']}")
        if parser.tags["svg"] != 1 or parser.tags["desc"] != 1 or parser.tags["table"] != 1 or parser.tags["details"] != 1:
            document_failures.append(f"anatomy:{record['path']}")
        if len(parser.ids) != len(set(parser.ids)):
            document_failures.append(f"duplicate-id:{record['path']}")
        try:
            metadata = json.loads(unescape(parser.metadata_text))
            if metadata["fixture_id"] != record["fixture_id"] or metadata["mode"] != record["mode"] or metadata.get("visual_parent_manifest_sha256") != P18_PARENT_MANIFEST_SHA256:
                document_failures.append(f"embedded-metadata:{record['path']}")
        except (KeyError, json.JSONDecodeError):
            document_failures.append(f"metadata-json:{record['path']}")
        if re.search(r"(?:https?:|//fonts\.|<script\b|javascript:|\son[a-z]+\s*=)", value, re.IGNORECASE):
            security_failures.append(record["path"])
        if record["sha256"] != sha256(path):
            hash_failures.append(record["path"])
        svg = value[value.index("<svg "):value.index("</svg>") + 6]
        geometry_groups.setdefault(record["fixture_id"], []).append(svg.replace(record["mode"], "MODE"))

    check(checks, "document-metadata-and-anatomy", not document_failures, f"failures={len(document_failures)}")
    check(checks, "standalone-security", not security_failures, f"failures={len(security_failures)}")
    check(checks, "per-file-hashes", not hash_failures, f"failures={len(hash_failures)}")
    geometry_failures = [key for key, values in geometry_groups.items() if len(values) != 3 or len(set(values)) != 1]
    check(checks, "three-mode-geometry-invariance", not geometry_failures, f"failures={len(geometry_failures)}")
    all_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in files)
    check(checks, "legacy-blue-direction-absent", "#246bce" not in all_text and "#f5f7fa" not in all_text, "forbidden legacy palette literals absent")
    check(checks, "p18-typography-role-receipts", all(value in all_text for value in ("georgia · display", "avenir next · material", "menlo · technical")), "87 specimens expose P-18 resolved typography roles")
    check(checks, "p18-visual-grammar-marker", all('data-visual-grammar="p18r6-review17"' in path.read_text(encoding="utf-8") for path in files), "87/87")

    index_path = GALLERY / "index.html"
    index_parser = DocumentParser()
    index_parser.feed(index_path.read_text(encoding="utf-8"))
    expected_links = {record["path"] for record in records}
    expected_links.update("../../p18/r6/" + r["html"].split("/r6/", 1)[1] for r in p18_references())
    check(checks, "index-link-completeness", set(index_parser.hrefs) == expected_links and len(index_parser.hrefs) == 101, f"links={len(index_parser.hrefs)}")
    check(checks, "index-card-count", index_parser.tags["article"] == 43, f"cards={index_parser.tags['article']}")
    check(checks, "approved-p18-reuse-bindings", inventory["reused_p18_anchors"] == p18_references(), "14 unchanged approved anchors, no generated copies")
    check(checks, "no-duplicate-p19-types", not ({r["identity"] for r in canonical_records} & REUSED_TYPES), "withdrawn 14 canonical types absent; capabilities retained")
    check(checks, "combined-canonical-coverage", len({r["identity"] for r in canonical_records} | REUSED_TYPES) == 39, "25 P-19 + 14 P-18 = 39 canonical types")
    manifest_failures = []
    for item in manifest["records"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            manifest_failures.append(item["path"])
    check(checks, "manifest-integrity", not manifest_failures, f"records={len(manifest['records'])} failures={len(manifest_failures)}")
    lineage = json.loads((HISTORY / "INITIAL-CANDIDATE-LINEAGE.json").read_text(encoding="utf-8"))
    archived_hashes = {
        "gallery_manifest_sha256": sha256(HISTORY / "gallery/P-19B-MANIFEST.json"),
        "plan_manifest_sha256": sha256(HISTORY / "evidence/P-19B-PLAN-MANIFEST.json"),
        "source_manifest_sha256": sha256(HISTORY / "evidence/P-19B-SOURCE-MANIFEST.json"),
    }
    check(checks, "initial-candidate-archive-immutability", all(lineage[key] == value for key, value in archived_hashes.items()), str(archived_hashes))

    sources = [(fixture_id, ir) for fixture_id, _, ir in specimen_sources()]
    memory_hashes = {
        (fixture_id, mode): hashlib.sha256(render_gallery_html(ir, mode, fixture_id).encode("utf-8")).hexdigest()
        for fixture_id, ir in sources for mode in MODES
    }
    deterministic = all(memory_hashes.get((item["fixture_id"], item["mode"])) == item["sha256"] for item in records)
    check(checks, "deterministic-memory-regeneration", deterministic, f"hashes={len(memory_hashes)}")
    check(checks, "p19c-boundary", inventory["boundary"]["p19c_full_qa_freeze_owner_review"] == "not-performed", inventory["boundary"]["p19c_full_qa_freeze_owner_review"])
    check(checks, "g04-boundary", inventory["boundary"]["g04_1_5_0"] == "NOT-EVALUATED", inventory["boundary"]["g04_1_5_0"])
    check(checks, "non-package-boundary", not any(inventory["boundary"][key] for key in ("package_build", "dist_mutation", "publication_mutation", "git_release_mutation")), "all false")

    failures = [item for item in checks if item["status"] != "PASS"]
    report = {
        "schema_version": "1.0",
        "candidate_id": P19B_CANDIDATE_ID,
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "checks": checks,
        "limitations": [
            "This is P-19B focused static verification, not P-19C full QA/freeze/owner review.",
            "Masked recognition, five-second review, full pairwise geometry/typography and G-04@1.5.0 evaluation remain P-19C.",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "pass_count": report["pass_count"], "check_count": report["check_count"], "report": str(REPORT_PATH.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
