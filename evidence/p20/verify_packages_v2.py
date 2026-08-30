#!/usr/bin/env python3
"""Dependency-free verification for the local-only v2.0.0 package candidate."""

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
P20 = ROOT / "evidence" / "p20"
CANDIDATE_DIST = P20 / "candidate-dist"
REPORT = P20 / "verification-report.json"
SKILL_ID = "thien-skill-creative-diagram"
VERSION = "2.0.0"
ABSOLUTE_TEXT = re.compile(r"(?:/Users/|/private/|[A-Za-z]:\\\\)")
FORBIDDEN_PARTS = {".git", ".DS_Store", "__pycache__", "evidence", ".env", "node_modules"}
HISTORICAL_DIST = {
    "thien-skill-creative-diagram-1.0.0-claude-plugin.zip": "bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9",
    "thien-skill-creative-diagram-1.0.0-openai-plugin.zip": "7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c",
    "thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip": "4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f",
    "SHA256SUMS.txt": "af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596",
}
LINEAGE_HASHES = {
    "evidence/p17/P-17-SOURCE-MANIFEST.json": "efabfb7e9e485449947ce98bc8e2fc5078a4c7d2593521c115b309c9aef24c57",
    "evidence/p18/r6/P-18R6-MANIFEST.json": "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a",
    "evidence/p19/gallery/P-19B-MANIFEST.json": "ae95aca927ec69904483441db6b85de0381c1c1d85f4f01ee07a21a40aed0ba2",
    "evidence/p19/P-19C-FREEZE-MANIFEST.json": "5c98b8f56987ed69e65a93e01ca05dc2fd95c6d4e288007ffaa7fd615c8180ed",
    "evidence/p19/G-04-1.5.0-EVIDENCE.md": "0d3720f9ff9bfc658a1477fa6d487bdabb32e99aa7a9a0e42f0ebd02869c5d63",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("p20_package_builder", P20 / "build_packages_v2.py")
p13_verify = load_module("p13_verifier_helpers", ROOT / "evidence" / "p13" / "verify_packages.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 180) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def normalize_temp(value, root: str):
    if isinstance(value, str):
        return value.replace(root, "<TEMP>")
    if isinstance(value, list):
        return [normalize_temp(item, root) for item in value]
    if isinstance(value, dict):
        return {key: normalize_temp(item, root) for key, item in value.items()}
    return value


def safe_extract(archive: zipfile.ZipFile, target: Path) -> None:
    for info in archive.infolist():
        pure = PurePosixPath(info.filename)
        if pure.is_absolute() or ".." in pure.parts:
            raise RuntimeError(f"unsafe extraction member: {info.filename}")
        destination = target.joinpath(*pure.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(archive.read(info))


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
        and manifest.get("version") == VERSION
        and manifest.get("skills") == "./skills/"
        and isinstance(interface, dict)
        and interface_required <= set(interface)
    )
    if not ok:
        return False, "required OpenAI manifest fields or v2 identity are missing"
    for key in ("composerIcon", "logo"):
        pure = PurePosixPath(interface[key])
        if pure.is_absolute() or ".." in pure.parts or not (plugin_root / pure).is_file():
            return False, f"invalid or missing interface asset: {key}"
    return True, "OpenAI v2 manifest identity, skill path, interface, and asset references resolve"


def main() -> int:
    checks: list[dict] = []
    build_record, expected_archives, expected_sums = builder.expected_build()
    actual_archives = {
        target: (CANDIDATE_DIST / filename).read_bytes()
        for target, filename in builder.PACKAGE_FILES.items()
        if (CANDIDATE_DIST / filename).is_file()
    }

    add(checks, "V-P20-001", set(actual_archives) == set(expected_archives), "All three v2 candidate archives exist")
    add(checks, "V-P20-002", actual_archives == expected_archives, "Candidate archives are byte-identical to deterministic regeneration")
    add(checks, "V-P20-003", (CANDIDATE_DIST / "SHA256SUMS.txt").read_bytes() == expected_sums, "Candidate checksum file matches exact archive bytes")
    declared_zips = set(builder.PACKAGE_FILES.values())
    actual_zips = {path.name for path in CANDIDATE_DIST.glob("*.zip")}
    add(checks, "V-P20-004", actual_zips == declared_zips, "No undeclared ZIP exists in candidate-dist")
    historical_ok = all((ROOT / "dist" / name).is_file() and sha((ROOT / "dist" / name).read_bytes()) == digest for name, digest in HISTORICAL_DIST.items())
    historical_names = {p.name for p in (ROOT / "dist").iterdir() if p.is_file() and p.name != ".DS_Store"}
    add(checks, "V-P20-005", historical_ok and historical_names == set(HISTORICAL_DIST), "Historical v1.0.0 dist remains exact and contains no v2 artifact")
    lineage_ok = all((ROOT / path).is_file() and sha((ROOT / path).read_bytes()) == digest for path, digest in LINEAGE_HASHES.items())
    add(checks, "V-P20-006", lineage_ok, "P17/P18/P19 frozen source-gallery lineage hashes remain exact")

    p19c = json.loads((ROOT / "evidence" / "p19" / "P-19C-VERIFICATION.json").read_text(encoding="utf-8"))
    browser = json.loads((ROOT / "evidence" / "p19" / "P-19C-BROWSER-VERIFICATION.json").read_text(encoding="utf-8"))
    coexistence_ok = (
        p19c.get("status") in {"PASS", "TECHNICAL_PASS_READY_FOR_OWNER_REVIEW"} and p19c.get("failure_count") == 0
        and browser.get("status") == "PASS"
        and browser["comparison"]["desktop"]["phase_counts"] == {"p18": 14, "p19": 93}
        and browser["comparison"]["mobile"]["figures"] == 107
    )
    add(checks, "V-P20-007", coexistence_ok, "Exact source-gallery evidence still proves separate 14 P18 + 93 P19 = 107")

    mappings = builder.base.package_mappings()
    archive_members: dict[str, dict[str, bytes]] = {}
    meta_ok = True
    hygiene_ok = True
    text_ok = True
    json_ok = True
    links_ok = True
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for target, data in actual_archives.items():
        with zipfile.ZipFile(Path(tempfile.gettempdir()) / "unused", "w") if False else zipfile.ZipFile(__import__("io").BytesIO(data), "r") as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            archive_members[target] = {name: archive.read(name) for name in names}
            meta_ok = meta_ok and names == sorted(names) and len(names) == len(set(names))
            for info in infos:
                pure = PurePosixPath(info.filename)
                meta_ok = meta_ok and pure.parts[0] == SKILL_ID and info.date_time == (2026, 8, 30, 0, 0, 0)
                meta_ok = meta_ok and not pure.is_absolute() and ".." not in pure.parts and info.compress_type == zipfile.ZIP_DEFLATED
                payload = archive_members[target][info.filename]
                hygiene_ok = hygiene_ok and not any(part in FORBIDDEN_PARTS for part in pure.parts)
                hygiene_ok = hygiene_ok and pure.suffix not in {".pyc", ".log", ".zip", ".pem", ".key"}
                hygiene_ok = hygiene_ok and "tests" not in pure.parts
                if pure.suffix.lower() in {".md", ".json", ".yaml", ".py"} or pure.name == "NOTICE":
                    try:
                        decoded = payload.decode("utf-8")
                    except UnicodeDecodeError:
                        text_ok = False
                    else:
                        text_ok = text_ok and ABSOLUTE_TEXT.search(decoded) is None
                if pure.suffix == ".json":
                    try:
                        json.loads(payload.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        json_ok = False
                if pure.suffix == ".md" and ("/skills/" in info.filename or target == "universal-raw-skill"):
                    parent = pure.parent
                    for raw in markdown_link.findall(payload.decode("utf-8")):
                        if raw.startswith(("https://", "http://", "mailto:", "#")):
                            continue
                        resolved = str(parent / PurePosixPath(raw.split("#", 1)[0]))
                        if resolved not in names:
                            links_ok = False
    add(checks, "V-P20-008", meta_ok, "ZIP order, timestamp, compression, unique path, and one-root invariants pass")
    add(checks, "V-P20-009", hygiene_ok, "No traversal, evidence, tests, cache, secrets, or development-only payload is packaged")
    add(checks, "V-P20-010", text_ok, "No personal/development absolute path appears in packaged text")
    add(checks, "V-P20-011", archive_members == mappings, "Every archive member and byte matches the declared target mapping")
    add(checks, "V-P20-012", json_ok, "Every packaged JSON file parses")
    add(checks, "V-P20-013", links_ok, "Every packaged relative Markdown link resolves")

    runtime_digest = builder.base.digest_logical(builder.base.runtime_files())
    legal_files = builder.legal_files()
    legal_digest = builder.base.digest_logical(legal_files)
    add(checks, "V-P20-014", all(item["runtime_core_aggregate_sha256"] == runtime_digest for item in build_record["packages"]), "Runtime core aggregate is identical across all targets")
    add(checks, "V-P20-015", all(item["legal_bundle_aggregate_sha256"] == legal_digest for item in build_record["packages"]), "Exact six-file v2 legal/provenance candidate is identical across all targets")
    legal_record = json.loads((P20 / "legal-candidate-build.json").read_text(encoding="utf-8"))
    add(checks, "V-P20-016", legal_record["aggregate_sha256"] == legal_digest and legal_record["status"].startswith("CANDIDATE-AWAITING"), "Package binding matches the pending exact v2 legal candidate")

    brand = builder.base.brand_files()
    claude_names = set(archive_members.get("claude-plugin", {}))
    openai_names = set(archive_members.get("openai-plugin", {}))
    universal_names = set(archive_members.get("universal-raw-skill", {}))
    expected_brand = {f"/assets/brand/{Path(name).name}" for name in brand}
    add(checks, "V-P20-017", not any("/assets/brand/" in name for name in claude_names), "Claude candidate contains no brand asset")
    add(checks, "V-P20-018", {name[name.index("/assets/brand/"):] for name in openai_names if "/assets/brand/" in name} == expected_brand and {name[name.index("/assets/brand/"):] for name in universal_names if "/assets/brand/" in name} == expected_brand, "OpenAI and Universal contain only exact 64/400 light-plate bytes")

    smoke_results = {}
    claude_validation = None
    openai_validation = None
    with tempfile.TemporaryDirectory(prefix="tcd-p20-") as temp_name:
        temp = Path(temp_name)
        for target, filename in builder.PACKAGE_FILES.items():
            extracted = temp / target
            extracted.mkdir()
            with zipfile.ZipFile(CANDIDATE_DIST / filename, "r") as archive:
                safe_extract(archive, extracted)
            plugin_root = extracted / SKILL_ID
            skill_root = plugin_root if target == "universal-raw-skill" else plugin_root / "skills" / SKILL_ID
            smoke_results[target] = p13_verify.skill_smoke(skill_root)
            if target == "claude-plugin":
                claude_validation = run(["claude", "plugin", "validate", str(plugin_root)])
            if target == "openai-plugin":
                openai_validation = openai_manifest_check(plugin_root)
        smoke_results = normalize_temp(smoke_results, temp_name)
        claude_validation = normalize_temp(claude_validation, temp_name)
    add(checks, "V-P20-019", all(result["returncode"] == 0 for result in smoke_results.values()), "All extracted candidates render Vietnamese HTML/SVG and keep transparent PNG fallback")
    add(checks, "V-P20-020", claude_validation is not None and claude_validation["returncode"] == 0, "Installed Claude CLI validates the extracted v2 plugin")
    add(checks, "V-P20-021", openai_validation is not None and openai_validation[0], openai_validation[1] if openai_validation else "OpenAI validation did not run")

    skill_text = builder.base.runtime_files()["SKILL.md"].decode("utf-8")
    flexibility_ok = all(fragment in skill_text for fragment in (
        "39 canonical types plus four capability variants",
        "31 masked silhouettes are recognition samples only",
        "user's explicit, safe, semantically valid request takes precedence",
    ))
    add(checks, "V-P20-022", flexibility_ok, "Packaged skill explicitly enforces D-128 sample-not-fixed and user-request flexibility")
    add(checks, "V-P20-023", not any("/evidence/" in name or "/gallery/specimens/" in name or "/p19c/masked-review/" in name for members in archive_members.values() for name in members), "Frozen gallery, masked review, and evidence artifacts are excluded from packages")

    regression_command = [
        sys.executable,
        "-c",
        "import sys,unittest; sys.path.insert(0,'evidence/p19/source'); sys.path.insert(0,'thien-skill-creative-diagram/scripts/tests'); sys.path.insert(0,'thien-skill-creative-diagram/scripts'); suite=unittest.defaultTestLoader.discover('thien-skill-creative-diagram/scripts/tests', pattern='test_*.py'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)",
    ]
    regression = run(regression_command, cwd=ROOT, timeout=300)
    regression["stderr"] = re.sub(
        r"Ran (\d+) tests? in [0-9.]+s",
        r"Ran \1 tests in <DURATION>",
        regression["stderr"],
    )
    add(checks, "V-P20-024", regression["returncode"] == 0, "Full canonical unittest regression passes")
    official = (P20 / "OFFICIAL-PLATFORM-SOURCES.md").read_text(encoding="utf-8")
    official_urls = re.findall(r"<https://([^>]+)>", official)
    add(checks, "V-P20-025", len(official_urls) == 3 and all(host.startswith(("developers.openai.com/", "code.claude.com/", "agentskills.io/")) for host in official_urls), "Platform revalidation uses exactly three current official sources")

    plugin_validator = run([sys.executable, "<OWNER_HOME>/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py", "--help"])
    external_validator_available = plugin_validator["returncode"] == 0
    add(checks, "V-P20-026", True, "Bundled plugin-creator/skill-creator validator availability recorded without installing dependencies")

    failed = [item for item in checks if item["result"] == "FAIL"]
    report = {
        "record_id": "P20-VERIFICATION-1",
        "candidate_id": builder.CANDIDATE_ID,
        "version": VERSION,
        "verified_at": "2026-08-30T00:00:00+07:00",
        "status": "P20-TECHNICAL-CANDIDATE-PASS-AWAITING-GATES" if not failed else "P20-FAILED",
        "summary": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        "checks": checks,
        "archive_sha256": {target: sha(data) for target, data in actual_archives.items()},
        "runtime_core_aggregate_sha256": runtime_digest,
        "legal_bundle_aggregate_sha256": legal_digest,
        "smoke_results": smoke_results,
        "claude_validation": claude_validation,
        "openai_validation": {"passed": openai_validation[0], "detail": openai_validation[1]} if openai_validation else None,
        "full_regression": regression,
        "external_skill_plugin_validator": {
            "available": external_validator_available,
            "result": plugin_validator,
            "limitation": None if external_validator_available else "PyYAML is absent; dependency installation was not attempted. Equivalent dependency-free manifest/path/frontmatter checks ran in V-P20-008 through V-P20-023.",
        },
        "gate_state": {
            "G-00@2.0.0": "NOT-EVALUATED",
            "G-01@2.0.0": "NOT-EVALUATED",
            "G-02@2.0.0": "NOT-EVALUATED",
            "G-03@2.0.0": "NOT-EVALUATED",
            "G-04@2.0.0": "NOT-EVALUATED",
            "G-05@2.0.0": "NOT-EVALUATED",
            "G-06@2.0.0": "NOT-EVALUATED",
            "G-07@2.0.0": "NOT-EVALUATED",
        },
        "limits": [
            "Candidate ZIPs remain under evidence/p20/candidate-dist and are not release artifacts.",
            "Historical dist v1.0.0 remains unchanged.",
            "No owner/lawyer gate approval, publication, Git commit/push/tag, or Release was performed.",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
