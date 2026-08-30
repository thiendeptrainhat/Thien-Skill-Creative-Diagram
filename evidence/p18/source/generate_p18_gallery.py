"""Generate the exact deterministic P-18 owner-review gallery and manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from html import escape
from pathlib import Path
from typing import Any


SOURCE_DIR = Path(__file__).resolve().parent
P18_DIR = SOURCE_DIR.parent
GALLERY_DIR = P18_DIR / "gallery"
ANCHOR_DIR = P18_DIR / "anchor-proof"
REPO_ROOT = P18_DIR.parents[1]
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from p18_cases import CASE_META, MODES  # noqa: E402
from p18_qa import validate_rendered  # noqa: E402
from p18_renderer import RenderedSpecimen, render_specimen  # noqa: E402


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_bundle_hash() -> str:
    paths = sorted(path for path in SOURCE_DIR.iterdir() if path.suffix in {".py", ".js"}) + [
        P18_DIR / "DESIGN-CONTRACT.md",
        P18_DIR / "VISUAL-CRAFT-RUBRIC.md",
        REPO_ROOT / "thien-skill-creative-diagram" / "references" / "visual-system.json",
    ]
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(REPO_ROOT).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def render_all() -> list[RenderedSpecimen]:
    bundle_hash = source_bundle_hash()
    return [render_specimen(case_id, mode, source_bundle_hash=bundle_hash) for case_id in CASE_META for mode in MODES]


def render_index(rendered: list[RenderedSpecimen], bundle_hash: str) -> str:
    cards: list[str] = []
    for specimen in rendered:
        meta = CASE_META[specimen.case_id]
        cards.append(
            f'''<article class="card" data-case-id="{specimen.case_id}" data-mode="{specimen.mode}">
  <div class="card-head"><div><p>{specimen.case_id} · {escape(meta['capability'])}</p><h2>{escape(meta['title'])}</h2></div><span>{specimen.mode}</span></div>
  <a class="preview" href="gallery/{specimen.filename}" aria-label="Mở {escape(meta['title'])}, {specimen.mode}">{specimen.svg}</a>
</article>'''
        )
    return f'''<!doctype html>
<html lang="vi" data-phase="P-18" data-source-bundle-hash="{bundle_hash}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>P-18 · Visual vNext pilot gallery</title>
  <style>
    :root{{--canvas:#0c111b;--panel:#151d2a;--ink:#f2f6fb;--quiet:#aeb9c8;--border:#425066;--accent:#7fb1ff}}
    *{{box-sizing:border-box}}html{{font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--canvas);color:var(--ink)}}
    body{{margin:0}}header{{padding:clamp(28px,5vw,72px);border-bottom:1px solid var(--border);background:radial-gradient(circle at 80% 0%,#1f3557 0,transparent 35%),var(--canvas)}}
    .kicker{{margin:0 0 12px;color:var(--accent);font-size:.8rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}}h1{{margin:0;max-width:980px;font-size:clamp(2.2rem,6vw,5.2rem);line-height:.96;letter-spacing:-.055em}}
    header>p:last-child{{max-width:900px;margin:24px 0 0;color:var(--quiet);font-size:1.05rem;line-height:1.7}}
    .status{{display:inline-flex;margin-top:24px;padding:9px 13px;border:1px solid var(--border);border-radius:999px;color:var(--quiet)}}
    main{{padding:clamp(20px,4vw,52px)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;align-items:start}}
    .card{{min-width:0;border:1px solid var(--border);border-radius:22px;background:var(--panel);overflow:hidden;box-shadow:0 16px 42px #0006}}
    .card-head{{min-height:102px;padding:18px 20px;display:flex;justify-content:space-between;gap:16px;align-items:start}}.card-head p{{margin:0 0 7px;color:var(--accent);font-size:.72rem;font-weight:800;letter-spacing:.08em}}.card-head h2{{margin:0;font-size:1.05rem}}.card-head span{{color:var(--quiet);font-size:.72rem;white-space:nowrap}}
    .preview{{display:block;background:#0a0f18;border-top:1px solid var(--border)}}.preview:focus-visible{{outline:4px solid var(--accent);outline-offset:-4px}}.preview svg{{display:block;width:100%;height:auto}}
    footer{{padding:30px 52px 60px;color:var(--quiet);line-height:1.65}}code{{color:var(--ink);overflow-wrap:anywhere}}
    @media(max-width:1050px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:680px){{.grid{{grid-template-columns:1fr}}header,main,footer{{padding-inline:18px}}}}
    @media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
  </style>
</head>
<body>
  <header><p class="kicker">Thien-Skill-Creative-Diagram · P-18</p><h1>Visual vNext pilot gallery</h1><p>36 original, self-contained owner-review candidates: 12 locked families across neutral light, neutral dark and editorial. Every card opens the exact standalone HTML with a visible semantic/data ledger.</p><span class="status">G-03@1.5.0 · owner review pending</span></header>
  <main><section class="grid" aria-label="36 P-18 pilot specimens">{''.join(cards)}</section></main>
  <footer><strong>QA-only, non-package.</strong> Clean-room-oriented independent reimplementation. No upstream gallery/code/template/asset used.<br>Source bundle SHA-256: <code>{bundle_hash}</code></footer>
</body>
</html>
'''


def build_outputs() -> dict[Path, bytes]:
    bundle_hash = source_bundle_hash()
    rendered = render_all()
    checks = {(item.case_id, item.mode): validate_rendered(item) for item in rendered}
    index_html = render_index(rendered, bundle_hash)
    outputs: dict[Path, bytes] = {GALLERY_DIR / item.filename: item.html.encode("utf-8") for item in rendered}
    outputs[P18_DIR / "index.html"] = index_html.encode("utf-8")
    anchor_case_ids = {"P18-C01-ARCH", "P18-C02-SWIM", "P18-C03-SANKEY"}
    anchor_items = [item for item in rendered if item.case_id in anchor_case_ids and item.mode == "neutral-light"]
    for item in anchor_items:
        anchor_html = item.html.replace(f"gallery/{item.filename}", f"anchor-proof/{item.filename}")
        outputs[ANCHOR_DIR / item.filename] = anchor_html.encode("utf-8")

    artifacts: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    for item in rendered:
        path = GALLERY_DIR / item.filename
        relative = path.relative_to(REPO_ROOT).as_posix()
        artifact_hash = sha256_bytes(outputs[path])
        artifact_check = checks[(item.case_id, item.mode)]
        artifacts.append({
            "case_id": item.case_id,
            "type": CASE_META[item.case_id]["type"],
            "capability_id": CASE_META[item.case_id]["capability"],
            "mode": item.mode,
            "path": relative,
            "sha256": artifact_hash,
            "source_fixture_sha256": item.source_hash,
            "source_bundle_sha256": item.source_bundle_hash,
            "checks": artifact_check,
        })
        receipts.append({
            "case_id": item.case_id,
            "mode": item.mode,
            "path": relative,
            "artifact_sha256": artifact_hash,
            "source_fixture_sha256": item.source_hash,
            "generator_source_bundle_sha256": item.source_bundle_hash,
            "implementation_model": "clean-room-oriented independent reimplementation",
            "upstream_gallery_code_css_template_asset_used": False,
            "benchmark_expression_reused": False,
            "visual_review_status": "OWNER-REVIEW-PENDING",
        })

    index_relative = (P18_DIR / "index.html").relative_to(REPO_ROOT).as_posix()
    manifest = {
        "schema_version": "2.0",
        "manifest_id": "P18-PILOT-1.5.0-VISUAL-CRAFT-REPLACEMENT",
        "target_version": "1.5.0",
        "authority": "PROJECT-CONTRACT.md D-049/D-050",
        "contract": "evidence/p16/PILOT-GALLERY-CONTRACT.md",
        "status": "REPLACEMENT-CANDIDATE-READY-FOR-OWNER-REVIEW",
        "gate": "G-03@1.5.0 NOT-EVALUATED",
        "owner_visual_approval": "PENDING",
        "source_bundle_sha256": bundle_hash,
        "case_family_count": 12,
        "mode_count": 3,
        "specimen_count": len(artifacts),
        "expected_specimen_count": 36,
        "index": {"path": index_relative, "sha256": sha256_bytes(index_html.encode("utf-8")), "counted_as_specimen": False},
        "anchor_proof": {
            "stage": "P-18R1",
            "counted_as_specimen": False,
            "mode": "neutral-light",
            "artifacts": [
                {
                    "case_id": item.case_id,
                    "path": (ANCHOR_DIR / item.filename).relative_to(REPO_ROOT).as_posix(),
                    "sha256": sha256_bytes(outputs[ANCHOR_DIR / item.filename]),
                }
                for item in anchor_items
            ],
        },
        "artifacts": artifacts,
        "technical_summary": {
            "semantic_pass": sum(item["checks"]["semantic"]["status"] == "PASS" for item in artifacts),
            "quantitative_pass": sum(item["checks"]["quantitative"]["status"] == "PASS" for item in artifacts),
            "geometry_pass": sum(item["checks"]["geometry"]["status"] == "PASS" for item in artifacts),
            "accessibility_pass": sum(item["checks"]["accessibility"]["status"] == "PASS" for item in artifacts),
            "security_standalone_pass": sum(item["checks"]["security_standalone"]["status"] == "PASS" for item in artifacts),
            "contrast_pass": sum(item["checks"]["contrast"]["status"] == "PASS" for item in artifacts),
            "visual_review_pending": len(artifacts),
        },
        "scope_boundary": "QA-only evidence; no P-19, package, dist, Git, tag or release authority.",
        "supersedes_manifest_sha256": "01d1cb76e1e191b9a6c4ede5fc37ef3990f61db74f0d74be744ecc977dc3a3fa",
    }
    provenance = {
        "schema_version": "1.0",
        "phase": "P-18",
        "target_version": "1.5.0",
        "upstream_snapshot": "diagram-design@648c2a597839301e06df1e7434a08bde9f42eed3",
        "policy": "abstract quality outcome only; independent project expression",
        "receipt_count": len(receipts),
        "receipts": receipts,
    }
    outputs[P18_DIR / "PILOT-MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    outputs[P18_DIR / "PROVENANCE-RECEIPTS.json"] = (json.dumps(provenance, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when generated gallery/evidence differs from source.")
    args = parser.parse_args()
    outputs = build_outputs()
    drift: list[str] = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                drift.append(path.relative_to(REPO_ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    expected = {path.resolve() for path in outputs}
    if GALLERY_DIR.exists():
        unexpected = [path for path in GALLERY_DIR.glob("*.html") if path.resolve() not in expected]
        drift.extend(path.relative_to(REPO_ROOT).as_posix() for path in unexpected)
    if drift:
        print("P-18 gallery drift: " + ", ".join(sorted(drift)))
        return 1
    print("P-18 gallery: PASS" if args.check else "P-18 gallery generated: 36 specimens + 3 non-counted anchors + index + manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
