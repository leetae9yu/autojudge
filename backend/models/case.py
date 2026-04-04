"""Case models."""

# pyright: reportMissingImports=false

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


DISCLAIMER = "본 서비스는 법률 자문을 제공하지 않습니다. 생성된 시나리오는 참고용이며, 실제 법적 결정은 반드시 변호사와 상담하십시오."


class CaseType(str, Enum):
    손해배상 = "손해배상"
    계약위반 = "계약위반"
    부당이득 = "부당이득"
    기타 = "기타"


class CaseInput(BaseModel):
    case_type: CaseType
    parties: str
    facts: str
    claims: str
    evidence: list[str] = Field(default_factory=list)


class Case(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disclaimer: str = DISCLAIMER
    input_data: CaseInput
