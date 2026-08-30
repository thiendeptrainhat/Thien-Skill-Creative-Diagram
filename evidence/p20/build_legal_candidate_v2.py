#!/usr/bin/env python3
"""Build the local-only v2.0.0 legal/provenance carry-forward candidate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "thien-skill-creative-diagram"
P20 = ROOT / "evidence" / "p20"
OUTPUT = P20 / "legal-candidate"
VERSION = "2.0.0"
CANDIDATE_ID = "TCD-LEGAL-2.0.0-RC1"
GENERATED_AT = "2026-08-30T00:00:00+07:00"
LEGAL_NAMES = (
    "LICENSE.md",
    "LICENSE-APPLICATION.md",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_MANIFEST.json",
    "ASSET_MANIFEST.json",
)


def stable_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_logical(files: dict[str, bytes]) -> str:
    payload = b"".join(
        name.encode("utf-8") + b"\0" + sha(data).encode("ascii") + b"\n"
        for name, data in sorted(files.items())
    )
    return sha(payload)


def source_manifest() -> dict:
    value = copy.deepcopy(json.loads((CANONICAL / "SOURCE_MANIFEST.json").read_text(encoding="utf-8")))
    value["schema_version"] = "2.0-candidate"
    value["generated_at"] = GENERATED_AT
    value["project"]["version"] = VERSION
    value["release_lineage"] = {
        "authorization": "D-130",
        "target_version": VERSION,
        "source_gallery_gate": {
            "instance": "G-04@1.5.0",
            "result": "PASS",
            "record": "evidence/p19/G-04-1.5.0-EVIDENCE.md",
            "sha256": "0d3720f9ff9bfc658a1477fa6d487bdabb32e99aa7a9a0e42f0ebd02869c5d63",
        },
        "p17_source_manifest_sha256": "efabfb7e9e485449947ce98bc8e2fc5078a4c7d2593521c115b309c9aef24c57",
        "p18_manifest_sha256": "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a",
        "p19b_manifest_sha256": "ae95aca927ec69904483441db6b85de0381c1c1d85f4f01ee07a21a40aed0ba2",
        "p19c_freeze_sha256": "5c98b8f56987ed69e65a93e01ca05dc2fd95c6d4e288007ffaa7fd615c8180ed",
        "coexistence": {"p18": 14, "p19": 93, "combined": 107, "substitution": False},
        "flexibility_condition": "D-128: 31 masked silhouettes are QA samples, not fixed outputs; safe semantically valid user requests take precedence.",
        "gate_state": "G-00...G-07@2.0.0 NOT-EVALUATED until separately reviewed",
    }

    sources = {item["source_id"]: item for item in value["sources"]}
    upstream = sources["SRC-DIAGRAM-DESIGN"]
    upstream["snapshot"].update({
        "captured_at": "2026-08-22T15:34:21Z",
        "revision": "648c2a597839301e06df1e7434a08bde9f42eed3",
        "commit_time": "2026-08-21T17:26:23-05:00",
        "tree": "614419398b69ca9d4dfbd6681b259304dfd0fe62",
        "sha256": "c36ef92b3e1eb1ba486a331bfad357a9435b699a93c96adb7075d6134d22bf17",
        "tag": None,
    })
    upstream["files_evaluated"] = [{
        "path_or_url": "skills/diagram-design/SKILL.md",
        "sha256": "553191201faf2e61a9b3cc24f01b688de172f67b3f9da69b544f194252fcacee",
        "purpose": "Functional taxonomy and abstract behavior study only",
    }]
    upstream["notice"]["source_url"] = "https://github.com/cathrynlavery/diagram-design/tree/648c2a597839301e06df1e7434a08bde9f42eed3"

    docs = {
        "SRC-AGENT-SKILLS-SPEC": "https://agentskills.io/specification",
        "SRC-ANTHROPIC-DOCS": "https://code.claude.com/docs/en/plugins-reference",
        "SRC-OPENAI-DOCS": "https://developers.openai.com/plugins/build/plugins",
    }
    for source_id, url in docs.items():
        item = sources[source_id]
        item["locator"]["canonical"] = url
        item["snapshot"].update({
            "captured_at": GENERATED_AT,
            "revision_kind": "document-current-at-date",
            "revision": "verified-2026-08-30",
        })
        item["license"]["evidence_locator"] = url
        item["notice"]["source_url"] = url
    return value


def asset_manifest() -> dict:
    value = copy.deepcopy(json.loads((CANONICAL / "ASSET_MANIFEST.json").read_text(encoding="utf-8")))
    value["schema_version"] = "2.0-candidate"
    value["record_id"] = "P20-ASSET-MANIFEST-CANDIDATE-1"
    value["generated_at"] = GENERATED_AT
    value["project"]["version"] = VERSION
    value["status"] = "candidate-awaiting-owner-and-vietnamese-lawyer-review"
    for item in value["approved_candidates"]:
        selected = bool(item.get("package_targets"))
        item["scope"] = "v2.0.0-brand-presentation-candidate" if selected else "owner-approved-provenance-not-packaged-v2.0.0"
        item["destination_status"] = "D-130 exact-byte carry-forward candidate; G-06@2.0.0 owner/legal approval pending"
        item["release_eligible"] = False
        for destination in item.get("destinations", []):
            destination["intended_use"] = "OpenAI icon carry-forward candidate; P-20 revalidates the official host field and smoke-tests exact bytes"
    for item in value["excluded_qa_only"]:
        item["exclusion_reason"] = "D-130 candidate continues the D-027 exclusion of 32px and 48px derivatives for v2.0.0"
    value["package_mapping_decision"] = {
        "decision": "D-130 candidate carry-forward of exact D-027/D-028 bytes",
        "policy": "Propose exact light-plate 64px and 400px for OpenAI plugin and Universal raw skill; no Claude brand asset; all other approved derivatives remain provenance-only.",
        "state": "candidate-awaiting-owner-and-vietnamese-lawyer-review",
        "p20_boundary": "P-20 may build local-only candidate archives and evidence; no dist, publication, Git, tag, Release, or release eligibility before G-06/G-07@2.0.0 approvals.",
    }
    return value


def patched_legal_text(name: str) -> bytes:
    text = (CANONICAL / name).read_text(encoding="utf-8")
    if name == "LICENSE-APPLICATION.md":
        replacements = {
            "package v1.0.0 được xác định bởi release manifest cuối cùng": "package v2.0.0 được xác định bởi release manifest cuối cùng",
            "v1.0.0 packages identified by the final release manifest": "v2.0.0 packages identified by the final release manifest",
            "Theo quyết định D-028, package scope v1.0.0 chỉ chọn derivative light-plate 64px và 400px cho OpenAI plugin và Universal raw skill tại `assets/brand/`; không chọn asset brand cho Claude. Các derivative owner-approved còn lại chỉ giữ vai trò provenance và không được đóng gói trong v1.0.0. P-13 chỉ được xác minh field host hiện hành, copy đúng byte đã khai báo, tạo overlay và smoke-test sau khi được phép; không được tự thay đổi manifest đã duyệt.": "Theo D-130, legal/brand candidate v2.0.0 đề xuất tiếp tục dùng đúng byte derivative light-plate 64px và 400px cho OpenAI plugin và Universal raw skill tại `assets/brand/`; không chọn asset brand cho Claude. Các derivative owner-approved còn lại chỉ giữ vai trò provenance và không được đóng gói trong v2.0.0. P-20 chỉ được xác minh field host hiện hành, copy đúng byte đã khai báo, tạo candidate overlay và smoke-test; candidate phải được owner và luật sư Việt Nam duyệt theo exact hash trước khi đủ điều kiện phát hành.",
            "Under decision D-028, the v1.0.0 package scope selects only the 64px and 400px light-plate derivatives for the OpenAI plugin and Universal raw skill under `assets/brand/`; no Claude brand asset is selected. The remaining owner-approved derivatives are retained for provenance only and are not packaged in v1.0.0. Once authorized, P-13 may only re-verify current host fields, copy the declared bytes, create overlays, and smoke-test; it may not silently change the approved manifest.": "Under D-130, the v2.0.0 legal/brand candidate proposes carrying forward the exact 64px and 400px light-plate bytes for the OpenAI plugin and Universal raw skill under `assets/brand/`; no Claude brand asset is selected. The remaining owner-approved derivatives stay provenance-only and are not packaged in v2.0.0. P-20 may re-verify current host fields, copy the declared bytes, create candidate overlays, and smoke-test; owner and Vietnamese-lawyer approval of the exact hash is required before release eligibility.",
        }
        for old, new in replacements.items():
            old_count = text.count(old)
            new_count = text.count(new)
            if old_count == 1 and new_count == 0:
                text = text.replace(old, new)
            elif old_count == 0 and new_count == 1:
                continue
            else:
                raise RuntimeError(f"expected one old or promoted legal text anchor in {name}: {old[:48]}")
    elif name == "NOTICE":
        old = "ASSET_MANIFEST.json records 16 owner-approved derivatives at 64px or larger and 6 QA-only 32/48px derivatives excluded from v1.0.0. Under D-028, only the light-plate 64px and 400px derivatives target the OpenAI plugin and Universal raw skill under assets/brand; Claude receives no brand asset. The other owner-approved derivatives remain provenance-only and are not packaged in v1.0.0. No asset is release-eligible before G-06 and P-13 execution."
        new = "ASSET_MANIFEST.json records 16 owner-approved derivatives at 64px or larger and 6 QA-only 32/48px derivatives excluded from the v2.0.0 candidate. Under D-130, the candidate proposes carrying forward only the exact light-plate 64px and 400px bytes for the OpenAI plugin and Universal raw skill under assets/brand; Claude receives no brand asset. The other owner-approved derivatives remain provenance-only and are not packaged. No asset is release-eligible before G-06@2.0.0 and G-07@2.0.0 approvals."
        if text.count(old) == 1 and text.count(new) == 0:
            text = text.replace(old, new)
        elif not (text.count(old) == 0 and text.count(new) == 1):
            raise RuntimeError("NOTICE brand-scope anchor drift")
        old = "This candidate is not release authorization. Vietnamese counsel must approve the exact legal-candidate version/hash, and G-06 must pass, before package construction can begin."
        new = "This candidate is not release authorization. Vietnamese counsel must approve the exact legal-candidate version/hash and G-06@2.0.0 must pass before these local candidate archives can be promoted to a release payload."
        if text.count(old) == 1 and text.count(new) == 0:
            text = text.replace(old, new)
        elif not (text.count(old) == 0 and text.count(new) == 1):
            raise RuntimeError("NOTICE approval anchor drift")
    return text.encode("utf-8")


def candidate_files() -> dict[str, bytes]:
    return {
        "LICENSE.md": (CANONICAL / "LICENSE.md").read_bytes(),
        "LICENSE-APPLICATION.md": patched_legal_text("LICENSE-APPLICATION.md"),
        "NOTICE": patched_legal_text("NOTICE"),
        "THIRD_PARTY_NOTICES.md": (CANONICAL / "THIRD_PARTY_NOTICES.md").read_bytes(),
        "SOURCE_MANIFEST.json": stable_json(source_manifest()),
        "ASSET_MANIFEST.json": stable_json(asset_manifest()),
    }


def build_record(files: dict[str, bytes]) -> dict:
    return {
        "record_id": "P20-LEGAL-CANDIDATE-BUILD-1",
        "candidate_id": CANDIDATE_ID,
        "version": VERSION,
        "generated_at": GENERATED_AT,
        "authorization": "D-130",
        "status": "CANDIDATE-AWAITING-G06-2.0.0-OWNER-AND-VIETNAMESE-LAWYER-APPROVAL",
        "aggregate_sha256": digest_logical(files),
        "artifacts": [
            {"path": name, "bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(files.items())
        ],
        "unchanged_legal_bytes": ["LICENSE.md", "THIRD_PARTY_NOTICES.md"],
        "changed_candidate_bytes": ["LICENSE-APPLICATION.md", "NOTICE", "SOURCE_MANIFEST.json", "ASSET_MANIFEST.json"],
        "limits": [
            "No file is release-eligible before exact G-06@2.0.0 owner and Vietnamese-lawyer approval.",
            "The candidate does not authorize dist, publication, Git, tag, Release, or release actions.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = candidate_files()
    record = stable_json(build_record(files))
    expected = {OUTPUT / name: data for name, data in files.items()}
    expected[P20 / "legal-candidate-build.json"] = record
    if args.check:
        drift = [str(path.relative_to(ROOT)) for path, data in expected.items() if not path.is_file() or path.read_bytes() != data]
        print(json.dumps({"status": "PASS" if not drift else "FAIL", "drift": drift}, indent=2))
        return 1 if drift else 0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path, data in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({"status": "BUILT", "candidate_id": CANDIDATE_ID, "aggregate_sha256": build_record(files)["aggregate_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
