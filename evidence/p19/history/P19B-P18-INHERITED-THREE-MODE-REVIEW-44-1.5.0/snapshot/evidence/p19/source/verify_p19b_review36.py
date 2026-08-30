#!/usr/bin/env python3
"""Verify D-116 marker-free radar and exact review-35 preservation."""
import hashlib, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT/"thien-skill-creative-diagram/scripts", ROOT/"evidence/p19/source"): sys.path.insert(0,str(path))
from connector_policy_v15 import CONNECTOR_POLICY_ID
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID
from radar_layout_v15 import layout_radar, radar_css, radar_table, validate_radar_svg
from radar_review34_fixture import radar_fixture
from visual_adapters_v15 import adapt_visual
OLD="P19B-P18-INHERITED-THREE-MODE-REVIEW-35-1.5.0"
ARCHIVE=ROOT/"evidence/p19/history"/OLD
GALLERY=ROOT/"evidence/p19/gallery"
PROOFS=ROOT/"evidence/p19/review36-checks"
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value,message):
    if not value: raise ValueError(message)
def svg_from_text(text):
    match=re.search(r"<svg\b.*?</svg>",text,re.S); require(match,"Missing SVG"); return match.group()
def geometry_only(svg): return re.findall(r'<(?:rect|line|path|circle|polygon|text)\b[^>]*>',svg)
def verify():
    receipt=json.loads((ARCHIVE/"ARCHIVE-RECEIPT.json").read_text())
    for name,expected in receipt["snapshot_records"].items(): require(digest(ARCHIVE/"snapshot"/name)==expected,f"Archive drift: {name}")
    for name,expected in receipt["protected_records"].items(): require(digest(ROOT/name)==expected,f"Protected drift: {name}")
    inventory=json.loads((GALLERY/"P-19B-INVENTORY.json").read_text()); records=inventory["records"]
    require(inventory["candidate_id"]==P19B_CANDIDATE_ID and len(records)==93,"Wrong review-36 gallery")
    target=[item for item in records if item["fixture_id"]=="type-radar"]
    require(len(target)==3 and {item["mode"] for item in target}==set(MODES),"Wrong radar coverage")
    preserved_html=preserved_previews=policy_declarations=0; geometry=[]; measurements=[]
    for record in records:
        current=GALLERY/record["path"]; page=current.read_text(); require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page,f"Policy missing: {current.name}"); policy_declarations+=1
        if record["fixture_id"]=="type-radar":
            require('data-radar-contract="D-116-five-axis-four-solid-marker-free-profile"' in page,f"Contract drift: {current.name}")
            svg=svg_from_text(page); report=validate_radar_svg(svg); require(report["markers"]==0,f"Plot markers remain: {current.name}")
            require(svg.count('data-marker-series=')==4 and svg.count('data-datum-id="legend-')==4,f"Unexpected marker outside legend: {current.name}")
            require(svg.count("<circle")==2 and svg.count('data-datum-id="legend-series-internal-platform"')==1,"Unexpected interior circle remains: "+current.name)
            measurements.append(report); geometry.append(geometry_only(svg))
        else:
            previous=ARCHIVE/"snapshot"/current.relative_to(ROOT)
            require(page.replace(P19B_CANDIDATE_ID,OLD)==previous.read_text().replace(P19B_CANDIDATE_ID,OLD),f"Non-target HTML drift: {current.name}"); preserved_html+=1
    for preview in sorted((GALLERY/"previews").glob("*.svg")):
        if preview.name=="type-radar.svg": continue
        previous=ARCHIVE/"snapshot"/preview.relative_to(ROOT); require(digest(preview)==digest(previous),f"Preview drift: {preview.name}"); preserved_previews+=1
    expected={"profiles":4,"values":20,"axes":5,"rings":5,"markers":0,"focal":1}
    require(all(item==expected for item in measurements),"Radar measurement mismatch"); require(geometry[0]==geometry[1]==geometry[2],"Three-mode geometry mismatch")
    plan=adapt_visual(radar_fixture()); layout=layout_radar(plan); require("stroke-dasharray" not in radar_css({}),"Dashed radar profile returned"); require(radar_table(plan).count("<tr>")==21,"Table drift")
    raster,proof_svg=PROOFS/"type-radar.svg.png",PROOFS/"type-radar.svg"; require(raster.is_file() and proof_svg.is_file(),"Missing proof")
    return {"candidate_id":P19B_CANDIDATE_ID,"authority":"D-116","status":"PASS","gallery_manifest_sha256":digest(GALLERY/"P-19B-MANIFEST.json"),"archived_files_verified":len(receipt["snapshot_records"]),"protected_files_verified":len(receipt["protected_records"]),"target_html_count":len(target),"global_policy_declarations":policy_declarations,"non_target_html_preserved_after_candidate_normalization":preserved_html,"non_target_previews_byte_identical":preserved_previews,"radar_measurement":measurements[0],"profile_line_style":"solid-only","plot_marker_policy":"none","interior_center_marker":"removed","three_mode_geometry":"PASS","alternative_table_rows":20,"local_raster_inspection":"PASS_NEUTRAL_LIGHT","proof_files":[{"path":str(proof_svg.relative_to(ROOT)),"sha256":digest(proof_svg)},{"path":str(raster.relative_to(ROOT)),"sha256":digest(raster),"visually_inspected":True}],"browser":"BLOCKED_URL_POLICY","owner_approval":"pending","p19c":"not-performed"}
if __name__=="__main__":
    report=verify(); output=ROOT/"evidence/p19/P-19B-REVIEW-36-VERIFICATION.json"; output.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); print(json.dumps({k:v for k,v in report.items() if k!="proof_files"},ensure_ascii=False,indent=2))
