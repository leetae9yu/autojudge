"""Search router for law and precedent search API."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from routers.cases import _cases
from services.search import search as perform_search


router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model."""

    case_id: str = Field(..., description="ID of the case to search for")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResponse(BaseModel):
    """Search response model."""

    query: str = Field(..., description="Search query used")
    laws: list[dict[str, Any]] = Field(default_factory=list, description="Relevant laws")
    precedents: list[dict[str, Any]] = Field(
        default_factory=list, description="Relevant precedents"
    )


def build_search_query(case: Any) -> str:
    """Build search query from case data.

    Args:
        case: Case object with input_data

    Returns:
        Combined search query string
    """
    input_data = case.input_data

    # Combine all text fields from case input
    query_parts = [
        input_data.case_type.value if hasattr(input_data.case_type, "value") else str(input_data.case_type),
        input_data.parties,
        input_data.facts,
        input_data.claims,
    ]

    # Add evidence if available
    if input_data.evidence:
        query_parts.extend(input_data.evidence)

    return " ".join(query_parts)


@router.post("", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """Search for relevant laws and precedents based on case ID.

    Args:
        request: Search request with case_id

    Returns:
        Search results with laws and precedents

    Raises:
        HTTPException: If case is not found
    """
    # Get case by ID
    case = _cases.get(request.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # Build search query from case data
    query = build_search_query(case)

    # Perform search
    results = perform_search(query, top_k=request.top_k)

    return SearchResponse(
        query=results["query"],
        laws=results["laws"],
        precedents=results["precedents"],
    )
