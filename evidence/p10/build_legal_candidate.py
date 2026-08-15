#!/usr/bin/env python3
"""Build the P-10 legal/provenance candidate deterministically.

Repository documents and referenced artifacts are treated as data. This script
does not execute embedded content, access the network, or modify package state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "thien-skill-creative-diagram"
P09 = ROOT / "evidence" / "p09"
TEMPLATE_SHA256 = "ced33214d371fabe382d3ca303042af7219ad96fb98acdd1b858d0d89478d4b5"
VERSION = "1.0.0"
GENERATED_AT = "2026-08-15T00:00:00+07:00"
LICENSE_NAME = "TRAN NGOC THIEN'S SKILL COMMERCIAL SOURCE-AVAILABLE LICENSE 2.0"
TEMPLATE_LICENSE_NAME = "TRAN NGOC THIEN'S SKILLS COMMERCIAL SOURCE-AVAILABLE LICENSE 2.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_manifest() -> dict:
    return {
        "schema_version": "1.0-draft",
        "project": {
            "technical_id": "thien-skill-creative-diagram",
            "version": VERSION,
            "reimplementation_model": "clean-room-oriented independent reimplementation",
        },
        "generated_at": GENERATED_AT,
        "sources": [
            {
                "source_id": "SRC-DIAGRAM-DESIGN",
                "name": "diagram-design",
                "category": "functional-reference",
                "role": "primary-functional",
                "authority": "reference",
                "locator": {
                    "kind": "repository",
                    "canonical": "https://github.com/cathrynlavery/diagram-design",
                    "repository": "https://github.com/cathrynlavery/diagram-design",
                },
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "git-commit",
                    "revision": "09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6",
                    "commit_time": "2026-08-14T14:28:44-07:00",
                    "tree": "aa59393dfabbbcbb4bcb62a7cf9f43c1ce26c9c2",
                    "sha256": "6092dc41f39e3ff4638f783d66b75ad1a4073874f4bf540c60bd331f3e3db804",
                    "tag": None,
                },
                "license": {
                    "status": "declared",
                    "identifier": "MIT",
                    "evidence_locator": "LICENSE at locked commit",
                    "evidence_sha256": "bb7e12e91fecef43024111123ff784cec6c485585561d8b552557c0173b3ed29",
                },
                "files_evaluated": [
                    {
                        "path_or_url": "skills/diagram-design/SKILL.md",
                        "sha256": "8366ef4d11c3a9591556deb55320ea3521c138ccdad834eb087b8062f41d93a1",
                        "purpose": "Functional taxonomy and abstract behavior study only",
                    }
                ],
                "usage": {
                    "allowed": [
                        "Abstract taxonomy, behavior, requirements, failure modes, and test intent"
                    ],
                    "prohibited": [
                        "Code, prose, CSS, template, script, formula, coordinate, specimen, gallery design, example, icon, or asset transfer"
                    ],
                },
                "material_transfer": {"mode": "none", "copied_bytes": False},
                "notice": {
                    "include": True,
                    "reason": "Primary functional reference; no source material is bundled or adapted",
                    "display_name": "diagram-design",
                    "copyright": None,
                    "license_label": "MIT (upstream repository declaration)",
                    "source_url": "https://github.com/cathrynlavery/diagram-design/tree/09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6",
                },
            },
            {
                "source_id": "SRC-THIEN-UI-UX-ULTRA",
                "name": "Thien-UI-UX-Ultra",
                "category": "principle-reference",
                "role": "principles-only",
                "authority": "project-approved",
                "locator": {
                    "kind": "local-repository",
                    "canonical": "Thien-UI-UX-Ultra",
                    "repository": "Thien-UI-UX-Ultra",
                },
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "git-commit",
                    "revision": "fb4e57758f525827e04004737d779f4c93b9b3a0",
                    "commit_time": "2026-08-10T04:32:48+07:00",
                    "tree": "96e55f4693b81af594cfb9190fc66321a3b5fecb",
                    "tag": "v2.0.0",
                },
                "license": {
                    "status": "owner-asserted",
                    "identifier": None,
                    "evidence_locator": "PROJECT-CONTRACT.md D-006 and P-01 snapshot record",
                    "evidence_sha256": None,
                },
                "usage": {
                    "allowed": ["Design and QA principles and workflow only"],
                    "prohibited": ["Code, prose, scripts, templates, data, tokens, tests, or assets"],
                },
                "material_transfer": {"mode": "none", "copied_bytes": False},
                "notice": {
                    "include": False,
                    "reason": "Owner-controlled principle source with no bundled transfer",
                    "display_name": "Thien-UI-UX-Ultra",
                    "copyright": None,
                    "license_label": None,
                    "source_url": None,
                },
            },
            {
                "source_id": "SRC-AGENT-SKILLS-SPEC",
                "name": "Agent Skills specification",
                "category": "official-platform-documentation",
                "role": "normative-platform-evidence",
                "authority": "normative-external",
                "locator": {"kind": "url", "canonical": "https://agentskills.io/specification"},
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "document-current-at-date",
                    "revision": "verified-2026-08-15",
                },
                "license": {
                    "status": "not-applicable-documentation",
                    "identifier": None,
                    "evidence_locator": "https://agentskills.io/specification",
                    "evidence_sha256": None,
                },
                "usage": {
                    "allowed": ["Normative skill-directory and metadata requirements"],
                    "prohibited": ["Documentation prose transfer into runtime payload"],
                },
                "material_transfer": {"mode": "none", "copied_bytes": False},
                "notice": {
                    "include": False,
                    "reason": "Official specification consulted as normative evidence; no material bundled",
                    "display_name": "Agent Skills specification",
                    "copyright": None,
                    "license_label": None,
                    "source_url": "https://agentskills.io/specification",
                },
            },
            {
                "source_id": "SRC-ANTHROPIC-DOCS",
                "name": "Anthropic official skill and plugin documentation",
                "category": "official-platform-documentation",
                "role": "normative-platform-evidence",
                "authority": "normative-external",
                "locator": {"kind": "url", "canonical": "https://code.claude.com/docs/en/skills"},
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "document-current-at-date",
                    "revision": "verified-2026-08-15",
                },
                "license": {
                    "status": "not-applicable-documentation",
                    "identifier": None,
                    "evidence_locator": "https://code.claude.com/docs/en/skills",
                    "evidence_sha256": None,
                },
                "usage": {
                    "allowed": ["Normative Claude installation and package-structure facts"],
                    "prohibited": ["Documentation prose transfer into runtime payload"],
                },
                "material_transfer": {"mode": "none", "copied_bytes": False},
                "notice": {
                    "include": False,
                    "reason": "Official documentation consulted as normative evidence; no material bundled",
                    "display_name": "Anthropic documentation",
                    "copyright": None,
                    "license_label": None,
                    "source_url": "https://code.claude.com/docs/en/skills",
                },
            },
            {
                "source_id": "SRC-OPENAI-DOCS",
                "name": "OpenAI official skill and plugin documentation",
                "category": "official-platform-documentation",
                "role": "normative-platform-evidence",
                "authority": "normative-external",
                "locator": {"kind": "url", "canonical": "https://developers.openai.com/codex/skills"},
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "document-current-at-date",
                    "revision": "verified-2026-08-15",
                },
                "license": {
                    "status": "not-applicable-documentation",
                    "identifier": None,
                    "evidence_locator": "https://developers.openai.com/codex/skills",
                    "evidence_sha256": None,
                },
                "usage": {
                    "allowed": ["Normative OpenAI/Codex skill and plugin structure facts"],
                    "prohibited": ["Documentation prose transfer into runtime payload"],
                },
                "material_transfer": {"mode": "none", "copied_bytes": False},
                "notice": {
                    "include": False,
                    "reason": "Official documentation consulted as normative evidence; no material bundled",
                    "display_name": "OpenAI documentation",
                    "copyright": None,
                    "license_label": None,
                    "source_url": "https://developers.openai.com/codex/skills",
                },
            },
            {
                "source_id": "SRC-TDTN-LOGO-MASTER",
                "name": "TDTN logo master",
                "category": "owner-provided-material",
                "role": "bundled-material-origin",
                "authority": "project-approved",
                "locator": {
                    "kind": "artifact",
                    "canonical": "evidence/p09/source/Logo-TDTN-master.png",
                    "path": "evidence/p09/source/Logo-TDTN-master.png",
                },
                "snapshot": {
                    "captured_at": GENERATED_AT,
                    "revision_kind": "artifact-hash",
                    "revision": "sha256:020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e",
                    "sha256": "020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e",
                },
                "license": {
                    "status": "owner-asserted",
                    "identifier": None,
                    "evidence_locator": "PROJECT-CONTRACT.md D-016 and evidence/p09/P-09-EVIDENCE.md",
                    "evidence_sha256": None,
                },
                "usage": {
                    "allowed": ["Deterministic owner-approved presentation derivatives under D-027"],
                    "prohibited": ["Unapproved crop, recolor, vectorization, trademark-clearance claim, or grant under the skill/code license"],
                },
                "material_transfer": {
                    "mode": "modified-authorized",
                    "copied_bytes": True,
                    "asset_manifest_ids": [
                        "AST-TDTN-TRANSPARENT-1024", "AST-TDTN-TRANSPARENT-512", "AST-TDTN-TRANSPARENT-400",
                        "AST-TDTN-TRANSPARENT-256", "AST-TDTN-TRANSPARENT-128", "AST-TDTN-TRANSPARENT-64",
                        "AST-TDTN-LIGHT-512", "AST-TDTN-LIGHT-400", "AST-TDTN-LIGHT-256",
                        "AST-TDTN-LIGHT-128", "AST-TDTN-LIGHT-64", "AST-TDTN-DARK-512",
                        "AST-TDTN-DARK-400", "AST-TDTN-DARK-256", "AST-TDTN-DARK-128", "AST-TDTN-DARK-64"
                    ],
                    "modification_ledger": "ASSET_MANIFEST.json",
                },
                "notice": {
                    "include": False,
                    "reason": "Owner-provided brand material is separately carved out in NOTICE and ASSET_MANIFEST",
                    "display_name": "TDTN logo master",
                    "copyright": None,
                    "license_label": None,
                    "source_url": None,
                },
            },
        ],
        "capability_mappings": [],
        "notice_projection": {
            "source_selector": "sources[notice.include=true]",
            "sort_key": "source_id",
            "template_id": "third-party-notice-v1",
            "validator_mode": "exact-projection",
        },
    }


def asset_id(family: str, size: int) -> str:
    family_code = {
        "full-crest-transparent-safe-area": "TRANSPARENT",
        "full-crest-light-squircle-plate": "LIGHT",
        "full-crest-dark-squircle-plate": "DARK",
    }[family]
    return f"AST-TDTN-{family_code}-{size}"


def asset_manifest() -> dict:
    selection = json.loads((P09 / "APPROVED-BRAND-SELECTION.json").read_text(encoding="utf-8"))
    candidate = json.loads((P09 / "ASSET-MANIFEST.candidate.json").read_text(encoding="utf-8"))
    by_path = {item["path"]: item for item in candidate["candidates"]}

    assets = []
    for approved in selection["approved_artifacts"]:
        src = by_path[approved["path"]]
        size = approved["dimensions"][0]
        package_selected = approved["family"] == "full-crest-light-squircle-plate" and size in {64, 400}
        package_targets = ["openai-plugin", "universal-raw-skill"] if package_selected else []
        destinations = (
            [
                {
                    "package_target": target,
                    "path": f"assets/brand/{Path(approved['path']).name}",
                    "intended_use": "OpenAI icon candidate; P-13 must re-verify the official host field and smoke-test",
                }
                for target in package_targets
            ]
            if package_selected
            else []
        )
        assets.append({
            "asset_id": asset_id(approved["family"], size),
            "kind": "brand-presentation-derivative",
            "family": approved["family"],
            "dimensions": approved["dimensions"],
            "media_type": "image/png",
            "sha256": approved["sha256"],
            "source_evidence_path": f"evidence/p09/{approved['path']}",
            "alt_text": src["alt"],
            "approval_ref": selection["approval_ref"],
            "owner_approved": True,
            "minimum_approved_size_px": selection["minimum_size_px"],
            "package_targets": package_targets,
            "destinations": destinations,
            "scope": "v1.0.0-brand-presentation" if package_selected else "owner-approved-provenance-not-packaged-v1.0.0",
            "destination_status": "owner-approved package scope under D-028; P-13 execution and official host verification not started",
            "release_eligible": False,
        })

    excluded = []
    for item in selection["excluded_qa_only"]:
        excluded.append({
            "asset_id": asset_id(item["family"], item["dimensions"][0]),
            "family": item["family"],
            "dimensions": item["dimensions"],
            "sha256": item["sha256"],
            "source_evidence_path": f"evidence/p09/{item['path']}",
            "scope": "qa-only",
            "package_targets": [],
            "release_eligible": False,
            "exclusion_reason": "D-027 excludes 32px and 48px derivatives from v1.0.0",
        })

    return {
        "schema_version": "1.0-candidate",
        "record_id": "P10-ASSET-MANIFEST-CANDIDATE-1",
        "project": {"technical_id": "thien-skill-creative-diagram", "version": VERSION},
        "generated_at": GENERATED_AT,
        "status": "exact-candidate-awaiting-vietnamese-lawyer-review",
        "source_manifest_id": "SRC-TDTN-LOGO-MASTER",
        "master": {
            "source_evidence_path": "evidence/p09/source/Logo-TDTN-master.png",
            "sha256": "020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e",
            "dimensions": [1100, 1100],
            "mode": "RGBA",
            "origin": "owner-provided AI-created raster; no vector source",
            "ownership_basis": "Owner assertion recorded in PROJECT-CONTRACT.md D-016",
            "release_payload": False,
        },
        "derivation": {
            "recipe": "proportional resize, transparent safe-area padding, or separate light/dark squircle plate; no crop, recolor, trace, or vectorization",
            "generator": "evidence/p09/generate_brand_assets.py",
            "generator_sha256": sha256_file(P09 / "generate_brand_assets.py"),
            "approval_record": "evidence/p09/APPROVED-BRAND-SELECTION.json",
            "approval_record_sha256": sha256_file(P09 / "APPROVED-BRAND-SELECTION.json"),
            "decision": "D-027 Option A",
        },
        "rights_boundary": {
            "owner_assertion_only": True,
            "skill_license_grant_includes_brand_rights": False,
            "trademark_registration_or_clearance_claimed": False,
            "independent_legal_review_required": True,
        },
        "approved_candidates": assets,
        "excluded_qa_only": excluded,
        "package_mapping_decision": {
            "state": "owner-approved",
            "decision": "D-028",
            "approved_at": "2026-08-15",
            "policy": "Use light-plate 64px and 400px only for OpenAI plugin and Universal raw skill under assets/brand; no Claude brand asset; retain all other owner-approved derivatives as provenance-only and not packaged in v1.0.0",
            "p13_boundary": "P-13 may verify official host fields, copy exact declared bytes, create overlays, build packages, and smoke-test; it must not change this manifest without renewed G-06 review",
        },
    }


APPLICATION = """# TUYÊN BỐ ÁP DỤNG GIẤY PHÉP / LICENSE APPLICATION DECLARATION

