"""Bounded, inert P-07 carrier parsing and fidelity helpers.

The module uses only the Python standard library. It never fetches resources,
executes source text, evaluates formulas, renders Mermaid, installs packages,
or writes files. Carrier data becomes plain records with stable source IDs; a
separate explicit semantic mapping is required before common-IR construction.
"""

from __future__ import annotations

import base64
import binascii
import csv
import hashlib
import io
import json
import math
import re
import struct
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.0"
TEXT_LIMIT = 5 * 1024 * 1024
DRAWIO_LIMIT = 20 * 1024 * 1024
DECODED_LIMIT = 20 * 1024 * 1024
EXPANSION_LIMIT = 20
DEPTH_LIMIT = 64
PAGE_LIMIT = 50
BLOCK_LIMIT = 50
NODE_LIMIT = 1_000
EDGE_LIMIT = 2_000
ITEM_LIMIT = 5_000
LABEL_LIMIT = 4_096
NORMALIZED_TEXT_LIMIT = 2_000_000

CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
BIDI_RE = re.compile(r"[\u202a-\u202e\u2066-\u2069]")
ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]{0,127}$")
FORBIDDEN_XML_RE = re.compile(r"<!\s*(?:DOCTYPE|ENTITY)|<\s*(?:xi:include|xinclude)\b", re.I)
FORBIDDEN_MERMAID_RE = re.compile(
    r"%%\{|\bclick\b|\bcallback\b|\bhref\b|<\s*/?\s*(?:script|style|iframe|object|embed|a)\b|https?://|javascript:",
    re.I,
)


class ImportFailure(Exception):
    """Stable, user-safe P-07 import failure."""

    def __init__(self, code: str, message: str, *, field: str = "source", status: str = "invalid") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field
        self.status = status

    def issue(self) -> dict[str, str]:
        return {"code": self.code, "stage": "safe-import", "field": self.field, "message": self.message}


def _fail(code: str, message: str, *, field: str = "source", status: str = "invalid") -> None:
    raise ImportFailure(code, message, field=field, status=status)


def _bounded_bytes(value: str | bytes, *, drawio: bool = False) -> bytes:
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    limit = DRAWIO_LIMIT if drawio else TEXT_LIMIT
    if len(raw) > limit:
        _fail("source-over-limit", "Source exceeds the approved byte ceiling.")
    return raw


