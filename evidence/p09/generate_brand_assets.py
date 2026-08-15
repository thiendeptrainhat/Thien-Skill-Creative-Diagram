"""Generate deterministic QA-only P-09 logo derivative candidates.

The master is never overwritten, cropped, recolored, traced, or vectorized.
Every candidate is derived from the complete square master by proportional
downsampling, safe-area padding, and (for plate variants) a separate backdrop.
"""

from __future__ import annotations

import hashlib
import html
import io
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "Logo-TDTN-master.png"
CANDIDATES = ROOT / "candidates"
PREVIEWS = ROOT / "previews"
SOURCE_SHA256 = "020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e"
APPROVAL_REF = "P09-OWNER-A-2026-08-15"
APPROVAL_DECISION = "D-027"
MINIMUM_APPROVED_SIZE = 64
TRANSPARENT_SIZES = (1024, 512, 400, 256, 128, 64, 48, 32)
PLATE_SIZES = (512, 400, 256, 128, 64, 48, 32)
SAFE_SCALE = 0.82
PLATE_SCALE = 0.74
PALETTE = {
    "navy": "#071A33",
    "gold": "#C3AA75",
    "parchment": "#F8F5E8",
    "white": "#FFFFFF",
    "ink": "#10213A",
    "muted": "#5E6A7C",
    "line": "#D7DCE5",
}
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


def approval_state(size: int) -> str:
    return "owner-approved" if size >= MINIMUM_APPROVED_SIZE else "owner-excluded-qa-only"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_bytes(image: Image.Image) -> bytes:
    pnginfo = PngInfo()
    pnginfo.add(b"sRGB", b"\x00")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", compress_level=9, optimize=False, pnginfo=pnginfo)
    return buffer.getvalue()


def write_deterministic(path: Path, image: Image.Image) -> dict[str, Any]:
    first = png_bytes(image)
    second = png_bytes(image)
    if first != second:
        raise RuntimeError(f"Non-deterministic PNG serialization: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(first)
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(first),
        "bytes": len(first),
        "dimensions": list(image.size),
        "mode": image.mode,
        "alpha_bbox": list(bbox) if bbox else None,
    }


def place_master(master: Image.Image, size: int, scale: float) -> Image.Image:
    target = max(1, round(size * scale))
    resized = master.resize((target, target), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - target) // 2, (size - target) // 2)
    canvas.alpha_composite(resized, offset)
    return canvas


def rounded_plate(size: int, fill: str, outline: str) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    inset = max(2, round(size * 0.025))
    width = max(1, round(size * 0.012))
    radius = round(size * 0.22)
    draw.rounded_rectangle(
        (inset, inset, size - inset - 1, size - inset - 1),
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )
    return canvas


def plate_candidate(master: Image.Image, size: int, mode: str) -> Image.Image:
    if mode == "light":
        plate = rounded_plate(size, PALETTE["parchment"], PALETTE["navy"])
    elif mode == "dark":
        plate = rounded_plate(size, PALETTE["navy"], PALETTE["gold"])
    else:  # pragma: no cover - fixed recipe guard
        raise ValueError(mode)
    mark = place_master(master, size, PLATE_SCALE)
    plate.alpha_composite(mark)
    return plate


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf") if bold else FONT_PATH
    return ImageFont.truetype(str(path), size)


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill="#E7EAF0")
    return image


def preview_tile(asset: Image.Image, size: int, background: str | None = None) -> Image.Image:
    tile = checkerboard((size, size)) if background is None else Image.new("RGB", (size, size), background)
    tile.paste(asset, (0, 0), asset if asset.mode == "RGBA" else None)
    return tile


def masked_preview(asset: Image.Image, shape: str, size: int = 180) -> Image.Image:
    background = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    inset = 4
    if shape == "square":
        draw.rectangle((inset, inset, size - inset - 1, size - inset - 1), fill=255)
    elif shape == "circle":
        draw.ellipse((inset, inset, size - inset - 1, size - inset - 1), fill=255)
    elif shape == "squircle":
        draw.rounded_rectangle((inset, inset, size - inset - 1, size - inset - 1), radius=round(size * 0.23), fill=255)
    else:  # pragma: no cover
        raise ValueError(shape)
    plate = Image.new("RGBA", (size, size), PALETTE["parchment"])
    plate.alpha_composite(asset.resize((size, size), Image.Resampling.LANCZOS))
    plate.putalpha(ImageChops.multiply(plate.getchannel("A"), mask))
    background.alpha_composite(plate)
    return background


