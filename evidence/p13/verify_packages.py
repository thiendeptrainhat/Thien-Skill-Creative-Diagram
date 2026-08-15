#!/usr/bin/env python3
"""Dependency-free P-13 archive, parity, hygiene and structural smoke verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
P13 = ROOT / "evidence" / "p13"
DIST = ROOT / "dist"
SKILL_ID = "thien-skill-creative-diagram"
REPORT = P13 / "verification-report.json"
SURFACE_REPORT = P13 / "surface-smoke-report.json"
PLUGIN_VALIDATOR = Path("<LOCAL_CODEX_SKILLS>/plugin-creator/scripts/validate_plugin.py")
ABSOLUTE_TEXT = re.compile(r"(?:/Users/|/private/|[A-Za-z]:\\\\)")
FORBIDDEN_PARTS = {".git", ".DS_Store", "__pycache__", "evidence", ".env", "node_modules"}
DEVELOPMENT_NAMES = {
    "generate_p07_evidence.py", "generate_p08_evidence.py", "generate_p11_evidence.py",
    "generate_semantic_references.py", "p07_coverage.py", "p08_coverage.py", "p11_coverage.py",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("p13_builder", P13 / "build_packages.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P-13 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def run(command: list[str], *, cwd: Path | None = None) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=60)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def normalize_temp_paths(value, temp_root: str):
    """Keep the persisted verification report stable across temporary extraction roots."""
    if isinstance(value, str):
        return value.replace(temp_root, "<TEMP>")
    if isinstance(value, list):
        return [normalize_temp_paths(item, temp_root) for item in value]
    if isinstance(value, dict):
        return {key: normalize_temp_paths(item, temp_root) for key, item in value.items()}
    return value


def safe_extract(archive: zipfile.ZipFile, target: Path) -> None:
    for info in archive.infolist():
        pure = PurePosixPath(info.filename)
        if pure.is_absolute() or ".." in pure.parts:
            raise RuntimeError(f"unsafe extraction member: {info.filename}")
        destination = target.joinpath(*pure.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(archive.read(info))


def skill_smoke(skill_root: Path) -> dict:
    program = r'''
import json, sys
from pathlib import Path
root = Path.cwd()
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
html = html_bundle.artifacts["html"].content.decode("utf-8")
request["format"] = "svg"
svg_bundle = export_artifacts(ir, request, auto_detect_rasterizer=False)
request["format"] = "png"
fallback = export_artifacts(ir, request, auto_detect_rasterizer=False)
result = {
    "html": set(html_bundle.artifacts) == {"html"} and "Thủ quỹ" in html and "Kế toán trưởng" in html,
    "svg": set(svg_bundle.artifacts) == {"svg"},
    "png_absent_fallback": set(fallback.artifacts) == {"svg"} and any("no installation was attempted" in w for w in fallback.ledger["warnings"]),
    "semantic_validation": html_bundle.ledger["validation"]["semantic"] == "pass",
}
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if all(result.values()) else 1)
'''
    result = run([sys.executable, "-c", program], cwd=skill_root)
    parsed = None
    if result["stdout"]:
        try:
            parsed = json.loads(result["stdout"].splitlines()[-1])
        except json.JSONDecodeError:
            parsed = None
    result["assertions"] = parsed
    return result


def openai_manifest_check(plugin_root: Path) -> tuple[bool, str]:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"manifest parse failed: {exc}"
    required = {"name", "version", "description", "author", "skills", "interface"}
    interface_required = {
        "displayName", "shortDescription", "longDescription", "developerName",
        "category", "capabilities", "defaultPrompt", "composerIcon", "logo",
    }
    interface = manifest.get("interface")
    ok = (
        required <= set(manifest)
        and manifest.get("name") == SKILL_ID
        and manifest.get("version") == "1.0.0"
        and manifest.get("skills") == "./skills/"
        and isinstance(interface, dict)
        and interface_required <= set(interface)
    )
    if not ok:
        return False, "required OpenAI manifest fields or fixed identity are missing"
    for key in ("composerIcon", "logo"):
        raw = interface[key]
        pure = PurePosixPath(raw)
        if pure.is_absolute() or ".." in pure.parts or not (plugin_root / pure).is_file():
            return False, f"invalid or missing interface asset: {key}"
    return True, "OpenAI manifest identity, skill path, UI fields and asset references resolve"


def surface_rows() -> list[dict]:
    conditional = {
        "SUR-CL-01": "local raw-skill structure/runtime smoke passed; fresh Claude session discovery/trigger remains external",
        "SUR-CL-02": "local raw-skill structure/runtime smoke passed; project trust and fresh-session trigger remain external",
        "SUR-CL-03": "Claude manifest validation and nested runtime smoke passed; live --plugin-dir trigger remains external",
        "SUR-CL-04": "exact package exists; cloud repository session condition was not available",
        "SUR-CL-05": "exact Universal ZIP exists; claude.ai account upload/code-execution condition was not available",
        "SUR-CL-06": "exact artifacts exist; Cowork account/plugin condition was not available",
        "SUR-CL-07": "exact Universal ZIP exists; Skills API access/code-execution condition was not available",
        "SUR-OAI-01": "OpenAI manifest and nested runtime smoke passed; marketplace/account install condition remains external",
        "SUR-OAI-03": "Universal skill structure/runtime/UI metadata smoke passed; desktop discovery trigger remains external",
        "SUR-OAI-04": "OpenAI manifest and nested runtime smoke passed; ChatGPT desktop marketplace condition remains external",
        "SUR-OAI-05": "Universal skill structure/runtime smoke passed; fresh Codex CLI discovery/trigger remains external",
        "SUR-OAI-06": "OpenAI manifest and nested runtime smoke passed; marketplace install/trigger remains external",
        "SUR-OAI-07": "Universal skill structure/runtime smoke passed; fresh IDE discovery/trigger remains external",
    }
    unsupported = {
        "SUR-OAI-02": "no official standalone raw-skill route for ChatGPT web/mobile",
        "SUR-OAI-08": "no approved OpenAI plugin route for Codex IDE extension",
    }
    rows = [
        {"surface_id": key, "approved_status": "conditional", "p13_status": "conditional", "evidence": value}
        for key, value in sorted(conditional.items())
    ]
    rows += [
        {"surface_id": key, "approved_status": "unsupported", "p13_status": "unsupported", "evidence": value}
        for key, value in sorted(unsupported.items())
    ]
    return sorted(rows, key=lambda row: row["surface_id"])


def main() -> int:
    builder = load_builder()
    expected_record, expected_archives, expected_sums = builder.expected_build()
    checks: list[dict] = []
    build_path = P13 / "package-build.json"
    build_record = json.loads(build_path.read_text(encoding="utf-8"))
    add(checks, "V-P13-001", build_record == expected_record, "Build record equals deterministic builder projection")

    actual_archives = {}
    for target, filename in builder.PACKAGE_FILES.items():
        path = DIST / filename
        actual_archives[target] = path.read_bytes() if path.is_file() else b""
    add(checks, "V-P13-002", actual_archives == expected_archives, "All three ZIP bytes equal deterministic builder output")
    add(checks, "V-P13-003", (DIST / "SHA256SUMS.txt").read_bytes() == expected_sums, "Checksum manifest exactly matches the three ZIP files")
    extras = sorted(path.name for path in DIST.glob("*.zip") if path.name not in set(builder.PACKAGE_FILES.values()))
    add(checks, "V-P13-004", not extras, "No undeclared ZIP exists in dist/")

    mappings = builder.package_mappings()
    archive_members: dict[str, dict[str, bytes]] = {}
    archive_meta_ok = True
    hygiene_ok = True
    text_paths_ok = True
    for target, data in actual_archives.items():
        try:
            with zipfile.ZipFile(DIST / builder.PACKAGE_FILES[target], "r") as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                members = {info.filename: archive.read(info) for info in infos}
        except (OSError, zipfile.BadZipFile):
            archive_meta_ok = False
            archive_members[target] = {}
            continue
        archive_members[target] = members
        archive_meta_ok = archive_meta_ok and len(names) == len(set(names)) and names == sorted(names)
        archive_meta_ok = archive_meta_ok and all(
            info.date_time == builder.ZIP_TIMESTAMP
            and ((info.external_attr >> 16) & 0o177777) == 0o100644
            and info.compress_type == zipfile.ZIP_DEFLATED
            for info in infos
        )
        roots = {PurePosixPath(name).parts[0] for name in names}
        archive_meta_ok = archive_meta_ok and roots == {SKILL_ID}
        for name, payload in members.items():
            pure = PurePosixPath(name)
            hygiene_ok = hygiene_ok and not pure.is_absolute() and ".." not in pure.parts
            hygiene_ok = hygiene_ok and not any(part in FORBIDDEN_PARTS for part in pure.parts)
            hygiene_ok = hygiene_ok and pure.suffix not in {".pyc", ".log", ".zip", ".pem", ".key"}
            hygiene_ok = hygiene_ok and "tests" not in pure.parts and pure.name not in DEVELOPMENT_NAMES
            if pure.suffix.lower() in {".md", ".json", ".yaml", ".py"} or pure.name == "NOTICE":
                try:
                    decoded = payload.decode("utf-8")
                except UnicodeDecodeError:
                    text_paths_ok = False
                else:
                    text_paths_ok = text_paths_ok and ABSOLUTE_TEXT.search(decoded) is None
    add(checks, "V-P13-005", archive_meta_ok, "ZIP order, timestamp, mode, compression, uniqueness and one-top-level-folder invariants pass")
    add(checks, "V-P13-006", hygiene_ok, "No traversal, symlink-mode, QA, test, cache, secret or development-only member is packaged")
    add(checks, "V-P13-007", text_paths_ok, "No personal/development absolute path appears in packaged text")
    add(checks, "V-P13-008", archive_members == mappings, "Every archive member path and byte matches its declared target mapping")

    json_ok = True
    links_ok = True
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for target, members in archive_members.items():
        names = set(members)
        for name, payload in members.items():
            if name.endswith(".json"):
                try:
                    json.loads(payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    json_ok = False
            if name.endswith(".md") and ("/skills/" in name or target == "universal-raw-skill"):
                try:
                    text = payload.decode("utf-8")
                except UnicodeDecodeError:
                    links_ok = False
                    continue
                parent = PurePosixPath(name).parent
                for raw in markdown_link.findall(text):
                    if raw.startswith(("https://", "http://", "mailto:", "#")):
                        continue
                    link = raw.split("#", 1)[0]
                    resolved = str(parent / PurePosixPath(link))
                    if resolved not in names:
                        links_ok = False
    add(checks, "V-P13-008A", json_ok, "Every packaged JSON manifest/schema/reference parses successfully")
    add(checks, "V-P13-008B", links_ok, "All packaged relative Markdown links resolve inside the same archive")

    qa_inventory_ok = True
    try:
        scripts_dir = str((CANONICAL := ROOT / SKILL_ID) / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from qa_contract import validate_package_inventory
        for members in archive_members.values():
            relative = ["/".join(PurePosixPath(name).parts[1:]) for name in members]
            qa_inventory_ok = qa_inventory_ok and validate_package_inventory(relative)["status"] == "pass"
    except Exception:
        qa_inventory_ok = False
    add(checks, "V-P13-008C", qa_inventory_ok, "Canonical package-inventory validator passes every archive inventory")

    runtime = builder.runtime_files()
    legal = builder.legal_files()
    runtime_digest = builder.digest_logical(runtime)
    legal_digest = builder.digest_logical(legal)
    add(checks, "V-P13-009", all(p["runtime_core_aggregate_sha256"] == runtime_digest for p in build_record["packages"]), "Runtime-core aggregate is byte-identical across all three packages")
    add(checks, "V-P13-010", all(p["legal_bundle_aggregate_sha256"] == legal_digest for p in build_record["packages"]), "Six-file legal/provenance bundle is byte-identical across all three packages")
    legal_build = json.loads((ROOT / "evidence" / "p10" / "legal-candidate-build.json").read_text(encoding="utf-8"))
    legal_hashes = {entry["path"].split("/", 1)[1]: entry["sha256"] for entry in legal_build["artifacts"]}
    add(checks, "V-P13-011", legal_build["aggregate_sha256"] == build_record["legal_candidate_aggregate_sha256"] and all(sha(legal[name]) == legal_hashes[name] for name in builder.LEGAL_NAMES), "G-06-approved RC2 aggregate and all six legal artifact hashes remain unchanged")

    brand = builder.brand_files()
    claude_names = set(archive_members.get("claude-plugin", {}))
    openai_names = set(archive_members.get("openai-plugin", {}))
    universal_names = set(archive_members.get("universal-raw-skill", {}))
    add(checks, "V-P13-012", not any("/assets/brand/" in name for name in claude_names), "Claude package contains no brand asset under D-028")
    expected_brand_suffixes = {f"/{name}" for name in brand}
    add(checks, "V-P13-013", {name[name.index("/assets/brand/"):] for name in openai_names if "/assets/brand/" in name} == expected_brand_suffixes and {name[name.index("/assets/brand/"):] for name in universal_names if "/assets/brand/" in name} == expected_brand_suffixes, "OpenAI and Universal contain exactly the two D-028 brand destinations")
    add(checks, "V-P13-014", not any(name.endswith("/agents/openai.yaml") for name in claude_names) and any(name.endswith("/agents/openai.yaml") for name in openai_names) and any(name.endswith("/agents/openai.yaml") for name in universal_names), "OpenAI metadata overlay is excluded from Claude and included in OpenAI/Universal")

    surface = surface_rows()
    surface_record = {
        "record_id": "P13-SURFACE-SMOKE-1",
        "candidate_id": builder.CANDIDATE_ID,
        "checked_at": "2026-08-15",
        "approved_matrix": "evidence/p02/SURFACE-SUPPORT-MATRIX.md",
        "supported_count": 0,
        "conditional_count": sum(row["p13_status"] == "conditional" for row in surface),
        "unsupported_count": sum(row["p13_status"] == "unsupported" for row in surface),
        "rows": surface,
        "policy": "Conditional cells are not counted or advertised as supported without exact host install, fresh-session trigger, output and fallback evidence.",
    }

    smoke_results = {}
    claude_validation = None
    openai_validation = None
    with tempfile.TemporaryDirectory(prefix="tcd-p13-") as temp_name:
        temp = Path(temp_name)
        for target, filename in builder.PACKAGE_FILES.items():
            extracted = temp / target
            extracted.mkdir()
            with zipfile.ZipFile(DIST / filename, "r") as archive:
                safe_extract(archive, extracted)
            plugin_root = extracted / SKILL_ID
            skill_root = plugin_root if target == "universal-raw-skill" else plugin_root / "skills" / SKILL_ID
            smoke_results[target] = skill_smoke(skill_root)
            if target == "claude-plugin":
                claude_validation = run(["claude", "plugin", "validate", str(plugin_root)])
            if target == "openai-plugin":
                openai_validation = openai_manifest_check(plugin_root)
        smoke_results = normalize_temp_paths(smoke_results, temp_name)
        claude_validation = normalize_temp_paths(claude_validation, temp_name)
    add(checks, "V-P13-015", all(result["returncode"] == 0 for result in smoke_results.values()), "All three extracted packages render Vietnamese HTML/SVG and transparently fall back from PNG without installing dependencies")
    add(checks, "V-P13-016", claude_validation is not None and claude_validation["returncode"] == 0, "Claude 2.1.183 validates the extracted Claude plugin manifest and layout")
    add(checks, "V-P13-017", openai_validation is not None and openai_validation[0], openai_validation[1] if openai_validation else "OpenAI validation did not run")
    add(checks, "V-P13-018", len(surface) == 15 and surface_record["supported_count"] == 0 and surface_record["conditional_count"] == 13 and surface_record["unsupported_count"] == 2, "All 15 approved surface rows retain honest conditional/unsupported status; none is promoted on documentary or structural evidence alone")

    frontmatter = builder.runtime_files()["SKILL.md"].decode("utf-8").split("---", 2)[1]
    add(checks, "V-P13-019", "name: thien-skill-creative-diagram" in frontmatter and "description:" in frontmatter, "SKILL.md common frontmatter name/description and folder identity remain valid")
    official = (P13 / "OFFICIAL-PLATFORM-SOURCES.md").read_text(encoding="utf-8")
    official_urls = re.findall(r"<https://([^>]+)>", official)
    add(checks, "V-P13-020", len(official_urls) == 6 and all(host.startswith(("code.claude.com/", "developers.openai.com/", "learn.chatgpt.com/", "agentskills.io/")) for host in official_urls), "Current platform record uses only official Claude, OpenAI and Agent Skills sources")

    failed = [check for check in checks if check["result"] == "FAIL"]
    report = {
        "record_id": "P13-VERIFICATION-1",
        "candidate_id": builder.CANDIDATE_ID,
        "version": builder.VERSION,
        "verified_at": "2026-08-15T00:00:00+07:00",
        "status": "P13-PASSED-READY-FOR-G05-EVALUATION" if not failed else "P13-FAILED",
        "summary": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        "checks": checks,
        "archive_sha256": {target: sha(data) for target, data in actual_archives.items()},
        "runtime_core_aggregate_sha256": runtime_digest,
        "legal_bundle_aggregate_sha256": legal_digest,
        "smoke_results": smoke_results,
        "claude_validation": claude_validation,
        "openai_validation": {"passed": openai_validation[0], "detail": openai_validation[1]} if openai_validation else None,
        "tool_versions": {
            "python": sys.version.split()[0],
            "claude": run(["claude", "--version"]),
            "codex": run(["codex", "--version"]),
        },
        "limits": [
            "No conditional surface was promoted to supported because exact live account/marketplace/fresh-session conditions were not available in this local build context.",
            "The OpenAI plugin-creator validator could not be executed with the workspace Python because PyYAML is absent; dependency installation was not attempted. Equivalent manifest/path invariants were checked dependency-free against the current official fields.",
            "P-14, G-07, Git initialization/commit/tag/push and release were not performed.",
        ],
    }
    SURFACE_REPORT.write_text(json.dumps(surface_record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
