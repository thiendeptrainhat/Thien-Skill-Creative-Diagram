"""Dependency-free verification for P-09 candidate PNGs and provenance."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "ASSET-MANIFEST.candidate.json"
SELECTION = ROOT / "APPROVED-BRAND-SELECTION.json"
REPORT = ROOT / "verification-report.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FORBIDDEN_METADATA_CHUNKS = {b"eXIf", b"iTXt", b"tEXt", b"zTXt"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_png(data: bytes) -> dict[str, Any]:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid PNG signature")
    position = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    width = height = bit_depth = color_type = None
    while position < len(data):
        if position + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", data[position : position + 4])[0]
        chunk_type = data[position + 4 : position + 8]
        payload_start = position + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise ValueError("PNG chunk length exceeds file")
        expected_crc = struct.unpack(">I", data[payload_end:crc_end])[0]
        import zlib

        actual_crc = zlib.crc32(chunk_type + data[payload_start:payload_end]) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"PNG CRC mismatch for {chunk_type!r}")
        chunks.append(chunk_type)
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", data[payload_start : payload_start + 10])
        position = crc_end
        if chunk_type == b"IEND":
            break
    if chunks[0] != b"IHDR" or chunks[-1] != b"IEND":
        raise ValueError("PNG chunk order is incomplete")
    return {"width": width, "height": height, "bit_depth": bit_depth, "color_type": color_type, "chunks": chunks}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    checks: list[dict[str, Any]] = []

    source_path = ROOT / manifest["master"]["path"]
    source_hash = sha256(source_path.read_bytes())
    if source_hash != manifest["master"]["sha256"]:
        failures.append({"code": "master-hash-drift", "path": manifest["master"]["path"]})

    declared_paths = set()
    for item in manifest["candidates"]:
        relative = item["path"]
        declared_paths.add(relative)
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            failures.append({"code": "candidate-path-escape", "path": relative})
            continue
        data = path.read_bytes()
        parsed = parse_png(data)
        issues = []
        if sha256(data) != item["sha256"]:
            issues.append("hash-drift")
        if [parsed["width"], parsed["height"]] != item["dimensions"]:
            issues.append("dimension-drift")
        if parsed["width"] != parsed["height"]:
            issues.append("non-square")
        if parsed["bit_depth"] != 8 or parsed["color_type"] != 6:
            issues.append("not-8-bit-rgba")
        if b"sRGB" not in parsed["chunks"]:
            issues.append("srgb-chunk-missing")
        if FORBIDDEN_METADATA_CHUNKS.intersection(parsed["chunks"]):
            issues.append("copied-or-freeform-metadata-present")
        size = item["dimensions"][0]
        expected_approval = "owner-approved" if size >= 64 else "owner-excluded-qa-only"
        expected_selection = "approved-brand-derivative" if size >= 64 else "qa-only"
        if item["release_eligible"] is not False:
            issues.append("premature-release-eligibility")
        if item["approval_state"] != expected_approval or item["selection_state"] != expected_selection:
            issues.append("owner-selection-drift")
        if item.get("approval_ref") != "P09-OWNER-A-2026-08-15":
            issues.append("approval-reference-drift")
        if item["family"] == "full-crest-transparent-safe-area":
            left, top, right, bottom = item["alpha_bbox"]
            minimum = int(parsed["width"] * 0.07)
            if min(left, top, parsed["width"] - right, parsed["height"] - bottom) < minimum:
                issues.append("safe-area-too-small")
        checks.append({"path": relative, "sha256": item["sha256"], "chunks": [value.decode("ascii") for value in parsed["chunks"]], "issues": issues, "status": "pass" if not issues else "fail"})
        failures.extend({"code": issue, "path": relative} for issue in issues)

    actual_paths = {path.relative_to(ROOT).as_posix() for path in (ROOT / "candidates").glob("*.png")}
    if actual_paths != declared_paths:
        failures.append({"code": "candidate-inventory-drift", "path": "candidates/"})

    if manifest["approval"] != {
        "approval_ref": "P09-OWNER-A-2026-08-15",
        "decision": "D-027",
        "minimum_size_px": 64,
        "option": "A",
        "release_blockers": ["P-10 and G-06 legal/provenance approval", "P-13 platform mapping and package build"],
        "release_eligible": False,
        "simplified_mark": "not-created-for-v1.0.0",
        "state": "owner-approved-selection",
    }:
        failures.append({"code": "manifest-approval-drift", "path": MANIFEST.name})

    expected_approved = {
        item["path"]: item["sha256"]
        for item in manifest["candidates"]
        if item["dimensions"][0] >= 64
    }
    expected_excluded = {
        item["path"]: item["sha256"]
        for item in manifest["candidates"]
        if item["dimensions"][0] < 64
    }
    selected_approved = {item["path"]: item["sha256"] for item in selection["approved_artifacts"]}
    selected_excluded = {item["path"]: item["sha256"] for item in selection["excluded_qa_only"]}
    if selected_approved != expected_approved or len(selected_approved) != 16:
        failures.append({"code": "approved-selection-drift", "path": SELECTION.name})
    if selected_excluded != expected_excluded or len(selected_excluded) != 6:
        failures.append({"code": "qa-only-selection-drift", "path": SELECTION.name})
    if (
        selection.get("approval") != "owner-approved"
        or selection.get("approval_ref") != "P09-OWNER-A-2026-08-15"
        or selection.get("decision") != "D-027"
        or selection.get("option") != "A"
        or selection.get("minimum_size_px") != 64
        or selection.get("simplified_mark") != "not-created-for-v1.0.0"
        or selection.get("immutable") is not True
        or selection.get("release_eligible") is not False
    ):
        failures.append({"code": "selection-record-drift", "path": SELECTION.name})

    report = {
        "schema_version": "1.0",
        "status": "pass" if not failures else "fail",
        "source_sha256": source_hash,
        "candidate_count": len(checks),
        "approved_count": len(selected_approved),
        "qa_only_excluded_count": len(selected_excluded),
        "checks": checks,
        "hard_failures": failures,
        "release_eligible": False,
        "approval_state": manifest["approval"]["state"],
        "approval_ref": manifest["approval"]["approval_ref"],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "candidate_count": report["candidate_count"], "hard_failures": len(failures)}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