def _text(value: Any, *, field: str = "source", warnings: list[str] | None = None, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        _fail("text-required", "Expected inert Unicode text.", field=field)
    value = unicodedata.normalize("NFC", value)
    if len(value) > LABEL_LIMIT:
        _fail("label-over-limit", "A label exceeds the approved Unicode-scalar ceiling.", field=field)
    cleaned = CONTROL_RE.sub("", value)
    if cleaned != value and warnings is not None:
        warnings.append(f"neutralized-control:{field}")
    value = cleaned
    cleaned = BIDI_RE.sub("", value)
    if cleaned != value and warnings is not None:
        warnings.append(f"neutralized-bidi:{field}")
    value = cleaned
    if not allow_empty and not value.strip():
        _fail("blank-label", "A material label is blank and requires clarification.", field=field, status="needs-clarification")
    return value


def _source_id(carrier: str, locator: str, ordinal: int) -> str:
    digest = hashlib.sha256(f"{carrier}\0{locator}\0{ordinal}".encode("utf-8")).hexdigest()[:16]
    return f"src-{digest}"


def _record(carrier: str, locator: str, ordinal: int, content_class: str, **values: Any) -> dict[str, Any]:
    return {"id": _source_id(carrier, locator, ordinal), "source_kind": carrier, "locator": locator, "content_class": content_class, **values}


def _bundle(carrier: str, documents: list[dict[str, Any]], warnings: Iterable[str] = ()) -> dict[str, Any]:
    records = [record for document in documents for record in document["records"]]
    if len(documents) > PAGE_LIMIT or len(records) > ITEM_LIMIT:
        _fail("semantic-item-over-limit", "Decoded source exceeds the approved page or semantic-item ceiling.")
    normalized_size = sum(len(str(record.get("label", ""))) for record in records)
    if normalized_size > NORMALIZED_TEXT_LIMIT:
        _fail("normalized-text-over-limit", "Normalized source text exceeds the approved ceiling.")
    if len({record["id"] for record in records}) != len(records):
        _fail("source-id-collision", "Stable source IDs are not unique.")
    return {"schema_version": SCHEMA_VERSION, "carrier": carrier, "documents": documents, "warnings": sorted(set(warnings)), "record_count": len(records)}


def parse_natural_language(content: str) -> dict[str, Any]:
    _bounded_bytes(content)
    warnings: list[str] = []
    lines = [(index, line.strip()) for index, line in enumerate(content.splitlines(), 1) if line.strip()]
    if not lines:
        _fail("missing-input", "Natural-language source is empty.")
    records = [
        _record("natural-language", f"line:{line_no}", index, "annotation", record_type="text", label=_text(line, field=f"line:{line_no}", warnings=warnings))
        for index, (line_no, line) in enumerate(lines)
    ]
    return _bundle("natural-language", [{"id": "doc-1", "name": "Source text", "records": records}], warnings)


def _tabular_bundle(carrier: str, headers: Sequence[str], rows: Sequence[Sequence[str]], warnings: list[str]) -> dict[str, Any]:
    clean_headers = [_text(header, field=f"header:{index + 1}", warnings=warnings) for index, header in enumerate(headers)]
    if len(set(clean_headers)) != len(clean_headers):
        _fail("duplicate-header", "Table headers must be unique.", field="source.headers")
    records: list[dict[str, Any]] = []
    ordinal = 0
    for column, header in enumerate(clean_headers, 1):
        records.append(_record(carrier, f"header:{column}", ordinal, "label", record_type="header", column=column, label=header))
        ordinal += 1
    for row_number, row in enumerate(rows, 1):
        if len(row) != len(clean_headers):
            _fail("ragged-table", "Every row must have the same number of cells as the header.", field=f"source.rows[{row_number}]")
        for column, raw in enumerate(row, 1):
            value = _text(str(raw), field=f"row:{row_number}:column:{column}", warnings=warnings, allow_empty=True)
            formula_literal = bool(value) and value[0] in "=+-@"
            records.append(_record(carrier, f"row:{row_number}:column:{column}", ordinal, "value", record_type="cell", row=row_number, column=column, header=clean_headers[column - 1], label=value, formula_literal=formula_literal))
            ordinal += 1
    return _bundle(carrier, [{"id": "table-1", "name": "Table", "headers": clean_headers, "row_count": len(rows), "records": records}], warnings)


def parse_pasted_table(content: str) -> dict[str, Any]:
    _bounded_bytes(content)
    warnings: list[str] = []
    lines = [line for line in content.splitlines() if line.strip()]
    if len(lines) < 2:
        _fail("table-shape-invalid", "A pasted table needs a header and at least one data row.")
    if "\t" in lines[0]:
        rows = [line.split("\t") for line in lines]
    elif "|" in lines[0]:
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
        if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
            rows.pop(1)
    else:
        _fail("table-delimiter-ambiguous", "Use tab-separated or Markdown-pipe table input.", status="needs-clarification")
    return _tabular_bundle("pasted-table", rows[0], rows[1:], warnings)


def parse_csv_text(content: str, *, delimiter: str | None = None) -> dict[str, Any]:
    _bounded_bytes(content)
    warnings: list[str] = []
    if delimiter is None:
        first_line = content.splitlines()[0] if content.splitlines() else ""
        candidates = [candidate for candidate in (",", "\t", ";") if candidate in first_line]
        if len(candidates) != 1:
            _fail("csv-dialect-ambiguous", "CSV delimiter is ambiguous; provide an explicit delimiter.", status="needs-clarification")
        delimiter = candidates[0]
    if delimiter not in {",", "\t", ";"}:
        _fail("csv-delimiter-unsupported", "Only comma, tab, or semicolon delimiters are supported.")
    try:
        rows = list(csv.reader(io.StringIO(content), delimiter=delimiter, strict=True))
    except csv.Error as error:
        _fail("csv-malformed", f"CSV is malformed: {error}.")
    if len(rows) < 2:
        _fail("table-shape-invalid", "CSV needs a header and at least one data row.")
    return _tabular_bundle("csv", rows[0], rows[1:], warnings)


def _reject_constant(token: str) -> None:
    _fail("json-nonfinite", f"Non-finite JSON token is unsupported: {token}.")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("json-duplicate-key", "Duplicate JSON keys are rejected because they can change semantics.")
        result[key] = value
    return result


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > DEPTH_LIMIT:
        _fail("json-depth-over-limit", "JSON nesting exceeds the approved ceiling.")
    if isinstance(value, Mapping):
        return max([depth] + [_json_depth(item, depth + 1) for item in value.values()])
    if isinstance(value, list):
        return max([depth] + [_json_depth(item, depth + 1) for item in value])
    return depth


def parse_json_text(content: str) -> dict[str, Any]:
    _bounded_bytes(content)
    warnings: list[str] = []
    try:
        value = json.loads(content, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except ImportFailure:
        raise
    except (json.JSONDecodeError, TypeError) as error:
        _fail("json-malformed", f"JSON is malformed at a bounded parser location: {getattr(error, 'pos', 0)}.")
    _json_depth(value)
    records: list[dict[str, Any]] = []

    def walk(item: Any, pointer: str = "", ordinal: list[int] = [0]) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                clean_key = _text(str(key), field=f"json-key:{pointer}", warnings=warnings)
                escaped = clean_key.replace("~", "~0").replace("/", "~1")
                walk(child, f"{pointer}/{escaped}", ordinal)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{pointer}/{index}", ordinal)
        else:
            if isinstance(item, float) and not math.isfinite(item):
                _fail("json-nonfinite", "Non-finite numeric values are unsupported.")
            label = _text("null" if item is None else str(item), field=f"json:{pointer}", warnings=warnings, allow_empty=True)
            records.append(_record("json", pointer or "/", ordinal[0], "value", record_type="json-value", value=item, label=label))
            ordinal[0] += 1

    walk(value)
    document: dict[str, Any] = {"id": "json-1", "name": "JSON", "root_type": type(value).__name__, "records": records}
    if isinstance(value, list) and value and all(isinstance(item, Mapping) for item in value):
        headers = list(value[0])
        if all(list(item) == headers for item in value):
            document["table"] = {
                "headers": [_text(str(header), field="json.table.header", warnings=warnings) for header in headers],
                "rows": [[item[header] for header in headers] for item in value],
            }
    return _bundle("json", [document], warnings)


def tabular_matrix(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Return one carrier-neutral table without interpreting any cell."""

    documents = bundle.get("documents")
    if not isinstance(documents, list) or len(documents) != 1:
        _fail("tabular-document-invalid", "Exactly one tabular document is required.")
    document = documents[0]
    if bundle.get("carrier") in {"pasted-table", "csv"}:
        headers = document.get("headers", [])
        row_count = document.get("row_count", 0)
        cells = [record for record in document.get("records", []) if record.get("record_type") == "cell"]
        rows = [[next(record["label"] for record in cells if record["row"] == row and record["column"] == column) for column in range(1, len(headers) + 1)] for row in range(1, row_count + 1)]
        return {"headers": list(headers), "rows": rows}
    if bundle.get("carrier") == "json" and isinstance(document.get("table"), Mapping):
        return {"headers": list(document["table"]["headers"]), "rows": [list(row) for row in document["table"]["rows"]]}
    _fail("tabular-shape-unsupported", "JSON must be a non-empty array of objects with identical ordered keys.")


def _clean_semantic_id(value: str, field: str) -> str:
    if not ID_RE.fullmatch(value):
        _fail("semantic-id-invalid", "Diagram identifiers must use the supported inert identifier subset.", field=field)
    return value


def _mermaid_node(token: str) -> tuple[str, str, str]:
    token = token.strip()
    patterns = (
        (r"^([A-Za-z_][\w.:-]*)\[([^\[\]]+)\]$", "item"),
        (r"^([A-Za-z_][\w.:-]*)\{([^{}]+)\}$", "decision"),
        (r"^([A-Za-z_][\w.:-]*)\(\(([^()]+)\)\)$", "terminal"),
        (r"^([A-Za-z_][\w.:-]*)\(([^()]+)\)$", "state"),
        (r"^([A-Za-z_][\w.:-]*)$", "item"),
    )
    for pattern, role in patterns:
        match = re.fullmatch(pattern, token)
        if match:
            semantic_id = _clean_semantic_id(match.group(1), "mermaid.node")
            label = match.group(2) if match.lastindex and match.lastindex > 1 else semantic_id
            return semantic_id, label, role
    _fail("mermaid-node-unsupported", "Node syntax is outside the approved Mermaid subset.")


def _parse_mermaid_block(text: str, block_index: int) -> dict[str, Any]:
    if FORBIDDEN_MERMAID_RE.search(text):
        _fail("mermaid-executable-feature", "Mermaid directives, HTML, actions, callbacks, links, and remote resources are rejected.")
    lines = [(number, line.strip()) for number, line in enumerate(text.splitlines(), 1) if line.strip() and not line.strip().startswith("%%")]
    if not lines:
        _fail("mermaid-empty", "Mermaid block is empty.")
    header = lines.pop(0)[1]
    if re.fullmatch(r"(?:flowchart|graph)\s+(?:TD|TB|BT|LR|RL)", header, re.I):
        kind = "flowchart"
    elif header == "sequenceDiagram":
        kind = "sequence"
    elif header in {"stateDiagram-v2", "stateDiagram"}:
        kind = "state-machine"
    elif header == "erDiagram":
        kind = "er-data-model"
    else:
        _fail("mermaid-kind-unsupported", "Only flowchart/graph, sequenceDiagram, stateDiagram-v2, and erDiagram are supported.")

    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    known_nodes: set[str] = set()
    ordinal = 0

    def add_node(semantic_id: str, label: str, role: str, locator: str) -> None:
        nonlocal ordinal
        if semantic_id in known_nodes:
            return
        known_nodes.add(semantic_id)
        records.append(_record("mermaid", locator, ordinal, "entity", record_type="node", semantic_id=semantic_id, suggested_role=role, label=_text(label, field=locator, warnings=warnings)))
        ordinal += 1

    def add_edge(source: str, target: str, label: str, kind_name: str, locator: str) -> None:
        nonlocal ordinal
        records.append(_record("mermaid", locator, ordinal, "relation", record_type="edge", source_semantic_id=source, target_semantic_id=target, suggested_kind=kind_name, label=_text(label, field=locator, warnings=warnings, allow_empty=True)))
        ordinal += 1

    if kind == "flowchart":
        edge_re = re.compile(r"^(.+?)\s*(-->|---|-.->|==>)\s*(?:\|([^|]*)\|\s*)?(.+?)\s*$")
        for line_no, line in lines:
            locator = f"block:{block_index}:line:{line_no}"
            match = edge_re.fullmatch(line)
            if match:
                source, source_label, source_role = _mermaid_node(match.group(1))
                target, target_label, target_role = _mermaid_node(match.group(4))
                add_node(source, source_label, source_role, locator + ":source")
                add_node(target, target_label, target_role, locator + ":target")
                add_edge(source, target, match.group(3) or "", "flow" if match.group(2) != "---" else "association", locator + ":edge")
            else:
                semantic_id, label, role = _mermaid_node(line)
                add_node(semantic_id, label, role, locator)
    elif kind == "sequence":
        participant_re = re.compile(r"^(?:participant|actor)\s+([A-Za-z_][\w.:-]*)(?:\s+as\s+(.+))?$")
        message_re = re.compile(r"^([A-Za-z_][\w.:-]*)\s*(--?>>|->>|-->|->)\s*([A-Za-z_][\w.:-]*)\s*:\s*(.+)$")
        for line_no, line in lines:
            locator = f"block:{block_index}:line:{line_no}"
            participant = participant_re.fullmatch(line)
            message = message_re.fullmatch(line)
            if participant:
                add_node(participant.group(1), participant.group(2) or participant.group(1), "participant", locator)
            elif message:
                add_node(message.group(1), message.group(1), "participant", locator + ":source")
                add_node(message.group(3), message.group(3), "participant", locator + ":target")
                add_edge(message.group(1), message.group(3), message.group(4), "message", locator + ":message")
            else:
                _fail("mermaid-sequence-unsupported", "Sequence line is outside the approved participant/message subset.", field=locator)
    elif kind == "state-machine":
        state_re = re.compile(r'^state\s+"([^"]+)"\s+as\s+([A-Za-z_][\w.:-]*)$')
        transition_re = re.compile(r"^(\[\*\]|[A-Za-z_][\w.:-]*)\s*-->\s*(\[\*\]|[A-Za-z_][\w.:-]*)(?:\s*:\s*(.+))?$")
        for line_no, line in lines:
            locator = f"block:{block_index}:line:{line_no}"
            state = state_re.fullmatch(line)
            transition = transition_re.fullmatch(line)
            if state:
                add_node(state.group(2), state.group(1), "state", locator)
            elif transition:
                source = "state-initial" if transition.group(1) == "[*]" else transition.group(1)
                target = "state-terminal" if transition.group(2) == "[*]" else transition.group(2)
                add_node(source, "Bắt đầu" if source == "state-initial" else source, "initial" if source == "state-initial" else "state", locator + ":source")
                add_node(target, "Kết thúc" if target == "state-terminal" else target, "terminal" if target == "state-terminal" else "state", locator + ":target")
                add_edge(source, target, transition.group(3) or "", "transition", locator + ":transition")
            else:
                _fail("mermaid-state-unsupported", "State line is outside the approved state/transition subset.", field=locator)
    else:
        relation_re = re.compile(r"^([A-Za-z_][\w.:-]*)\s+([|o}{.]+)--([|o}{.]+)\s+([A-Za-z_][\w.:-]*)\s*:\s*(.+)$")
        for line_no, line in lines:
            locator = f"block:{block_index}:line:{line_no}"
            relation = relation_re.fullmatch(line)
            if not relation:
                _fail("mermaid-er-unsupported", "ER line is outside the approved relationship subset.", field=locator)
            add_node(relation.group(1), relation.group(1), "entity", locator + ":source")
            add_node(relation.group(4), relation.group(4), "entity", locator + ":target")
            add_edge(relation.group(1), relation.group(4), relation.group(5), f"{relation.group(2)}--{relation.group(3)}", locator + ":relation")
    if len(known_nodes) > NODE_LIMIT or len([r for r in records if r["record_type"] == "edge"]) > EDGE_LIMIT:
        _fail("graph-over-limit", "Mermaid graph exceeds the approved node or edge ceiling.")
    return {"id": f"block-{block_index}", "name": f"Mermaid {kind}", "diagram_kind": kind, "records": records, "warnings": warnings}


def parse_mermaid_text(content: str, *, block_selection: Sequence[int] | str | None = None) -> dict[str, Any]:
    _bounded_bytes(content)
    fences = re.findall(r"```mermaid\s*\n(.*?)```", content, re.I | re.S)
    blocks = fences if fences else [content]
    if len(blocks) > BLOCK_LIMIT:
        _fail("mermaid-block-over-limit", "Mermaid block count exceeds the approved ceiling.")
    if len(blocks) > 1 and block_selection is None:
        _fail("mermaid-selection-required", "Multiple Mermaid blocks require explicit block_selection.", status="needs-clarification")
    selected = _select_indices(len(blocks), block_selection, "block_selection")
    documents = [_parse_mermaid_block(blocks[index - 1], index) for index in selected]
    warnings = [warning for document in documents for warning in document.pop("warnings", [])]
    return _bundle("mermaid", documents, warnings)


def _select_indices(count: int, selection: Sequence[int] | str | None, field: str) -> list[int]:
    if selection in (None, "all"):
        return list(range(1, count + 1))
    if not isinstance(selection, Sequence) or isinstance(selection, (str, bytes)):
        _fail("selection-invalid", "Selection must be 'all' or unique one-based integers.", field=field)
    values = list(selection)
    if not values or len(values) != len(set(values)) or any(isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > count for value in values):
        _fail("selection-invalid", "Selection must contain unique existing one-based indices.", field=field)
    return values


def _safe_xml(raw: bytes) -> ET.Element:
    if len(raw) > DECODED_LIMIT:
        _fail("decoded-over-limit", "Decoded XML exceeds the approved ceiling.")
    prefix = raw[: min(len(raw), 131_072)].decode("utf-8", "ignore")
    if FORBIDDEN_XML_RE.search(prefix):
        _fail("xml-external-feature", "DTD, entities, XInclude, and external XML features are rejected.")
    try:
        return ET.fromstring(raw)
    except ET.ParseError as error:
        _fail("xml-malformed", f"XML is malformed at a bounded parser location: {error.position}.")


def _bounded_decompress(raw: bytes, *, wbits: int = zlib.MAX_WBITS) -> bytes:
    decompressor = zlib.decompressobj(wbits)
    output = decompressor.decompress(raw, DECODED_LIMIT + 1)
    output += decompressor.flush(DECODED_LIMIT + 1 - len(output))
    if len(output) > DECODED_LIMIT or (len(raw) and len(output) > len(raw) * EXPANSION_LIMIT):
        _fail("decompression-over-limit", "Compressed model exceeds size or expansion-ratio ceilings.")
    return output


def _decode_diagram_text(text: str) -> bytes:
    direct = urllib.parse.unquote(text).encode("utf-8")
    if direct.lstrip().startswith(b"<"):
        return direct
    try:
        compressed = base64.b64decode(text, validate=True)
        decoded = _bounded_decompress(compressed, wbits=-15)
        return urllib.parse.unquote_to_bytes(decoded.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, zlib.error, ValueError):
        _fail("drawio-model-corrupt", "Embedded draw.io model is missing or corrupt.")


def _drawio_pages(root: ET.Element) -> list[tuple[str, str, ET.Element]]:
    tag = root.tag.rsplit("}", 1)[-1]
    if tag == "mxGraphModel":
        return [("page-1", "Page 1", root)]
    if tag != "mxfile":
        _fail("drawio-root-unsupported", "Expected mxfile or mxGraphModel root.")
    pages: list[tuple[str, str, ET.Element]] = []
    for index, diagram in enumerate([child for child in root if child.tag.rsplit("}", 1)[-1] == "diagram"], 1):
        page_id = diagram.attrib.get("id") or f"page-{index}"
        name = diagram.attrib.get("name") or f"Page {index}"
        nested = next((child for child in diagram if child.tag.rsplit("}", 1)[-1] == "mxGraphModel"), None)
        model = nested if nested is not None else _safe_xml(_decode_diagram_text(diagram.text or ""))
        pages.append((page_id, name, model))
    if not pages:
        _fail("drawio-page-missing", "draw.io document contains no page model.")
    if len(pages) > PAGE_LIMIT:
        _fail("drawio-page-over-limit", "draw.io page count exceeds the approved ceiling.")
    return pages


def _drawio_records(page_id: str, model: ET.Element, warnings: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    ordinal = 0
    cells = [element for element in model.iter() if element.tag.rsplit("}", 1)[-1] == "mxCell"]
    for cell in cells:
        if any(key.lower() in {"link", "href", "url", "onclick", "onload"} for key in cell.attrib):
            warnings.append(f"discarded-executable-attribute:{page_id}:{cell.attrib.get('id', '?')}")
        if cell.attrib.get("style"):
            warnings.append(f"discarded-style:{page_id}:{cell.attrib.get('id', '?')}")
        semantic_id = cell.attrib.get("id")
        if not semantic_id or semantic_id in {"0", "1"}:
            continue
        _clean_semantic_id(semantic_id, "drawio.cell.id")
        locator = f"page:{page_id}:cell:{semantic_id}"
        if cell.attrib.get("vertex") == "1":
            label = _text(cell.attrib.get("value", semantic_id), field=locator, warnings=warnings)
            records.append(_record("drawio", locator, ordinal, "entity", record_type="node", semantic_id=semantic_id, suggested_role="item", parent_semantic_id=cell.attrib.get("parent"), label=label))
            ordinal += 1
        elif cell.attrib.get("edge") == "1":
            source = cell.attrib.get("source")
            target = cell.attrib.get("target")
            if not source or not target:
                records.append(_record("drawio", locator, ordinal, "source-rot", record_type="source-rot", label="Unconnected draw.io edge", reason="missing endpoint"))
                ordinal += 1
                continue
            label = _text(cell.attrib.get("value", ""), field=locator, warnings=warnings, allow_empty=True)
            records.append(_record("drawio", locator, ordinal, "relation", record_type="edge", source_semantic_id=source, target_semantic_id=target, suggested_kind="relation", label=label))
            ordinal += 1
    nodes = {record["semantic_id"] for record in records if record["record_type"] == "node"}
    for record in records:
        if record["record_type"] == "edge" and (record["source_semantic_id"] not in nodes or record["target_semantic_id"] not in nodes):
            record["record_type"] = "source-rot"
            record["content_class"] = "source-rot"
            record["reason"] = "dangling endpoint"
    if len(nodes) > NODE_LIMIT or len([record for record in records if record["record_type"] == "edge"]) > EDGE_LIMIT:
        _fail("graph-over-limit", "draw.io model exceeds the approved node or edge ceiling.")
    return records


def _png_embedded_model(raw: bytes) -> bytes:
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        _fail("drawio-png-invalid", "PNG signature is invalid.")
    offset = 8
    candidates: list[bytes] = []
    while offset + 12 <= len(raw):
        length = struct.unpack(">I", raw[offset:offset + 4])[0]
        chunk_type = raw[offset + 4:offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if length > DECODED_LIMIT or data_end + 4 > len(raw):
            _fail("drawio-png-corrupt", "PNG chunk is corrupt or over the approved ceiling.")
        data = raw[data_start:data_end]
        if chunk_type == b"tEXt" and b"\x00" in data:
            key, value = data.split(b"\x00", 1)
            if key.lower() in {b"mxfile", b"mxgraphmodel", b"content"}:
                candidates.append(value)
        elif chunk_type == b"zTXt" and b"\x00" in data:
            key, remainder = data.split(b"\x00", 1)
            if key.lower() in {b"mxfile", b"mxgraphmodel", b"content"} and len(remainder) > 1:
                candidates.append(_bounded_decompress(remainder[1:]))
        if chunk_type == b"IEND":
            break
        offset = data_end + 4
    if not candidates:
        _fail("drawio-model-missing", "PNG contains no supported embedded draw.io model.")
    return _decode_diagram_text(candidates[0].decode("utf-8", "strict"))


def parse_drawio(value: str | bytes, *, carrier: str = "xml", page_selection: Sequence[int] | str | None = None) -> dict[str, Any]:
    raw = _bounded_bytes(value, drawio=True)
    if carrier == "png":
        raw = _png_embedded_model(raw)
    elif carrier == "svg":
        svg_root = _safe_xml(raw)
        if svg_root.tag.rsplit("}", 1)[-1] != "svg":
            _fail("drawio-svg-invalid", "Expected an SVG root.")
        embedded = svg_root.attrib.get("content") or svg_root.attrib.get("data-mxgraph")
        if not embedded:
            _fail("drawio-model-missing", "SVG contains no supported embedded draw.io model.")
        raw = _decode_diagram_text(embedded)
    elif carrier != "xml":
        _fail("drawio-carrier-unsupported", "Supported draw.io carriers are xml, png, and svg.")
    root = _safe_xml(raw)
    pages = _drawio_pages(root)
    selected = _select_indices(len(pages), page_selection, "page_selection")
    warnings: list[str] = []
    documents = [
        {"id": pages[index - 1][0], "name": _text(pages[index - 1][1], warnings=warnings), "records": _drawio_records(pages[index - 1][0], pages[index - 1][2], warnings)}
        for index in selected
    ]
    return _bundle("drawio", documents, warnings)


def source_records(bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(record) for document in bundle.get("documents", []) for record in document.get("records", [])]


def reconcile_fidelity(bundle: Mapping[str, Any], fidelity: Mapping[str, Any]) -> dict[str, Any]:
    source_ids = {record["id"] for record in source_records(bundle)}
    seen: set[str] = set()
    for disposition in ("kept", "merged", "dropped", "source_rot"):
        entries = fidelity.get(disposition, [])
        if not isinstance(entries, list):
            _fail("fidelity-shape-invalid", "Every fidelity disposition must be an array.", field=f"fidelity.{disposition}")
        for entry in entries:
            ids = entry.get("source_ids", [])
            if not ids or any(source_id not in source_ids or source_id in seen for source_id in ids):
                _fail("fidelity-reconciliation-failed", "Every source ID must appear exactly once across fidelity dispositions.", field=f"fidelity.{disposition}")
            seen.update(ids)
    if seen != source_ids or fidelity.get("invented_count") != 0:
        _fail("fidelity-reconciliation-failed", "Source = kept + merged + dropped + source rot and invented_count must equal zero.", field="fidelity")
    return {"source_count": len(source_ids), "reconciled": True, "invented_count": 0}


def explicit_parsed_model(
    bundle: Mapping[str, Any],
    *,
    title: str,
    route_candidates: Sequence[Mapping[str, Any]],
    nodes: Sequence[Mapping[str, Any]] = (),
    edges: Sequence[Mapping[str, Any]] = (),
    groups: Sequence[Mapping[str, Any]] = (),
    lanes: Sequence[Mapping[str, Any]] = (),
    series: Sequence[Mapping[str, Any]] = (),
    axes: Sequence[Mapping[str, Any]] = (),
    annotations: Sequence[Mapping[str, Any]] = (),
    dropped: Sequence[Mapping[str, Any]] = (),
    source_rot: Sequence[Mapping[str, Any]] = (),
    variant_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Create a parsed-model envelope from an explicit, reviewable mapping.

    The caller must provide source_refs on every material element. This function
    does not infer roles, relationships, values, or diagram type from appearance.
    """

    collections = {"nodes": nodes, "edges": edges, "groups": groups, "lanes": lanes, "series": series, "axes": axes, "annotations": annotations}
    known = {record["id"] for record in source_records(bundle)}
    used: dict[str, list[str]] = {}
    item_refs: dict[str, list[str]] = {}
    copied: dict[str, list[dict[str, Any]]] = {}
    reading_order: list[str] = []
    for collection, values in collections.items():
        copied[collection] = []
        for raw in values:
            item = dict(raw)
            refs = item.get("source_refs")
            if not isinstance(refs, list) or not refs or any(ref not in known for ref in refs):
                _fail("explicit-source-ref-invalid", "Every semantic element needs valid explicit source_refs.", field=f"{collection}.source_refs")
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                _fail("explicit-id-invalid", "Every semantic element needs a stable internal ID.", field=f"{collection}.id")
            for ref in refs:
                used.setdefault(ref, []).append(item_id)
            item_refs[item_id] = list(refs)
            reading_order.append(item_id)
            copied[collection].append(item)
    dropped_entries = [dict(entry) for entry in dropped]
    rot_entries = [dict(entry) for entry in source_rot]
    disposed = {source_id for entry in dropped_entries + rot_entries for source_id in entry.get("source_ids", [])}
    overlap = disposed & set(used)
    if overlap:
        _fail("fidelity-duplicate-disposition", "A source item cannot be both rendered and dropped/source rot.")
    merged_sources = {source_id for refs in item_refs.values() if len(refs) > 1 for source_id in refs}
    if any(len(used[source_id]) > 1 for source_id in merged_sources):
        _fail("fidelity-merge-ambiguous", "A source item in an explicit merge cannot also map to another semantic element.")
    kept = [{"source_ids": [source_id], "ir_ids": ids, "reason": "Explicit source-backed semantic mapping."} for source_id, ids in used.items() if source_id not in merged_sources]
    merged = [{"source_ids": refs, "ir_ids": [item_id], "reason": "Explicitly equivalent source items merged into one semantic element."} for item_id, refs in item_refs.items() if len(refs) > 1]
    fidelity = {"kept": kept, "merged": merged, "dropped": dropped_entries, "source_rot": rot_entries, "invented_count": 0}
    reconcile_fidelity(bundle, fidelity)
    source_items = [{key: record[key] for key in ("id", "source_kind", "locator", "content_class")} for record in source_records(bundle)]
    return {
        "title": _text(title),
        "route_candidates": [dict(candidate) for candidate in route_candidates],
        "variant_ids": list(variant_ids),
        **copied,
        "source_items": source_items,
        "fidelity": fidelity,
        "accessibility": {"name": _text(title), "description": "Source-backed diagram.", "reading_order": reading_order, "data_representation_required": bool(copied["series"])},
    }


def validate_workspace_target(target: str | Path, workspace_root: str | Path) -> Path:
    root = Path(workspace_root).resolve()
    candidate = Path(target)
    if candidate.is_absolute():
        _fail("absolute-target-rejected", "Absolute output targets are not accepted from source data.", field="target")
    resolved = (root / candidate).resolve()
    if resolved == root or root not in resolved.parents:
        _fail("path-traversal-rejected", "Output target escapes the approved workspace.", field="target")
    return resolved


def parse_source(kind: str, content: str | bytes, **options: Any) -> dict[str, Any]:
    if kind == "natural-language":
        return parse_natural_language(str(content))
    if kind == "pasted-table":
        return parse_pasted_table(str(content))
    if kind == "csv":
        return parse_csv_text(str(content), delimiter=options.get("delimiter"))
    if kind == "json":
        return parse_json_text(str(content))
    if kind == "mermaid":
        return parse_mermaid_text(str(content), block_selection=options.get("block_selection"))
    if kind == "drawio":
        return parse_drawio(content, carrier=options.get("carrier", "xml"), page_selection=options.get("page_selection"))
    _fail("carrier-unsupported", "Source kind is outside the approved P-07 carrier set.", field="source.kind")


__all__ = [
    "ImportFailure",
    "explicit_parsed_model",
    "parse_csv_text",
    "parse_drawio",
    "parse_json_text",
    "parse_mermaid_text",
    "parse_natural_language",
    "parse_pasted_table",
    "parse_source",
    "reconcile_fidelity",
    "source_records",
    "tabular_matrix",
    "validate_workspace_target",
]
