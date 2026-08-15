#!/usr/bin/env python3
"""Build the three deterministic P-13 delivery archives from one canonical skill."""

from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


ROOT = Path(__file__).resolve().parents[2]
P13 = ROOT / "evidence" / "p13"
CANONICAL = ROOT / "thien-skill-creative-diagram"
DIST = ROOT / "dist"
SKILL_ID = "thien-skill-creative-diagram"
VERSION = "1.0.0"
CANDIDATE_ID = "TCD-PACKAGES-1.0.0-RC1"
ZIP_TIMESTAMP = (2026, 8, 15, 0, 0, 0)
LEGAL_NAMES = (
    "LICENSE.md",
    "LICENSE-APPLICATION.md",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_MANIFEST.json",
    "ASSET_MANIFEST.json",
)
DEVELOPMENT_SCRIPTS = {
    "generate_p07_evidence.py",
    "generate_p08_evidence.py",
    "generate_p11_evidence.py",
    "generate_semantic_references.py",
    "p07_coverage.py",
    "p08_coverage.py",
    "p11_coverage.py",
}
PACKAGE_FILES = {
    "claude-plugin": f"{SKILL_ID}-{VERSION}-claude-plugin.zip",
    "openai-plugin": f"{SKILL_ID}-{VERSION}-openai-plugin.zip",
    "universal-raw-skill": f"{SKILL_ID}-{VERSION}-universal-raw-skill.zip",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"expected regular file: {path}")
    return path.read_bytes()


def runtime_files() -> dict[str, bytes]:
    files = {"SKILL.md": read_file(CANONICAL / "SKILL.md")}
    for directory in ("references", "scripts"):
        base = CANONICAL / directory
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                raise RuntimeError(f"symlink is not allowed in canonical runtime: {path}")
            if not path.is_file():
                continue
            rel = path.relative_to(CANONICAL).as_posix()
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".log", ".zip"}:
                continue
            if directory == "scripts" and ("tests" in path.relative_to(base).parts or path.name in DEVELOPMENT_SCRIPTS):
                continue
            files[rel] = path.read_bytes()
    return dict(sorted(files.items()))


def legal_files() -> dict[str, bytes]:
    return {name: read_file(CANONICAL / name) for name in LEGAL_NAMES}


