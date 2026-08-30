"""Create an inert viewing aid from exact local candidates; never render diagrams."""
import argparse
import base64
import hashlib
import html
import json
import os
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P18 = ROOT / "evidence/p18/r6"
P19 = ROOT / "evidence/p19/gallery"
MODES = ("neutral-light", "neutral-dark", "editorial")
PINS = {
    "evidence/p18/r6/P-18R6-MANIFEST.json": "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a",
    "evidence/p19/gallery/P-19B-MANIFEST.json": "1306774de9b1be0aa2e70caa6e5d79b98c8b56966e700543c38b8fa794c657e9",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "afdb9efb33ab772c1cc033d25bb0fda02638746f30f1c0926c18cdd1e0fad2c1",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "f45190f1918643fe4a9383ac3fd6864088b66c89ed1a3126fdc47ad306fd878d",
    "evidence/p19/P-19A-SOURCE-MANIFEST.json": "87a5ef0fdb7f2903490f67be757662139eb9dffe8ffd6a111547583fba6d8ae0",
    "evidence/p19/P-19A-PLAN-MANIFEST.json": "c47a66f9555492207c3676ffd8d3f66c4d6688571d63c77b9284afcf0ebc6361",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_snapshot():
    result = {}
    for path, expected in PINS.items():
        require(sha((ROOT / path).read_bytes()) == expected, f"Candidate pin drift: {path}")
        result[path] = expected
    # Older P-19A source entries were legitimately superseded by P-19B;
    # only the frozen A manifest bytes, not its old source versions, are pinned.
    for name in ("evidence/p18/r6/P-18R6-MANIFEST.json",
                 "evidence/p19/gallery/P-19B-MANIFEST.json",
                 "evidence/p19/P-19B-SOURCE-MANIFEST.json"):
        manifest = read_json(ROOT / name)
        for record in manifest.get("files", manifest.get("records", [])):
            path = (ROOT / record["path"]).resolve()
            require(path.is_relative_to(ROOT), "Source outside repository")
            actual = sha(path.read_bytes())
            require(actual == record["sha256"], f"Source drift: {record['path']}")
            result[record["path"]] = actual
    return result


def safe_svg(data):
    text = data.decode("utf-8")
    require("<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper(), "Unsafe XML")
    root = ET.fromstring(text)
    require(root.tag.rsplit("}", 1)[-1] == "svg", "Expected SVG")
    for element in root.iter():
        require(element.tag.rsplit("}", 1)[-1] not in ("script", "foreignObject", "iframe", "image", "use"), "Unexpected active/external SVG element")
        for name, value in element.attrib.items():
            local = name.rsplit("}", 1)[-1].lower()
            require(not local.startswith("on"), "SVG event handler")
            if local == "href":
                require(value.startswith("#"), "External SVG link")
    require(not re.search(r"@import|javascript:|url\(\s*['\"]?(?!#)[^\s'\")]+", text, re.I), "External/active SVG CSS")
    return root


def p19_preview(page):
    text = page.decode("utf-8")
    svgs = re.findall(r"<svg\b.*?</svg>", text, re.S)
    styles = re.findall(r"<style>(.*?)</style>", text, re.S)
    require(len(svgs) == len(styles) == 1, "Expected one SVG and one stylesheet")
    raw = svgs[0]
    css = styles[0].split("@media", 1)[0]
    # Current sources have no nested base CSS; fail closed if structure changes.
    require(css.count("{") == css.count("}"), "Unbalanced base CSS")
    require("@" not in css and "]]>" not in css, "Unexpected stylesheet syntax")
    geometry = ET.fromstring(raw).attrib["viewBox"].split()
    width, height = geometry[2:]
    payload = raw.replace("<svg ", f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" ', 1)
    end = payload.index(">") + 1
    payload = payload[:end] + "<style><![CDATA[" + css + "]]></style>" + payload[end:]
    encoded = payload.encode("utf-8")
    safe_svg(encoded)
    return encoded, sha(raw.encode("utf-8")), sha(css.encode("utf-8"))


def link(path):
    require(path.is_file(), f"Missing source link: {path}")
    return quote(os.path.relpath(path, HERE), safe="/-._")


def image_block(payload, source, label, phase, identity, mode):
    root = safe_svg(payload)
    width, height = root.attrib["viewBox"].split()[2:]
    encoded = base64.b64encode(payload).decode("ascii")
    return (f'<figure data-phase="{phase}" data-identity="{html.escape(identity)}" data-mode="{mode}">'
            f'<a class="diagram" href="{link(source)}" target="_blank" rel="noopener" '
            f'aria-label="{html.escape(label)} — mở bản gốc trong tab mới">'
            f'<img src="data:image/svg+xml;base64,{encoded}" width="{width}" height="{height}" '
            f'alt="{html.escape(label)}" decoding="async"></a>'
            f'<figcaption><span>{html.escape(mode)}</span><a href="{link(source)}" '
            'target="_blank" rel="noopener">Mở bản gốc ↗</a></figcaption></figure>')


CSS = """
:root{color-scheme:light;--paper:#eeece7;--canvas:#f7f6f2;--ink:#252b3c;--muted:#596276;--line:#c7ccd2;--accent:#b7471d}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 'Avenir Next',Avenir,'Segoe UI',sans-serif}
a{color:inherit;text-underline-offset:4px}a:hover{color:var(--accent)}a:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
.skip{position:absolute;left:20px;top:-100px;background:white;padding:12px;z-index:5}.skip:focus{top:12px}
.page{padding:36px clamp(16px,3vw,60px) 80px;max-width:2560px;margin:auto}.eyebrow{font:700 12px/1.5 Menlo,monospace;letter-spacing:.12em;color:var(--accent);margin:0 0 12px}
h1{font:400 clamp(32px,4vw,56px)/1.1 Georgia,serif;margin:0 0 16px}header>p{max-width:1060px;margin:10px 0}.intro{font-size:19px}.note{color:var(--muted)}
.source-strip{display:grid;grid-template-columns:1fr 1fr;gap:28px;border-block:1px solid var(--line);padding:18px 0;margin:24px 0}
.source-strip strong{display:block;font-size:18px}.source-strip code{display:block;font-size:11px;overflow-wrap:anywhere;margin:6px 0;color:var(--muted)}
nav{display:flex;gap:6px 20px;flex-wrap:wrap;margin:20px 0 28px}nav a{font-size:13px;padding:7px 0;min-height:36px}
#large{width:20px;height:20px;margin:0 8px 0 0;accent-color:var(--accent);vertical-align:middle}.zoom-label{display:inline-block;padding:10px 0;cursor:pointer;font-weight:650}.hint{color:var(--muted);font-size:14px;margin:0 0 32px}
.engine{margin:0 0 64px;scroll-margin-top:20px}.engine-heading{border-top:2px solid var(--ink);padding:14px 0 18px;display:flex;gap:16px;align-items:baseline;justify-content:space-between}
h2{font:400 clamp(24px,2.2vw,34px)/1.2 Georgia,serif;margin:0}.count{color:var(--muted);font:12px Menlo,monospace;white-space:nowrap}
.approved-only .comparison{display:block}.approved-only .reference{position:static}.approved-only .current{margin-top:16px}.comparison{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,3fr);gap:24px}.reference{align-self:start;position:sticky;top:16px}.column-label{margin:0 0 10px;font-size:13px;font-weight:700}
.reference h3{margin:0 0 8px;font-size:19px}.reference .takeaway{font-size:14px;color:var(--muted)}.type-row{margin:0 0 28px}.type-row h3{font-size:18px;margin:0 0 10px}.type-row small{font-weight:400;color:var(--muted);font-size:12px;margin-left:8px}
.modes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0;min-width:0}.diagram{display:block;border:1px solid var(--line);background:var(--canvas);border-radius:6px;overflow:hidden}.diagram:hover{border-color:var(--accent)}img{display:block;width:100%;height:auto}
figcaption{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap;font:11px/1.5 Menlo,monospace;padding-top:8px}figcaption a{padding:5px 0;min-height:28px}
#large:checked~main .comparison{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}#large:checked~main .modes{grid-template-columns:1fr;gap:20px}
footer{border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:13px}.top-link{display:inline-block;margin-top:12px;padding:8px 0}
@media(max-width:1100px){.comparison{grid-template-columns:minmax(0,1fr) minmax(0,2fr)}.modes{grid-template-columns:1fr}.reference{top:12px}.source-strip{gap:18px}}
@media(max-width:700px){.page{padding-top:24px}.source-strip{grid-template-columns:1fr}.comparison,#large:checked~main .comparison{grid-template-columns:1fr}.reference{position:static;border-bottom:1px solid var(--line);padding-bottom:24px}.engine-heading{display:block}.count{display:block;margin-top:8px}.engine{margin-bottom:44px}.modes{grid-template-columns:1fr}nav{gap:2px 16px}figcaption{font-size:12px}}
@media print{.skip,nav,#large,.zoom-label,.hint,.top-link{display:none}.page{padding:0}.reference{position:static}.comparison,#large:checked~main .comparison{grid-template-columns:1fr 2fr}.modes,#large:checked~main .modes{grid-template-columns:repeat(3,minmax(0,1fr))}.engine{break-before:page}.type-row,figure{break-inside:avoid}}
"""


class InspectHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.figures = []
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        require(tag not in ("script", "iframe", "object", "embed"), "Active viewer content")
        require(not any(k.startswith("on") for k in attrs), "Event handler")
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "figure":
            self.figures.append(attrs)
        if tag == "a":
            self.links.append(attrs["href"])


def generate():
    before = source_snapshot()
    a = read_json(P18 / "P-18R6-INVENTORY.json")
    b = read_json(P19 / "P-19B-INVENTORY.json")
    anchors = sorted(a["engines"], key=lambda r: r["order"])
    records = b["records"]
    require(len(anchors) == 14 and len(records) == 90, "Wrong candidate coverage")
    require(b["visual_parent_candidate_id"] == a["candidate_id"], "Wrong visual parent")
    require(Counter(r["mode"] for r in records) == Counter({m: 30 for m in MODES}), "Wrong mode coverage")
    groups = defaultdict(dict)
    for record in records:
        key = (record["layout_engine"], record["fixture_id"])
        require(record["mode"] not in groups[key], "Duplicate specimen")
        groups[key][record["mode"]] = record
    require(len(groups) == 30, "Wrong unique type/capability/variant count")
    require(sum(not v["neutral-light"]["capability_id"] and not v["neutral-light"].get("presentation_variant_id") for v in groups.values()) == 25, "Wrong canonical count")
    require(sum(bool(v["neutral-light"].get("presentation_variant_id")) for v in groups.values()) == 1, "Wrong presentation variant count")
    require({key[0] for key in groups} <= {r["engine"] for r in anchors}, "Engine mismatch")
    require(all(set(g) == set(MODES) for g in groups.values()), "Incomplete mode row")
    reused = {r["canonical_type"] for r in anchors}
    require(not ({r["identity"] for r in records if not r["capability_id"]} & reused), "Duplicate P-19 canonical type")
    require({r["identity"] for r in b["reused_p18_anchors"]} == reused, "P-18 reuse mapping mismatch")
    sections, provenance = [], []
    for anchor in anchors:
        engine = anchor["engine"]
        source = P18 / anchor["html"]
        svg_path = P18 / anchor["svg"]
        payload = svg_path.read_bytes()
        label = f'P-18 · {anchor["canonical_type"]} · neutral-light · review-17 đã duyệt'
        p18_img = image_block(payload, source, label, "p18", anchor["canonical_type"], "neutral-light")
        provenance.append({"phase": "p18", "engine": engine, "identity": anchor["canonical_type"],
                           "mode": "neutral-light", "source": str(source.relative_to(ROOT)),
                           "source_sha256": sha(source.read_bytes()), "svg_source": str(svg_path.relative_to(ROOT)),
                           "svg_source_sha256": sha(payload), "preview_sha256": sha(payload)})
        rows = []
        engine_groups = [(key, modes) for key, modes in groups.items() if key[0] == engine]
        for (_, fixture), modes in engine_groups:
            first = modes["neutral-light"]
            name = first["identity"] if not first["capability_id"] else fixture.removeprefix("cap-").upper()
            kind = f'presentation variant · parent: {first["parent"]}' if first.get("presentation_variant_id") else "canonical type" if not first["capability_id"] else f'capability · parent: {first["parent"]}'
            images = []
            for mode in MODES:
                record = modes[mode]
                source = P19 / record["path"]
                page = source.read_bytes()
                require(sha(page) == record["sha256"], "Inventory source mismatch")
                payload, inline_hash, css_hash = p19_preview(page)
                images.append(image_block(payload, source, f'P-19 · {name} · {mode}', "p19", fixture, mode))
                provenance.append({"phase": "p19", "engine": engine, "identity": fixture, "mode": mode,
                                   "source": str(source.relative_to(ROOT)), "source_sha256": sha(page),
                                   "inline_svg_sha256": inline_hash, "base_css_sha256": css_hash,
                                   "preview_sha256": sha(payload)})
            rows.append(f'<article class="type-row"><h3>{html.escape(name)}<small>{html.escape(kind)}</small></h3><div class="modes">{"".join(images)}</div></article>')
        section_class = "engine" if engine_groups else "engine approved-only"
        empty_note = "" if rows else "<p>Giữ bản P‑18 đã duyệt; không còn bản P‑19 trùng lặp.</p>"
        sections.append(f'<section class="{section_class}" id="{engine}" aria-labelledby="heading-{engine}">'
                        f'<div class="engine-heading"><h2 id="heading-{engine}">{anchor["order"]:02d} · {html.escape(engine)}</h2>'
                        f'<span class="count">1 P-18 / {len(engine_groups) * 3} P-19</span></div>'
                        '<div class="comparison"><aside class="reference"><p class="column-label">P-18 · ĐÃ DUYỆT · NEUTRAL-LIGHT</p>'
                        f'<h3>{html.escape(anchor["canonical_type"])}</h3>{p18_img}<p class="takeaway">{html.escape(anchor["takeaway"])}</p></aside>'
                        f'<div class="current"><p class="column-label">P-19 · PHẦN BỔ SUNG · CHƯA ĐƯỢC OWNER DUYỆT</p>{empty_note}{"".join(rows)}</div></div>'
                        '<a class="top-link" href="#top">↑ Về mục lục</a></section>')
    nav = "".join(f'<a href="#{r["engine"]}">{r["order"]:02d} {html.escape(r["engine"])}</a>' for r in anchors)
    page = f'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
    <title>P-18 ↔ P-19 · Toàn bộ 104 diagram</title><style>{CSS}</style></head>
<body><a class="skip" href="#diagrams">Bỏ qua mục lục, đến diagram</a><div class="page" id="top">
<header><p class="eyebrow">THIEN CREATIVE DIAGRAM · OWNER COMPARISON · QA-ONLY</p>
<h1>P-18 ↔ P-19<br>Toàn bộ diagram, cùng một trang.</h1>
    <p class="intro">14 anchor P-18 đã duyệt + 90 specimen P-19 bổ sung · Tổng cộng 39 loại + 4 capability + presentation variant “layers”, không trùng loại giữa hai bộ.</p>
    <p class="note">Theo D-084/D-085/D-095/D-096/D-097: <strong>giữ nguyên 14 bản P-18, bỏ các bản P-19 trùng loại, giữ layers và detailed line-chart, thay riêng detailed medallion</strong>. P-19 có 25 loại + 4 capability + 1 presentation variant, mỗi identity đủ 3 mode; P-18 chỉ dùng neutral-light đã duyệt, không tự tạo thêm màu.</p>
<div class="source-strip"><div><strong>P-18 · review-17 · Đã duyệt theo D-077</strong><code>{html.escape(a['candidate_id'])}</code>
<a href="{link(P18 / 'index.html')}" target="_blank" rel="noopener">Mở gallery P-18 ↗</a></div>
    <div><strong>P-19B · review-17 · Chờ owner review</strong><code>{html.escape(b['candidate_id'])}</code>
<a href="{link(P19 / 'index.html')}" target="_blank" rel="noopener">Mở gallery P-19 ↗</a></div></div></header>
<nav aria-label="Mục lục 14 layout engine">{nav}</nav>
<input type="checkbox" id="large"><label class="zoom-label" for="large">Phóng lớn diagram để đọc chi tiết</label>
    <p class="hint">Mặc định ba mode P-19 nằm cạnh nhau trên màn hình rộng. Phóng lớn sẽ xếp các mode dọc, vẫn giữ đủ 104 diagram. Bấm diagram để mở bản gốc trong tab mới.</p>
<main id="diagrams">{''.join(sections)}</main>
<footer>Trang đối chiếu phụ trợ · không thay đổi hai bộ gốc hoặc trạng thái phase. Không bao gồm candidate lịch sử đã bị thay thế.
<br>Nguồn SVG/CSS và checksum: <a href="COMPARISON-MANIFEST.json">manifest đối chiếu</a> · <a href="README.md">phạm vi và giới hạn kiểm chứng</a>.
<br>Chưa kiểm chứng render trong browser do chính sách URL local-file; không xem đây là browser QA PASS.</footer>
</div></body></html>'''
    inspector = InspectHTML()
    inspector.feed(page)
    require(len(inspector.images) == len(inspector.figures) == 104, "Wrong image count")
    require(len(inspector.ids) == len(set(inspector.ids)), "Duplicate viewer IDs")
    require(Counter(f["data-phase"] for f in inspector.figures) == {"p18": 14, "p19": 90}, "Wrong phase count")
    require(len({(f['data-phase'], f['data-identity'], f['data-mode']) for f in inspector.figures}) == 104, "Duplicate diagram")
    for img, record in zip(inspector.images, provenance):
        require(bool(img.get("alt")), "Missing image alternative")
        data = base64.b64decode(img["src"].split(",", 1)[1], validate=True)
        safe_svg(data)
        require(sha(data) == record["preview_sha256"], "Embedded preview mismatch")
    for target in inspector.links:
        if target.startswith("#"):
            require(target[1:] in inspector.ids, "Dangling fragment")
        elif target not in ("COMPARISON-MANIFEST.json", "README.md"):
            require((HERE / unquote(target)).is_file(), f"Missing local link: {target}")
    require(before == source_snapshot(), "Original sources changed during generation")
    page_bytes = page.encode("utf-8")
    manifest = {"schema_version": "1.0", "purpose": "auxiliary-view-only-not-a-candidate",
                "p18_candidate": a["candidate_id"], "p19_candidate": b["candidate_id"],
                "source_manifest_pins": PINS, "counts": {"p18": 14, "p19": 90, "total": 104, "engines": 14, "p19_identities": 30, "reused_canonical_types": 14, "presentation_variants": 1},
                "checks": {"source_file_hashes": len(before), "source_preservation": "PASS",
                           "unique_coverage": "PASS", "three_modes_per_p19_fixture": "PASS",
                           "svg_xml_and_inert_payloads": "PASS", "local_links_and_fragments": "PASS",
                           "browser_render_keyboard_and_responsive": "BLOCKED_NOT_EXECUTABLE"},
                "comparison_html_sha256": sha(page_bytes),
                "generator_sha256": sha(Path(__file__).read_bytes()),
                "design_contract_sha256": sha((HERE / "README.md").read_bytes()), "records": provenance}
    return {"index.html": page_bytes,
            "COMPARISON-MANIFEST.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only deterministic check")
    args = parser.parse_args()
    outputs = generate()
    for filename, data in outputs.items():
        path = HERE / filename
        if args.check:
            require(path.read_bytes() == data, f"Generated file drift: {filename}")
        else:
            path.write_bytes(data)
    print(json.dumps({"result": "PASS", "mode": "check" if args.check else "generate",
                      "diagrams": 104, "html_bytes": len(outputs["index.html"]),
                      "html_sha256": sha(outputs["index.html"]), "browser": "BLOCKED_NOT_EXECUTABLE"}, indent=2))