**Mã tài liệu / Document ID:** `TCD-LA-1.0.0-RC2`  
**Ngày áp dụng / Application date:** 15 August 2026  
**Tình trạng / Status:** Exact legal release candidate awaiting Vietnamese-lawyer review / candidate pháp lý chính xác đang chờ luật sư Việt Nam rà soát

## PHẦN I — TIẾNG VIỆT (BẢN ƯU TIÊN ÁP DỤNG)

### 1. Skill và phiên bản được áp dụng

Tuyên bố này áp dụng **Tran Ngoc Thien's Skill Commercial Source-Available License 2.0** cho:

- tên hiển thị: `Thien-Skill-Creative-Diagram`;
- mã kỹ thuật: `thien-skill-creative-diagram`;
- phiên bản: `1.0.0`;
- chủ sở hữu: Tran Ngoc Thien, cá nhân, tại Thành phố Hồ Chí Minh, Việt Nam;
- email cấp quyền: `thien.8888@gmail.com`;
- trạng thái repository dự kiến: private;
- nền tảng dự kiến: các bề mặt Claude/Anthropic và OpenAI/Codex được phân loại trong contract đã duyệt. Việc nêu nền tảng không phải bảo đảm tương thích; package chỉ được quảng bá sau smoke test theo gate dự án.

