"""Compose retained P-18R owner-review contact sheets from browser captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


SOURCE_DIR = Path(__file__).resolve().parent
P18_DIR = SOURCE_DIR.parent
REPO_ROOT = P18_DIR.parents[1]
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from p18_cases import CASE_META, MODES  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_sheet(mode: str, screenshots: Path, output_dir: Path) -> dict[str, object]:
    width = 2400
    margin = 36
    gap = 18
    columns = 3
    cell_width = (width - margin * 2 - gap * (columns - 1)) // columns
    ordered = [f'{meta["slug"]}--{mode}.png' for meta in CASE_META.values()]
    images = [Image.open(screenshots / name).convert("RGB") for name in ordered]
    target_heights = [round(image.height * cell_width / image.width) for image in images]
    cell_height = max(target_heights)
    rows = (len(images) + columns - 1) // columns
    height = margin * 2 + rows * cell_height + (rows - 1) * gap
    background = (10, 15, 24) if mode == "neutral-dark" else (225, 228, 232)
    canvas = Image.new("RGB", (width, height), background)
    for index, image in enumerate(images):
        resized_height = target_heights[index]
        resized = image.resize((cell_width, resized_height), Image.Resampling.LANCZOS)
        column = index % columns
        row = index // columns
        x = margin + column * (cell_width + gap)
        y = margin + row * (cell_height + gap) + (cell_height - resized_height) // 2
        canvas.paste(resized, (x, y))
    output = output_dir / f"{mode}.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="JPEG", quality=94, subsampling=0, optimize=True, progressive=False)
    return {
        "mode": mode,
        "path": output.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(output),
        "width": width,
        "height": height,
        "columns": columns,
        "rows": rows,
        "source_capture_count": len(images),
        "source_files": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=P18_DIR / "contact-sheets")
    args = parser.parse_args()
    missing = [
        f'{meta["slug"]}--{mode}.png'
        for mode in MODES
        for meta in CASE_META.values()
        if not (args.screenshots / f'{meta["slug"]}--{mode}.png').is_file()
    ]
    if missing:
        raise SystemExit("Missing screenshots: " + ", ".join(missing))
    manifest = json.loads((P18_DIR / "PILOT-MANIFEST.json").read_text(encoding="utf-8"))
    sheets = [build_sheet(mode, args.screenshots, args.output_dir) for mode in MODES]
    record = {
        "schema_version": "2.0",
        "phase": "P-18R2",
        "candidate_manifest_id": manifest["manifest_id"],
        "candidate_source_bundle_sha256": manifest["source_bundle_sha256"],
        "layout": "3 columns × 4 rows; artifact-frame crop; ledger/provenance excluded",
        "sheet_count": len(sheets),
        "sheets": sheets,
    }
    manifest_path = args.output_dir.parent / "CONTACT-SHEET-MANIFEST.json"
    manifest_path.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sheet_count": len(sheets), "manifest": manifest_path.relative_to(REPO_ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
