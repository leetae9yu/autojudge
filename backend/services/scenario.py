# pyright: reportMissingImports=false, reportMissingTypeStubs=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field

from config import settings
from models.case import Case


DISCLAIMER = "본 서비스는 법률 자문을 제공하지 않습니다. 생성된 시나리오는 참고용이며, 실제 법적 결정은 반드시 변호사와 상담하십시오."
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class ScenarioItem(BaseModel):
    title: str
    interpretation: str
    basis: list[str] = Field(default_factory=list)
    probability: Literal["high", "medium", "low"]
    key_factors: list[str] = Field(default_factory=list)
    disclaimer: str = DISCLAIMER


class ScenarioGenerationRequest(BaseModel):
    case_id: str
    count: int = Field(default=3, ge=1, le=5)


class ScenarioGenerationResult(BaseModel):
    id: str
    case_id: str
    disclaimer: str = DISCLAIMER
    scenarios: list[ScenarioItem]


class ScenarioLLMResponse(BaseModel):
    scenarios: list[ScenarioItem]


@dataclass(slots=True)
class ReferenceDocument:
    source_type: str
    identifier: str
    title: str
    summary: str
    body: str

    @property
    def citation(self) -> str:
        return f"[{self.source_type}] {self.identifier} - {self.title}"


def generate_scenarios(case: Case, count: int = 3) -> list[ScenarioItem]:
    references = _load_reference_documents(case)
    client = _build_client()
    response = client.chat.completions.create(
        model=settings.openrouter_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _build_system_prompt(count=count, references=references)},
            {"role": "user", "content": _build_user_prompt(case=case, references=references, count=count)},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Scenario model returned an empty response")

    payload = ScenarioLLMResponse.model_validate(json.loads(content))
    scenarios = payload.scenarios[:count]
    if len(scenarios) != count:
        raise ValueError(f"Expected {count} scenarios, received {len(scenarios)}")

    allowed_citations = {reference.citation for reference in references}
    for scenario in scenarios:
        if not scenario.interpretation.strip():
            raise ValueError("Scenario interpretation is required")
        if not scenario.basis:
            raise ValueError("Scenario basis is required")
        invalid_citations = [citation for citation in scenario.basis if citation not in allowed_citations]
        if invalid_citations:
            raise ValueError(f"Scenario cited unsupported references: {invalid_citations}")
        scenario.disclaimer = DISCLAIMER

    return scenarios


def _build_client() -> OpenAI:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")

    return OpenAI(api_key=settings.openrouter_api_key, base_url=OPENROUTER_BASE_URL)


def _build_system_prompt(*, count: int, references: list[ReferenceDocument]) -> str:
    citations = "\n".join(f"- {reference.citation}" for reference in references)
    return (
        "You are generating legal interpretation scenarios for a Korean civil-case simulator. "
        "This is not legal advice. "
        "Only cite provided laws/precedents. "
        "Be uncertain if evidence is insufficient. "
        f"Return exactly {count} scenarios in JSON with this shape: "
        '{"scenarios":[{"title":"...","interpretation":"...","basis":["..."],"probability":"high|medium|low","key_factors":["..."]}]}. '
        "Each interpretation must explain how the dispute could be viewed, avoid definitive win/loss claims, and include the disclaimer meaningfully. "
        "Use only citations from this allowlist:\n"
        f"{citations}"
    )


def _build_user_prompt(*, case: Case, references: list[ReferenceDocument], count: int) -> str:
    reference_blocks = "\n\n".join(
        (
            f"{reference.citation}\n"
            f"Title: {reference.title}\n"
            f"Summary: {reference.summary}\n"
            f"Body excerpt:\n{reference.body[:1200]}"
        )
        for reference in references
    )
    evidence_text = ", ".join(case.input_data.evidence) if case.input_data.evidence else "No specific evidence provided"
    return (
        f"Generate top {count} legal interpretation scenarios for the following case.\n\n"
        f"Case ID: {case.id}\n"
        f"Case Type: {case.input_data.case_type.value}\n"
        f"Parties: {case.input_data.parties}\n"
        f"Facts: {case.input_data.facts}\n"
        f"Claims: {case.input_data.claims}\n"
        f"Evidence: {evidence_text}\n\n"
        "Provided laws/precedents:\n"
        f"{reference_blocks}\n\n"
        "For each scenario, keep basis limited to the provided citations, explain uncertainty where record support is thin, and surface the 핵심 쟁점 in key_factors."
    )


def _load_reference_documents(case: Case) -> list[ReferenceDocument]:
    documents = _read_markdown_documents("laws", "law") + _read_markdown_documents("precedents", "precedent")
    if not documents:
        raise ValueError("No laws or precedents are available for scenario generation")

    ranked = sorted(documents, key=lambda document: _document_score(document, case), reverse=True)
    selected = ranked[:6]
    if len(selected) < 2:
        raise ValueError("At least two reference documents are required")
    return selected


def _read_markdown_documents(directory: str, source_type: str) -> list[ReferenceDocument]:
    docs_dir = _project_root() / "data" / directory
    if not docs_dir.exists():
        return []

    documents: list[ReferenceDocument] = []
    for path in sorted(docs_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        frontmatter, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        identifier = frontmatter.get("id", path.stem)
        title = frontmatter.get("name") or frontmatter.get("case_name") or path.stem
        summary = frontmatter.get("summary") or frontmatter.get("holding") or (body.splitlines()[0] if body.splitlines() else title)
        documents.append(
            ReferenceDocument(
                source_type=source_type,
                identifier=identifier,
                title=title,
                summary=summary,
                body=body.strip(),
            )
        )
    return documents


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}, content

    _, raw_frontmatter, body = parts
    metadata: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body


def _document_score(document: ReferenceDocument, case: Case) -> int:
    haystack = " ".join(
        [
            case.input_data.case_type.value,
            case.input_data.parties,
            case.input_data.facts,
            case.input_data.claims,
            " ".join(case.input_data.evidence),
        ]
    ).lower()
    keywords = {token for token in re.split(r"[^0-9a-zA-Z가-힣]+", haystack) if len(token) >= 2}
    score = 0
    document_text = f"{document.title} {document.summary} {document.body}".lower()
    title_text = document.title.lower()
    for keyword in keywords:
        if keyword in document_text:
            score += 3 if keyword in title_text else 1
    if case.input_data.case_type.value.lower() in document_text:
        score += 5
    return score


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]
