#!/usr/bin/env python3
"""Build or verify the deterministic P-14 sanitized publication mirror."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = "TCD-RELEASE-1.0.0-RC1"
STAGE_ROOT = ROOT / ".release-staging" / CANDIDATE
MANIFEST_REL = Path("evidence/p14/publication-mirror-manifest.json")
LOCAL_MANIFEST = ROOT / MANIFEST_REL
OWNER_HOME = "/" + "Users" + "/" + "thiendeptrainhat"
PERSONAL_PATH_TOKEN = OWNER_HOME.encode("utf-8")

EXCLUDED_PARTS = {
    ".git",
    ".release-staging",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}

REPLACEMENTS = {
    "workspace": (
        f"{OWNER_HOME}/Documents/Thien's Skills Library/Thien-Creative-Diagram",
        "<LOCAL_WORKSPACE>",
    ),
    "ui_ux_reference": (
        f"{OWNER_HOME}/Documents/Thien's Skills Library/Thien-UI-UX-Ultra",
        "<LOCAL_REFERENCE_REPOSITORY>/Thien-UI-UX-Ultra",
    ),
    "owner_logo_source": (
        f"{OWNER_HOME}/Documents/Logo TDTN.png",
        "<OWNER_ASSET_SOURCE>/Logo TDTN.png",
    ),
    "owner_license_template": (
        f"{OWNER_HOME}/Documents/Thien's Skills Library/Thien-Skills-License-Template/Tran-Ngoc-Thiens-Skills-Commercial-Source-Available-License-2.0.md",
        "<OWNER_LICENSE_TEMPLATE_SOURCE>/Tran-Ngoc-Thiens-Skills-Commercial-Source-Available-License-2.0.md",
    ),
    "local_plugin_validator": (
        f"{OWNER_HOME}/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py",
        "<LOCAL_CODEX_SKILLS>/plugin-creator/scripts/validate_plugin.py",
    ),
}

FILE_PLAN = {
    "HANDOFF-P01.md": ["workspace", "ui_ux_reference", "owner_logo_source"],
    "PROJECT-CONTRACT.md": ["owner_logo_source", "owner_license_template"],
    "evidence/p01/SNAPSHOT-RECORD.md": ["ui_ux_reference"],
    "evidence/p09/P-09-EVIDENCE.md": ["owner_logo_source"],
    "evidence/p13/verify_packages.py": ["local_plugin_validator"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_excluded(relative: Path) -> bool:
    if relative == MANIFEST_REL:
        return True
    return (
        any(part in EXCLUDED_PARTS for part in relative.parts)
        or relative.name in EXCLUDED_NAMES
        or relative.suffix in EXCLUDED_SUFFIXES
    )


def source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if is_excluded(relative):
            continue
        if path.is_symlink():
            raise RuntimeError(f"Symlink is not allowed in publication scope: {relative.as_posix()}")
        if path.is_file():
            files.append(relative)
    return sorted(files, key=lambda item: item.as_posix())


def transformed(relative: Path, data: bytes) -> tuple[bytes, list[dict]]:
    key = relative.as_posix()
    replacement_records: list[dict] = []
    if key not in FILE_PLAN:
        return data, replacement_records
    text = data.decode("utf-8")
    for replacement_id in FILE_PLAN[key]:
        original, placeholder = REPLACEMENTS[replacement_id]
        count = text.count(original)
        if count == 0:
            raise RuntimeError(f"Expected replacement {replacement_id} is absent from {key}")
        text = text.replace(original, placeholder)
        replacement_records.append({"replacement_id": replacement_id, "count": count})
    result = text.encode("utf-8")
    if PERSONAL_PATH_TOKEN in result:
        raise RuntimeError(f"Personal path remains after sanitization: {key}")
    return result, replacement_records


def normalized_mode(path: Path) -> int:
    return 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644


def expected_tree() -> tuple[list[dict], list[dict]]:
    entries: list[dict] = []
    changes: list[dict] = []
    for relative in source_files():
        source = ROOT / relative
        source_data = source.read_bytes()
        mirror_data, replacements = transformed(relative, source_data)
        mode = normalized_mode(source)
        entry = {
            "path": relative.as_posix(),
            "mode": f"{mode:04o}",
            "bytes": len(mirror_data),
            "sha256": sha256(mirror_data),
        }
        entries.append(entry)
        if replacements:
            changes.append(
                {
                    "path": relative.as_posix(),
                    "source_sha256": sha256(source_data),
                    "mirror_sha256": entry["sha256"],
                    "replacements": replacements,
                }
            )
    return entries, changes


def aggregate(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["mode"].encode("ascii"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def manifest(entries: list[dict], changes: list[dict]) -> dict:
    return {
        "record_id": "P14-PUBLICATION-MIRROR-1",
        "candidate": CANDIDATE,
        "decision": "D-036",
        "publication_scope": "A_FULL_PRIVATE_AUDIT_REPOSITORY_SANITIZED_MIRROR",
        "source_root": "<LOCAL_WORKSPACE>",
        "mirror_root": f"<LOCAL_RELEASE_STAGING>/{CANDIDATE}",
        "generated_manifest_path": MANIFEST_REL.as_posix(),
        "aggregate_excludes_generated_manifest": True,
        "source_file_count": len(entries),
        "mirror_file_count_including_manifest": len(entries) + 1,
        "changed_file_count": len(changes),
        "changed_files": changes,
        "excluded_classes": sorted(EXCLUDED_PARTS | EXCLUDED_NAMES | EXCLUDED_SUFFIXES),
        "tree_aggregate_sha256": aggregate(entries),
        "personal_machine_path_scan": {
            "forbidden_token": "/Users/<owner>",
            "matches": 0,
            "result": "PASS",
        },
        "generic_security_patterns_preserved": [
            "validator regex for absolute paths",
            "generic /Users/example test fixture",
        ],
        "git_or_release_mutation_performed": False,
    }


def manifest_bytes(record: dict) -> bytes:
    return (json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build() -> dict:
    entries, changes = expected_tree()
    record = manifest(entries, changes)
    if STAGE_ROOT.exists():
        shutil.rmtree(STAGE_ROOT)
    STAGE_ROOT.mkdir(parents=True, exist_ok=True)
    entry_by_path = {entry["path"]: entry for entry in entries}
    for relative in source_files():
        source = ROOT / relative
        mirror_data, _ = transformed(relative, source.read_bytes())
        destination = STAGE_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(mirror_data)
        os.chmod(destination, int(entry_by_path[relative.as_posix()]["mode"], 8))
    encoded = manifest_bytes(record)
    LOCAL_MANIFEST.write_bytes(encoded)
    stage_manifest = STAGE_ROOT / MANIFEST_REL
    stage_manifest.parent.mkdir(parents=True, exist_ok=True)
    stage_manifest.write_bytes(encoded)
    os.chmod(LOCAL_MANIFEST, 0o644)
    os.chmod(stage_manifest, 0o644)
    return verify()


def refresh_git_worktree() -> dict:
    """Refresh the already initialized staging worktree without touching .git."""
    git_dir = STAGE_ROOT / ".git"
    if not git_dir.is_dir():
        raise RuntimeError("Refusing refresh: staging target is not an initialized Git worktree")
    entries, changes = expected_tree()
    record = manifest(entries, changes)
    expected_paths = {entry["path"] for entry in entries} | {MANIFEST_REL.as_posix()}
    for path in sorted(STAGE_ROOT.rglob("*"), reverse=True):
        relative = path.relative_to(STAGE_ROOT)
        if ".git" in relative.parts:
            continue
        if path.is_file() and relative.as_posix() not in expected_paths:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    entry_by_path = {entry["path"]: entry for entry in entries}
    for relative in source_files():
        source = ROOT / relative
        mirror_data, _ = transformed(relative, source.read_bytes())
        destination = STAGE_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(mirror_data)
        os.chmod(destination, int(entry_by_path[relative.as_posix()]["mode"], 8))
    encoded = manifest_bytes(record)
    LOCAL_MANIFEST.write_bytes(encoded)
    stage_manifest = STAGE_ROOT / MANIFEST_REL
    stage_manifest.parent.mkdir(parents=True, exist_ok=True)
    stage_manifest.write_bytes(encoded)
    os.chmod(LOCAL_MANIFEST, 0o644)
    os.chmod(stage_manifest, 0o644)
    return verify()


def verify() -> dict:
    entries, changes = expected_tree()
    record = manifest(entries, changes)
    failures: list[str] = []
    expected_paths = {entry["path"] for entry in entries} | {MANIFEST_REL.as_posix()}
    actual_paths = {
        path.relative_to(STAGE_ROOT).as_posix()
        for path in STAGE_ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(STAGE_ROOT).parts
    } if STAGE_ROOT.is_dir() else set()
    if actual_paths != expected_paths:
        failures.append("mirror inventory differs from expected publication scope")
    for entry in entries:
        destination = STAGE_ROOT / entry["path"]
        if not destination.is_file():
            continue
        data = destination.read_bytes()
        if sha256(data) != entry["sha256"]:
            failures.append(f"hash mismatch: {entry['path']}")
        if PERSONAL_PATH_TOKEN in data:
            failures.append(f"personal path remains: {entry['path']}")
    expected_manifest = manifest_bytes(record)
    if not LOCAL_MANIFEST.is_file() or LOCAL_MANIFEST.read_bytes() != expected_manifest:
        failures.append("local manifest differs from expected record")
    stage_manifest = STAGE_ROOT / MANIFEST_REL
    if not stage_manifest.is_file() or stage_manifest.read_bytes() != expected_manifest:
        failures.append("staged manifest differs from expected record")
    return {
        "record_id": record["record_id"],
        "candidate": CANDIDATE,
        "checks": 5,
        "failed": len(failures),
        "passed": 5 - len(failures),
        "status": "PASS" if not failures else "FAIL",
        "source_file_count": record["source_file_count"],
        "mirror_file_count_including_manifest": record["mirror_file_count_including_manifest"],
        "changed_file_count": record["changed_file_count"],
        "tree_aggregate_sha256": record["tree_aggregate_sha256"],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify the existing mirror without writing")
    parser.add_argument(
        "--refresh-git-worktree",
        action="store_true",
        help="refresh an initialized staging worktree without changing its .git directory",
    )
    args = parser.parse_args()
    if args.check and args.refresh_git_worktree:
        parser.error("choose only one of --check or --refresh-git-worktree")
    if args.refresh_git_worktree:
        result = refresh_git_worktree()
    else:
        result = verify() if args.check else build()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