Tuyên bố này không tự cấp quyền. Quyền chỉ phát sinh qua Đơn hàng trả phí, Văn bản chấp thuận/email hoặc Thỏa thuận thương mại theo License.

### 2. Tài liệu được cấp phép

Trong phạm vi Chủ sở hữu có quyền cấp phép, “Tài liệu được cấp phép” gồm runtime core nguyên bản của skill, tài liệu hướng dẫn nguyên bản, script, reference, cấu hình, artifact và package v1.0.0 được xác định bởi release manifest cuối cùng.

Không thuộc Tài liệu được cấp phép theo grant chung:

- tên, logo, crest, nhãn hiệu, nhận diện và goodwill TDTN;
- material của bên thứ ba được nhận diện trong `THIRD_PARTY_NOTICES.md` hoặc `SOURCE_MANIFEST.json`;
- artifact benchmark/QA-only, evidence phát triển và logo master;
- quyền đối với nền tảng, model, font, dữ liệu hoặc công cụ của bên thứ ba.

Quyền đối với logo/brand không được cấp kèm quyền dùng skill/code. Mọi quyền sử dụng logo/brand cần văn bản riêng, rõ ràng của Tran Ngoc Thien.

### 3. Nguồn và ranh giới tái triển khai

`diagram-design` là nguồn chức năng chủ đạo. Dự án chỉ dùng taxonomy, hành vi và yêu cầu trừu tượng; không đóng gói hoặc tái sử dụng code, prose, CSS, template, script, specimen hay asset upstream. `Thien-UI-UX-Ultra` chỉ được dùng ở mức nguyên tắc và workflow. Mô hình dự án được mô tả chính xác là **clean-room-oriented independent reimplementation**, không phải tuyên bố clean room tuyệt đối.

