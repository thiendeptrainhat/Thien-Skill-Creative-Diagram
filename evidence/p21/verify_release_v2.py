#!/usr/bin/env python3
"""Dependency-free local verifier for the exact v2.0.0 private release input."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
P20 = ROOT / "evidence" / "p20"
P21 = ROOT / "evidence" / "p21"
REPORT = P21 / "pre-release-verification.json"
RELEASE_MANIFEST_SHA = "2905d4d3945a75ba9b644aece005bcb6de5bb2278ca8f7e47a4247189c77be72"
P20_REPORT_SHA = "8d147d5affb25597125771bf15c458fb5563d2828294e531c49d0f14eb91bc44"
V1 = {
    "SHA256SUMS.txt": "af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596",
    "thien-skill-creative-diagram-1.0.0-claude-plugin.zip": "bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9",
    "thien-skill-creative-diagram-1.0.0-openai-plugin.zip": "7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c",
    "thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip": "4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f",
}
V2 = {
    "SHA256SUMS-2.0.0.txt": "96246d4d62153b82c9e3505ebe904433225f15b106e002d026fa069e8a4a8f17",
    "thien-skill-creative-diagram-2.0.0-claude-plugin.zip": "7ef52b21be9dcc96caae5621e7788f9eb31cd46ae26ef94e47e3a75889ce99f6",
    "thien-skill-creative-diagram-2.0.0-openai-plugin.zip": "65c2d6fbc33dc6d3065c5d6ae44a5b4fe02e5f7e8838b7f05eede07766124315",
    "thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip": "88e22caee1f7df7ff8893dbd5cb461c6117921765e56c349e3da6c6452f15f93",
}
LEGAL_NAMES = (
    "LICENSE.md",
    "LICENSE-APPLICATION.md",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_MANIFEST.json",
    "ASSET_MANIFEST.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], timeout: int = 300) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    stderr = re.sub(
        r"Ran (\d+) tests? in [0-9.]+s",
        r"Ran \1 tests in <DURATION>",
        completed.stderr.strip(),
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": stderr,
    }


def add(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    checks: list[dict] = []
    release_manifest_path = P20 / "RELEASE-CANDIDATE-2.0.0.json"
    release_manifest = json.loads(release_manifest_path.read_text(encoding="utf-8"))
    add(checks, "V-P21-001", digest(release_manifest_path) == RELEASE_MANIFEST_SHA, "Exact D-131 release manifest hash matches")
    add(checks, "V-P21-002", set(release_manifest["gate_results"].values()) == {"PASS"}, "All eight v2.0.0 gate results are PASS")

    dist = ROOT / "dist"
    actual_dist = {path.name for path in dist.iterdir() if path.is_file() and path.name != ".DS_Store"}
    add(checks, "V-P21-003", actual_dist == set(V1) | set(V2), "Dist contains exact v1 and v2 inventories only")
    add(checks, "V-P21-004", all(digest(dist / name) == value for name, value in V1.items()), "Historical v1.0.0 dist bytes remain exact")
    add(checks, "V-P21-005", all(digest(dist / name) == value for name, value in V2.items()), "Promoted v2.0.0 dist bytes match approved candidate")

    candidate = P20 / "candidate-dist"
    candidate_map = {
        "thien-skill-creative-diagram-2.0.0-claude-plugin.zip": "thien-skill-creative-diagram-2.0.0-claude-plugin.zip",
        "thien-skill-creative-diagram-2.0.0-openai-plugin.zip": "thien-skill-creative-diagram-2.0.0-openai-plugin.zip",
        "thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip": "thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip",
        "SHA256SUMS.txt": "SHA256SUMS-2.0.0.txt",
    }
    add(checks, "V-P21-006", all((candidate / source).read_bytes() == (dist / target).read_bytes() for source, target in candidate_map.items()), "Dist promotion is byte-identical to candidate-dist")
    add(checks, "V-P21-007", all((ROOT / "thien-skill-creative-diagram" / name).read_bytes() == (P20 / "legal-candidate" / name).read_bytes() for name in LEGAL_NAMES), "Canonical legal/provenance files match exact approved v2 candidate")

    p20_report_path = P20 / "verification-report.json"
    p20_report = json.loads(p20_report_path.read_text(encoding="utf-8"))
    add(checks, "V-P21-008", digest(p20_report_path) == P20_REPORT_SHA and p20_report["summary"] == {"checks": 26, "passed": 26, "failed": 0}, "Frozen P-20 package verification remains exact at 26/26 PASS")

    legal_check = run([sys.executable, "evidence/p20/build_legal_candidate_v2.py", "--check"])
    package_check = run([sys.executable, "evidence/p20/build_packages_v2.py", "--check"])
    add(checks, "V-P21-009", legal_check["returncode"] == 0, "Exact legal candidate regenerates without drift")
    add(checks, "V-P21-010", package_check["returncode"] == 0, "All three package candidates regenerate without drift")

    regression = run([
        sys.executable,
        "-c",
        "import sys,unittest; sys.path.insert(0,'evidence/p19/source'); sys.path.insert(0,'thien-skill-creative-diagram/scripts/tests'); sys.path.insert(0,'thien-skill-creative-diagram/scripts'); suite=unittest.defaultTestLoader.discover('thien-skill-creative-diagram/scripts/tests', pattern='test_*.py'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)",
    ])
    add(checks, "V-P21-011", regression["returncode"] == 0 and "Ran 414 tests" in regression["stderr"], "Full canonical regression is 414/414 PASS")

    preflight = json.loads((P21 / "PRE-RELEASE-PREFLIGHT.json").read_text(encoding="utf-8"))
    add(checks, "V-P21-012", preflight["result"] == "PASS" and preflight["repository"]["visibility"] == "PRIVATE", "Exact remote target/private preflight passes")
    add(checks, "V-P21-013", preflight["release_target"]["tag_preflight"] == "ABSENT_HTTP_404" and preflight["release_target"]["release_preflight"] == "ABSENT_HTTP_404", "v2.0.0 tag and Release were absent at preflight")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    add(checks, "V-P21-014", all(name in readme for name in V2 if name.endswith(".zip")) and all(value in readme for name, value in V2.items() if name.endswith(".zip")), "README binds all exact v2 archive names and hashes")
    add(checks, "V-P21-015", "31 masked silhouette" in readme and "không phải template/catalog/output cố định" in readme, "README preserves D-128 sample-not-fixed flexibility")

    failed = [item for item in checks if item["result"] == "FAIL"]
    report = {
        "record_id": "P21-PRE-RELEASE-VERIFICATION-1",
        "candidate_id": "TCD-RELEASE-2.0.0-RC1",
        "version": "2.0.0",
        "verified_at": "2026-08-31T00:00:00+07:00",
        "status": "PASS" if not failed else "FAIL",
        "summary": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        "checks": checks,
        "legal_regeneration": legal_check,
        "package_regeneration": package_check,
        "full_regression": regression,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
