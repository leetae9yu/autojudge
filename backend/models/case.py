from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


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
    input_data: CaseInput
