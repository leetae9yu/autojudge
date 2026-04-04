from uuid import uuid4

from fastapi import APIRouter, HTTPException

from models.case import Case, CaseInput
from models.whatif import (
    FieldDifference,
    WhatIfComparison,
    WhatIfRequest,
    WhatIfResponse,
)
from routers.cases import _cases

router = APIRouter(prefix="/api/whatif", tags=["whatif"])
_whatif_scenarios: dict[str, WhatIfResponse] = {}


def _apply_changes(original_input: CaseInput, changes) -> CaseInput:
    """Apply changes to create modified case input."""
    modified_dict = original_input.model_dump()

    if changes.facts is not None:
        modified_dict["facts"] = changes.facts
    if changes.evidence is not None:
        modified_dict["evidence"] = changes.evidence
    if changes.claims is not None:
        modified_dict["claims"] = changes.claims

    return CaseInput(**modified_dict)


def _compute_differences(
    original_input: CaseInput, modified_input: CaseInput
) -> list[FieldDifference]:
    """Compute differences between original and modified case inputs."""
    differences = []

    if original_input.facts != modified_input.facts:
        differences.append(
            FieldDifference(
                field="facts", original=original_input.facts, modified=modified_input.facts
            )
        )

    if original_input.evidence != modified_input.evidence:
        differences.append(
            FieldDifference(
                field="evidence",
                original=original_input.evidence,
                modified=modified_input.evidence,
            )
        )

    if original_input.claims != modified_input.claims:
        differences.append(
            FieldDifference(
                field="claims",
                original=original_input.claims,
                modified=modified_input.claims,
            )
        )

    return differences


def _generate_summary(differences: list[FieldDifference]) -> str:
    """Generate a human-readable summary of changes."""
    if not differences:
        return "No changes were made to the scenario."

    field_names = [diff.field for diff in differences]
    if len(field_names) == 1:
        return f"Modified {field_names[0]} to explore alternative scenario."
    else:
        return f"Modified {', '.join(field_names)} to explore alternative scenario."


@router.post("", response_model=WhatIfResponse)
def create_whatif_scenario(request: WhatIfRequest) -> WhatIfResponse:
    """
    Generate a what-if scenario by modifying 1-2 variables from an original case.

    - **original_scenario_id**: ID of the original case to modify
    - **changes**: Changes to apply (facts, evidence, or claims - max 2)
    """
    # Find original case
    original_case = _cases.get(request.original_scenario_id)
    if original_case is None:
        raise HTTPException(status_code=404, detail="Original scenario not found")

    # Apply changes to create modified input
    modified_input = _apply_changes(original_case.input_data, request.changes)

    # Create modified case
    modified_case = Case(
        id=str(uuid4()),
        input_data=modified_input,
    )

    # Compute differences
    differences = _compute_differences(
        original_case.input_data, modified_case.input_data
    )

    # Generate summary
    summary = _generate_summary(differences)

    # Build comparison
    comparison = WhatIfComparison(
        original_case=original_case,
        modified_case=modified_case,
        differences=differences,
        summary=summary,
    )

    # Create and store what-if scenario
    whatif = WhatIfResponse(
        id=str(uuid4()),
        original_scenario_id=request.original_scenario_id,
        comparison=comparison,
    )
    _whatif_scenarios[whatif.id] = whatif

    # Also store the modified case for reference
    _cases[modified_case.id] = modified_case

    return whatif


@router.get("", response_model=list[WhatIfResponse])
def list_whatif_scenarios() -> list[WhatIfResponse]:
    """List all what-if scenarios."""
    return list(_whatif_scenarios.values())


@router.get("/{scenario_id}", response_model=WhatIfResponse)
def get_whatif_scenario(scenario_id: str) -> WhatIfResponse:
    """Get a specific what-if scenario by ID."""
    scenario = _whatif_scenarios.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="What-if scenario not found")
    return scenario
