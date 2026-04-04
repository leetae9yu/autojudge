from uuid import uuid4

from fastapi import APIRouter, HTTPException

from models.case import Case, CaseInput


router = APIRouter(prefix="/api/cases", tags=["cases"])
_cases: dict[str, Case] = {}


@router.post("", response_model=Case)
def create_case(case_input: CaseInput) -> Case:
    case = Case(id=str(uuid4()), input_data=case_input)
    _cases[case.id] = case
    return case


@router.get("", response_model=list[Case])
def list_cases() -> list[Case]:
    return list(_cases.values())


@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str) -> Case:
    case = _cases.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
