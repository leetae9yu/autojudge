# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from openai import APIError
from pydantic import ValidationError

from routers.cases import _cases
from services.scenario import ScenarioGenerationRequest, ScenarioGenerationResult, generate_scenarios


router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])
_scenario_results: dict[str, ScenarioGenerationResult] = {}


@router.post("", response_model=ScenarioGenerationResult)
def create_scenarios(request: ScenarioGenerationRequest) -> ScenarioGenerationResult:
    case = _cases.get(request.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        scenarios = generate_scenarios(case, count=request.count)
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenRouter request failed: {exc}") from exc

    result = ScenarioGenerationResult(id=str(uuid4()), case_id=case.id, scenarios=scenarios)
    _scenario_results[result.id] = result
    return result


@router.get("/{scenario_id}", response_model=ScenarioGenerationResult)
def get_scenarios(scenario_id: str) -> ScenarioGenerationResult:
    result = _scenario_results.get(scenario_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Scenario result not found")
    return result
