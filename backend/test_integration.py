"""
AutoJudge 통합 테스트

이 모듈은 AutoJudge API의 전체 플로우를 테스트합니다.
OpenRouter API 호출은 mocking됩니다.

실행 방법:
    cd /root/projects/autojudge/backend
    python -m pytest test_integration.py -v
"""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(__file__).rsplit("/backend", 1)[0] + "/backend")

from main import app
from models.case import CaseType


# TestClient fixture
@pytest.fixture
def client():
    """FastAPI TestClient fixture"""
    return TestClient(app)


# OpenRouter API mocking fixture
@pytest.fixture
def mock_openrouter():
    """OpenRouter API 호출을 mocking하는 fixture"""
    with patch("services.scenario.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test-api-key"
        mock_settings.openrouter_model = "test-model"
        
        with patch("services.scenario.OpenAI") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=json.dumps({
                    "scenarios": [
                        {
                            "title": "유리한 시나리오",
                            "interpretation": "증거가 명확하여 원고의 승소 가능성이 높습니다.",
                            "basis": ["[law] law-civil-code-001 - 민법"],
                            "probability": "high",
                            "key_factors": ["명확한 증거", "피고의 인정"]
                        },
                        {
                            "title": "중립적 시나리오",
                            "interpretation": "증거가 부분적으로만 확인되어 승패가 불확실합니다.",
                            "basis": ["[precedent] precedent-2024-001 - 손해배상 청구 사건"],
                            "probability": "medium",
                            "key_factors": ["증거 불충분", "양측 주장 대립"]
                        },
                        {
                            "title": "불리한 시나리오",
                            "interpretation": "증거가 불충분하여 원고의 패소 가능성이 있습니다.",
                            "basis": ["[law] law-civil-code-001 - 민법"],
                            "probability": "low",
                            "key_factors": ["증거 부족", "피고의 반증"]
                        }
                    ]
                })))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            yield mock_client_class


# ==============================================================================
# 샘플 테스트 데이터 (docs/test-cases.md 참조)
# ==============================================================================

# 샘플 사건 1: 손해배상 (교통사고)
CASE_1_TRAFFIC_ACCIDENT = {
    "case_type": CaseType.손해배상.value,
    "parties": "원고: 김철수, 피고: 박영희",
    "facts": (
        "2024년 3월 15일 오후 2시경, 서울시 강남구 테헤란로에서 원고 김철수는 "
        "직진 신호를 받고 교차로를 통과하던 중, 좌회전 신호를 위반한 피고 박영희의 "
        "차량과 충돌하였습니다. 이 사고로 원고의 차량 앞부분이 파손되었고, "
        "원고는 경추 염좌로 3주간 치료를 받았습니다."
    ),
    "claims": (
        "차량 수리비 3,500,000원, 치료비 1,200,000원, 통원치료 교통비 150,000원, "
        "업무상 손해 2,000,000원, 총 청구액 6,850,000원"
    ),
    "evidence": [
        "CCTV 영상 - 교차로 CCTV에 충돌 장면 녹화",
        "교통사고사실확인원 - 경찰서 발급, 피고의 신호위반 사실 기재",
        "진단서 - 병원 발급, 경추 염좌 진단",
        "수리비 견적서 - 자동차 정비소 발급",
        "소득증명원 - 원고의 직장 발급"
    ]
}

# 샘플 사건 2: 계약위반 (임대차)
CASE_2_LEASE_VIOLATION = {
    "case_type": CaseType.계약위반.value,
    "parties": "임대인(원고): 이상호, 임차인(피고): 최민지",
    "facts": (
        "2023년 1월 1일, 원고 이상호와 피고 최민지는 서울시 마포구 아파트에 대해 "
        "2년 임대차계약을 체결하였습니다. 계약서에는 '임차인은 임대차 목적물을 "
        "주거 외의 목적으로 사용할 수 없다'는 조항이 포함되어 있었습니다. "
        "2024년 2월, 원고는 피고가 해당 주택을 불법 숙박업소로 운영하고 있다는 "
        "민원을 접수하고 현장을 확인하였습니다. 피고는 에어비앤비 플랫폼을 통해 "
        "단기 임대를 하고 있었습니다."
    ),
    "claims": (
        "1) 계약 해지 - 계약위반으로 인한 임대차계약 해지, "
        "2) 보증금 반환 거부 - 위약금으로 보증금 5천만원 중 1천만원 공제, "
        "3) 손해배상 - 불법 영업으로 인한 손해 500만원, "
        "4) 명도 청구 - 즉시 주택 인도 요구"
    ),
    "evidence": [
        "임대차계약서 - 주거 외 사용 금지 조항 포함",
        "에어비앤비 예약 내역 스크린샷 - 피고의 숙박업 운영 증거",
        "수익 정산 내역 - 플랫폼에서의 수익 내역",
        "관할 주민센터 민원 접수증 - 불법 숙박업 신고 내역",
        "동대표 확인서 - 건축물 위반 사실 확인"
    ]
}