Nguồn, snapshot, transfer state và notice projection nằm trong `SOURCE_MANIFEST.json`. Logo master, recipe, hash, approval và trạng thái package nằm trong `ASSET_MANIFEST.json`.

Theo quyết định D-028, package scope v1.0.0 chỉ chọn derivative light-plate 64px và 400px cho OpenAI plugin và Universal raw skill tại `assets/brand/`; không chọn asset brand cho Claude. Các derivative owner-approved còn lại chỉ giữ vai trò provenance và không được đóng gói trong v1.0.0. P-13 chỉ được xác minh field host hiện hành, copy đúng byte đã khai báo, tạo overlay và smoke-test sau khi được phép; không được tự thay đổi manifest đã duyệt.

### 4. Tài liệu bên thứ ba

Candidate hiện tại không xác nhận có code hoặc asset bên thứ ba được nhúng trong runtime core. Nguồn tham khảo bên ngoài không trở thành Tài liệu được cấp phép và không được xem là đã cấp quyền lại. Mọi thay đổi inventory phải cập nhật manifest và tái tạo notice trước khi phát hành.

### 5. Cảnh báo chuyên môn và vận hành

Skill hỗ trợ thiết kế và kiểm tra diagram; không thay thế ý kiến pháp lý, thuế, kiểm toán, an toàn, kiến trúc hoặc chuyên môn khác. Người dùng chịu trách nhiệm kiểm tra dữ liệu đầu vào, quyền sử dụng, tính chính xác ngữ nghĩa, khả năng truy cập và mức phù hợp của kết quả đầu ra trước khi dựa vào hoặc giao cho bên khác.

