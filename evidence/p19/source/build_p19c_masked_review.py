#!/usr/bin/env python3
"""Build a deterministic text-free masked silhouette review pack from exact P-19B previews."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
GALLERY = ROOT / "evidence/p19/gallery"
OUT = ROOT / "evidence/p19/p19c/masked-review"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def strip_text(source: Path) -> bytes:
    root = ET.fromstring(source.read_bytes())
    for parent in list(root.iter()):
        for child in list(parent):
            if local_name(child.tag) in {"text", "title", "desc", "metadata"}:
                parent.remove(child)
    for key in list(root.attrib):
        if key in {"id", "aria-labelledby", "aria-label", "data-layout-engine", "data-silhouette"} or key.startswith("data-"):
            del root.attrib[key]
    root.set("role", "img")
    root.set("aria-label", "Masked silhouette")
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def build() -> dict:
    inventory_path = GALLERY / "P-19B-INVENTORY.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    records = [item for item in inventory["records"] if item["mode"] == "neutral-light"]
    if len(records) != 31:
        raise ValueError(f"Expected 31 neutral-light identities, got {len(records)}")
    ordered = sorted(records, key=lambda item: hashlib.sha256(item["fixture_id"].encode()).hexdigest())
    OUT.mkdir(parents=True, exist_ok=True)
    records_out = []
    cards = []
    for ordinal, record in enumerate(ordered, 1):
        code = f"M{ordinal:02d}"
        source = GALLERY / "previews" / f"{record['fixture_id']}.svg"
        if not source.is_file():
            raise ValueError(f"Missing preview: {source}")
        payload = strip_text(source)
        target = OUT / f"{code}.svg"
        target.write_bytes(payload)
        records_out.append({
            "code": code,
            "identity": record["identity"],
            "fixture_id": record["fixture_id"],
            "layout_engine": record["layout_engine"],
            "silhouette": record["silhouette"],
            "source_path": str(source.relative_to(ROOT)),
            "source_sha256": digest(source),
            "masked_path": str(target.relative_to(ROOT)),
            "masked_sha256": hashlib.sha256(payload).hexdigest(),
        })
        cards.append(
            f'<figure><img src="{code}.svg" alt="Silhouette {code}"><figcaption>'
            f'<strong>{code}</strong><span>Nhận diện: ____________________</span>'
            '<span>Five-second takeaway: ____________________</span></figcaption></figure>'
        )
    page = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>P-19C masked review · 31 silhouettes</title>
<style>:root{{--paper:#eeece7;--ink:#252b3c;--line:#c7ccd2;--accent:#b7471d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 Avenir,"Segoe UI",sans-serif}}main{{max-width:1900px;margin:auto;padding:32px}}h1{{font:400 42px/1.1 Georgia,serif;margin:0 0 10px}}p{{max-width:900px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;margin-top:28px}}figure{{margin:0;border:1px solid var(--line);background:#f7f6f2;border-radius:10px;overflow:hidden}}img{{display:block;width:100%;height:260px;object-fit:contain;background:#f7f6f2}}figcaption{{display:grid;gap:5px;padding:12px 14px;border-top:1px solid var(--line)}}strong{{color:var(--accent);font:700 13px Menlo,monospace}}span{{font-size:13px}}@media(max-width:500px){{main{{padding:20px 12px}}h1{{font-size:34px}}img{{height:220px}}}}</style></head>
<body><main><p>THIEN CREATIVE DIAGRAM · P-19C · MASKED REVIEW</p><h1>31 text-free silhouettes</h1>
<p>Không mở <code>MASKED-KEY.json</code> trước khi hoàn tất. Với mỗi mã, ghi identity nhận diện được và takeaway trong năm giây. Ngưỡng đề xuất: ít nhất 27/31 identity đúng; không hard-fail hoặc takeaway đảo nghĩa.</p>
<section class="grid">{''.join(cards)}</section></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "candidate_id": "P19C-FULL-QA-FREEZE-REVIEW-01-1.5.0",
        "purpose": "owner-masked-recognition-and-five-second-review",
        "status": "READY_FOR_OWNER_REVIEW",
        "source_inventory_sha256": digest(inventory_path),
        "record_count": len(records_out),
        "text_elements_removed": True,
        "ordering": "sha256(fixture_id)",
        "records": records_out,
    }
    (OUT / "MASKED-KEY.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({"status": result["status"], "record_count": result["record_count"], "path": str(OUT.relative_to(ROOT))}, indent=2))
