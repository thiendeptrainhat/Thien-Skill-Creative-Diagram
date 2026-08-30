#!/usr/bin/env python3
"""Generate the exact P-18R6 14-engine neutral-light gallery."""

from __future__ import annotations

import hashlib
from html import escape
import json
from pathlib import Path
import shutil

from gallery_kernel import Anchor, TYPOGRAPHY, anchors_without_swimlane, orthogonal_route_d, render_html


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
ANCHORS = R6 / "anchors"
REVIEW = R6 / "review"
R5 = ROOT / "evidence/p18/r5"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lane_anchor() -> Anchor:
    source = R5 / "anchor/swimlane--neutral-light.svg"
    svg = source.read_text(encoding="utf-8")
    return Anchor(
        order=6,
        engine="lane-interaction",
        canonical_type="swimlane",
        filename="06-lane-interaction--neutral-light",
        title="Lane interaction anchor",
        takeaway="Nhánh cập nhật công nợ là focal handoff; crossing dùng hop geometry liên tục đã được owner duyệt.",
        svg=svg,
        facts=(
            ("lineage", "Exact frozen P-18R5 review-04 SVG"),
            ("source_sha256", sha256(source)),
            ("manifest_sha256", sha256(R5 / "P-18R5-MANIFEST.json")),
            ("engine", "lane-interaction"),
        ),
    )


def all_anchors() -> tuple[Anchor, ...]:
    return tuple(sorted((*anchors_without_swimlane(), lane_anchor()), key=lambda item: item.order))


def shell_css() -> str:
    return """
    :root{--paper:#eeece7;--canvas:#f7f6f2;--ink:#252b3c;--muted:#687286;--line:#d6d4ce;--accent:#f26a32}
    *{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--paper);color:var(--ink)}
    body{font-family:system-ui,sans-serif;padding:44px 24px 72px}main{width:min(100%,1840px);margin:auto}
    .eyebrow{margin:0 0 8px;font:700 14px ui-monospace,monospace;letter-spacing:.16em;color:var(--accent)}
    h1{margin:0;font-family:Georgia,serif;font-size:48px;line-height:1.06;font-weight:400}.lede{max-width:880px;margin:12px 0 32px;font-size:16px;line-height:1.6;color:var(--muted)}
    .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.card{display:flex;flex-direction:column;min-width:0;border:1px solid var(--line);border-radius:18px;background:#ffffff8f;overflow:hidden;box-shadow:0 16px 44px #2d344314}
    .preview{display:flex;align-items:center;justify-content:center;aspect-ratio:16/9;padding:10px;background:var(--canvas);border-bottom:1px solid var(--line)}.preview img{display:block;width:100%;height:100%;object-fit:contain}
    .meta{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:16px 18px}.num{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:#e4e2dd;font:700 14px ui-monospace,monospace}.meta h2{margin:0;font-size:20px}.meta p{margin:4px 0 0;color:var(--muted);font:14px ui-monospace,monospace}.open{color:var(--accent);text-decoration:none;font-weight:700}.open:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
    @media(max-width:980px){.grid{grid-template-columns:1fr}}@media(max-width:650px){body{padding:24px 12px 48px}h1{font-size:40px}.meta{grid-template-columns:auto 1fr}.open{grid-column:2}}
    """