# 샘플 사건 3: 부당이득 (오입금)
CASE_3_UNJUST_ENRICHMENT = {
    "case_type": CaseType.부당이득.value,
    "parties": "원고(송금인): 정재훈, 피고(수취인): 한수민",
    "facts": (
        "2024년 1월 10일, 원고 정재훈은 거래처 '한수산업'에 대금 10,000,000원을 "
        "송금하고자 하였습니다. 은행 앱에서 수취인을 검색하는 과정에서, 유사한 이름의 "
        "피고 한수민의 계좌를 실수로 선택하여 송금하였습니다. 원고는 즉시 은행에 "
        "연락하였으나, 피고 계좌는 이미 해지되었고 잔액이 인출된 상태였습니다. "
        "원고는 피고에게 연락을 시도하였으나, 피고는 '돈을 받은 적 없다'며 부인하고 있습니다."
    ),
    "claims": (
        "부당이득 반환 청구 - 10,000,000원 및 지연 이자(연 5%), 소송 비용은 피고 부담"
    ),
    "evidence": [
        "송금 내역 - 은행 송금 확인증",
        "원고-거래처 이메일 - '한수산업'과의 거래 내용 및 송금 요청",
        "통장 거래 내역 - 원고 계좌에서 1천만원 출금 기록",
        "피고 계좌 해지 내역 - 은행 발급, 송금일 다음 날 해지",
        "원고-피고 통화 녹취 - 피고가 수취 부인하는 내용"
    ]
}


# ==============================================================================
# 기본 API 테스트
# ==============================================================================

def test_health_check(client):
    """TC-000: Health check 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """TC-000: 루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "AutoJudge API"


# ==============================================================================
# E2E 테스트: Input Form → API → Results
# ==============================================================================

class TestEndToEndFlow:
    """E2E 테스트: 전체 플로우 (사건 생성 → 시나리오 생성 → 결과 조회)"""
    
    def test_e2e_traffic_accident_case(self, client, mock_openrouter):
        """TC-001: 교통사고 손해배상 사건 E2E 테스트"""
        # Step 1: 사건 생성
        response = client.post("/api/cases", json=CASE_1_TRAFFIC_ACCIDENT)
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        case_data = response.json()
        case_id = case_data["id"]
        assert case_id is not None
        assert case_data["input_data"]["case_type"] == CaseType.손해배상.value
        
        # Step 2: 시나리오 생성
        scenario_request = {"case_id": case_id, "count": 3}
        response = client.post("/api/scenarios", json=scenario_request)
        assert response.status_code == 200, f"Scenario creation failed: {response.text}"
        scenario_data = response.json()
        scenario_id = scenario_data["id"]
        
        # Step 3: 결과 검증
        assert scenario_data["case_id"] == case_id
        assert len(scenario_data["scenarios"]) == 3
        
        for scenario in scenario_data["scenarios"]:
            assert "title" in scenario
            assert "interpretation" in scenario
            assert "basis" in scenario
            assert "probability" in scenario
            assert scenario["probability"] in ["high", "medium", "low"]
            assert "key_factors" in scenario
            assert "disclaimer" in scenario
        
        # Step 4: 저장된 시나리오 조회
        response = client.get(f"/api/scenarios/{scenario_id}")
        assert response.status_code == 200
        assert response.json()["id"] == scenario_id
    
    def test_e2e_lease_violation_case(self, client, mock_openrouter):
        """TC-002: 임대차 계약위반 사건 E2E 테스트"""
        # Step 1: 사건 생성
        response = client.post("/api/cases", json=CASE_2_LEASE_VIOLATION)
        assert response.status_code == 200
        case_data = response.json()
        case_id = case_data["id"]
        
        # Step 2: 시나리오 생성 (2개만 요청)
        scenario_request = {"case_id": case_id, "count": 2}
        response = client.post("/api/scenarios", json=scenario_request)
        assert response.status_code == 200
        scenario_data = response.json()
        
        # Step 3: 결과 검증
        assert len(scenario_data["scenarios"]) == 2
        assert scenario_data["disclaimer"] is not None
    
    def test_e2e_unjust_enrichment_case(self, client, mock_openrouter):
        """TC-003: 부당이득 사건 E2E 테스트"""
        # Step 1: 사건 생성
        response = client.post("/api/cases", json=CASE_3_UNJUST_ENRICHMENT)
        assert response.status_code == 200
        case_data = response.json()
        case_id = case_data["id"]
        
        # Step 2: 시나리오 생성
        scenario_request = {"case_id": case_id, "count": 3}
        response = client.post("/api/scenarios", json=scenario_request)
        assert response.status_code == 200
        
        # Step 3: 사건 목록 조회
        response = client.get("/api/cases")
        assert response.status_code == 200
        cases = response.json()
        assert len(cases) >= 1
        
        # Step 4: 특정 사건 조회
        response = client.get(f"/api/cases/{case_id}")
        assert response.status_code == 200
        assert response.json()["id"] == case_id


