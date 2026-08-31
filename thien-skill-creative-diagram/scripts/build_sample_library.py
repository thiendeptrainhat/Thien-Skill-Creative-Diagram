#!/usr/bin/env python3
"""Build the unified 135-diagram HTML sample library.

The approved 107-source baseline remains in evidence.  This builder creates a
user-facing catalog without phase labels, adds dark/editorial color variants
for the fourteen approved anchors, and keeps provenance only in hidden machine
metadata.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
import sys
from typing import Iterable, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
P18_SOURCE = ROOT / "evidence/p18/r6/anchors"
P19_SOURCE = ROOT / "evidence/p19/gallery/specimens"
ASSETS = ROOT / "assets"
DIAGRAMS = ASSETS / "diagrams"
SCREENSHOTS = ROOT / "screenshots/diagrams"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_renderer_v15 import P18_VISUAL_MODES  # noqa: E402


MODES = ("neutral-light", "neutral-dark", "editorial")
MODE_LABELS = {
    "neutral-light": "Neutral light",
    "neutral-dark": "Neutral dark",
    "editorial": "Editorial",
}

# Exact P-18R6/R5 neutral-light colors are mapped to the already-approved
# P-19 three-mode semantic palette.  Geometry, labels and typography roles are
# deliberately excluded from this transformation.
P18_COLOR_ROLES = {
    "#f7f6f2": "canvas",
    "#fbfaf7": "surface",
    "#ffffff": "surface",
    "#fff": "surface",
    "#eeece7": "surface_alt",
    "#e8ebee": "surface_alt",
    "#f1f0ec": "surface_alt",
    "#252b3c": "text",
    "#242b3d": "text",
    "#2d3443": "text",
    "#53627b": "muted",
    "#778194": "muted",
    "#687286": "muted",
    "#657086": "muted",
    "#667085": "muted",
    "#526078": "muted",
    "#4f5e76": "connector",
    "#51617a": "connector",
    "#c7ccd2": "border",
    "#c9cdd2": "border",
    "#d8d6d1": "border",
    "#dfe1e2": "border",
    "#d9d7d2": "grid",
    "#f26a32": "accent",
    "#f8e7dd": "accent_soft",
    "#fff3ec": "accent_soft",
    "#fad8c9": "accent_soft",
    "#df5522": "accent_text",
    "#b84a1b": "accent_text",
    "#2f65af": "blue",
    "#4f6f94": "blue",
    "#7c9167": "green",
    "#5e7452": "green",
    "#b9894b": "amber",
    "#8c632e": "amber",
    "#a56545": "amber",
    "#756b7f": "plum",
    "#675d73": "plum",
}

HEX_COLOR = re.compile(r"#[0-9a-fA-F]{8}|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}(?![0-9a-fA-F])")
SVG_BLOCK = re.compile(r"(<svg\b.*?</svg>)", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class Sample:
    stem: str
    title: str
    takeaway: str
    engine: str
    identity: str
    mode: str
    lineage: str
    source: Path
    svg: str
    svg_css: str


def _extract(pattern: str, text: str, *, default: str = "") -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else default


def extract_svg(text: str) -> str:
    match = SVG_BLOCK.search(text)
    if not match:
        raise ValueError("Standalone HTML does not contain one SVG")
    return match.group(1)


def mode_from_stem(stem: str) -> str:
    for mode in MODES:
        if stem.endswith(f"--{mode}"):
            return mode
    raise ValueError(f"No supported mode suffix in {stem!r}")


def identity_from_stem(stem: str) -> str:
    identity = re.sub(r"^\d+-", "", stem)
    return re.sub(r"--(?:neutral-light|neutral-dark|editorial)$", "", identity)


def _theme_hex(match: re.Match[str], tokens: Mapping[str, str]) -> str:
    raw = match.group(0)
    lower = raw.lower()
    alpha = ""
    base = lower
    if len(lower) == 9:
        base, alpha = lower[:7], lower[7:]
    role = P18_COLOR_ROLES.get(base)
    if role is None:
        return raw
    return tokens[role] + alpha


def theme_anchor_svg(svg: str, mode: str) -> str:
    if mode == "neutral-light":
        return svg
    tokens = P18_VISUAL_MODES[mode]
    themed = HEX_COLOR.sub(lambda match: _theme_hex(match, tokens), svg)
    themed = themed.replace('data-mode="neutral-light"', f'data-mode="{mode}"')
    themed = themed.replace("NEUTRAL-LIGHT", mode.upper())
    themed = themed.replace("neutral-light", mode)
    return themed


def p18_samples() -> list[Sample]:
    samples: list[Sample] = []
    sources = sorted(P18_SOURCE.glob("*.html"))
    if len(sources) != 14:
        raise ValueError(f"Expected 14 approved anchor HTML files, found {len(sources)}")
    for source in sources:
        html = source.read_text(encoding="utf-8")
        source_svg = extract_svg(html)
        source_stem = source.stem
        title = _extract(r"<h1>(.*?)</h1>", html, default=identity_from_stem(source_stem))
        takeaway = _extract(r'<p class="lede">(.*?)</p>', html)
        engine = _extract(r'data-layout-engine="([^"]+)"', source_svg, default=identity_from_stem(source_stem))
        identity = identity_from_stem(source_stem)
        base = source_stem.removesuffix("--neutral-light")
        for mode in MODES:
            stem = f"{base}--{mode}"
            samples.append(
                Sample(
                    stem=stem,
                    title=title,
                    takeaway=takeaway,
                    engine=engine,
                    identity=identity,
                    mode=mode,
                    lineage="approved-anchor",
                    source=source,
                    svg=theme_anchor_svg(source_svg, mode),
                    svg_css="",
                )
            )
    return samples


def p19_samples() -> list[Sample]:
    samples: list[Sample] = []
    sources = sorted(P19_SOURCE.glob("*.html"))
    if len(sources) != 93:
        raise ValueError(f"Expected 93 approved gallery HTML files, found {len(sources)}")
    for source in sources:
        html = source.read_text(encoding="utf-8")
        svg = extract_svg(html)
        svg_css = _extract(r"<style>(.*?)</style>", html)
        if not svg_css:
            raise ValueError(f"Approved gallery specimen is missing its visual stylesheet: {source.name}")
        mode = mode_from_stem(source.stem)
        title = _extract(r"<h1>(.*?)</h1>", html, default=identity_from_stem(source.stem))
        takeaway = _extract(r'<p class="takeaway">(.*?)</p>', html)
        engine = _extract(r'data-layout-engine="([^"]+)"', html, default="diagram")
        samples.append(
            Sample(
                stem=source.stem,
                title=title,
                takeaway=takeaway,
                engine=engine,
                identity=identity_from_stem(source.stem),
                mode=mode,
                lineage="approved-gallery",
                source=source,
                svg=svg,
                svg_css=svg_css,
            )
        )
    return samples


def all_samples() -> list[Sample]:
    samples = p18_samples() + p19_samples()
    stems = [item.stem for item in samples]
    if len(samples) != 135 or len(set(stems)) != 135:
        raise ValueError("Unified library must contain exactly 135 unique samples")
    return sorted(samples, key=lambda item: (item.identity, MODES.index(item.mode), item.stem))


def page_css(mode: str) -> str:
    tokens = P18_VISUAL_MODES[mode]
    display = "Georgia,'Times New Roman',serif" if mode == "editorial" else "Georgia,'Times New Roman',serif"
    radius = "2px" if mode == "editorial" else "18px"
    ui_muted = "#53627b" if mode == "neutral-light" else tokens["muted"]
    ui_accent = "#b34417" if mode == "neutral-light" else "#a43c18" if mode == "editorial" else tokens["accent_text"]
    return f"""
    :root{{--paper:{tokens['paper']};--canvas:{tokens['canvas']};--surface:{tokens['surface']};--surface-alt:{tokens['surface_alt']};--text:{tokens['text']};--muted:{tokens['muted']};--ui-muted:{ui_muted};--border:{tokens['border']};--accent:{tokens['accent']};--accent-soft:{tokens['accent_soft']};--accent-text:{tokens['accent_text']};--ui-accent:{ui_accent};--on-accent:{tokens['on_accent']};--connector:{tokens['connector']};--series-1:{tokens['blue']};--series-2:{tokens['accent']};--series-3:{tokens['green']};--series-4:{tokens['amber']};--grid:{tokens['grid']};--success:{tokens['green']};--danger:{tokens['danger']}}}
    *{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:var(--paper);color:var(--text)}}
    body{{font-family:'Avenir Next',Avenir,'Segoe UI',sans-serif;padding:48px 24px 80px}}main{{width:min(100%,1720px);margin:auto}}
    header{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;margin-bottom:24px}}
    .eyebrow{{margin:0 0 8px;font:700 13px Menlo,Monaco,monospace;letter-spacing:.16em;color:var(--ui-accent)}}
    h1{{margin:0;font:400 clamp(38px,5vw,52px)/1.06 {display}}}.takeaway{{max-width:820px;margin:10px 0 0;color:var(--ui-muted);font-size:16px;line-height:1.55}}
    .mode{{align-self:start;padding:8px 11px;border:1px solid var(--border);border-radius:999px;background:color-mix(in srgb,var(--surface) 74%,transparent);font:700 12px Menlo,Monaco,monospace;color:var(--ui-muted)}}
    .artifact-frame{{margin:0;overflow:hidden;border:1px solid var(--border);border-radius:{radius};background:var(--canvas);box-shadow:0 20px 60px color-mix(in srgb,var(--text) 10%,transparent)}}
    .artifact-frame>svg{{display:block;width:100%;height:auto;background:var(--canvas)}}
    .facts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;margin-top:16px;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--border)}}
    .fact{{padding:14px 16px;background:var(--surface)}}.fact span{{display:block;color:var(--ui-muted);font:700 11px Menlo,Monaco,monospace;letter-spacing:.1em}}.fact strong{{display:block;margin-top:5px;font-size:14px;overflow-wrap:anywhere}}
    @media(max-width:820px){{body{{padding:24px 12px 48px}}header{{grid-template-columns:1fr}}h1{{font-size:40px}}.artifact-frame{{overflow:auto}}.artifact-frame>svg{{min-width:760px}}.facts{{grid-template-columns:1fr}}}}
    @media print{{body{{padding:0;background:#fff}}header,.facts{{display:none}}.artifact-frame{{border:0;box-shadow:none}}}}
    @media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;animation:none!important;transition:none!important}}}}
    """


def render_detail(sample: Sample) -> str:
    metadata = {
        "schema_version": "1.0",
        "catalog": "unified-135",
        "identity": sample.identity,
        "engine": sample.engine,
        "mode": sample.mode,
        "lineage": sample.lineage,
        "source": str(sample.source.relative_to(ROOT)),
    }
    color_scheme = "dark" if sample.mode == "neutral-dark" else "light"
    return f'''<!doctype html>
<html lang="vi" data-catalog="unified-135" data-identity="{escape(sample.identity)}" data-mode="{sample.mode}" data-layout-engine="{escape(sample.engine)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="{color_scheme}">
<title>{escape(sample.title)} · {MODE_LABELS[sample.mode]}</title><style>{sample.svg_css}\n{page_css(sample.mode)}</style></head>
<body><main><header><div><p class="eyebrow">THIEN CREATIVE DIAGRAM · {escape(sample.engine.upper())}</p><h1>{escape(sample.title)}</h1><p class="takeaway">{sample.takeaway}</p></div><span class="mode">{MODE_LABELS[sample.mode]}</span></header>
<figure class="artifact-frame" aria-label="{escape(sample.title)} · {MODE_LABELS[sample.mode]}">{sample.svg}</figure>
<section class="facts" aria-label="Thông tin diagram"><div class="fact"><span>DIAGRAM</span><strong>{escape(sample.identity)}</strong></div><div class="fact"><span>LAYOUT</span><strong>{escape(sample.engine)}</strong></div><div class="fact"><span>MODE</span><strong>{MODE_LABELS[sample.mode]}</strong></div></section>
<script type="application/json" id="diagram-metadata">{escape(json.dumps(metadata, ensure_ascii=False, sort_keys=True), quote=False)}</script>
</main></body></html>'''


def index_css() -> str:
    return """
    :root{--paper:#eeece7;--surface:#fbfaf7;--ink:#252b3c;--muted:#53627b;--line:#cfccc5;--accent:#b34417;--focus:#2f65af}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:'Avenir Next',Avenir,'Segoe UI',sans-serif}
    .skip{position:absolute;left:16px;top:-80px;z-index:20;padding:10px 14px;background:var(--ink);color:#fff}.skip:focus{top:12px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    .page{width:min(100%,1560px);margin:auto;padding:44px 24px 72px}header{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:28px;align-items:end}
    .eyebrow{margin:0 0 9px;color:var(--accent);font:700 13px Menlo,Monaco,monospace;letter-spacing:.17em}h1{max-width:920px;margin:0;font:400 clamp(44px,7vw,86px)/.94 Georgia,'Times New Roman',serif;letter-spacing:-.035em}
    .lede{max-width:820px;margin:18px 0 0;color:var(--muted);font-size:18px;line-height:1.6}.stats{display:grid;grid-template-columns:repeat(3,auto);gap:1px;border:1px solid var(--line);background:var(--line)}.stat{min-width:112px;padding:14px;background:var(--surface)}.stat strong{display:block;font:700 22px Menlo,Monaco,monospace}.stat span{display:block;margin-top:4px;color:var(--muted);font-size:12px}
    .tools{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:34px 0 24px;padding:14px;border:1px solid var(--line);background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(14px)}
    .filter{min-height:42px;padding:9px 13px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink);font:700 13px inherit}.filter[aria-pressed=true]{border-color:var(--ink);background:var(--ink);color:#fff}.filter:focus-visible,.search:focus-visible,a:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
    .search-wrap{display:flex;flex:1 1 280px;justify-content:flex-end}.search{width:min(100%,390px);min-height:42px;padding:9px 12px;border:1px solid var(--line);border-radius:0;background:var(--surface);color:var(--ink);font:inherit}.result{margin-left:auto;color:var(--muted);font:700 12px Menlo,Monaco,monospace}
    .grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.card{min-width:0;border:1px solid var(--line);background:var(--surface)}.card[hidden]{display:none}.preview{display:block;aspect-ratio:16/10;overflow:hidden;background:#f7f6f2;border-bottom:1px solid var(--line)}.preview img{display:block;width:100%;height:100%;object-fit:cover;object-position:top center;transition:transform .2s ease}.preview:hover img{transform:scale(1.015)}
    .meta{display:grid;grid-template-columns:1fr auto;gap:12px;padding:15px}.meta h2{margin:0;font-size:17px;line-height:1.3}.meta p{margin:6px 0 0;color:var(--muted);font:12px Menlo,Monaco,monospace}.mode{align-self:start;padding:5px 7px;border:1px solid var(--line);font:700 10px Menlo,Monaco,monospace;color:var(--muted)}
    .empty{padding:64px 20px;border:1px dashed var(--line);text-align:center;color:var(--muted)}
    @media(max-width:1100px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}header{grid-template-columns:1fr}.stats{justify-self:start}}
    @media(max-width:680px){.page{padding:26px 12px 48px}.grid{grid-template-columns:1fr}.stats{width:100%;grid-template-columns:repeat(3,1fr)}.stat{min-width:0}.tools{top:0}.result{width:100%;margin-left:0}.preview{aspect-ratio:16/9}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.preview img{transition:none}}
    """


def render_index(samples: Iterable[Sample]) -> str:
    items = list(samples)
    identities = len({item.identity for item in items})
    cards = []
    for item in items:
        search = " ".join((item.title, item.identity, item.engine, item.mode)).lower()
        cards.append(
            f'''<article class="card" data-mode="{item.mode}" data-search="{escape(search)}"><a class="preview" href="diagrams/{escape(item.stem)}.html" aria-label="Mở {escape(item.title)} · {MODE_LABELS[item.mode]}"><img src="../screenshots/diagrams/{escape(item.stem)}.png" alt="{escape(item.title)} · {MODE_LABELS[item.mode]}" loading="lazy" decoding="async"></a><div class="meta"><div><h2>{escape(item.title)}</h2><p>{escape(item.engine)}</p></div><span class="mode">{MODE_LABELS[item.mode]}</span></div></article>'''
        )
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Thư viện 135 diagram · Thien Creative Diagram</title><style>{index_css()}</style></head><body><a class="skip" href="#catalog">Đến thư viện diagram</a><div class="page"><header><div><p class="eyebrow">THIEN CREATIVE DIAGRAM · SAMPLE LIBRARY</p><h1>Một thư viện. 135 cách trình bày.</h1><p class="lede">Khám phá {identities} cấu trúc diagram qua ba visual mode đồng bộ. Đây là bộ mẫu tham khảo linh hoạt, không phải giới hạn output cố định.</p></div><div class="stats" aria-label="Thống kê thư viện"><div class="stat"><strong>{identities}</strong><span>cấu trúc</span></div><div class="stat"><strong>3</strong><span>visual mode</span></div><div class="stat"><strong>{len(items)}</strong><span>diagram</span></div></div></header><section class="tools" aria-label="Bộ lọc thư viện"><button class="filter" type="button" data-filter="all" aria-pressed="true">Tất cả · {len(items)}</button><button class="filter" type="button" data-filter="neutral-light" aria-pressed="false">Neutral light · 45</button><button class="filter" type="button" data-filter="neutral-dark" aria-pressed="false">Neutral dark · 45</button><button class="filter" type="button" data-filter="editorial" aria-pressed="false">Editorial · 45</button><label class="search-wrap"><span class="sr-only">Tìm diagram</span><input class="search" type="search" placeholder="Tìm theo tên hoặc layout…" autocomplete="off"></label><output class="result" aria-live="polite">{len(items)} kết quả</output></section><main id="catalog" class="grid">{"".join(cards)}</main><p class="empty" hidden>Không tìm thấy diagram phù hợp.</p></div><script>
    const cards=[...document.querySelectorAll('.card')],buttons=[...document.querySelectorAll('.filter')],search=document.querySelector('.search'),result=document.querySelector('.result'),empty=document.querySelector('.empty');let active='all';
    function apply(){{const query=search.value.trim().toLocaleLowerCase('vi');let count=0;for(const card of cards){{const show=(active==='all'||card.dataset.mode===active)&&(!query||card.dataset.search.includes(query));card.hidden=!show;if(show)count++;}}result.value=`${{count}} kết quả`;empty.hidden=count!==0;}}
    for(const button of buttons)button.addEventListener('click',()=>{{active=button.dataset.filter;for(const item of buttons)item.setAttribute('aria-pressed',String(item===button));apply();}});search.addEventListener('input',apply);
    </script></body></html>'''


def build() -> list[Sample]:
    samples = all_samples()
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    expected = {f"{item.stem}.html" for item in samples}
    for stale in DIAGRAMS.glob("*.html"):
        if stale.name not in expected:
            stale.unlink()
    for item in samples:
        (DIAGRAMS / f"{item.stem}.html").write_text(render_detail(item), encoding="utf-8")
    (ASSETS / "index.html").write_text(render_index(samples), encoding="utf-8")
    return samples


def _visible_text(html: str) -> str:
    text = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"<[^>]+>", " ", text)


def _normalized_anchor_svg(svg: str) -> str:
    normalized = HEX_COLOR.sub("#COLOR", svg)
    normalized = re.sub(r"neutral-(?:light|dark)|editorial", "MODE", normalized, flags=re.IGNORECASE)
    return normalized


def validate(*, require_screenshots: bool = False) -> dict[str, int]:
    samples = all_samples()
    files = sorted(DIAGRAMS.glob("*.html"))
    if len(files) != 135:
        raise ValueError(f"Expected 135 detail HTML files, found {len(files)}")
    expected = {f"{item.stem}.html" for item in samples}
    if {path.name for path in files} != expected:
        raise ValueError("Detail HTML filenames do not match the canonical sample inventory")
    index = (ASSETS / "index.html").read_text(encoding="utf-8")
    links = set(re.findall(r'href="diagrams/([^"]+\.html)"', index))
    images = set(re.findall(r'src="\.\./screenshots/diagrams/([^"]+\.png)"', index))
    if links != expected or len(images) != 135:
        raise ValueError("Unified index must contain 135 unique detail links and image paths")
    forbidden = re.compile(r"(?<![A-Za-z0-9])P[‑-](?:18|19)(?!\d)", re.IGNORECASE)
    for path in [ASSETS / "index.html", *files]:
        if forbidden.search(_visible_text(path.read_text(encoding="utf-8"))):
            raise ValueError(f"Publicly visible phase label remains in {path}")
    p18 = [item for item in samples if item.lineage == "approved-anchor"]
    by_identity: dict[str, dict[str, str]] = {}
    for item in p18:
        output_svg = extract_svg((DIAGRAMS / f"{item.stem}.html").read_text(encoding="utf-8"))
        by_identity.setdefault(item.identity, {})[item.mode] = output_svg
        if item.mode == "neutral-light" and output_svg != extract_svg(item.source.read_text(encoding="utf-8")):
            raise ValueError(f"Neutral-light anchor SVG changed for {item.identity}")
    for identity, variants in by_identity.items():
        normalized = {_normalized_anchor_svg(value) for value in variants.values()}
        if len(variants) != 3 or len(normalized) != 1:
            raise ValueError(f"Anchor geometry/text drift across modes for {identity}")
    for item in (sample for sample in samples if sample.lineage == "approved-gallery"):
        output_html = (DIAGRAMS / f"{item.stem}.html").read_text(encoding="utf-8")
        output_svg = extract_svg(output_html)
        if output_svg != extract_svg(item.source.read_text(encoding="utf-8")):
            raise ValueError(f"Approved gallery SVG changed for {item.stem}")
        if item.svg_css not in output_html:
            raise ValueError(f"Approved gallery visual stylesheet is missing for {item.stem}")
    counts = {mode: sum(item.mode == mode for item in samples) for mode in MODES}
    if counts != {mode: 45 for mode in MODES}:
        raise ValueError(f"Expected 45 samples per mode, found {counts}")
    if require_screenshots:
        pngs = {path.name for path in SCREENSHOTS.glob("*.png")}
        expected_pngs = {name.removesuffix(".html") + ".png" for name in expected}
        if pngs != expected_pngs:
            raise ValueError("Screenshot inventory does not match the 135 HTML samples")
    return {"details": len(files), "identities": len({item.identity for item in samples}), **counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the existing generated library without rebuilding it")
    parser.add_argument("--with-screenshots", action="store_true", help="Require a one-to-one PNG screenshot inventory")
    args = parser.parse_args()
    if not args.check:
        build()
    print(json.dumps(validate(require_screenshots=args.with_screenshots), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
