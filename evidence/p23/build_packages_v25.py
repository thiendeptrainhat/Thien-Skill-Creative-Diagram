#!/usr/bin/env python3
"""Build the deterministic D-201 three-envelope v2.5.0 staging candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import zipfile


ROOT = Path(__file__).resolve().parents[2]
P23 = ROOT / "evidence" / "p23"
CANONICAL = ROOT / "thien-skill-creative-diagram"
STAGING = P23 / "candidate-dist" / "2.5.0"
VERSION = "2.5.0"
CANDIDATE_ID = "TCD-PACKAGES-2.5.0-RC1"
SKILL_ID = "thien-skill-creative-diagram"
DISPLAY_NAME = "Thiện’s Skill — Creative Diagram"
ZIP_TIMESTAMP = (2026, 9, 2, 0, 0, 0)
D200_BINDING = "49b273f91cb9bd78701484e4d943d494b4f3cc5f86cf093db6ab584814cd58b8"
EXPECTED_RUNTIME = (110, 1484424, "9344048c269944cba14a1ae0ae1d7f7239bd951bdf54d69d2d31f980dc502a35")
TARGET_ORDER = ("claude-plugin", "openai-plugin", "universal-raw-skill")
PACKAGE_FILES = {
    "claude-plugin": "Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip",
    "openai-plugin": "Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip",
    "universal-raw-skill": "Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip",
}
FINAL_INVENTORY = (
    "SHA256SUMS",
    "packaging-report.json",
    PACKAGE_FILES["claude-plugin"],
    PACKAGE_FILES["openai-plugin"],
    PACKAGE_FILES["universal-raw-skill"],
)
LEGAL_NAMES = (
    "LICENSE.md", "LICENSE-APPLICATION.md", "NOTICE",
    "THIRD_PARTY_NOTICES.md", "SOURCE_MANIFEST.json", "ASSET_MANIFEST.json",
)
DEVELOPMENT_SCRIPTS = {
    "generate_p07_evidence.py", "generate_p08_evidence.py", "generate_p11_evidence.py",
    "generate_semantic_references.py", "p07_coverage.py", "p08_coverage.py", "p11_coverage.py",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load controller: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


legal_builder = load_module("p23_legal_builder", P23 / "build_legal_candidate_v25.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest_logical(files: dict[str, bytes]) -> str:
    payload = b"".join(
        name.encode("utf-8") + b"\0" + sha(data).encode("ascii") + b"\n"
        for name, data in sorted(files.items())
    )
    return sha(payload)


def read_regular(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"expected regular file: {path.relative_to(ROOT)}")
    return path.read_bytes()


def runtime_files() -> dict[str, bytes]:
    files = {"SKILL.md": read_regular(CANONICAL / "SKILL.md")}
    for directory in ("references", "scripts"):
        base = CANONICAL / directory
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                raise RuntimeError(f"symlink is forbidden in runtime: {path.relative_to(ROOT)}")
            if not path.is_file():
                continue
            rel = path.relative_to(CANONICAL).as_posix()
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".log", ".zip"}:
                continue
            if directory == "scripts" and (
                "tests" in path.relative_to(base).parts or path.name in DEVELOPMENT_SCRIPTS
            ):
                continue
            files[rel] = path.read_bytes()
    files = dict(sorted(files.items()))
    actual = (len(files), sum(len(data) for data in files.values()), digest_logical(files))
    if actual != EXPECTED_RUNTIME:
        raise RuntimeError(f"D-193 runtime candidate drift: {actual}")
    return files


def legal_files() -> dict[str, bytes]:
    return legal_builder.candidate_files()


def brand_files() -> dict[str, bytes]:
    manifest = json.loads((CANONICAL / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    selected: dict[str, bytes] = {}
    for item in manifest["approved_candidates"]:
        if item["asset_id"] not in {"AST-TDTN-LIGHT-64", "AST-TDTN-LIGHT-400"}:
            continue
        if set(item["package_targets"]) != {"openai-plugin", "universal-raw-skill"}:
            raise RuntimeError(f"brand target drift: {item['asset_id']}")
        source = ROOT / item["source_evidence_path"]
        data = read_regular(source)
        if sha(data) != item["sha256"]:
            raise RuntimeError(f"brand byte drift: {item['asset_id']}")
        destinations = {entry["path"] for entry in item["destinations"]}
        if len(destinations) != 1:
            raise RuntimeError(f"brand destination drift: {item['asset_id']}")
        selected[destinations.pop()] = data
    expected = {
        "assets/brand/full-crest-plate-light-64.png",
        "assets/brand/full-crest-plate-light-400.png",
    }
    if set(selected) != expected:
        raise RuntimeError("exact two-file D-197 brand selection is incomplete")
    return dict(sorted(selected.items()))


def claude_manifest() -> bytes:
    return canonical_json({
        "author": {"email": "thien.8888@gmail.com", "name": "Tran Ngoc Thien"},
        "description": "Design original professional diagrams with semantic, quantitative, accessibility and Vietnamese-text safeguards.",
        "displayName": DISPLAY_NAME,
        "name": SKILL_ID,
        "skills": "./skills/",
        "version": VERSION,
    })


def openai_manifest() -> bytes:
    return canonical_json({
        "author": {"email": "thien.8888@gmail.com", "name": "Tran Ngoc Thien"},
        "description": "Design original professional diagrams with semantic, quantitative, accessibility and Vietnamese-text safeguards.",
        "interface": {
            "capabilities": ["Read", "Write"],
            "category": "Productivity",
            "composerIcon": "./assets/brand/full-crest-plate-light-64.png",
            "defaultPrompt": ["Create a professional diagram from my requirements."],
            "developerName": "Tran Ngoc Thien",
            "displayName": DISPLAY_NAME,
            "longDescription": "Create original architecture, process, data-platform and quantitative diagrams with portable HTML/SVG output and explicit fallbacks.",
            "logo": "./assets/brand/full-crest-plate-light-400.png",
            "shortDescription": "Professional semantic diagram workflows",
        },
        "name": SKILL_ID,
        "skills": "./skills/",
        "version": VERSION,
    })


def base_openai_overlay() -> bytes:
    data = read_regular(CANONICAL / "agents" / "openai.yaml")
    text = data.decode("utf-8")
    required = (
        f'  display_name: "{DISPLAY_NAME}"\n',
        '  short_description: "Design professional, semantic diagrams"\n',
        '  default_prompt: "Use $thien-skill-creative-diagram to create a professional diagram from my requirements."\n',
    )
    if not all(fragment in text for fragment in required):
        raise RuntimeError("canonical agents/openai.yaml identity drift")
    return data


def universal_openai_overlay() -> bytes:
    text = base_openai_overlay().decode("utf-8")
    anchor = '  short_description: "Design professional, semantic diagrams"\n'
    if text.count(anchor) != 1 or "icon_small:" in text or "icon_large:" in text:
        raise RuntimeError("canonical OpenAI overlay anchor drift")
    icons = (
        '  icon_small: "./assets/brand/full-crest-plate-light-64.png"\n'
        '  icon_large: "./assets/brand/full-crest-plate-light-400.png"\n'
    )
    return text.replace(anchor, anchor + icons).encode("utf-8")


def add_skill(mapping: dict[str, bytes], prefix: str, runtime: dict[str, bytes]) -> None:
    for logical, data in runtime.items():
        mapping[f"{prefix}/{logical}"] = data


def package_mappings() -> dict[str, dict[str, bytes]]:
    runtime = runtime_files()
    legal = legal_files()
    brand = brand_files()
    root = SKILL_ID

    claude = {f"{root}/.claude-plugin/plugin.json": claude_manifest()}
    add_skill(claude, f"{root}/skills/{SKILL_ID}", runtime)
    for name, data in legal.items():
        claude[f"{root}/{name}"] = data

    openai = {f"{root}/.codex-plugin/plugin.json": openai_manifest()}
    add_skill(openai, f"{root}/skills/{SKILL_ID}", runtime)
    openai[f"{root}/skills/{SKILL_ID}/agents/openai.yaml"] = base_openai_overlay()
    for name, data in legal.items():
        openai[f"{root}/{name}"] = data
    for name, data in brand.items():
        openai[f"{root}/{name}"] = data

    universal: dict[str, bytes] = {}
    add_skill(universal, root, runtime)
    universal[f"{root}/agents/openai.yaml"] = universal_openai_overlay()
    for name, data in legal.items():
        universal[f"{root}/{name}"] = data
    for name, data in brand.items():
        universal[f"{root}/{name}"] = data

    return {
        "claude-plugin": dict(sorted(claude.items())),
        "openai-plugin": dict(sorted(openai.items())),
        "universal-raw-skill": dict(sorted(universal.items())),
    }


def zip_bytes(files: dict[str, bytes]) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(
        stream, "w", compression=zipfile.ZIP_DEFLATED,
        compresslevel=9, strict_timestamps=True,
    ) as archive:
        for name in sorted(files):
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts or pure.parts[0] != SKILL_ID:
                raise RuntimeError(f"unsafe archive path: {name}")
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(info, files[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return stream.getvalue()


def role_for(member: str) -> str:
    if "/.claude-plugin/" in member or "/.codex-plugin/" in member or member.endswith("/agents/openai.yaml"):
        return "platform-overlay"
    if "/assets/brand/" in member:
        return "brand-presentation"
    if member.rsplit("/", 1)[-1] in LEGAL_NAMES:
        return "legal-provenance"
    return "runtime-core"


def controller_hashes() -> dict[str, str]:
    paths = {
        "build_legal_candidate_v25.py": P23 / "build_legal_candidate_v25.py",
        "build_packages_v25.py": P23 / "build_packages_v25.py",
        "verify_packages_v25.py": P23 / "verify_packages_v25.py",
    }
    return {name: sha(read_regular(path)) for name, path in paths.items()}


def expected_build() -> tuple[dict, dict[str, bytes], bytes]:
    mappings = package_mappings()
    runtime = runtime_files()
    legal = legal_files()
    archives = {target: zip_bytes(mappings[target]) for target in TARGET_ORDER}
    packages = []
    for target in TARGET_ORDER:
        members = [
            {"path": path, "role": role_for(path), "bytes": len(data), "sha256": sha(data)}
            for path, data in mappings[target].items()
        ]
        packages.append({
            "target": target,
            "filename": PACKAGE_FILES[target],
            "bytes": len(archives[target]),
            "sha256": sha(archives[target]),
            "file_count": len(members),
            "runtime_core_aggregate_sha256": digest_logical(runtime),
            "legal_bundle_aggregate_sha256": digest_logical(legal),
            "members": members,
        })
    sums = "".join(f"{item['sha256']}  {item['filename']}\n" for item in packages).encode("utf-8")
    report = {
        "record_id": "P23-PACKAGING-REPORT-1",
        "candidate_id": CANDIDATE_ID,
        "version": VERSION,
        "display_name": DISPLAY_NAME,
        "technical_id": SKILL_ID,
        "status": "BUILD-COMPLETE / G-05-NOT-EVALUATED",
        "authorization": {"decision": "D-201", "d200_aggregate_binding_sha256": D200_BINDING},
        "staging_root": "evidence/p23/candidate-dist/2.5.0",
        "final_root": "dist/2.5.0",
        "final_inventory_order": list(FINAL_INVENTORY),
        "canonical_source": {
            "path": SKILL_ID,
            "files": len(runtime),
            "bytes": sum(len(data) for data in runtime.values()),
            "logical_sha256": digest_logical(runtime),
        },
        "legal_candidate": {
            "candidate_id": legal_builder.CANDIDATE_ID,
            "files": len(legal),
            "bytes": sum(len(data) for data in legal.values()),
            "logical_sha256": digest_logical(legal),
            "g06_status": "PENDING OWNER DISPOSITION",
        },
        "zip_parameters": {
            "timestamp": "2026-09-02T00:00:00",
            "compression": "ZIP_DEFLATED level 9",
            "member_mode": "0100644",
            "member_order": "UTF-8 path sorted",
            "one_safe_root": SKILL_ID,
        },
        "packages": packages,
        "parity_allowlist": {
            "claude-plugin": [".claude-plugin/plugin.json", "nested skills/ runtime", "no brand"],
            "openai-plugin": [".codex-plugin/plugin.json", "nested skills/ runtime", "canonical agents/openai.yaml", "64px/400px approved brand"],
            "universal-raw-skill": ["raw skill root", "agents/openai.yaml icon overlay", "64px/400px approved brand"],
        },
        "controllers": controller_hashes(),
        "checksum": {"filename": "SHA256SUMS", "bytes": len(sums), "sha256": sha(sums)},
        "release_notes_sha256": sha(read_regular(ROOT / "evidence" / "p21" / "RELEASE-NOTES-v2.5.0.md")),
        "g05": {"status": "NOT-EVALUATED", "checks": [], "smoke_results": {}},
        "limits": [
            "Candidate bytes remain in evidence/p23 staging and are not release artifacts.",
            "G-06, dist promotion, Git, tag, GitHub Release and publication remain unauthorized.",
        ],
    }
    return report, archives, sums


def report_without_g05(value: dict) -> dict:
    projected = dict(value)
    projected.pop("g05", None)
    projected["status"] = "BUILD-COMPLETE / G-05-NOT-EVALUATED"
    return projected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report, archives, sums = expected_build()
    expected = {STAGING / PACKAGE_FILES[target]: archives[target] for target in TARGET_ORDER}
    expected[STAGING / "SHA256SUMS"] = sums
    allowed = set(FINAL_INVENTORY)

    if args.check:
        drift = [
            str(path.relative_to(ROOT)) for path, data in expected.items()
            if not path.is_file() or path.read_bytes() != data
        ]
        report_path = STAGING / "packaging-report.json"
        try:
            actual_report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            drift.append(str(report_path.relative_to(ROOT)))
        else:
            if report_without_g05(actual_report) != report_without_g05(report):
                drift.append(str(report_path.relative_to(ROOT)))
        actual_names = {path.name for path in STAGING.iterdir()} if STAGING.is_dir() else set()
        if actual_names != allowed:
            drift.append("evidence/p23/candidate-dist/2.5.0 inventory")
        print(json.dumps({"status": "PASS" if not drift else "FAIL", "drift": sorted(set(drift))}, indent=2))
        return 1 if drift else 0

    if STAGING.exists() and not STAGING.is_dir():
        raise RuntimeError("staging root exists but is not a directory")
    STAGING.mkdir(parents=True, exist_ok=True)
    extras = {path.name for path in STAGING.iterdir()} - allowed
    if extras:
        raise RuntimeError(f"undeclared staging entries: {sorted(extras)}")
    for path, data in expected.items():
        path.write_bytes(data)
    (STAGING / "packaging-report.json").write_bytes(canonical_json(report))
    print(json.dumps({"status": "BUILT", "candidate_id": CANDIDATE_ID, "packages": 3}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
