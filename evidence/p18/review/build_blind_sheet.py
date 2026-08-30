#!/usr/bin/env python3
"""Build a metadata-free thumbnail sheet for the P-18R3 silhouette review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ORDER = (
    "wardley-map",
    "sankey",
    "bubble",
    "swimlane",
    "fishbone",
    "architecture",
    "ridgeline",
    "user-journey",
    "treemap",
    "slopegraph",
    "deployment",
    "dumbbell",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sheet = Image.new("RGB", (2400, 1740), "#e9edf0")
    draw = ImageDraw.Draw(sheet)
    label_font = font(28)
    caption_font = font(18)
    card_w, card_h = 560, 500
    gap_x, gap_y = 30, 40
    origin_x, origin_y = 35, 40
    answer_key: list[dict[str, str | int]] = []

    for index, family in enumerate(ORDER, start=1):
        source = args.screenshots / f"{family}--neutral-light.png"
        image = Image.open(source).convert("RGB")
        # Remove the external artifact header. The remaining crop contains only
        # the semantic SVG field and type legend, with no family/title metadata.
        crop = image.crop((18, 190, image.width - 18, image.height - 12))
        thumb = ImageOps.contain(crop, (card_w - 28, card_h - 58), Image.Resampling.LANCZOS)
        col = (index - 1) % 4
        row = (index - 1) // 4
        x = origin_x + col * (card_w + gap_x)
        y = origin_y + row * (card_h + gap_y)
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=16, fill="#f8fafb", outline="#bcc6cf", width=2)
        thumb_x = x + (card_w - thumb.width) // 2
        thumb_y = y + 42 + (card_h - 52 - thumb.height) // 2
        sheet.paste(thumb, (thumb_x, thumb_y))
        draw.text((x + 18, y + 10), f"{index:02d}", fill="#263141", font=label_font)
        answer_key.append({"slot": index, "family": family, "source_sha256": sha256(source)})

    draw.text((38, 1675), "P-18R3 · MASKED FAMILY / TITLE METADATA · NEUTRAL-LIGHT", fill="#536273", font=caption_font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, quality=94, subsampling=0)
    key_path = args.output.with_suffix(".answer-key.json")
    key_path.write_text(json.dumps({"protocol": "fixed shuffled order; metadata-free thumbnails", "entries": answer_key}, indent=2) + "\n")
    print(f"Wrote {args.output}")
    print(f"Wrote {key_path}")


if __name__ == "__main__":
    main()
