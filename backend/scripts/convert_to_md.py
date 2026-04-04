#!/usr/bin/env python3
# pyright: reportAny=false, reportExplicitAny=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false, reportUnknownParameterType=false
"""Convert legal JSON records into Markdown with YAML frontmatter.

Supports two record types:
- laws: frontmatter + article sections
- precedents: frontmatter + full text body

Usage:
    python backend/scripts/convert_to_md.py --input data/raw/laws/sample.json
    python backend/scripts/convert_to_md.py --input data/raw/precedents/sample.json
    python backend/scripts/convert_to_md.py --input data/raw/laws
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LAW_FIELDS = [
    "id",
    "name",
    "type",
    "department",
    "date_promulgated",
    "date_enforced",
    "articles_count",
]

PRECEDENT_FIELDS = [
    "id",
    "case_name",
    "case_number",
    "court",
    "date_judgment",
    "judgment_type",
    "holding",
    "summary",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_scalar(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)

    text = str(value)
    if "\n" in text:
        indented = "\n".join(f"  {line}" for line in text.splitlines())
        return f"|-\n{indented}"

    if text == "" or any(ch in text for ch in [":", "#", "{", "}", "[", "]", "&", "*", "?", "|", "<", ">", "=", "!", "%", "@", "`", "\n"]):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def make_frontmatter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {dump_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def detect_kind(input_path: Path, record: dict[str, Any]) -> str:
    path_text = str(input_path).lower()
    if "/laws/" in path_text or {"articles", "name", "department"}.issubset(record.keys()):
        return "law"
    if "/precedents/" in path_text or {"case_name", "holding", "summary"}.issubset(record.keys()):
        return "precedent"
    raise ValueError(f"Unable to detect record kind for {input_path}")


def render_law_markdown(record: dict[str, Any]) -> str:
    frontmatter = make_frontmatter({field: record.get(field, "") for field in LAW_FIELDS})
    body_lines = []
    articles = record.get("articles", []) or []
    for article in articles:
        number = article.get("number", "")
        title = article.get("title", "")
        heading = f"## 제{number}조 {title}".strip()
        body_lines.append(heading)
        text = article.get("text", "")
        if text:
            body_lines.append(text)
        for clause in article.get("clauses", []) or []:
            body_lines.append(f"- {clause}")
        body_lines.append("")
    if not body_lines:
        body_lines.append("_No articles provided._")
    return frontmatter + "\n\n" + "\n".join(body_lines).rstrip() + "\n"


def render_precedent_markdown(record: dict[str, Any]) -> str:
    frontmatter = make_frontmatter({field: record.get(field, "") for field in PRECEDENT_FIELDS})
    full_text = record.get("full_text", "")
    body = full_text if full_text else "_No full text provided._"
    return frontmatter + "\n\n" + body.rstrip() + "\n"


def output_name(record: dict[str, Any], input_path: Path) -> str:
    base = record.get("id") or input_path.stem
    return f"{base}.md"


def output_dir_for(kind: str, repo_root: Path) -> Path:
    return repo_root / "data" / ("laws" if kind == "law" else "precedents")


def convert_file(input_path: Path, repo_root: Path) -> Path:
    record = load_json(input_path)
    if not isinstance(record, dict):
        raise ValueError(f"Expected a JSON object in {input_path}")

    kind = detect_kind(input_path, record)
    output_dir = output_dir_for(kind, repo_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown = render_law_markdown(record) if kind == "law" else render_precedent_markdown(record)
    output_path = output_dir / output_name(record, input_path)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def iter_input_files(input_path: Path):
    if input_path.is_dir():
        yield from sorted(input_path.rglob("*.json"))
    else:
        yield input_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert law/precedent JSON into Markdown")
    parser.add_argument("--input", required=True, help="JSON file or directory to convert")
    args = parser.parse_args()

    script_root = Path(__file__).resolve().parents[2]
    input_path = (script_root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)

    if not input_path.exists():
        raise SystemExit(f"Input path does not exist: {input_path}")

    written = []
    for file_path in iter_input_files(input_path):
        if file_path.suffix.lower() != ".json":
            continue
        written.append(convert_file(file_path, script_root))

    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
