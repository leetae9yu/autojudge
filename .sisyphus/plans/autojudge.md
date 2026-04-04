# AutoJudge - 재판 시뮬레이터

## TL;DR

> **한 줄 요약**: 민사 사건(손핵배상/계약)을 입력하면 관련 법률/판례를 기반으로 가능한 법적 해석 시나리오 Top3를 제공하고, What-If 형식으로 변수를 변경하며 추가 시나리오를 생성하는 로컬 법률 시뮬레이터
> 
> **핵심 가치**: "이 사건은 법적으로 이렇게 해석될 수 있다"는 관점 제공 (법률 자문이 아닌 참고용)
> 
> **기술 스택**: Python FastAPI + Vue 3 + TypeScript + Markdown 기반 데이터 저장 + OpenRouter (BYOK)
> 
> **데이터 전략**: korean-law-mcp로 초기 일회성 수집 → Markdown으로 변환 → 지식 그래프 형태로 연결

**예상 소요시간**: 3-4일 (MVP 기준)  
**병렬 실행**: 가능 (5개 웨이브로 구성)  
**크리티컬 패스**: 환경설정 → 데이터 수집 → 백엔드 API → 프론트엔드 → 통합테스트

---

## Context

### 원래 요청
> https://github.com/SeoNaRu/korean-law-mcp 를 통해 데이터를 얻고, https://github.com/666ghj/MiroFish 와 비슷한 로직을 통해서 '재판 시뮬레이터'를 만들고자 함. 각종 법적 리스크를 피하기 위해서, API BYOK 방식으로 진행할거고, 웹서비스라기 보다는 그냥 localhost로 접속해서 돌릴 듯. 특정 사건에 대한 정보를 입력하면(증거 등도 포함) 법령&판례를 기반으로 하여 가능한 시나리오 Top3를 제공하고, What-If 형식으로 계속해서 여러 시나리오를 생성할 수 있도록 할 예정. root/projects/ 에 autojudge라는 폴징 만들어서 거기서 작업할 예정. 일단 플래닝부터 들어가자. 반드시 git으로 버전 관리도 해야함

### 인터뷰/협의 내역

**핵심 결정사항**:
- **도메인**: 민사 (손핵배상, 계약) - 사법 리스크가 상대적으로 낮은 영역
- **출력 형식**: 법적 해석형 - "이렇게 해석될 수 있다"는 관점으로 접근 (법률 자문 회피)
- **AI 모델**: OpenRouter (BYOK - 사용자가 직접 API 키 입력) - GPT-4.1, Claude 등 모델 선택 가능
- **데이터 수집**: 초기 일회성 (korean-law-mcp 활용) - **판례는 2024년까지만 수집 (2025년은 테스트 세트)**
- **입력 방식**: 폼 기반 구조화 (5개 핵심 필드)

**범위 확정**:
- ✅ **INCLUDE**: 민사 사건 시뮬레이션, 법률/판례 기반 해석, What-If 시나리오 생성
- ❌ **EXCLUDE**: 형사/행정/노동 사건, 실제 소송 대행, 법률 자문 제공
- ❌ **EXCLUDE**: 문서 업로드/OCR, 실시간 판례 업데이트, 멀티에이전트 시뮬레이션 (v2)

### Metis 갭 분석 결과

**P0 갭 (해결됨)**:
1. ✅ 대상 사건 범위: 민사로 확정
2. ✅ 법적 책임 경계: "법률 자문 아님" 고지 필수
3. ✅ 출력 계약: 법적 해석형 Top3 (승소/패소가 아닌 해석 가능성)
4. ✅ 근거 기반 생성: 인용된 법률/판례만 사용 규칙 적용
5. ✅ 평가 방식: 샘플 사건 + 기대 인용 + 수동 평가표 (QA 시나리오에 포함)

**P1 갭 (플랜에 반영)**:
- Markdown 저장 규격 정의 (frontmatter 스키마)
- 판례 범위: 대법원 중심, **2024년까지 (2025년은 성능 평가용 테스트 세트)**
- 입력 스키마: 5개 핵심 필드로 상세화

### 리서치 결과

**korean-law-mcp 분석**:
- 국가법령정보센터 Open API 활용
- 법령 검색/상세 조회, 판례 검색/상세 조회, 행정규칙 검색 제공
- XML 응답 형식, 24시간 캐싱 지원
- 초기 데이터 동기화: 주요 키워드로 목록 수집 → 상세 정보 수집 순차 진행

**MiroFish 분석**:
- 5단계 워크플로우: 그래프 구축 → 환경 설정 → 시뮬레이션 → 보고서 → 상호작용
- 핵심 패턴: Ontology Generator → Profile Generator → Simulation → ReportAgent
- Zep Cloud를 활용한 GraphRAG + 메모리 관리
- 우리 프로젝트에서는 "단일 LLM + RAG"로 단순화하여 적용

**AI 모델 벤치마크**:
- 1위: OpenAI GPT-4.1 (법률 추론 최강, API 안정적)
- 2위: Anthropic Claude Sonnet 4 (긴 문서 처리 우수)
- 3위: NAVER HyperCLOVA X (한국어 처리 우수, BYOK 어려움)
- 결정: OpenRouter를 통한 GPT-4.1/Claude 등 + 한국 법률 RAG 조합
- OpenRouter 장점: 단일 API 키로 여러 모델 사용 가능, 비용 효율적

---

## Work Objectives

### 핵심 목표
민사 사건(손핵배상, 계약 분쟁)에 대해 법률/판례를 기반으로 한 법적 해석 시나리오 Top3를 생성하고, What-If 방식으로 변수를 변경하며 추가 시나리오를 탐색할 수 있는 로컬 법률 시뮬레이터 개발

### 구체적 산출물
- **Backend**: FastAPI 기반 API 서버 (`/api/cases`, `/api/scenarios`, `/api/whatif`)
- **Frontend**: Vue 3 + TypeScript SPA (사건 입력 폼, 시나리오 뷰, What-If 인터페이스)
- **Data**: Markdown 기반 법률/판례 데이터베이스 (AI-friendly 구조)
- **Documentation**: API 문서, 사용 가이드, 데이터 스키마 정의

### 완료 기준 (Definition of Done)
- [ ] 사건을 구조화 폼으로 입력할 수 있다
- [ ] 관련 법률/판례를 검색해 보여준다 (최소 3개 이상 인용)
- [ ] Top3 법적 해석 시나리오를 생성한다 (각 시나리오는 2개 이상 인용 근거 포함)
- [ ] 입력 변수 1~2개 변경 후 결과 비교가 가능하다 (What-If)
- [ ] 모든 결과에 "법률 자문 아님" 고지가 포함된다
- [ ] 저장된 Markdown 문서에 표준 메타데이터가 있다
- [ ] FastAPI + Vue 앱이 localhost에서 실행 가능하다 (`npm run dev`)
- [ ] Git 버전 관리가 설정되어 있다 (main/feature 브랜치 전략)