def brand_files() -> dict[str, bytes]:
    manifest = json.loads((CANONICAL / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    selected = {}
    for item in manifest["approved_candidates"]:
        if item["asset_id"] not in {"AST-TDTN-LIGHT-64", "AST-TDTN-LIGHT-400"}:
            continue
        expected_targets = {"openai-plugin", "universal-raw-skill"}
        if set(item["package_targets"]) != expected_targets:
            raise RuntimeError(f"unexpected target set for {item['asset_id']}")
        source = ROOT / item["source_evidence_path"]
        data = read_file(source)
        if sha(data) != item["sha256"]:
            raise RuntimeError(f"brand source hash drift: {source}")
        destinations = {d["path"] for d in item["destinations"] if d["package_target"] in expected_targets}
        if len(destinations) != 1:
            raise RuntimeError(f"brand destination drift: {item['asset_id']}")
        selected[destinations.pop()] = data
    expected = {
        "assets/brand/full-crest-plate-light-64.png",
        "assets/brand/full-crest-plate-light-400.png",
    }
    if set(selected) != expected:
        raise RuntimeError("D-028 brand selection is incomplete")
    return dict(sorted(selected.items()))


def claude_manifest() -> bytes:
    return canonical_json({
        "author": {"email": "thien.8888@gmail.com", "name": "Tran Ngoc Thien"},
        "description": "Design original professional diagrams with semantic, quantitative, accessibility and Vietnamese-text safeguards.",
        "displayName": "Thien-Skill-Creative-Diagram",
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
            "displayName": "Thien-Skill-Creative-Diagram",
            "longDescription": "Create original architecture, process, data-platform and quantitative diagrams with portable HTML/SVG output and explicit fallbacks.",
            "logo": "./assets/brand/full-crest-plate-light-400.png",
            "shortDescription": "Professional semantic diagram workflows",
        },
        "name": SKILL_ID,
        "skills": "./skills/",
        "version": VERSION,
    })


def base_openai_overlay() -> bytes:
    return read_file(CANONICAL / "agents" / "openai.yaml")


def universal_openai_overlay() -> bytes:
    text = base_openai_overlay().decode("utf-8")
    anchor = '  short_description: "Design professional, semantic diagrams"\n'
    if text.count(anchor) != 1 or "icon_small:" in text or "icon_large:" in text:
        raise RuntimeError("canonical agents/openai.yaml no longer matches the approved adapter anchor")
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

    claude: dict[str, bytes] = {f"{root}/.claude-plugin/plugin.json": claude_manifest()}
    add_skill(claude, f"{root}/skills/{SKILL_ID}", runtime)
    for name, data in legal.items():
        claude[f"{root}/{name}"] = data

    openai: dict[str, bytes] = {f"{root}/.codex-plugin/plugin.json": openai_manifest()}
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
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for name in sorted(files):
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts or len(pure.parts) < 2:
                raise RuntimeError(f"unsafe archive path: {name}")
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(info, files[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return stream.getvalue()


def digest_logical(files: dict[str, bytes]) -> str:
    payload = b"".join(name.encode("utf-8") + b"\0" + sha(data).encode("ascii") + b"\n" for name, data in sorted(files.items()))
    return sha(payload)


def role_for(member: str) -> str:
    if "/.claude-plugin/" in member or "/.codex-plugin/" in member or member.endswith("/agents/openai.yaml"):
        return "platform-overlay"
    if "/assets/brand/" in member:
        return "brand-presentation"
    if member.rsplit("/", 1)[-1] in LEGAL_NAMES:
        return "legal-provenance"
    return "runtime-core"


def expected_build() -> tuple[dict, dict[str, bytes], bytes]:
    mappings = package_mappings()
    runtime_digest = digest_logical(runtime_files())
    legal_digest = digest_logical(legal_files())
    archives = {target: zip_bytes(files) for target, files in mappings.items()}
    packages = []
    for target in sorted(archives):
        members = [
            {"path": path, "role": role_for(path), "bytes": len(data), "sha256": sha(data)}
            for path, data in mappings[target].items()
        ]
        packages.append({
            "target": target,
            "filename": PACKAGE_FILES[target],
            "sha256": sha(archives[target]),
            "bytes": len(archives[target]),
            "file_count": len(members),
            "runtime_core_aggregate_sha256": runtime_digest,
            "legal_bundle_aggregate_sha256": legal_digest,
            "members": members,
        })
    record = {
        "record_id": "P13-PACKAGE-BUILD-1",
        "candidate_id": CANDIDATE_ID,
        "version": VERSION,
        "built_at": "2026-08-15T00:00:00+07:00",
        "zip_timestamp": "2026-08-15T00:00:00",
        "canonical_source": SKILL_ID,
        "legal_candidate_id": "TCD-LEGAL-1.0.0-RC2",
        "legal_candidate_aggregate_sha256": "8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6",
        "brand_decision": "D-028",
        "authorization": "D-032",
        "packages": packages,
    }
    sums = "".join(f"{item['sha256']}  {item['filename']}\n" for item in packages).encode("utf-8")
    return record, archives, sums


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record, archives, sums = expected_build()
    record_bytes = canonical_json(record)
    if args.check:
        expected = {DIST / PACKAGE_FILES[target]: data for target, data in archives.items()}
        expected[P13 / "package-build.json"] = record_bytes
        expected[DIST / "SHA256SUMS.txt"] = sums
        drift = [str(path.relative_to(ROOT)) for path, data in expected.items() if not path.is_file() or path.read_bytes() != data]
        if drift:
            print(json.dumps({"status": "FAIL", "drift": drift}, indent=2))
            return 1
        print(json.dumps({"status": "PASS", "packages": len(archives), "candidate_id": CANDIDATE_ID}, indent=2))
        return 0
    DIST.mkdir(parents=True, exist_ok=True)
    P13.mkdir(parents=True, exist_ok=True)
    for target, data in archives.items():
        (DIST / PACKAGE_FILES[target]).write_bytes(data)
    (DIST / "SHA256SUMS.txt").write_bytes(sums)
    (P13 / "package-build.json").write_bytes(record_bytes)
    print(json.dumps({"status": "BUILT", "packages": len(archives), "candidate_id": CANDIDATE_ID}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