# ==============================================================================
# What-If 시나리오 테스트
# ==============================================================================

class TestWhatIfScenarios:
    """What-If 테스트: 변수 변경 시나리오 비교"""
    
    def test_whatif_change_facts(self, client):
        """TC-004: 사실관계 변경 What-If 테스트"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_1_TRAFFIC_ACCIDENT)
        assert response.status_code == 200
        original_case_id = response.json()["id"]
        
        # What-If 시나리오 생성 (사실관계 변경)
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {
                "facts": (
                    "2024년 3월 15일 오후 2시경, 서울시 강남구 테헤란로에서 원고 김철수는 "
                    "직진 신호를 받고 교차로를 통과하던 중, 좌회전 신호를 위반한 피고 박영희의 "
                    "차량과 충돌하였습니다. 원고는 당시 속도가 시속 80km로 제한속도 60km를 "
                    "초과하고 있었습니다."
                )
            }
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 200
        whatif_data = response.json()
        
        # 검증
        assert whatif_data["original_scenario_id"] == original_case_id
        assert "comparison" in whatif_data
        assert "original_case" in whatif_data["comparison"]
        assert "modified_case" in whatif_data["comparison"]
        assert "differences" in whatif_data["comparison"]
        assert len(whatif_data["comparison"]["differences"]) == 1
        assert whatif_data["comparison"]["differences"][0]["field"] == "facts"
        assert "summary" in whatif_data["comparison"]
    
    def test_whatif_change_evidence(self, client):
        """TC-005: 증거 변경 What-If 테스트 (CCTV 제외)"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_1_TRAFFIC_ACCIDENT)
        assert response.status_code == 200
        original_case_id = response.json()["id"]
        
        # What-If 시나리오 생성 (CCTV 증거 제외)
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {
                "evidence": [
                    "교통사고사실확인원 - 경찰서 발급, 피고의 신호위반 사실 기재",
                    "진단서 - 병원 발급, 경추 염좌 진단",
                    "수리비 견적서 - 자동차 정비소 발급"
                    # CCTV 영상 제외됨
                ]
            }
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 200
        whatif_data = response.json()
        
        # 검증
        differences = whatif_data["comparison"]["differences"]
        assert len(differences) == 1
        assert differences[0]["field"] == "evidence"
        assert "CCTV" not in str(differences[0]["modified"])
    
    def test_whatif_change_two_variables(self, client):
        """TC-006: 2개 변수 동시 변경 What-If 테스트"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_2_LEASE_VIOLATION)
        assert response.status_code == 200
        original_case_id = response.json()["id"]
        
        # What-If 시나리오 생성 (사실관계 + 청구내용 변경)
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {
                "facts": "피고가 2024년 1월에 이미 주택을 비우고 퇴실함",
                "claims": "보증금 5천만원 전액 반환 청구"
            }
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 200
        whatif_data = response.json()
        
        # 검증 - 2개 필드 변경됨
        differences = whatif_data["comparison"]["differences"]
        changed_fields = {diff["field"] for diff in differences}
        assert changed_fields == {"facts", "claims"}
    
    def test_whatif_list_and_get(self, client):
        """TC-007: What-If 목록 조회 및 개별 조회 테스트"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_3_UNJUST_ENRICHMENT)
        assert response.status_code == 200
        original_case_id = response.json()["id"]
        
        # What-If 시나리오 생성
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {
                "claims": "부당이득 반환 청구 - 5,000,000원 (부분 반환)"
            }
        }
        response = client.post("/api/whatif", json=whatif_request)
        whatif_id = response.json()["id"]
        
        # 목록 조회
        response = client.get("/api/whatif")
        assert response.status_code == 200
        whatif_list = response.json()
        assert len(whatif_list) >= 1
        
        # 개별 조회
        response = client.get(f"/api/whatif/{whatif_id}")
        assert response.status_code == 200
        assert response.json()["id"] == whatif_id


