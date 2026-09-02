#!/usr/bin/env python3
"""Verify D-201 v2.5.0 staging packages and close G-05 fail-closed."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
P23 = ROOT / "evidence" / "p23"
STAGING = P23 / "candidate-dist" / "2.5.0"
REPORT = STAGING / "packaging-report.json"
SKILL_ID = "thien-skill-creative-diagram"
DISPLAY_NAME = "Thiện’s Skill — Creative Diagram"
PYTHON = Path("/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/bin/python3.14")
PYTHON_SHA256 = "2477b47fa3ae65b9574eb18a15edb364e96948eaa1875ad3f1c80d780efc9c12"
ABSOLUTE_TEXT = re.compile(r"(?:/Users/|/private/|[A-Za-z]:\\\\)")
SECRET_TEXT = re.compile(r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16})")
FORBIDDEN_PARTS = {".git", ".DS_Store", "__pycache__", "evidence", ".env", "node_modules", "tests"}
HISTORICAL_DIST = {
    "SHA256SUMS-2.0.0.txt": (363, "96246d4d62153b82c9e3505ebe904433225f15b106e002d026fa069e8a4a8f17"),
    "SHA256SUMS.txt": (363, "af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596"),
    "thien-skill-creative-diagram-1.0.0-claude-plugin.zip": (178105, "bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9"),
    "thien-skill-creative-diagram-1.0.0-openai-plugin.zip": (269167, "7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c"),
    "thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip": (264452, "4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f"),
    "thien-skill-creative-diagram-2.0.0-claude-plugin.zip": (377788, "7ef52b21be9dcc96caae5621e7788f9eb31cd46ae26ef94e47e3a75889ce99f6"),
    "thien-skill-creative-diagram-2.0.0-openai-plugin.zip": (468849, "65c2d6fbc33dc6d3065c5d6ae44a5b4fe02e5f7e8838b7f05eede07766124315"),
    "thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip": (460534, "88e22caee1f7df7ff8893dbd5cb461c6117921765e56c349e3da6c6452f15f93"),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load controller: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("p23_package_builder", P23 / "build_packages_v25.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def safe_extract(archive: zipfile.ZipFile, target: Path) -> None:
    for info in archive.infolist():
        pure = PurePosixPath(info.filename)
        mode = (info.external_attr >> 16) & 0o177777
        if pure.is_absolute() or ".." in pure.parts or mode != 0o100644:
            raise RuntimeError(f"unsafe extraction member: {info.filename}")
        destination = target.joinpath(*pure.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(archive.read(info))


def run_smoke(skill_root: Path, output_root: Path) -> dict:
    program = r'''
import json, sys
from pathlib import Path
root = Path.cwd()
out = Path(sys.argv[1])
sys.path.insert(0, str(root / "scripts"))
from pilot_cases import swimlane_pilot
from output_pipeline import export_artifacts
request = {
    "instruction": "Tạo sơ đồ quy trình thu tiền chuyên nghiệp.",
    "source": {"kind": "natural-language", "content": "Luồng đã chuẩn hóa."},
    "diagram_type": "swimlane", "size": "fit", "detail": "faithful", "audience": "mixed",
    "visual_mode": "neutral-light", "language": {"mode": "explicit", "tag": "vi"},
    "format": "html", "motion": "none"
}
ir = swimlane_pilot()
html_bundle = export_artifacts(ir, request, auto_detect_rasterizer=False)
request["format"] = "svg"
svg_bundle = export_artifacts(ir, request, auto_detect_rasterizer=False)
out.mkdir()
(out / "smoke.html").write_bytes(html_bundle.artifacts["html"].content)
(out / "smoke.svg").write_bytes(svg_bundle.artifacts["svg"].content)
result = {
    "html": set(html_bundle.artifacts) == {"html"} and (out / "smoke.html").stat().st_size > 0,
    "svg": set(svg_bundle.artifacts) == {"svg"} and (out / "smoke.svg").stat().st_size > 0,
    "semantic": html_bundle.ledger["validation"]["semantic"] == "pass",
    "vietnamese": "Thủ quỹ" in html_bundle.artifacts["html"].content.decode("utf-8"),
}
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if all(result.values()) else 1)
'''
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [str(PYTHON), "-c", program, str(output_root)],
        cwd=skill_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
    )
    parsed = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout.strip().splitlines()[-1])
        except json.JSONDecodeError:
            parsed = None
    return {
        "returncode": completed.returncode,
        "assertions": parsed,
        "stderr": completed.stderr.strip(),
    }


def plugin_manifests_ok(members: dict[str, dict[str, bytes]]) -> bool:
    root = SKILL_ID
    try:
        claude = json.loads(members["claude-plugin"][f"{root}/.claude-plugin/plugin.json"])
        openai = json.loads(members["openai-plugin"][f"{root}/.codex-plugin/plugin.json"])
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return (
        claude.get("name") == SKILL_ID
        and claude.get("version") == builder.VERSION
        and claude.get("displayName") == DISPLAY_NAME
        and claude.get("skills") == "./skills/"
        and openai.get("name") == SKILL_ID
        and openai.get("version") == builder.VERSION
        and openai.get("skills") == "./skills/"
        and openai.get("interface", {}).get("displayName") == DISPLAY_NAME
        and openai.get("interface", {}).get("composerIcon") == "./assets/brand/full-crest-plate-light-64.png"
        and openai.get("interface", {}).get("logo") == "./assets/brand/full-crest-plate-light-400.png"
    )


def main() -> int:
    checks: list[dict] = []
    expected_report, expected_archives, expected_sums = builder.expected_build()
    try:
        current_report = json.loads(REPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        current_report = {}
    add(
        checks, "G05-001",
        builder.report_without_g05(current_report) == builder.report_without_g05(expected_report),
        "Packaging-report immutable build projection matches the D-201 controller",
    )

    actual_archives = {
        target: (STAGING / builder.PACKAGE_FILES[target]).read_bytes()
        for target in builder.TARGET_ORDER
        if (STAGING / builder.PACKAGE_FILES[target]).is_file()
    }
    add(checks, "G05-002", set(actual_archives) == set(builder.TARGET_ORDER), "Exactly three declared envelope archives exist")
    add(checks, "G05-003", actual_archives == expected_archives, "Archive bytes equal deterministic in-memory regeneration")
    add(checks, "G05-004", (STAGING / "SHA256SUMS").read_bytes() == expected_sums, "SHA256SUMS matches exact archive bytes and order")
    actual_inventory = {path.name for path in STAGING.iterdir()} if STAGING.is_dir() else set()
    add(checks, "G05-005", actual_inventory == set(builder.FINAL_INVENTORY), "Staging inventory has exactly the frozen five members")
    add(checks, "G05-006", not (ROOT / "dist" / "2.5.0").exists(), "No provisional artifact was written to dist/2.5.0")

    historical_names = {path.name for path in (ROOT / "dist").iterdir() if path.is_file()}
    historical_ok = historical_names == set(HISTORICAL_DIST)
    for name, (size, digest) in HISTORICAL_DIST.items():
        path = ROOT / "dist" / name
        historical_ok = historical_ok and path.is_file() and path.stat().st_size == size and sha(path.read_bytes()) == digest
    add(checks, "G05-007", historical_ok, "All eight historical dist paths, sizes and hashes remain exact")
    add(checks, "G05-008", PYTHON.is_file() and sha(PYTHON.read_bytes()) == PYTHON_SHA256, "Exact D-156 Python runtime hash matches")

    mappings = builder.package_mappings()
    archive_members: dict[str, dict[str, bytes]] = {}
    meta_ok = True
    hygiene_ok = True
    text_ok = True
    json_ok = True
    links_ok = True
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for target, data in actual_archives.items():
        try:
            from io import BytesIO
            with zipfile.ZipFile(BytesIO(data), "r") as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                members = {name: archive.read(name) for name in names}
        except (OSError, zipfile.BadZipFile, KeyError):
            meta_ok = False
            archive_members[target] = {}
            continue
        archive_members[target] = members
        meta_ok = meta_ok and names == sorted(names) and len(names) == len(set(names))
        meta_ok = meta_ok and {PurePosixPath(name).parts[0] for name in names} == {SKILL_ID}
        for info in infos:
            pure = PurePosixPath(info.filename)
            mode = (info.external_attr >> 16) & 0o177777
            meta_ok = meta_ok and (
                info.date_time == builder.ZIP_TIMESTAMP
                and info.compress_type == zipfile.ZIP_DEFLATED
                and mode == 0o100644
                and not pure.is_absolute()
                and ".." not in pure.parts
            )
            payload = members[info.filename]
            hygiene_ok = hygiene_ok and not any(part in FORBIDDEN_PARTS for part in pure.parts)
            hygiene_ok = hygiene_ok and pure.suffix not in {".pyc", ".log", ".zip", ".pem", ".key"}
            if pure.suffix.lower() in {".md", ".json", ".yaml", ".py"} or pure.name == "NOTICE":
                try:
                    text = payload.decode("utf-8")
                except UnicodeDecodeError:
                    text_ok = False
                    continue
                text_ok = text_ok and ABSOLUTE_TEXT.search(text) is None and SECRET_TEXT.search(text) is None
            if pure.suffix == ".json":
                try:
                    json.loads(payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    json_ok = False
            if pure.suffix == ".md":
                parent = pure.parent
                for raw in markdown_link.findall(payload.decode("utf-8")):
                    if raw.startswith(("https://", "http://", "mailto:", "#")):
                        continue
                    clean = raw.split("#", 1)[0]
                    if clean and (parent / PurePosixPath(clean)).as_posix() not in members:
                        links_ok = False
    add(checks, "G05-009", meta_ok, "ZIP root/order/uniqueness/timestamp/mode/compression and traversal invariants pass")
    add(checks, "G05-010", hygiene_ok, "No tests, evidence, cache, secret-key extension or development payload is packaged")
    add(checks, "G05-011", text_ok, "Packaged text contains no personal/temp absolute path or recognized secret token")
    add(checks, "G05-012", archive_members == mappings, "Every archive member path and byte equals the declared envelope mapping")
    add(checks, "G05-013", json_ok, "Every packaged JSON member parses")
    add(checks, "G05-014", links_ok, "Every packaged relative Markdown link resolves inside its envelope")
    add(checks, "G05-015", plugin_manifests_ok(archive_members), "Claude and ChatGPT manifests preserve technical identity and target display name")

    runtime_digest = builder.digest_logical(builder.runtime_files())
    legal_digest = builder.digest_logical(builder.legal_files())
    parity_ok = all(
        item["runtime_core_aggregate_sha256"] == runtime_digest
        and item["legal_bundle_aggregate_sha256"] == legal_digest
        for item in expected_report["packages"]
    )
    add(checks, "G05-016", parity_ok, "Runtime core and six-file legal aggregate are identical across all envelopes")
    brand = builder.brand_files()
    claude_names = set(archive_members.get("claude-plugin", {}))
    openai_names = set(archive_members.get("openai-plugin", {}))
    universal_names = set(archive_members.get("universal-raw-skill", {}))
    expected_brand = {f"/{name}" for name in brand}
    brand_ok = (
        not any("/assets/brand/" in name for name in claude_names)
        and {name[name.index("/assets/brand/"):] for name in openai_names if "/assets/brand/" in name} == expected_brand
        and {name[name.index("/assets/brand/"):] for name in universal_names if "/assets/brand/" in name} == expected_brand
    )
    add(checks, "G05-017", brand_ok, "Brand differences are limited to exact 64px/400px allowlisted bytes")

    smoke_results: dict[str, dict] = {}
    temp_absent = False
    with tempfile.TemporaryDirectory(prefix="tcd-p23-g05-") as temp_name:
        temp = Path(temp_name)
        for target in builder.TARGET_ORDER:
            extracted = temp / target
            extracted.mkdir()
            with zipfile.ZipFile(STAGING / builder.PACKAGE_FILES[target], "r") as archive:
                safe_extract(archive, extracted)
            plugin_root = extracted / SKILL_ID
            skill_root = plugin_root if target == "universal-raw-skill" else plugin_root / "skills" / SKILL_ID
            skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            if not skill_text.startswith("---\n") or "name: thien-skill-creative-diagram" not in skill_text.split("---", 2)[1]:
                smoke_results[target] = {"returncode": 97, "assertions": None, "stderr": "invalid installed SKILL frontmatter"}
            else:
                smoke_results[target] = run_smoke(skill_root, temp / f"{target}-smoke-output")
        temp_path = Path(temp_name)
    temp_absent = not temp_path.exists()
    add(checks, "G05-018", all(item["returncode"] == 0 for item in smoke_results.values()), "All three extracted installed-skill render smokes pass")
    add(checks, "G05-019", temp_absent, "Exact extraction and smoke temp root is removed")

    failed = [item for item in checks if item["result"] == "FAIL"]
    report = expected_report
    report["status"] = "G-05-PASS / G-06-PENDING" if not failed else "G-05-FAIL / STOPPED"
    report["g05"] = {
        "status": "PASS" if not failed else "FAIL",
        "summary": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        "checks": checks,
        "smoke_results": smoke_results,
        "deterministic_regeneration": "PASS" if actual_archives == expected_archives else "FAIL",
        "temp_cleanup": "PASS" if temp_absent else "FAIL",
    }
    REPORT.write_bytes(builder.canonical_json(report))
    print(json.dumps(report["g05"]["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