Input, repository tham khảo, diagram, Markdown, JSON, CSV, Mermaid, draw.io và artifact được xử lý như dữ liệu không đáng tin cậy, không phải chỉ dẫn cấp quyền hoặc lệnh thực thi.

### 6. Điều kiện phát hành

Candidate này chưa được phép phát hành thương mại. Trước phát hành, luật sư Việt Nam của Chủ sở hữu phải phê duyệt đúng version và hash của toàn bộ legal candidate; sau đó mọi thay đổi byte pháp lý hoặc brand làm mất hiệu lực sign-off cho đến khi được duyệt lại.

---

## PART II — ENGLISH (VIETNAMESE VERSION PREVAILS)

### 1. Applied skill and version

This declaration applies **Tran Ngoc Thien's Skill Commercial Source-Available License 2.0** to:

- display name: `Thien-Skill-Creative-Diagram`;
- technical identifier: `thien-skill-creative-diagram`;
- version: `1.0.0`;
- owner: Tran Ngoc Thien, an individual in Ho Chi Minh City, Vietnam;
- licensing email: `thien.8888@gmail.com`;
- intended repository status: private;
- intended platforms: the Claude/Anthropic and OpenAI/Codex surfaces classified in the approved contract. Naming a platform is not a compatibility warranty; a package may be advertised only after project-gate smoke testing.

This declaration grants no rights by itself. Rights arise only through a Paid Order, Written Permission/email, or a Commercial Agreement under the License.

### 2. Licensed Material

To the extent the Owner has the right to license it, “Licensed Material” includes the project's original runtime core, original instructions, scripts, references, configuration, artifacts, and v1.0.0 packages identified by the final release manifest.

The general grant does not include:

