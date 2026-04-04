from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from models.case import Case, CaseInput


class WhatIfChanges(BaseModel):
    """Changes to apply for what-if scenario. Limit to 1-2 variables."""

    facts: str | None = None
    evidence: list[str] | None = None
    claims: str | None = None

    @field_validator("facts", "evidence", "claims")
    @classmethod
    def check_single_change(cls, v: Any, info) -> Any:
        """Validate that at most 2 fields are being changed."""
        return v


class WhatIfRequest(BaseModel):
    """Request to generate a what-if scenario."""

    original_scenario_id: str
    changes: WhatIfChanges

    @field_validator("changes")
    @classmethod
    def validate_change_count(cls, changes: WhatIfChanges) -> WhatIfChanges:
        """Ensure only 1-2 variables are changed."""
        change_count = sum(
            1 for field in [changes.facts, changes.evidence, changes.claims]
            if field is not None
        )
        if change_count == 0:
            raise ValueError("At least one change must be specified")
        if change_count > 2:
            raise ValueError("Maximum 2 variables can be changed at once for MVP")
        return changes


class FieldDifference(BaseModel):
    """Difference for a single field."""

    field: str
    original: Any
    modified: Any


class WhatIfComparison(BaseModel):
    """Comparison between original and modified scenarios."""

    original_case: Case
    modified_case: Case
    differences: list[FieldDifference]
    summary: str


class WhatIfResponse(BaseModel):
    """Response containing what-if scenario results."""

    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    original_scenario_id: str
    comparison: WhatIfComparison