def build_index(anchors: tuple[Anchor, ...]) -> str:
    cards = []
    for item in anchors:
        cards.append(f'''<article class="card"><div class="preview"><img src="anchors/{escape(item.filename)}.svg" alt="{escape(item.title)}"></div><div class="meta"><span class="num">{item.order:02d}</span><div><h2>{escape(item.engine)}</h2><p>{escape(item.canonical_type)} · neutral-light</p></div><a class="open" href="anchors/{escape(item.filename)}.html">Open anchor →</a></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-18R6 · 14-engine anchor gallery</title><style>{shell_css()}</style></head><body><main><p class="eyebrow">P‑18R6 · OWNER REVIEW CONTACT SHEET</p><h1>Fourteen engines. Fourteen distinct silhouettes.</h1><p class="lede">QA-only neutral-light anchors derived from the locked semantic contract. This labeled sheet is for owner inspection; use the masked sheet for blind recognition.</p><section class="grid">{"".join(cards)}</section></main></body></html>'''


def build_blind(anchors: tuple[Anchor, ...]) -> str:
    # Fixed deterministic shuffle prevents the numeric order from revealing the engine map.
    order = (11, 3, 8, 1, 13, 5, 10, 2, 14, 7, 4, 12, 6, 9)
    lookup = {item.order: item for item in anchors}
    cards = []
    for blind_number, source_order in enumerate(order, 1):
        item = lookup[source_order]
        cards.append(f'''<article class="card"><div class="preview"><img src="anchors/{escape(item.filename)}.svg" alt="Masked candidate {blind_number:02d}"></div><div class="meta"><span class="num">{blind_number:02d}</span><div><h2>Masked candidate</h2><p>Identify the layout family from silhouette only.</p></div></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-18R6 · masked blind sheet</title><style>{shell_css()}</style></head><body><main><p class="eyebrow">P‑18R6 · MASKED REVIEW</p><h1>Silhouette recognition</h1><p class="lede">Review the numbered cards before opening the labeled contact sheet. Record one family guess per card.</p><section class="grid">{"".join(cards)}</section></main></body></html>'''


def main() -> None:
    ANCHORS.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    anchors = all_anchors()
    if len(anchors) != 14 or len({item.engine for item in anchors}) != 14:
        raise RuntimeError("P-18R6 must produce exactly fourteen unique engines")

    for item in anchors:
        (ANCHORS / f"{item.filename}.svg").write_text(item.svg, encoding="utf-8")
        (ANCHORS / f"{item.filename}.html").write_text(render_html(item), encoding="utf-8")

    (R6 / "index.html").write_text(build_index(anchors), encoding="utf-8")
    (R6 / "blind-review.html").write_text(build_blind(anchors), encoding="utf-8")
    shutil.copy2(R5 / "P-18R5-MANIFEST.json", REVIEW / "P-18R5-parent-manifest.json")

    inventory = {
        "schema_version": "1.0",
        "candidate_id": "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-04-1.5.0",
        "authority": ["D-051", "D-052", "D-058", "D-059", "D-060", "D-061", "D-062"],
        "mode": "neutral-light",
        "engine_count": len(anchors),
        "engines": [
            {
                "order": item.order,
                "engine": item.engine,
                "canonical_type": item.canonical_type,
                "html": f"anchors/{item.filename}.html",
                "svg": f"anchors/{item.filename}.svg",
                "takeaway": item.takeaway,
            }
            for item in anchors
        ],
        "typography": {
            role: {
                "preferred": resolved.requested_family,
                "resolved": resolved.resolved_family,
                "precedence": resolved.precedence_source,
                "fallback_used": resolved.fallback_used,
                "fallback_reason": resolved.fallback_reason,
            }
            for role, resolved in TYPOGRAPHY.items()
        },
        "connector_corner_style": {
            "scope": "whole-chart",
            "engines": ["topology-and-zones", "integration-pipeline", "runtime-deployment", "dependency-dag"],
            "default": "rounded",
            "allowed": ["rounded", "straight"],
            "explicit_user_choice_precedence": True,
            "rounded_example": orthogonal_route_d(((0, 0), (0, 40), (40, 40)), "rounded"),
            "straight_example": orthogonal_route_d(((0, 0), (0, 40), (40, 40)), "straight"),
        },
        "r5_parent": {
            "manifest": "review/P-18R5-parent-manifest.json",
            "manifest_sha256": sha256(R5 / "P-18R5-MANIFEST.json"),
            "swimlane_svg_sha256": sha256(R5 / "anchor/swimlane--neutral-light.svg"),
            "preserved_exactly": True,
        },
        "lineage": {
            "review": "review-04",
            "supersedes_for_owner_review": "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-03-1.5.0",
            "review_01_manifest_sha256": "fcdec11e49a00d89d82a3fafaba7cae2ac8e7c58908fa76cc2fa6eba383aad37",
            "review_01_archive": "history/review-01",
            "review_02_manifest_sha256": "2f9c7aad3a2dd9d43d575ddfb864effa915df909134d5401dbb075ed6ea2cf7b",
            "review_02_archive": "history/review-02",
            "review_03_manifest_sha256": "572de899399755268d63fa5cb49c598a6ee6c5d509418ed8d07484a750c62e54",
            "review_03_archive": "history/review-03",
        },
        "review": {"owner_status": "PENDING", "g03_1_5_0": "NOT-EVALUATED", "p19_authorized": False},
    }
    (R6 / "P-18R6-INVENTORY.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