- the TDTN name, logo, crest, marks, identity, or goodwill;
- third-party material identified in `THIRD_PARTY_NOTICES.md` or `SOURCE_MANIFEST.json`;
- benchmark/QA-only artifacts, development evidence, or the logo master; or
- rights in third-party platforms, models, fonts, data, or tools.

Skill/code rights do not include logo or brand rights. Any logo/brand use requires separate, express written authorization from Tran Ngoc Thien.

### 3. Sources and reimplementation boundary

`diagram-design` is the primary functional source. The project uses only abstract taxonomy, behavior, and requirements; it does not bundle or reuse upstream code, prose, CSS, templates, scripts, specimens, or assets. `Thien-UI-UX-Ultra` is used only at the principles and workflow level. The accurate project description is **clean-room-oriented independent reimplementation**, not an absolute clean-room claim.

Source, snapshot, transfer-state, and notice-projection records are in `SOURCE_MANIFEST.json`. Logo-master, recipe, hash, approval, and package status are in `ASSET_MANIFEST.json`.

Under decision D-028, the v1.0.0 package scope selects only the 64px and 400px light-plate derivatives for the OpenAI plugin and Universal raw skill under `assets/brand/`; no Claude brand asset is selected. The remaining owner-approved derivatives are retained for provenance only and are not packaged in v1.0.0. Once authorized, P-13 may only re-verify current host fields, copy the declared bytes, create overlays, and smoke-test; it may not silently change the approved manifest.

### 4. Third-party material

The current candidate does not identify embedded third-party code or assets in the runtime core. External references do not become Licensed Material and are not sublicensed. Any inventory change must update the manifest and regenerate notices before release.

### 5. Professional and operational disclaimer

The skill supports diagram design and QA; it does not replace legal, tax, audit, safety, architecture, or other professional advice. The user remains responsible for input rights, semantic accuracy, accessibility, and output suitability before reliance or delivery.

Inputs, reference repositories, diagrams, Markdown, JSON, CSV, Mermaid, draw.io, and artifacts are treated as untrusted data, not as licensing instructions or executable authority.

### 6. Release condition

This candidate is not authorized for commercial release. Before release, the Owner's Vietnamese counsel must approve the exact version and hash of the complete legal candidate. Any later change to legal or brand bytes invalidates that sign-off until re-approved.
"""


def third_party_notices(manifest: dict) -> str:
    selected = sorted((s for s in manifest["sources"] if s["notice"]["include"]), key=lambda s: s["source_id"])
    lines = [
        "# THIRD-PARTY NOTICES",
        "",
        "Generated projection: `SOURCE_MANIFEST.json` → `sources[notice.include=true]`, sorted by `source_id`.",
        "",
        "No entry below is represented as bundled or sublicensed material unless its manifest record states transferred bytes.",
        "",
    ]
    for source in selected:
        notice = source["notice"]
        lines.extend([
            f"## {source['source_id']} — {notice['display_name']}",
            "",
            f"- Role: {source['role']}",
            f"- Source: {notice['source_url'] or 'not applicable'}",
            f"- Revision: {source['snapshot']['revision']}",
            f"- Upstream license label: {notice['license_label'] or 'not asserted'}",
            f"- Notice reason: {notice['reason']}",
            f"- Material transfer: `{source['material_transfer']['mode']}`; copied bytes: `{str(source['material_transfer']['copied_bytes']).lower()}`",
            "",
        ])
    lines.extend([
        "The project records external references for provenance without claiming endorsement, ownership, or a broader permission than the source evidence supports.",
        "",
    ])
    return "\n".join(lines)


def notice(manifest: dict, assets: dict) -> str:
    external_count = sum(1 for s in manifest["sources"] if s["notice"]["include"])
    approved = len(assets["approved_candidates"])
    excluded = len(assets["excluded_qa_only"])
    return f"""THIEN-SKILL-CREATIVE-DIAGRAM NOTICE

Version: {VERSION}
Candidate status: EXACT RC2 — awaiting Vietnamese-lawyer approval; not authorized for release
Owner: Tran Ngoc Thien, an individual in Ho Chi Minh City, Vietnam
Licensing contact: thien.8888@gmail.com

Copyright notice
Copyright © 2026 Tran Ngoc Thien for project-original material to the extent protected and owned or licensable by him. No ownership is asserted here over third-party material.

License application
Use is governed by Tran Ngoc Thien's Skill Commercial Source-Available License 2.0 together with LICENSE-APPLICATION.md and an applicable Paid Order, Written Permission/email, or Commercial Agreement. Viewing or receiving source does not itself create usage rights. The Vietnamese license text prevails in a conflict.