### Must Have
- 민사 사건 입력 및 처리 (손핵배상, 계약 분쟁 중심)
- 핵심 법률 10개 이상 수집 및 Markdown 저장
- 관련 판례 수집 및 인용 연결
- OpenRouter 기반 시나리오 생성 (BYOK) - GPT-4.1, Claude 등 선택 가능
- 법적 해석 Top3 출력
- What-If 기본 기능 (변수 1개 변경)
- "법률 자문 아님" 고지

### Must NOT Have (Guardrails)
- ❌ 실제 법률 자문 제공
- ❌ 소송 대행 또는 대리인 연결
- ❌ 근거 없는 법률/판례 인용
- ❌ 개인정보 미마스킹 처리
- ❌ 형사/행정/노동 사건 처리 (v1 범위 밖)
- ❌ 문서 업로드/OCR 기능 (v1 범위 밖)
- ❌ 실시간 판례 업데이트 (초기 일회성 수집)
- ❌ 멀티에이전트 시뮬레이션 (v1 범위 밖)

---

## Verification Strategy

### 테스트 전략
- **자동화 테스트**: 없음 (MVP 수준, QA 시나리오로 대체)
- **QA 전략**: 모든 TODO에 Agent-Executed QA 시나리오 필수 포함
- **검증 방식**: 샘플 사건 3건에 대해 수동 평가 (관련성/설명성/인용 정확성)

### QA 정책
모든 작업은 **Agent-Executed QA 시나리오**를 포함해야 함. QA 증거는 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`에 저장.

- **Backend/API**: curl로 엔드포인트 호출 → 응답 JSON 검증
- **Frontend**: Playwright로 브라우저 자동화 → DOM 요소 확인, 스크린샷
- **Data**: Markdown 파일 존재 여부 및 frontmatter 검증
- **Integration**: 전체 플로우 테스트 (입력 → 검색 → 시나리오 생성)

---

## Execution Strategy

### 병렬 실행 웨이브

```
웨이브 1: 환경 설정 및 스캐폴딩 (즉시 시작 - 병렬 4개)
├── Task 1: 프로젝트 구조 생성 및 Git 초기화 [quick]
├── Task 2: Python 가상환경 및 FastAPI 의존성 설정 [quick]
├── Task 3: Vue 3 + TypeScript 프로젝트 설정 [quick]
└── Task 4: 환경 변수 및 설정 파일 템플릿 생성 [quick]

웨이브 2: 데이터 인프라 (웨이브 1 후 - 병렬 3개)
├── Task 5: korean-law-mcp 연동 및 데이터 수집 스크립트 [unspecified-high]
├── Task 6: Markdown 데이터 스키마 설계 및 저장 구조 [quick]
└── Task 7: 벡터 검색을 위한 임베딩 파이프라인 (선택) [unspecified-high]

웨이브 3: 백엔드 코어 API (웨이브 1 후 - 병렬 4개)
├── Task 8: 사건 입력 API 및 모델 정의 [quick]
├── Task 9: 법률/판례 검색 API (RAG) [unspecified-high]
├── Task 10: 시나리오 생성 API (GPT-4.1 연동) [deep]
└── Task 11: What-If API (변수 변경 및 재생성) [unspecified-high]

웨이브 4: 프론트엔드 UI (웨이브 3 후 - 병렬 3개)
├── Task 12: 사건 입력 폼 컴포넌트 (5개 필드) [visual-engineering]
├── Task 13: 시나리오 결과 뷰 컴포넌트 [visual-engineering]
└── Task 14: What-If 인터페이스 컴포넌트 [visual-engineering]

웨이브 5: 통합 및 마무리 (웨이브 3,4 후 - 병렬 3개)
├── Task 15: 프론트엔드-백엔드 연동 (API 클라이언트) [quick]
├── Task 16: 법적 책임 고지 및 안내 문구 추가 [quick]
└── Task 17: 통합 테스트 및 샘플 사건 검증 [unspecified-high]

웨이브 FINAL (모든 작업 후 - 병렬 3개)
├── Task F1: 전체 플로우 E2E 테스트 (oracle)
├── Task F2: 코드 품질 리뷰 및 문서화 [unspecified-high]
└── Task F3: 사용자 가이드 작성 [writing]

