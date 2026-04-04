# What-If API Implementation Learnings

## Files Created
- `/root/projects/autojudge/backend/models/whatif.py` - Pydantic models for what-if scenarios
- `/root/projects/autojudge/backend/routers/whatif.py` - FastAPI router for what-if endpoints
- Updated `/root/projects/autojudge/backend/main.py` - Added whatif router

## Implementation Patterns Followed
1. **Model Pattern**: Used Pydantic BaseModel with Field validators consistent with existing case.py
2. **Router Pattern**: APIRouter with prefix and tags, following cases.py pattern
3. **In-Memory Storage**: Used dict for storage like existing _cases pattern
4. **Validation**: Enforced 1-2 variable change limit using Pydantic field_validator

## API Endpoints
- `POST /api/whatif` - Create what-if scenario with changes to facts/evidence/claims
- `GET /api/whatif` - List all what-if scenarios
- `GET /api/whatif/{scenario_id}` - Get specific what-if scenario

## Key Features
- Accepts original_scenario_id and changes (facts/evidence/claims)
- Validates max 2 variables can be changed (MVP limitation)
- Creates modified case with new ID
- Returns comparison with original_case, modified_case, differences, and summary
- Stores modified case in _cases for reference

## Integration
- Imported _cases from routers.cases for accessing original cases
- Added whatif_router to main.py
- Follows existing import structure