# ==============================================================================
# 에러 핸들링 테스트
# ==============================================================================

class TestErrorHandling:
    """에러 핸들링 테스트"""
    
    def test_error_case_not_found(self, client, mock_openrouter):
        """TC-008: 존재하지 않는 사건으로 시나리오 생성 시 404 에러"""
        scenario_request = {
            "case_id": "non-existent-case-id-12345",
            "count": 3
        }
        response = client.post("/api/scenarios", json=scenario_request)
        assert response.status_code == 404
        assert "Case not found" in response.json()["detail"]
    
    def test_error_whatif_no_changes(self, client):
        """TC-009: 변경사항 없는 What-If 요청 시 400 에러"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_1_TRAFFIC_ACCIDENT)
        original_case_id = response.json()["id"]
        
        # 변경사항 없이 What-If 요청
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {}
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 422  # Pydantic validation error
        error_detail = str(response.json())
        assert "At least one change must be specified" in error_detail or "changes" in error_detail
    
    def test_error_whatif_too_many_changes(self, client):
        """TC-010: 3개 이상 변수 변경 시도 시 400 에러"""
        # 원본 사건 생성
        response = client.post("/api/cases", json=CASE_1_TRAFFIC_ACCIDENT)
        original_case_id = response.json()["id"]
        
        # 3개 변수 모두 변경 (최대 2개까지 허용)
        whatif_request = {
            "original_scenario_id": original_case_id,
            "changes": {
                "facts": "변경된 사실관계",
                "evidence": ["변경된 증거"],
                "claims": "변경된 청구내용"
            }
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 422  # Pydantic validation error
        error_detail = str(response.json())
        assert "Maximum 2 variables" in error_detail or "changes" in error_detail
    
    def test_error_whatif_original_not_found(self, client):
        """TC-011: 존재하지 않는 원본 사건으로 What-If 생성 시 404 에러"""
        whatif_request = {
            "original_scenario_id": "non-existent-id-12345",
            "changes": {
                "facts": "새로운 사실관계"
            }
        }
        
        response = client.post("/api/whatif", json=whatif_request)
        assert response.status_code == 404
        assert "Original scenario not found" in response.json()["detail"]
    
    def test_error_whatif_scenario_not_found(self, client):
        """TC-012: 존재하지 않는 What-If 시나리오 조회 시 404 에러"""
        response = client.get("/api/whatif/non-existent-id-12345")
        assert response.status_code == 404
        assert "What-if scenario not found" in response.json()["detail"]
    
    def test_error_scenario_not_found(self, client):
        """TC-013: 존재하지 않는 시나리오 조회 시 404 에러"""
        response = client.get("/api/scenarios/non-existent-id-12345")
        assert response.status_code == 404
        assert "Scenario result not found" in response.json()["detail"]
    
    def test_error_case_not_found_individual(self, client):
        """TC-014: 존재하지 않는 사건 개별 조회 시 404 에러"""
        response = client.get("/api/cases/non-existent-id-12345")
        assert response.status_code == 404
        assert "Case not found" in response.json()["detail"]


# ==============================================================================
# 시나리오 카운트 검증 테스트
# ==============================================================================

class TestScenarioCount:
    """시나리오 개수 요청 테스트"""
    
    def test_scenario_count_1(self, client, mock_openrouter):
        """TC-015: 1개 시나리오 요청"""
        response = client.post("/api/cases", json=CASE_3_UNJUST_ENRICHMENT)
        case_id = response.json()["id"]
        
        response = client.post("/api/scenarios", json={"case_id": case_id, "count": 1})
        assert response.status_code == 200
        assert len(response.json()["scenarios"]) == 1
    
    def test_scenario_count_5(self, client, mock_openrouter):
        """TC-016: 5개 시나리오 요청 (최대값)"""
        # Mock을 5개 시나리오로 재설정
        with patch("services.scenario.OpenAI") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=json.dumps({
                    "scenarios": [
                        {"title": f"시나리오 {i+1}", "interpretation": f"해석 {i+1}",
                         "basis": ["[law] law-civil-code-001 - 민법"], "probability": "high",
                         "key_factors": [f"쟁점 {i+1}"]}
                        for i in range(5)
                    ]
                })))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            response = client.post("/api/cases", json=CASE_3_UNJUST_ENRICHMENT)
            case_id = response.json()["id"]
            
            response = client.post("/api/scenarios", json={"case_id": case_id, "count": 5})
            assert response.status_code == 200
            assert len(response.json()["scenarios"]) == 5


# ==============================================================================
# 메인 실행 블록
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