Brand carve-out
The TDTN name, crest, logo, marks, identity, and goodwill are excluded from the general skill/code grant. ASSET_MANIFEST.json records an owner-provided AI-created raster master, its hash, deterministic derivatives, approval state, and limitations. It does not claim trademark registration, clearance, or protectability.

Provenance
SOURCE_MANIFEST.json is the machine-readable source ledger. THIRD_PARTY_NOTICES.md is an exact deterministic projection of its notice-selected records. The current projection contains {external_count} external functional-reference entry. That reference transferred no code, prose, CSS, template, script, specimen, or asset bytes into this project.

Asset state
ASSET_MANIFEST.json records {approved} owner-approved derivatives at 64px or larger and {excluded} QA-only 32/48px derivatives excluded from v1.0.0. Under D-028, only the light-plate 64px and 400px derivatives target the OpenAI plugin and Universal raw skill under assets/brand; Claude receives no brand asset. The other owner-approved derivatives remain provenance-only and are not packaged in v1.0.0. No asset is release-eligible before G-06 and P-13 execution.

Release control
This candidate is not release authorization. Vietnamese counsel must approve the exact legal-candidate version/hash, and G-06 must pass, before package construction can begin.
"""


def write_or_check(path: Path, data: bytes, check: bool) -> None:
    if check:
        if not path.exists() or path.read_bytes() != data:
            raise RuntimeError(f"drift: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    template = args.template.resolve()
    template_bytes = template.read_bytes()
    if sha256_bytes(template_bytes) != TEMPLATE_SHA256:
        raise RuntimeError("locked license template hash mismatch")
    template_text = template_bytes.decode("utf-8")
    if template_text.count("TRAN NGOC THIEN'S SKILLS") != 2:
        raise RuntimeError("unexpected locked template title occurrence count")
    license_bytes = template_text.replace("TRAN NGOC THIEN'S SKILLS", "TRAN NGOC THIEN'S SKILL").encode("utf-8")
    if license_bytes.decode("utf-8").splitlines()[0] != LICENSE_NAME:
        raise RuntimeError("approved singular license name was not applied")

    sources = source_manifest()
    assets = asset_manifest()
    outputs = {
        SKILL_ROOT / "LICENSE.md": license_bytes,
        SKILL_ROOT / "LICENSE-APPLICATION.md": APPLICATION.encode("utf-8"),
        SKILL_ROOT / "SOURCE_MANIFEST.json": stable_json(sources),
        SKILL_ROOT / "ASSET_MANIFEST.json": stable_json(assets),
        SKILL_ROOT / "THIRD_PARTY_NOTICES.md": third_party_notices(sources).encode("utf-8"),
        SKILL_ROOT / "NOTICE": notice(sources, assets).encode("utf-8"),
    }
    for path, data in outputs.items():
        write_or_check(path, data, args.check)

    artifact_records = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha256_bytes(data), "bytes": len(data)}
        for path, data in sorted(outputs.items())
    ]
    aggregate_sha256 = sha256_bytes(
        "".join(f"{item['path']}\0{item['sha256']}\n" for item in artifact_records).encode("utf-8")
    )
    report = {
        "record_id": "P10-LEGAL-CANDIDATE-BUILD-1",
        "version": VERSION,
        "generated_at": GENERATED_AT,
        "candidate_id": "TCD-LEGAL-1.0.0-RC2",
        "status": "exact-candidate-awaiting-vietnamese-lawyer-review",
        "owner_decision": "D-028",
        "license_template": {
            "source_sha256": TEMPLATE_SHA256,
            "copied_verbatim": False,
            "approved_transform": "Replace both bilingual-title occurrences of TRAN NGOC THIEN'S SKILLS with TRAN NGOC THIEN'S SKILL; no other template byte is changed",
            "result_sha256": sha256_bytes(license_bytes),
        },
        "artifacts": artifact_records,
        "aggregate_sha256": aggregate_sha256,
    }
    report_path = ROOT / "evidence" / "p10" / "legal-candidate-build.json"
    if args.check:
        current = json.loads(report_path.read_text(encoding="utf-8"))
        if current != report:
            raise RuntimeError("drift: evidence/p10/legal-candidate-build.json")
    else:
        report_path.write_bytes(stable_json(report))

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