def build_contact_sheet(master: Image.Image, assets: dict[str, Image.Image]) -> Image.Image:
    width, height = 1900, 1660
    sheet = Image.new("RGB", (width, height), "#EEF1F6")
    draw = ImageDraw.Draw(sheet)
    draw.text((72, 48), "P-09 · Owner-approved brand selection", font=font(46, True), fill=PALETTE["ink"])
    draw.text((72, 108), "Option A · full crest ≥64px approved · 32/48px QA-only", font=font(23), fill=PALETTE["muted"])

    # Source behavior on three backgrounds.
    draw.text((72, 170), "1 · Source behavior", font=font(28, True), fill=PALETTE["ink"])
    source = place_master(master, 300, SAFE_SCALE)
    for index, (label, bg) in enumerate((("Transparency", None), ("Light", PALETTE["parchment"]), ("Dark", PALETTE["navy"]))):
        x = 72 + index * 350
        tile = preview_tile(source, 300, bg)
        sheet.paste(tile, (x, 220))
        draw.text((x, 530), label, font=font(20, True), fill=PALETTE["ink"])

    # Plate candidates.
    draw.text((1150, 170), "2 · Plate candidates", font=font(28, True), fill=PALETTE["ink"])
    for index, mode in enumerate(("light", "dark")):
        asset = assets[f"full-crest-plate-{mode}-512.png"].resize((300, 300), Image.Resampling.LANCZOS)
        x = 1150 + index * 330
        sheet.paste(preview_tile(asset, 300), (x, 220))
        draw.text((x, 530), f"{mode.title()} plate", font=font(20, True), fill=PALETTE["ink"])

    # Actual pixel sizes plus nearest-neighbor detail views.
    draw.text((72, 610), "3 · Actual-size survival", font=font(28, True), fill=PALETTE["ink"])
    cursor = 72
    for size in (32, 48, 64, 128, 256):
        asset = assets[f"full-crest-transparent-{size}.png"]
        box_h = 300
        tile = Image.new("RGB", (300, box_h), "white")
        tile.paste(asset, ((300 - size) // 2, 24), asset)
        if size <= 64:
            detail = asset.resize((160, 160), Image.Resampling.NEAREST)
            tile.paste(detail, (70, 120), detail)
        sheet.paste(tile, (cursor, 660))
        disposition = "approved minimum" if size == 64 else ("QA-only · excluded" if size < 64 else "approved")
        label = f"{size}px · {disposition}"
        draw.text((cursor, 970), label, font=font(18, True), fill=PALETTE["ink"])
        cursor += 350

    # Shape masks preview the same transparent 128px candidate; no pixels are cropped from the stored asset.
    draw.text((72, 1050), "4 · Host-mask preview", font=font(28, True), fill=PALETTE["ink"])
    mark = assets["full-crest-transparent-128.png"]
    for index, shape in enumerate(("square", "circle", "squircle")):
        x = 72 + index * 260
        preview = masked_preview(mark, shape)
        sheet.paste(preview, (x, 1100), preview)
        draw.text((x, 1290), shape.title(), font=font(19, True), fill=PALETTE["ink"])

    draw.rounded_rectangle((900, 1090, 1828, 1515), radius=24, fill="white", outline=PALETTE["line"], width=2)
    draw.text((944, 1130), "Review notes", font=font(28, True), fill=PALETTE["ink"])
    notes = [
        "• Master remains byte-identical and outside release payload.",
        "• No crop, recolor, trace, vectorization, or generated mark.",
        "• Transparent use on dark navy loses navy detail; use the dark plate.",
        "• Owner approved all three full-crest families at 64px minimum.",
        "• 32/48px remain QA-only and are excluded from v1.0.0 release use.",
        "• No simplified mark will be created for v1.0.0.",
        "• Plate colors are measured candidate tones, not cleared brand claims.",
    ]
    y = 1190
    for line in notes:
        draw.text((944, y), line, font=font(19), fill=PALETTE["muted"])
        y += 48
    draw.text((72, 1585), "Generated deterministically with Pillow; see ASSET-MANIFEST.candidate.json and qa-report.json.", font=font(18), fill=PALETTE["muted"])
    return sheet


def build_html(rows: list[dict[str, Any]]) -> str:
    cards = []
    for row in rows:
        rel = "../" + row["path"]
        cards.append(
            f'<article><div class="frame"><img src="{html.escape(rel)}" alt="{html.escape(row["alt"])}"></div>'
            f'<h2>{html.escape(row["variant_id"])}</h2><p class="{html.escape(row["selection_state"])}">{row["dimensions"][0]}×{row["dimensions"][1]} · {html.escape(row["approval_state"])}</p>'
            f'<a href="{html.escape(rel)}">Open PNG</a></article>'
        )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-09 brand candidates</title><style>
:root{{--bg:#eef1f6;--paper:#fff;--ink:#10213a;--muted:#5e6a7c;--line:#d7dce5;--accent:#173d70;--ok:#1f6f50;--qa:#9a5c00}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 Arial,sans-serif}}header{{padding:36px clamp(20px,5vw,72px) 16px}}h1{{margin:0 0 8px;font-size:clamp(30px,4vw,50px)}}header p{{max-width:960px;color:var(--muted)}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:22px;padding:20px clamp(20px,5vw,72px) 60px}}article{{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:16px}}.frame{{aspect-ratio:1;display:grid;place-items:center;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:linear-gradient(45deg,#e7eaf0 25%,transparent 25%),linear-gradient(-45deg,#e7eaf0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e7eaf0 75%),linear-gradient(-45deg,transparent 75%,#e7eaf0 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}}img{{display:block;max-width:100%;max-height:100%}}h2{{font-size:17px;margin:14px 0 4px}}p{{margin:0 0 8px;color:var(--muted)}}.approved-brand-derivative{{color:var(--ok);font-weight:700}}.qa-only{{color:var(--qa);font-weight:700}}a{{color:var(--accent);font-weight:700}}
</style></head><body><header><h1>P-09 · Owner-approved brand selection</h1><p>Option A is locked: transparent, light-plate and dark-plate full-crest families are approved at a 64px minimum. The 32/48px files remain QA-only and excluded from v1.0.0; no simplified mark will be created for v1.0.0. Package mapping and release eligibility remain deferred.</p></header><main>{''.join(cards)}</main></body></html>'''


def main() -> None:
    if not SOURCE.is_file() or sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise RuntimeError("The P-09 master is missing or its bytes do not match the locked source hash.")
    master = Image.open(SOURCE).convert("RGBA")
    if master.size != (1100, 1100):
        raise RuntimeError("The locked master dimensions changed.")

    rows: list[dict[str, Any]] = []
    preview_assets: dict[str, Image.Image] = {}
    for size in TRANSPARENT_SIZES:
        filename = f"full-crest-transparent-{size}.png"
        asset = place_master(master, size, SAFE_SCALE)
        preview_assets[filename] = asset
        record = write_deterministic(CANDIDATES / filename, asset)
        rows.append({
            **record,
            "variant_id": filename.removesuffix(".png"),
            "family": "full-crest-transparent-safe-area",
            "recipe": {"operation": "proportional-downsample-complete-master-and-center", "scale": SAFE_SCALE, "resampling": "Pillow LANCZOS", "encoding": "lossless PNG with standard sRGB chunk"},
            "alt": "TDTN crest with sword, lion, letterforms and open book in navy and gold",
            "approval_state": approval_state(size),
            "selection_state": "approved-brand-derivative" if size >= MINIMUM_APPROVED_SIZE else "qa-only",
            "approval_ref": APPROVAL_REF,
            "release_eligible": False,
            "destination_status": "candidate; exact platform mapping deferred to P-13",
        })

    for mode in ("light", "dark"):
        for size in PLATE_SIZES:
            filename = f"full-crest-plate-{mode}-{size}.png"
            asset = plate_candidate(master, size, mode)
            preview_assets[filename] = asset
            record = write_deterministic(CANDIDATES / filename, asset)
            rows.append({
                **record,
                "variant_id": filename.removesuffix(".png"),
                "family": f"full-crest-{mode}-squircle-plate",
                "recipe": {"operation": "separate-rounded-plate-plus-proportional-complete-master", "mark_scale": PLATE_SCALE, "resampling": "Pillow LANCZOS", "encoding": "lossless PNG with standard sRGB chunk", "palette": PALETTE},
                "alt": f"TDTN crest on a {mode} rounded-square presentation plate",
                "approval_state": approval_state(size),
                "selection_state": "approved-brand-derivative" if size >= MINIMUM_APPROVED_SIZE else "qa-only",
                "approval_ref": APPROVAL_REF,
                "release_eligible": False,
                "destination_status": "candidate; exact platform mapping deferred to P-13",
            })

    contact = build_contact_sheet(master, preview_assets)
    contact_record = write_deterministic(PREVIEWS / "contact-sheet.png", contact)
    (PREVIEWS / "contact-sheet.html").write_text(build_html(rows), encoding="utf-8")

    manifest = {
        "schema_version": "1.0",
        "record_id": "P09-ASSET-CANDIDATE-1",
        "date": "2026-08-15",
        "scope": "P-09 QA-only candidate assets; not a release ASSET_MANIFEST",
        "master": {
            "path": "source/Logo-TDTN-master.png",
            "sha256": SOURCE_SHA256,
            "dimensions": [1100, 1100],
            "mode": "RGBA",
            "ownership_basis": "owner assertion recorded in PROJECT-CONTRACT.md D-016",
            "origin_note": "owner-provided AI-created raster; no vector source",
            "immutable": True,
            "package_targets": [],
        },
        "generation": {
            "script": "generate_brand_assets.py",
            "python": sys.version.split()[0],
            "pillow": Image.__version__,
            "color_space": "standard PNG sRGB chunk",
            "metadata_policy": "derivatives contain no copied EXIF/XMP; provenance stays in this manifest",
            "network": "none",
            "dependency_install": "none",
        },
        "palette_note": "Candidate presentation tones measured from visible master pixels; not a trademark, clearance, or final brand-token claim.",
        "approval": {
            "state": "owner-approved-selection",
            "approval_ref": APPROVAL_REF,
            "decision": APPROVAL_DECISION,
            "option": "A",
            "minimum_size_px": MINIMUM_APPROVED_SIZE,
            "simplified_mark": "not-created-for-v1.0.0",
            "release_eligible": False,
            "release_blockers": ["P-10 and G-06 legal/provenance approval", "P-13 platform mapping and package build"],
        },
        "candidates": rows,
        "preview": contact_record,
    }
    (ROOT / "ASSET-MANIFEST.candidate.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    source_bbox = list(master.getchannel("A").getbbox() or ())
    qa = {
        "schema_version": "1.0",
        "status": "pass-owner-approved",
        "source": {"sha256_match": True, "dimensions": list(master.size), "mode": master.mode, "alpha_bbox": source_bbox},
        "candidate_count": len(rows),
        "checks": {
            "source_byte_identity": "pass",
            "no_crop_recolor_trace_vectorization": "pass-by-recipe-and-output-inventory",
            "square_aspect": "pass",
            "embedded_srgb": "pass",
            "deterministic_png_serialization": "pass",
            "transparent_safe_area": "pass",
            "light_dark_background_preview": "pass-with-dark-plate-required-for-dark-navy-context",
            "square_circle_squircle_preview": "pass",
            "small_size_64": "pass-with-full-crest-detail-limit",
            "small_size_32_48": "qa-only-excluded-from-v1.0.0",
            "owner_selection": "pass-option-A-full-crest-families-at-64px-minimum",
            "simplified_mark_v1.0.0": "not-created-per-owner-decision",
            "trademark_clearance": "not-claimed",
        },
        "hard_failures": [],
        "owner_decisions_required": [],
    }
    (ROOT / "qa-report.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    approved = [item for item in rows if item["selection_state"] == "approved-brand-derivative"]
    excluded = [item for item in rows if item["selection_state"] == "qa-only"]
    selection = {
        "schema_version": "1.0",
        "record_id": "P09-APPROVED-BRAND-SELECTION-1",
        "date": "2026-08-15",
        "approval": "owner-approved",
        "approval_ref": APPROVAL_REF,
        "decision": APPROVAL_DECISION,
        "option": "A",
        "immutable": True,
        "minimum_size_px": MINIMUM_APPROVED_SIZE,
        "approved_families": ["full-crest-transparent-safe-area", "full-crest-light-squircle-plate", "full-crest-dark-squircle-plate"],
        "simplified_mark": "not-created-for-v1.0.0",
        "approved_artifacts": [{key: item[key] for key in ("path", "sha256", "family", "dimensions")} for item in approved],
        "excluded_qa_only": [{key: item[key] for key in ("path", "sha256", "family", "dimensions")} for item in excluded],
        "release_eligible": False,
        "release_blockers": ["P-10 and G-06 legal/provenance approval", "P-13 platform mapping and package build"],
    }
    selection_path = ROOT / "APPROVED-BRAND-SELECTION.json"
    selection_bytes = (json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if selection_path.exists() and selection_path.read_bytes() != selection_bytes:
        raise RuntimeError("Approved brand selection drifted; owner re-approval is required before changing the locked record.")
    if not selection_path.exists():
        selection_path.write_bytes(selection_bytes)
    print(json.dumps({"status": qa["status"], "candidates": len(rows), "contact_sheet": contact_record["path"], "hard_failures": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
