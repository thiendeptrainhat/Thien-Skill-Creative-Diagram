"""Read-only golden comparison harness for P-11.

The harness compares approved bytes with a manifest.  It intentionally has no
baseline-writing or update operation; approval and baseline creation remain an
owner-controlled workflow outside this script.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from qa_contract import QAFailure, sha256_bytes


GOLDEN_SCHEMA_VERSION = "1.0"


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise QAFailure("golden-manifest-invalid", "Golden manifest is not readable valid JSON.", location=str(path)) from error
    if set(value) != {"schema_version", "approval", "immutable", "artifacts"}:
        raise QAFailure("golden-manifest-invalid", "Golden manifest fields do not match the P-11 contract.", location=str(path))
    if value["schema_version"] != GOLDEN_SCHEMA_VERSION or value["immutable"] is not True:
        raise QAFailure("golden-manifest-mutable", "Golden manifest must declare the immutable P-11 schema.", location=str(path))
    if value["approval"] not in {"owner-approved", "approved-p06-direction"}:
        raise QAFailure("golden-approval-missing", "Golden comparison requires an explicit approved status.", location=str(path))
    if not isinstance(value["artifacts"], list) or not value["artifacts"]:
        raise QAFailure("golden-manifest-empty", "Golden manifest must list at least one approved artifact.", location=str(path))
    return value


def compare_manifest(manifest: Mapping[str, Any], root: Path) -> dict[str, Any]:
    root = root.resolve()
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in manifest["artifacts"]:
        if set(item) != {"path", "sha256", "media_type", "approval_ref"}:
            raise QAFailure("golden-entry-invalid", "Golden entry fields do not match the P-11 contract.", location="golden-manifest")
        relative = str(item["path"])
        if relative in seen:
            raise QAFailure("golden-entry-duplicate", "Golden manifest contains a duplicate path.", location=relative)
        seen.add(relative)
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise QAFailure("golden-path-escape", "Golden path escapes its declared root.", location=relative) from error
        if not candidate.is_file():
            raise QAFailure("golden-artifact-missing", "Approved golden artifact is missing.", location=relative)
        actual = sha256_bytes(candidate.read_bytes())
        if actual != item["sha256"]:
            raise QAFailure("golden-drift", "Approved golden bytes changed; review is required and no baseline was updated.", location=relative)
        results.append({"path": relative, "sha256": actual, "status": "match"})
    return {"status": "pass", "immutable": True, "compared": len(results), "results": results}


def compare(manifest_path: Path, root: Path) -> dict[str, Any]:
    return compare_manifest(load_manifest(manifest_path), root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare immutable approved golden bytes; this command cannot update baselines.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = compare(args.manifest, args.root)
    except QAFailure as error:
        payload = {"status": "fail", "issue": error.issue(), "baseline_updated": False}
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if args.json else f"FAIL {error.code}: {error.message}")
        return 1
    payload = {**result, "baseline_updated": False}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if args.json else f"PASS: {result['compared']} immutable golden artifacts match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

