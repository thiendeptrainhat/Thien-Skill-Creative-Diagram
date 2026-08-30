#!/usr/bin/env python3
"""Build or verify the deterministic sanitized publication mirror for v2.0.0."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "evidence" / "p14" / "build_publication_mirror.py"


def load_base():
    spec = importlib.util.spec_from_file_location("p14_publication_builder", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base()
base.CANDIDATE = "TCD-RELEASE-2.0.0-RC1"
base.STAGE_ROOT = ROOT / ".release-staging" / base.CANDIDATE
base.MANIFEST_REL = Path("evidence/p21/publication-mirror-manifest.json")
base.LOCAL_MANIFEST = ROOT / base.MANIFEST_REL

base_transformed = base.transformed
base_manifest = base.manifest


def transformed(relative: Path, data: bytes) -> tuple[bytes, list[dict]]:
    result, records = base_transformed(relative, data)
    if base.PERSONAL_PATH_TOKEN not in result:
        return result, records
    try:
        text = result.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"Owner path occurs in non-UTF-8 publication artifact: {relative.as_posix()}"
        ) from exc
    owner_home = base.OWNER_HOME
    count = text.count(owner_home)
    result = text.replace(owner_home, "<OWNER_HOME>").encode("utf-8")
    records.append({"replacement_id": "owner_home_global_v2", "count": count})
    return result, records


def manifest(entries: list[dict], changes: list[dict]) -> dict:
    record = base_manifest(entries, changes)
    record.update(
        {
            "record_id": "P21-PUBLICATION-MIRROR-2.0.0-1",
            "candidate": base.CANDIDATE,
            "decision": "D-132",
            "publication_scope": "A_FULL_PRIVATE_AUDIT_REPOSITORY_SANITIZED_MIRROR_V2",
            "sanitization_version": "2.0.0",
            "sanitization_note": "Exact owner-home paths are replaced in UTF-8 audit text; generic security fixtures remain unchanged.",
        }
    )
    return record


base.transformed = transformed
base.manifest = manifest


if __name__ == "__main__":
    raise SystemExit(base.main())
