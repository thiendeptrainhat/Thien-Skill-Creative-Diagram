#!/usr/bin/env python3
"""Rasterize P-18R6 SVG anchors with macOS Quick Look for visual inspection.

Quick Look emits square thumbnails.  A square viewport wrapper forces the SVG
viewBox to `meet`; Pillow then removes only the deterministic letterbox area.
No gallery source or frozen R5 input is modified.
"""

from __future__ import annotations

import re
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
ANCHORS = R6 / "anchors"
REVIEW = R6 / "review"
PREVIEWS = REVIEW / "previews"
TEMP = Path("/private/tmp/p18r6-quicklook")
SIDE = 2000


def viewbox(source: str) -> tuple[float, float]:
    match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', source)
    if not match:
        raise RuntimeError("SVG must have a numeric 0 0 viewBox")
    return float(match.group(1)), float(match.group(2))


def square_wrapper(source: str) -> str:
    source = re.sub(r'width="[0-9.]+" height="[0-9.]+"', f'width="{SIDE}" height="{SIDE}" preserveAspectRatio="xMidYMid meet"', source, count=1)
    return source


def crop_letterbox(image: Image.Image, source_width: float, source_height: float) -> Image.Image:
    ratio = source_width / source_height
    if ratio >= 1:
        content_width = SIDE
        content_height = round(SIDE / ratio)
        top = (SIDE - content_height) // 2
        return image.crop((0, top, SIDE, top + content_height))
    content_height = SIDE
    content_width = round(SIDE * ratio)
    left = (SIDE - content_width) // 2
    return image.crop((left, 0, left + content_width, SIDE))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    return ImageFont.truetype(path, size)


def contact_sheet(items: list[tuple[str, Image.Image]], output: Path, labels: bool) -> None:
    cols = 2
    card_w, art_h, meta_h, gap = 980, 560, 70 if labels else 34, 28
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w + (cols + 1) * gap, rows * (art_h + meta_h) + (rows + 1) * gap), "#eeece7")
    draw = ImageDraw.Draw(sheet)
    for index, (name, preview) in enumerate(items):
        row, col = divmod(index, cols)
        x = gap + col * (card_w + gap)
        y = gap + row * (art_h + meta_h + gap)
        card = Image.new("RGB", (card_w, art_h), "#f7f6f2")
        thumb = preview.copy()
        thumb.thumbnail((card_w - 20, art_h - 20), Image.Resampling.LANCZOS)
        card.paste(thumb, ((card_w - thumb.width) // 2, (art_h - thumb.height) // 2))
        sheet.paste(card, (x, y))
        draw.rounded_rectangle((x, y, x + card_w, y + art_h), radius=18, outline="#c7ccd2", width=2)
        label = f"{index + 1:02d}  {name}" if labels else f"{index + 1:02d}"
        draw.text((x + 14, y + art_h + 12), label, fill="#252b3c", font=font(24, labels))
    sheet.save(output, optimize=True)


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[str, Image.Image]] = []
    for path in sorted(ANCHORS.glob("*.svg")):
        source = path.read_text(encoding="utf-8")
        source_width, source_height = viewbox(source)
        wrapped = TEMP / path.name
        wrapped.write_text(square_wrapper(source), encoding="utf-8")
        raw = TEMP / f"{path.name}.png"
        if raw.exists():
            raw.unlink()
        subprocess.run(["qlmanage", "-t", "-s", str(SIDE), "-o", str(TEMP), str(wrapped)], check=True, capture_output=True)
        image = Image.open(raw).convert("RGB")
        cropped = crop_letterbox(image, source_width, source_height)
        output = PREVIEWS / f"{path.stem}.png"
        cropped.save(output, optimize=True)
        rendered.append((path.stem.replace("--neutral-light", ""), cropped))
    contact_sheet(rendered, REVIEW / "contact-sheet-labeled.png", labels=True)
    blind_order = (10, 2, 7, 0, 12, 4, 9, 1, 13, 6, 3, 11, 5, 8)
    contact_sheet([(f"masked-{idx + 1:02d}", rendered[source][1]) for idx, source in enumerate(blind_order)], REVIEW / "contact-sheet-masked.png", labels=False)


if __name__ == "__main__":
    main()