결과 보고 → 사용자 확인 → 작업 완료
```

### 의존성 매트릭스

| Task | 블록됨 | 블로킹 |
|------|--------|--------|
| T1 | - | T2, T3, T4 |
| T5 | T1 | T9 |
| T6 | T1 | T9 |
| T8 | T1 | T10, T11 |
| T9 | T5, T6 | T10, T11 |
| T10 | T8, T9 | T12, T13 |
| T11 | T8, T9 | T14 |
| T12 | T10 | T15 |
| T13 | T10 | T15 |
| T14 | T11 | T15 |
| T15 | T12, T13, T14 | F1 |
| F1-F3 | T15, T16, T17 | - |

### 에이전트 프로필 요약

- **Tasks 1-4**: `quick` - 환경 설정은 빠르게 처리
- **Tasks 5-7**: `unspecified-high` - 데이터 수집은 신중하게
- **Tasks 8-11**: `unspecified-high`/`deep` - API 로직은 정확하게
- **Tasks 12-14**: `visual-engineering` - UI는 사용자 친화적으로
- **Tasks 15-17**: `quick`/`unspecified-high` - 통합은 꼼꼼하게
- **Tasks F1-F3**: `oracle`/`writing` - 검증은 철저하게

---

## TODOs

> **주의**: 각 TODO는 반드시 **Agent-Executed QA 시나리오**를 포함해야 함.
> QA 시나리오는 구체적인 도구(curl/Playwright/Bash), 단계, 예상 결과, 실패 지표를 명시.

- [x] 1. 프로젝트 구조 생성 및 Git 초기화

  **What to do**:
  - `/root/projects/autojudge` 디렉토리 생성
  - Git 저장소 초기화 (`git init`)
  - 기본 `.gitignore` 생성 (Python, Node.js, 환경변수)
  - 디렉토리 구조 생성: `backend/`, `frontend/`, `data/`, `docs/`
  - 초기 README.md 작성

  **Must NOT do**:
  - `.env` 파일에 실제 API 키 저장 (템플릿만 생성)
  - 불필요한 파일 커밋

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 단순 디렉토리 및 파일 생성 작업

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: 웨이브 1 (Tasks 1-4)
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None

  **References**:
  - `.gitignore` 패턴: Python (`.pyc`, `__pycache__`), Node (`node_modules`), 환경변수 (`.env`)

  **Acceptance Criteria**:
  - [ ] `/root/projects/autojudge` 디렉토리 존재
  - [ ] `.git` 디렉토리 존재
  - [ ] `.gitignore` 파일 존재
  - [ ] 4개의 서브디렉토리 (`backend/`, `frontend/`, `data/`, `docs/`) 존재

  **QA Scenarios**:

  ```
  Scenario: 프로젝트 구조 생성 확인
    Tool: Bash (ls)
    Preconditions: 없음
    Steps:
      1. ls -la /root/projects/autojudge/ 실행
      2. .git, backend/, frontend/, data/, docs/ 존재 확인
    Expected Result: 모든 디렉토리와 .git 폴터 존재
    Failure Indicators: 디렉토리 누락, .git 없음
    Evidence: .sisyphus/evidence/task-1-structure-check.txt
  ```

  **Commit**: YES
  - Message: `chore: initialize project structure`
  - Files: 모든 신규 파일

---

- [x] 2. Python 가상환경 및 FastAPI 의존성 설정

  **What to do**:
  - Python 가상환경 생성 (`python3 -m venv venv`)
  - `backend/requirements.txt` 작성:
    - FastAPI, uvicorn
    - openai
    - pydantic, pydantic-settings
    - python-dotenv
    - requests (MCP 연동용)
  - `backend/main.py` 기본 FastAPI 앱 생성
  - CORS 설정 (localhost:3000 허용)

  **Must NOT do**:
  - 가상환경을 Git에 커밋
  - requirements.txt에 버전 고정 없이 작성

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 표준 Python/FastAPI 설정

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 1)
  - **Blocked By**: Task 1

  **References**:
  - FastAPI 공식 문서: https://fastapi.tiangolo.com/
  - Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

  **Acceptance Criteria**:
  - [ ] `backend/requirements.txt` 존재 및 의존성 목록 포함
  - [ ] `backend/main.py` 존재 (FastAPI 인스턴스 생성)
  - [ ] `uvicorn backend.main:app --reload`로 서버 시작 가능

  **QA Scenarios**:

  ```
  Scenario: FastAPI 서버 기동 확인
    Tool: Bash
    Preconditions: 가상환경 활성화
    Steps:
      1. cd /root/projects/autojudge/backend
      2. source venv/bin/activate
      3. uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 5 &
      4. sleep 2
      5. curl http://localhost:8000/health (또는 /docs)
    Expected Result: HTTP 200 또는 OpenAPI 문서 응답
    Failure Indicators: ImportError, 포트 충돌, 404
    Evidence: .sisyphus/evidence/task-2-server-start.txt
  ```

  **Commit**: YES
  - Message: `chore: setup FastAPI backend`
  - Files: `backend/`

---

- [x] 3. Vue 3 + TypeScript 프로젝트 설정

  **What to do**:
  - `npm create vue@latest frontend` 실행
    - TypeScript: YES
    - JSX Support: NO
    - Vue Router: YES
    - Pinia: YES
    - Vitest: NO (MVP에서 제외)
    - ESLint: YES
    - Prettier: YES
  - Vuetify 또는 Tailwind CSS 설치 (UI 프레임워크)
  - `frontend/src/api/` 디렉토리 생성 (API 클라이언트용)
  - 기본 라우트 설정 (`/`, `/case`, `/result`)

  **Must NOT do**:
  - 불필요한 의존성 추가
  - 복잡한 상태 관리 패턴 도입

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 표준 Vue 3 프로젝트 설정

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 1)
  - **Blocked By**: Task 1

  **References**:
  - Vue 3 Quick Start: https://vuejs.org/guide/quick-start.html
  - Vuetify: https://vuetifyjs.com/en/getting-started/installation/

  **Acceptance Criteria**:
  - [ ] `frontend/package.json` 존재 (vue 의존성 포함)
  - [ ] `frontend/src/main.ts` 존재
  - [ ] `npm run dev`로 개발 서버 시작 가능 (localhost:3000)

  **QA Scenarios**:

  ```
  Scenario: Vue 개발 서버 기동 확인
    Tool: Bash
    Preconditions: Node.js 설치
    Steps:
      1. cd /root/projects/autojudge/frontend
      2. npm install
      3. timeout 10s npm run dev &
      4. sleep 5
      5. curl http://localhost:3000
    Expected Result: HTML 응답 (Vue 앱 로딩)
    Failure Indicators: 404, 빈 페이지, 빌드 오류
    Evidence: .sisyphus/evidence/task-3-vue-start.txt
  ```

  **Commit**: YES
  - Message: `chore: setup Vue 3 frontend`
  - Files: `frontend/` (node_modules 제외)

---

- [x] 4. 환경 변수 및 설정 파일 템플릿 생성

  **What to do**:
  - `backend/.env.example` 작성:
    - OPENROUTER_API_KEY (OpenRouter API 키 - https://openrouter.ai/keys)
    - OPENROUTER_MODEL (선택적, 기본: openai/gpt-4.1)
    - LAW_API_KEY (korean-law-mcp용)
    - DATABASE_PATH (Markdown 데이터 저장 경로)
  - `frontend/.env.example` 작성:
    - VITE_API_BASE_URL
  - `backend/config.py` 작성 (Pydantic Settings 기반)
  - 설정 파일 `.gitignore`에 추가

  **Must NOT do**:
  - 실제 API 키가 포함된 `.env` 파일 커밋

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 단순 설정 파일 작성

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 1)
  - **Blocked By**: Task 1

  **References**:
  - Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

  **Acceptance Criteria**:
  - [ ] `backend/.env.example` 존재 (필수 변수 목록 포함)
  - [ ] `frontend/.env.example` 존재
  - [ ] `backend/config.py` 존재 (Pydantic Settings 클래스)

  **QA Scenarios**:

  ```
  Scenario: 설정 파일 로드 확인
    Tool: Bash (Python)
    Preconditions: 가상환경 활성화
    Steps:
      1. cd /root/projects/autojudge/backend
      2. python -c "from config import Settings; print(Settings().model_dump())"
    Expected Result: 설정 객체가 기본값 로드 (에러 없음)
    Failure Indicators: ImportError, ValidationError
    Evidence: .sisyphus/evidence/task-4-config-load.txt
  ```

  **Commit**: YES
  - Message: `chore: add environment configuration templates`
  - Files: `backend/.env.example`, `frontend/.env.example`, `backend/config.py`

---

- [x] 5. korean-law-mcp 연동 및 데이터 수집 스크립트

  **What to do**:
  - korean-law-mcp 저장소 클론 또는 의존성으로 추가
  - `backend/scripts/collect_laws.py` 작성:
    - 주요 법률 키워드로 검색 (민법, 상법 등)
    - 검색 결과 저장 (JSON)
    - 법령 상세 정보 수집
  - `backend/scripts/collect_precedents.py` 작성:
    - 판례 키워드로 검색 (손핵배상, 계약 등)
    - 대법원 판례만 필터링
    - **선고일자 기준 2024년까지만 수집 (2025년은 테스트 세트로 제외)**
    - 판례 상세 정보 수집
  - 수집된 데이터를 `data/raw/`에 저장

  **Must NOT do**:
  - API 호출 제한을 고려하지 않은 과도한 요청
  - 에러 처리 없는 스크립트 작성

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 외부 API 연동 및 데이터 수집은 주의 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 2)
  - **Blocked By**: Task 1
  - **Blocks**: Task 9

  **References**:
  - korean-law-mcp 도구: `search_law_tool`, `get_law_detail_tool`, `search_precedent_tool`
  - 국가법령정보센터 API: https://open.law.go.kr/

  **Acceptance Criteria**:
  - [ ] `backend/scripts/collect_laws.py` 존재 및 실행 가능
  - [ ] `backend/scripts/collect_precedents.py` 존재 및 실행 가능
  - [ ] 샘플 데이터 수집 확인 (최소 1개 법률, 1개 판례)

  **QA Scenarios**:

  ```
  Scenario: 법률 데이터 수집 확인
    Tool: Bash
    Preconditions: LAW_API_KEY 환경변수 설정
    Steps:
      1. cd /root/projects/autojudge/backend
      2. python scripts/collect_laws.py --keyword "민법" --limit 1
      3. ls -la data/raw/laws/
    Expected Result: JSON 파일 생성 (법률 데이터 포함)
    Failure Indicators: API 에러, 빈 파일, JSON 파싱 에러
    Evidence: .sisyphus/evidence/task-5-collect-law.json
  ```

  **Commit**: YES
  - Message: `feat: add law data collection scripts`
  - Files: `backend/scripts/`, 수집된 샘플 데이터

---

- [x] 6. Markdown 데이터 스키마 설계 및 저장 구조

  **What to do**:
  - `data/laws/` 및 `data/precedents/` 디렉토리 생성
  - Markdown frontmatter 스키마 정의:
    - 법률: id, name, type, department, date_promulgated, date_enforced, articles_count
    - 조문: article_number, article_title (법률 파일 내 섹션으로)
    - 판례: id, case_name, case_number, court, date_judgment, judgment_type, holding, summary
  - JSON → Markdown 변환 스크립트 작성 (`backend/scripts/convert_to_md.py`)
  - 법률-판례 연결 메커니즘 설계 (참조조문 파싱)

  **Must NOT do**:
  - 복잡한 관계형 스키마 (단순화 유지)
  - 원문 텍스트를 그대로 저장하지 않고 변형

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 스키마 설계는 결정사항 기반

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 2)
  - **Blocked By**: Task 1
  - **Blocks**: Task 9

  **References**:
  - Markdown frontmatter: YAML 형식 헤더
  - korean-law-mcp 스키마: 법령ID, 조문번호, 판례일련번호 등

  **Acceptance Criteria**:
  - [ ] `data/laws/README.md` (스키마 문서)
  - [ ] `data/precedents/README.md` (스키마 문서)
  - [ ] 변환 스크립트 실행 시 Markdown 파일 생성
  - [ ] 샘플 Markdown 파일 1개 이상 (frontmatter 포함)

  **QA Scenarios**:

  ```
  Scenario: Markdown 변환 확인
    Tool: Bash
    Preconditions: 수집된 JSON 데이터 존재
    Steps:
      1. cd /root/projects/autojudge/backend
      2. python scripts/convert_to_md.py --input data/raw/laws/sample.json --output data/laws/
      3. head -20 data/laws/*.md
    Expected Result: frontmatter (---로 둘러싸인 YAML 헤더) 존재
    Failure Indicators: frontmatter 없음, 깨진 인코딩
    Evidence: .sisyphus/evidence/task-6-markdown-sample.md
  ```

  **Commit**: YES
  - Message: `feat: design markdown schema and conversion`
  - Files: `data/`, `backend/scripts/convert_to_md.py`

---

- [ ] 7. 벡터 검색을 위한 임베딩 파이프라인 (선택사항)

  **What to do**:
  - ChromaDB 또는 유사한 경량 벡터 DB 설치 (`pip install chromadb`)
  - `backend/scripts/create_embeddings.py` 작성:
    - Markdown 파일 로드
    - OpenAI Embedding API로 임베딩 생성 (text-embedding-3-small)
    - ChromaDB에 저장 (메타데이터 포함)
  - 검색 함수 구현 (`search_similar_laws`, `search_similar_precedents`)

  **Must NOT do**:
  - Pinecone 등 외부 서비스 의존 (로컬 전용 유지)
  - 임베딩 없이 단순 키워드 매칭만으로 대체 (선택사항이지만 권장)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 벡터 DB 및 임베딩 처리는 복잡도 있음

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 2)
  - **Blocked By**: Task 6
  - **Blocks**: Task 9

  **References**:
  - ChromaDB: https://docs.trychroma.com/
  - OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings

  **Acceptance Criteria**:
  - [ ] ChromaDB 설치 및 임포트 가능
  - [ ] 임베딩 생성 스크립트 실행 가능
  - [ ] 유사도 검색 함수 동작 확인

  **QA Scenarios**:

  ```
  Scenario: 벡터 검색 동작 확인
    Tool: Bash (Python)
    Preconditions: 임베딩 생성 완료
    Steps:
      1. cd /root/projects/autojudge/backend
      2. python -c "
         from search import search_similar_laws
         results = search_similar_laws('손핵배상', top_k=3)
         print(f'Found {len(results)} results')
         for r in results[:3]:
             print(f'- {r.metadata.get(\"name\", \"N/A\")}')
         "
    Expected Result: 관련 법률/판례 목록 반환 (3개)
    Failure Indicators: 빈 결과, ChromaDB 연결 에러
    Evidence: .sisyphus/evidence/task-7-vector-search.txt
  ```

  **Commit**: YES
  - Message: `feat: add vector embedding pipeline`
  - Files: `backend/scripts/create_embeddings.py`, `backend/search.py`

---

- [ ] 8. 사건 입력 API 및 모델 정의

  **What to do**:
  - `backend/models/case.py` 작성 (Pydantic 모델):
    - `CaseInput`: 사건 유형, 당사자 관계, 사실관계, 주장/항변, 증거 목록
    - `Case`: DB 저장용 (id, created_at, input_data)
  - `backend/routers/cases.py` 작성:
    - POST `/api/cases` - 사건 생성
    - GET `/api/cases/{case_id}` - 사건 조회
    - GET `/api/cases` - 사건 목록
  - 사건 유형 Enum 정의 (손핵배상, 계약위반, 부당이득 등)

  **Must NOT do**:
  - 과도한 필드 검증 (MVP에서는 기본적인 타입 체크만)
  - 복잡한 관계형 DB 스키마 (Markdown 기반 유지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 표준 Pydantic + FastAPI 라우터 작성

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 3)
  - **Blocked By**: Task 1
  - **Blocks**: Task 10, 11

  **References**:
  - Pydantic: https://docs.pydantic.dev/
  - FastAPI Routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/

  **Acceptance Criteria**:
  - [ ] `POST /api/cases`로 사건 생성 가능
  - [ ] `GET /api/cases/{id}`로 사건 조회 가능
  - [ ] 입력 데이터 검증 (필수 필드 누락 시 422)

  **QA Scenarios**:

  ```
  Scenario: 사건 생성 API 테스트
    Tool: Bash (curl)
    Preconditions: FastAPI 서버 실행
    Steps:
      1. curl -X POST http://localhost:8000/api/cases \
         -H "Content-Type: application/json" \
         -d '{
           "case_type": "손핵배상",
           "parties": "원고: A, 피고: B",
           "facts": "A가 B의 차에 치임",
           "claims": "손핵 1000만원 청구",
           "evidence": ["CCTV", "병원진단서"]
         }'
    Expected Result: HTTP 200, {"id": "...", "case_type": "손핵배상", ...}
    Failure Indicators: 422, 500, 응답에 id 없음
    Evidence: .sisyphus/evidence/task-8-create-case.json
  ```

  **Commit**: YES
  - Message: `feat: add case input API`
  - Files: `backend/models/case.py`, `backend/routers/cases.py`

---

- [ ] 9. 법률/판례 검색 API (RAG)

  **What to do**:
  - `backend/services/search.py` 작성:
    - 사건 입력을 기반으로 검색 쿼리 생성 (LLM 활용 또는 키워드 추출)
    - Markdown 데이터에서 관련 법률/판례 검색
    - 결과 랭킹 및 필터링
  - `backend/routers/search.py` 작성:
    - POST `/api/search` - 사건 기반 검색
    - 쿼리 파라미터: case_id, top_k (기본값 5)
  - 검색 결과 포맷: 법률/판례 목록 + 관련성 점수 + 인용 텍스트

  **Must NOT do**:
  - 외부 검색 API 사용 (로컬 데이터만 사용)
  - 검색 결과 없을 때 가짜 결과 반환

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: RAG 로직 구현은 정확성 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 3)
  - **Blocked By**: Tasks 5, 6, 7
  - **Blocks**: Task 10, 11

  **References**:
  - Task 7의 벡터 검색 함수 활용
  - Task 6의 Markdown 스키마 참조

  **Acceptance Criteria**:
  - [ ] `POST /api/search`로 검색 가능
  - [ ] 검색 결과에 법률/판례 포함 (최소 1개)
  - [ ] 결과에 인용 텍스트 및 출처 포함

  **QA Scenarios**:

  ```
  Scenario: 사건 기반 검색 테스트
    Tool: Bash (curl)
    Preconditions: 사건 생성됨, 법률/판례 데이터 존재
    Steps:
      1. curl -X POST http://localhost:8000/api/search \
         -H "Content-Type: application/json" \
         -d '{"case_id": "...", "top_k": 3}'
    Expected Result: {"laws": [...], "precedents": [...], "query": "..."}
    Failure Indicators: 빈 결과, 500 에러
    Evidence: .sisyphus/evidence/task-9-search-results.json
  ```

  **Commit**: YES
  - Message: `feat: add law/precedent search API`
  - Files: `backend/services/search.py`, `backend/routers/search.py`

---

- [ ] 10. 시나리오 생성 API (GPT-4.1 연동)

  **What to do**:
  - `backend/services/scenario.py` 작성:
    - 프롬프트 템플릿 설계 (시스템 프롬프트 + 사용자 입력 + 검색 결과)
    - OpenRouter API 호출 (OpenAI SDK 호환, base_url: https://openrouter.ai/api/v1)
    - 모델 선택 가능 (openai/gpt-4.1, anthropic/claude-sonnet-4 등)
    - 응답 파싱 및 구조화 (JSON 모드 사용)
  - 시나리오 출력 형식 정의:
    - title: 시나리오 제목
    - interpretation: 법적 해석 설명
    - basis: 근거 법률/판례 목록
    - probability: 발생 가능성 (고/중/저)
    - key_factors: 핵심 쟁점
  - `backend/routers/scenarios.py` 작성:
    - POST `/api/scenarios` - 시나리오 생성 (case_id 받아서)
    - GET `/api/scenarios/{scenario_id}` - 시나리오 조회

  **Must NOT do**:
  - 근거 없는 법률/판례 인용 (검색 결과 기반만 사용)
  - "승소/패소" 확정적 표현 ("이렇게 해석될 수 있다" 사용)
  - API 키를 코드에 하드코딩

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: LLM 프롬프트 엔지니어링 및 API 연동은 정교함 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 3)
  - **Blocked By**: Tasks 8, 9
  - **Blocks**: Tasks 12, 13

  **References**:
  - OpenAI API: https://platform.openai.com/docs/api-reference/chat/create
  - JSON Mode: https://platform.openai.com/docs/guides/structured-outputs

  **Acceptance Criteria**:
  - [ ] 시나리오 생성 API 동작 (GPT-4.1 호출)
  - [ ] 응답에 title, interpretation, basis, probability 포함
  - [ ] 3개의 시나리오 생성 가능
  - [ ] 모든 시나리오에 "법률 자문 아님" 고지 포함

  **QA Scenarios**:

  ```
  Scenario: 시나리오 생성 테스트
    Tool: Bash (curl)
    Preconditions: OPENAI_API_KEY 설정, 사건 생성됨
    Steps:
      1. curl -X POST http://localhost:8000/api/scenarios \
         -H "Content-Type: application/json" \
         -d '{"case_id": "...", "count": 3}'
      2. 응답에서 scenarios[0].title, interpretation, basis 확인
      3. 응답에 "법률 자문" 또는 "참고용" 문구 포함 확인
    Expected Result: HTTP 200, scenarios 배열 (길이 3), 각 시나리오에 필수 필드 존재
    Failure Indicators: 500, 빈 scenarios, basis 없음
    Evidence: .sisyphus/evidence/task-10-scenarios.json
  ```

  **Commit**: YES
  - Message: `feat: add scenario generation with GPT-4.1`
  - Files: `backend/services/scenario.py`, `backend/routers/scenarios.py`

---

- [ ] 11. What-If API (변수 변경 및 재생성)

  **What to do**:
  - `backend/models/whatif.py` 작성:
    - `WhatIfRequest`: 변경할 변수 (사실관계, 증거, 주장 중 1-2개)
    - `WhatIfComparison`: 원본 vs 변경 시나리오 비교
  - `backend/routers/whatif.py` 작성:
    - POST `/api/whatif` - What-If 시나리오 생성
    - GET `/api/whatif/{comparison_id}` - 비교 결과 조회
  - 비교 로직 구현:
    - 원본 사건 복사 + 변수 변경
    - 변경된 사건으로 새 시나리오 생성
    - 원본 vs 변경 차이점 분석

  **Must NOT do**:
  - 3개 이상 변수 동시 변경 허용 (복잡도 관리)
  - 원본 사건 데이터 덮어쓰기

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 비교 로직 및 API 설계 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 3)
  - **Blocked By**: Tasks 8, 9
  - **Blocks**: Task 14

  **References**:
  - Task 10의 시나리오 생성 로직 재사용

  **Acceptance Criteria**:
  - [ ] What-If API로 변수 변경 가능
  - [ ] 변경된 시나리오 생성 가능
  - [ ] 원본 vs 변경 비교 결과 제공

  **QA Scenarios**:

  ```
  Scenario: What-If 생성 테스트
    Tool: Bash (curl)
    Preconditions: 원본 시나리오 생성됨
    Steps:
      1. curl -X POST http://localhost:8000/api/whatif \
         -H "Content-Type: application/json" \
         -d '{
           "original_scenario_id": "...",
           "changes": {"evidence": ["CCTV", "병원진단서", "목격자증언"]}
         }'
    Expected Result: HTTP 200, {original: {...}, modified: {...}, differences: "..."}
    Failure Indicators: 500, changes 반영 안 됨
    Evidence: .sisyphus/evidence/task-11-whatif.json
  ```

  **Commit**: YES
  - Message: `feat: add what-if scenario generation`
  - Files: `backend/models/whatif.py`, `backend/routers/whatif.py`

---

- [ ] 12. 사건 입력 폼 컴포넌트 (5개 필드)

  **What to do**:
  - `frontend/src/views/CaseInput.vue` 작성:
    - 5개 입력 필드: 사건 유형(드롭다운), 당사자 관계, 사실관계(텍스트영역), 주장/항변(텍스트영역), 증거 목록(태그 입력)
    - 폼 검증 (필수 필드)
    - 제출 버튼 및 로딩 상태
  - `frontend/src/components/CaseForm.vue` (재사용 가능한 컴포넌트)
  - Pinia store에 폼 상태 관리 (`stores/case.ts`)

  **Must NOT do**:
  - 복잡한 WYSIWYG 에디터 (기본 textarea로 충분)
  - 파일 업로드 기능 (v1 범위 밖)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []
  - **Reason**: Vue 컴포넌트 및 UI/UX 구현

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 4)
  - **Blocked By**: Tasks 3, 10
  - **Blocks**: Task 15

  **References**:
  - Vue 3 Composition API: https://vuejs.org/guide/extras/composition-api-faq.html
  - Vuetify Form Components: https://vuetifyjs.com/en/components/forms/

  **Acceptance Criteria**:
  - [ ] 5개 필드 모두 입력 가능
  - [ ] 필수 필드 검증 (누락 시 에러 메시지)
  - [ ] 제출 시 API 호출 및 로딩 상태 표시

  **QA Scenarios**:

  ```
  Scenario: 사건 입력 폼 테스트
    Tool: Playwright
    Preconditions: Vue 개발 서버 실행
    Steps:
      1. http://localhost:3000/case/new 접속
      2. 사건 유형: "손핵배상" 선택
      3. 당사자: "원고: A, 피고: B" 입력
      4. 사실관계: "사고 발생" 입력
      5. 주장: "손핵 1000만원" 입력
      6. 증거: "CCTV" 입력 후 Enter
      7. 제출 버튼 클릭
      8. 로딩 스피너 확인
      9. 결과 페이지로 이동 확인
    Expected Result: 모든 필드 입력 가능, 제출 시 로딩 표시, 결과 페이지로 네비게이션
    Failure Indicators: 필드 누락, 검증 에러 없음, 제출 실패
    Evidence: .sisyphus/evidence/task-12-case-form.png (스크린샷)
  ```

  **Commit**: YES
  - Message: `feat: add case input form component`
  - Files: `frontend/src/views/CaseInput.vue`, `frontend/src/components/CaseForm.vue`

---

- [ ] 13. 시나리오 결과 뷰 컴포넌트

  **What to do**:
  - `frontend/src/views/ScenarioResult.vue` 작성:
    - Top3 시나리오 카드 형태로 표시
    - 각 시나리오: 제목, 해석 설명, 근거 법률/판례 (링크), 발생 가능성
    - "법률 자문 아님" 고지 배너
    - What-If 버튼 (각 시나리오별)
  - `frontend/src/components/ScenarioCard.vue` (재사용)
  - 법률/판례 상세 모달/Drawer

  **Must NOT do**:
  - 승소/패소 확률을 %로 표시 (해석 가능성만 표시)
  - 과도한 시각화 (차트 등)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []
  - **Reason**: 결과 표시 UI 구현

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 4)
  - **Blocked By**: Tasks 3, 10
  - **Blocks**: Task 15

  **References**:
  - Vuetify Cards: https://vuetifyjs.com/en/components/cards/
  - Vuetify Alerts (고지용): https://vuetifyjs.com/en/components/alerts/

  **Acceptance Criteria**:
  - [ ] 3개 시나리오 모두 표시
  - [ ] 각 시나리오에 title, interpretation, basis 표시
  - [ ] "법률 자문 아님" 고지 표시
  - [ ] What-If 버튼 존재

  **QA Scenarios**:

  ```
  Scenario: 시나리오 결과 표시 테스트
    Tool: Playwright
    Preconditions: 시나리오 생성됨, 결과 페이지 접속
    Steps:
      1. http://localhost:3000/scenarios/{id} 접속
      2. 시나리오 카드 3개 존재 확인
      3. 첫 번째 카드 클릭 → 상세 내용 확인
      4. "법률 자문" 텍스트 확인 (배너 또는 카드 내)
      5. What-If 버튼 클릭 → What-If 페이지 이동 확인
    Expected Result: 3개 카드 표시, 고지 문구 존재, What-If 네비게이션 동작
    Failure Indicators: 시나리오 부족, 고지 문구 누락
    Evidence: .sisyphus/evidence/task-13-scenario-view.png
  ```

  **Commit**: YES
  - Message: `feat: add scenario result view component`
  - Files: `frontend/src/views/ScenarioResult.vue`, `frontend/src/components/ScenarioCard.vue`

---

- [ ] 14. What-If 인터페이스 컴포넌트

  **What to do**:
  - `frontend/src/views/WhatIf.vue` 작성:
    - 원본 시나리오 요약 표시
    - 변경 가능한 변수 선택 (라디오/체크박스): 사실관계, 증거, 주장
    - 선택된 변수 입력 폼 (동적)
    - 변경 적용 버튼 및 새 시나리오 생성
    - 원본 vs 변경 비교 뷰 (Side-by-side)
  - 변경 이력 저장 (선택사항)

  **Must NOT do**:
  - 3개 이상 변수 동시 변경 UI 허용
  - 변경사항 자동 저장 (명확한 제출 액션 필요)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []
  - **Reason**: 비교 UI 및 동적 폼 구현

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 4)
  - **Blocked By**: Tasks 3, 11
  - **Blocks**: Task 15

  **References**:
  - Task 11의 What-If API 스키마 참조

  **Acceptance Criteria**:
  - [ ] 원본 시나리오 표시
  - [ ] 변수 변경 UI (1-2개 선택 가능)
  - [ ] 변경 후 새 시나리오 생성
  - [ ] 원본 vs 변경 비교 표시

  **QA Scenarios**:

  ```
  Scenario: What-If 인터페이스 테스트
    Tool: Playwright
    Preconditions: 원본 시나리오 존재
    Steps:
      1. What-If 페이지 접속
      2. "증거" 변수 선택
      3. 증거 목록에 "목격자증언" 추가
      4. "새 시나리오 생성" 클릭
      5. 원본 vs 변경 비교 화면 확인
      6. differences 텍스트 존재 확인
    Expected Result: 비교 화면 표시, differences 내용 존재
    Failure Indicators: 변경 미반영, 비교 화면 없음
    Evidence: .sisyphus/evidence/task-14-whatif-view.png
  ```

  **Commit**: YES
  - Message: `feat: add what-if interface component`
  - Files: `frontend/src/views/WhatIf.vue`

---

- [ ] 15. 프론트엔드-백엔드 연동 (API 클라이언트)

  **What to do**:
  - `frontend/src/api/client.ts` 작성 (axios 기반):
    - 기본 URL 설정 (VITE_API_BASE_URL)
    - 에러 핸들링 (401, 500 등)
    - 요청/응답 인터셉터
  - `frontend/src/api/cases.ts`, `scenarios.ts`, `whatif.ts` 작성
  - Pinia store에서 API 호출 연동
  - CORS 설정 확인 (백엔드-프론트엔드)

  **Must NOT do**:
  - API 응답을 store에 직접 저장하지 않고 컴포넌트 내부에서 관리

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 표준 API 클라이언트 설정

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 5)
  - **Blocked By**: Tasks 12, 13, 14
  - **Blocks**: Tasks F1-F3

  **References**:
  - Axios: https://axios-http.com/docs/intro
  - Pinia: https://pinia.vuejs.org/

  **Acceptance Criteria**:
  - [ ] 프론트엔드에서 백엔드 API 호출 가능
  - [ ] CORS 에러 없음
  - [ ] 응답 데이터가 Vue 컴포넌트에 표시됨

  **QA Scenarios**:

  ```
  Scenario: E2E 연동 테스트
    Tool: Playwright
    Preconditions: 백엔드, 프론트엔드 모두 실행
    Steps:
      1. http://localhost:3000/case/new 접속
      2. 폼 입력 및 제출
      3. 네트워크 탭에서 API 호출 확인 (200)
      4. 결과 페이지에서 시나리오 표시 확인
    Expected Result: API 호출 성공, 데이터 표시
    Failure Indicators: CORS 에러, 500, 빈 화면
    Evidence: .sisyphus/evidence/task-15-integration.png
  ```

  **Commit**: YES
  - Message: `feat: connect frontend with backend API`
  - Files: `frontend/src/api/`, `frontend/src/stores/`

---

- [ ] 16. 법적 책임 고지 및 안내 문구 추가

  **What to do**:
  - 모든 결과 페이지에 "법률 자문 아님" 고지 배너 추가
  - 홈페이지에 사용 안내 및 제한사항 표시
  - README.md에 법적 고지 섹션 추가
  - API 응답에도 고지 문구 포함 (Task 10에서 이미 처리되어야 함)
  - `/terms` 페이지 생성 (이용약관)

  **Must NOT do**:
  - 고지 문구를 작은 글씨/숨은 곳에 배치
  - 법률 자문으로 오인될 수 있는 표현 사용

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 문구 작성 및 UI 추가

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 5)
  - **Blocked By**: Tasks 12, 13

  **Acceptance Criteria**:
  - [ ] 모든 결과 페이지에 고지 배너 존재
  - [ ] 홈페이지에 제한사항 안내 존재
  - [ ] README에 법적 고지 섹션 존재

  **QA Scenarios**:

  ```
  Scenario: 법적 고지 확인
    Tool: Playwright
    Preconditions: 앱 실행
    Steps:
      1. http://localhost:3000/ 접속 → 홈페이지 고지 확인
      2. 사건 입력 → 결과 페이지 접속 → 배너 고지 확인
      3. "법률 자문" 또는 "참고용" 텍스트 검색
    Expected Result: 모든 페이지에서 고지 문구 확인 가능
    Failure Indicators: 고지 문구 누락
    Evidence: .sisyphus/evidence/task-16-disclaimer.png
  ```

  **Commit**: YES
  - Message: `feat: add legal disclaimer throughout the app`
  - Files: `frontend/src/views/`, `README.md`

---

- [ ] 17. 통합 테스트 및 샘플 사건 검증

  **What to do**:
  - 샘플 사건 3건 준비:
    1. 손핵배상 (교통사고)
    2. 계약위반 (임대차)
    3. 부당이득
  - 각 사건으로 E2E 테스트 수행
  - 결과 평가표 작성:
    - 관련성: 생성된 시나리오가 사건과 관련 있는가?
    - 설명성: 법적 해석이 명확한가?
    - 인용 정확성: 법률/판례 인용이 실제 존재하는가?
  - 문제점 기록 및 개선

  **Must NOT do**:
  - 실제 사건/당사자 정보 사용 (가상 데이터만)
  - 자동화된 테스트 없이 수동 테스트만 (MVP에서는 수동 허용)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 테스트 케이스 설계 및 평가

  **Parallelization**:
  - **Can Run In Parallel**: YES (웨이브 5)
  - **Blocked By**: Task 15

  **Acceptance Criteria**:
  - [ ] 3개 샘플 사건 테스트 완료
  - [ ] 평가표 작성 (관련성/설명성/인용 정확성)
  - [ ] 주요 버그/개선사항 기록

  **QA Scenarios**:

  ```
  Scenario: 샘플 사건 1 - 손핵배상 테스트
    Tool: Playwright + 수동 평가
    Preconditions: 전체 앱 실행
    Steps:
      1. 사건 입력: 교통사고 손핵배상 청구
      2. 시나리오 생성 확인
      3. 결과 평가:
         - 관련성: 민법 제750조(불법행위) 언급 확인
         - 설명성: 손핵액 산정 근거 설명 확인
         - 인용 정확성: 인용된 판례 실제 존재 확인
    Expected Result: 3개 시나리오 생성, 민법 제750조 언급, 실제 판례 인용
    Failure Indicators: 무관한 법조 인용, 가짜 판례
    Evidence: .sisyphus/evidence/task-17-sample-test.md (평가표)
  ```

  **Commit**: YES
  - Message: `test: add integration tests with sample cases`
  - Files: `docs/test-cases.md`, 샘플 테스트 결과

---

## Final Verification Wave (모든 작업 완료 후)

> 모든 구현 작업 완료 후 병렬로 실행되는 검증 작업들

- [ ] F1. 전체 플로우 E2E 테스트

  **What to do**:
  - end-to-end 시나리오 테스트:
    1. 사건 입력 페이지 접속
    2. 모든 필드 입력 및 제출
    3. 검색 결과 확인
    4. Top3 시나리오 생성 확인
    5. What-If 실행 및 비교 확인
  - 각 단계별 스크린샷 및 로그 수집
  - 실패 지점 기록

  **Recommended Agent Profile**:
  - **Category**: `oracle`
  - **Skills**: []
  - **Reason**: 전체 시스템 관점에서 검증

  **QA Scenarios**:

  ```
  Scenario: 완전한 사용자 플로우
    Tool: Playwright
    Preconditions: 전체 앱 실행 (backend + frontend)
    Steps:
      1. http://localhost:3000 접속
      2. "새 사건 시작" 클릭
      3. 사건 입력 폼 작성 (5개 필드)
      4. 제출 → 로딩 확인
      5. 결과 페이지 (시나리오 3개) 확인
      6. 첫 번째 시나리오 What-If 클릭
      7. 증거 변수 변경
      8. 새 시나리오 생성
      9. 비교 결과 확인
    Expected Result: 전체 플로우 오류 없이 완료
    Failure Indicators: 중간 단계 실패, 500 에러
    Evidence: .sisyphus/evidence/f1-e2e-flow/ (스크린샷 시퀀스)
  ```

  **Commit**: NO (검증 작업)

---

- [ ] F2. 코드 품질 리뷰 및 문서화

  **What to do**:
  - Python 코드: `ruff check backend/` (또는 flake8)
  - TypeScript 코드: `npm run lint` (frontend)
  - Type checking: `mypy backend/`, `vue-tsc --noEmit` (frontend)
  - 문서화 확인:
    - API 엔드포인트 목록
    - 데이터 스키마 설명
    - 환경 설정 가이드
    - 실행 방법

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 코드 품질 및 문서화 검증

  **Acceptance Criteria**:
  - [ ] 린트 에러 0개 (또는 최소화)
  - [ ] 타입 에러 0개
  - [ ] README.md 완성
  - [ ] API 문서 존재

  **QA Scenarios**:

  ```
  Scenario: 코드 품질 확인
    Tool: Bash
    Preconditions: 의존성 설치 완료
    Steps:
      1. cd /root/projects/autojudge/backend && ruff check . 2>&1 | head -20
      2. cd /root/projects/autojudge/frontend && npm run lint 2>&1 | tail -10
      3. cat README.md | head -50
    Expected Result: 린트 에러 없음 또는 경미함, README 존재
    Failure Indicators: 치명적인 린트 에러, README 누락
    Evidence: .sisyphus/evidence/f2-quality-check.txt
  ```

  **Commit**: 선택적 (문서화 개선 시)

---

- [ ] F3. 사용자 가이드 작성

  **What to do**:
  - `docs/user-guide.md` 작성:
    - 설치 방법 (설치 스크립트 또는 수동)
    - 실행 방법 (개발 모드)
    - 사용 방법 (사건 입력 → 결과 확인 → What-If)
    - 주의사항 및 제한사항
    - FAQ
  - 스크린샷 포함
  - 샘플 사건 예시 포함

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []
  - **Reason**: 사용자 문서 작성

  **Acceptance Criteria**:
  - [ ] 설치/실행 가이드 존재
  - [ ] 사용 방법 설명 존재
  - [ ] 샘플 사건 예시 존재

  **QA Scenarios**:

  ```
  Scenario: 가이드 완성도 확인
    Tool: Read (file)
    Preconditions: docs/user-guide.md 존재
    Steps:
      1. cat docs/user-guide.md | grep -E "(설치|실행|사용|FAQ)" | wc -l
      2. ls docs/images/ | wc -l (스크린샷 존재 확인)
    Expected Result: 모든 섹션 존재, 스크린샷 3개 이상
    Failure Indicators: 주요 섹션 누락
    Evidence: .sisyphus/evidence/f3-user-guide.md
  ```

  **Commit**: YES
  - Message: `docs: add comprehensive user guide`
  - Files: `docs/user-guide.md`

---

## Commit Strategy

### 커밋 메시지 컨벤션
- `feat: ...` - 새로운 기능
- `chore: ...` - 설정, 의존성, 기타
- `docs: ...` - 문서
- `test: ...` - 테스트

### 브랜치 전략
- `main`: 안정 버전
- `feature/*`: 기능 개발 (예: `feature/case-input-api`)
- PR 머지 후 브랜치 삭제

### 커밋 그룹핑
- 웨이브별로 커밋 그룹핑
- 관련 파일끼리 묶어서 커밋
- 대형 커밋 피하기 (50라인 이상)

---

## Success Criteria

### 최종 검증 명령어

```bash
# 1. 백엔드 실행
cd /root/projects/autojudge/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. 프론트엔드 실행
cd /root/projects/autojudge/frontend
npm run dev &

# 3. API 테스트
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d '{"case_type": "손핵배상", "parties": "A vs B", "facts": "사고", "claims": "1000만원", "evidence": ["CCTV"]}'
# Expected: {"id": "...", ...}

# 4. 프론트엔드 접속
curl http://localhost:3000
# Expected: HTML 응답
```

### 최종 체크리스트
- [ ] 모든 Must Have 기능 구현
- [ ] 모든 Must NOT Have 준수
- [ ] 모든 TODO 완료 및 QA 시나리오 통과
- [ ] Final Verification Wave 완료
- [ ] 사용자 확인 및 승인

---

## 결정 사항 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| **도메인** | 민사 (손핵배상, 계약) | 사법 리스크 낮음, 데이터 풍부 |
| **출력 형식** | 법적 해석형 | "법률 자문" 오인 방지 |
| **AI 모델** | OpenRouter (GPT-4.1/Claude 등) | 단일 API 키로 다양한 모델 사용 가능, 비용 효율적 |
| **데이터 전략** | 초기 일회성 수집, **판례는 2024년까지만** | 2025년은 성능 평가용 테스트 세트로 활용 |
| **입력 방식** | 폼 기반 (5필드) | 구조화된 데이터, 처리 용이 |
| **DB** | Markdown 기반 | AI-friendly, 버전 관리 용이 |

---

## 실행 방법

플랜이 준비되었습니다. 다음 명령어로 작업을 시작하세요:

```bash
/start-work
```

또는:

```bash
cd /root/projects/autojudge
# Sisyphus가 플랜을 로드하고 작업을 시작합니다
```

