# AutoJudge - 재판 시뮬레이터

> 한국 법률 기반 AI 재판 시뮬레이터 | 법령·판례를 활용한 What-If 시나리오 생성

특정 사건을 입력하면 관련 법령과 판례를 분석하여 가능한 **법적 해석 시나리오 Top3**를 제공하고, 변수를 변경해가며 다양한 결과를 탐색할 수 있는 재판 시뮬레이터입니다.

⚠️ **본 서비스는 법률 자문을 제공하지 않습니다.** 생성된 시나리오는 참고용이며, 실제 법적 결정은 반드시 변호사와 상담하십시오.

## 🎯 주요 기능

- **사건 입력**: 사건 유형, 당사자 관계, 사실관계, 주장/항변, 증거 목록 입력
- **법률/판례 검색**: 입력된 사건과 관련된 법률 및 판례 자동 검색
- **시나리오 생성**: GPT-4.1 기반으로 가능한 법적 해석 시나리오 Top3 생성
- **What-If 분석**: 변수(사실관계, 증거, 주장) 변경 후 결과 비교

## 🛠 기술 스택

### Backend
- **FastAPI** - Python 웹 프레임워크
- **OpenRouter** - LLM API (GPT-4.1, Claude 등 지원)
- **Pydantic** - 데이터 검증 및 설정 관리

### Frontend
- **Vue 3** + **TypeScript** - 프레임워크
- **Vuetify** - UI 컴포넌트
- **Pinia** - 상태 관리
- **Axios** - API 클라이언트

### Data
- **korean-law-mcp** - 국가법령정보센터 Open API 연동
- **Markdown** - 법률/판례 데이터 저장 형식

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/USERNAME/autojudge.git
cd autojudge
```

### 2. 환경 설정

#### Backend

```bash
cd backend
cp .env.example .env
# .env 파일 수정
```

`.env` 파일:
```env
# OpenRouter API 키 (필수)
# https://openrouter.ai/keys 에서 발급
OPENROUTER_API_KEY=sk-or-v1-여기에_실제_키_입력

# 모델 선택 (선택사항, 기본값: openai/gpt-4.1)
# OPENROUTER_MODEL=anthropic/claude-sonnet-4

# Korean Law MCP (선택사항)
# 새로운 법률/판례 데이터 수집 시에만 필요
# LAW_API_KEY=your_law_api_key_here
```

#### Frontend

```bash
cd frontend
cp .env.example .env
# 기본값으로 두어도 됩니다
```

### 3. 실행

#### Backend 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

서버가 http://localhost:8000 에서 실행됩니다.

#### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

앱이 http://localhost:3000 에서 실행됩니다.

### 4. 브라우저에서 접속

http://localhost:3000 에 접속하여 사용을 시작하세요!

## 📖 사용 방법

### 1. 사건 입력

- **사건 유형**: 손핵배상, 계약위반, 부당이득 중 선택
- **당사자 관계**: 원고/피고 관계 입력 (예: "원고: A, 피고: B")
- **사실관계**: 사건의 구체적인 사실 입력
- **주장/항변**: 원고의 주장 및 피고의 항변 입력
- **증거 목록**: CCTV, 계약서, 문자메시지 등 증거 추가

### 2. 시나리오 확인

제출 후 AI가 관련 법률/판례를 검색하고 **3가지 법적 해석 시나리오**를 생성합니다:

- **시나리오 제목**: 해당 해석의 핵심
- **법적 해석**: 상세 설명
- **근거**: 인용된 법률 및 판례
- **발생 가능성**: 고/중/저
- **핵심 쟁점**: 주요 논점

### 3. What-If 분석

각 시나리오에서 **What-If** 버튼을 클릭하여:

- 사실관계 수정
- 증거 추가/삭제
- 주장 변경

변수를 변경하여 새로운 시나리오를 생성하고 원본과 비교할 수 있습니다.

## 📊 데이터 수집 (선택사항)

기본 샘플 데이터 외에 실제 법률/판례 데이터를 수집하려면:

1. [국가법령정보센터](https://open.law.go.kr/)에서 API 인증키 신청
2. `.env`에 `LAW_API_KEY` 설정
3. 데이터 수집 스크립트 실행:

```bash
cd backend
source venv/bin/activate

# 법률 수집
python scripts/collect_laws.py --keyword "민법" --limit 10

# 판례 수집 (2024년까지만)
python scripts/collect_precedents.py --keyword "손핵배상" --limit 10
```

## 🧪 테스트

```bash
cd backend
source venv/bin/activate
pytest test_integration.py -v
```

## ⚙️ 환경변수

| 변수명 | 설명 | 필수 여부 |
|--------|------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API 키 | ✅ 필수 |
| `OPENROUTER_MODEL` | 사용할 LLM 모델 | ❌ 선택 (기본: openai/gpt-4.1) |
| `LAW_API_KEY` | 국가법령정보센터 API 키 | ❌ 선택 (데이터 수집 시) |

### 지원하는 모델 (OpenRouter)

- `openai/gpt-4.1` (기본)
- `anthropic/claude-sonnet-4`
- `google/gemini-pro`
- 기타 OpenRouter 지원 모델

## ⚠️ 주의사항

1. **법률 자문 아님**: 본 서비스는 법률 자문을 제공하지 않습니다. 생성된 시나리오는 참고용이며, 실제 법적 결정은 반드시 변호사와 상담하십시오.

2. **API 비용**: OpenRouter API 사용 시 비용이 발생할 수 있습니다. 사용량을 모니터링하세요.

3. **데이터 정확성**: AI가 생성한 내용은 항상 정확하지 않을 수 있습니다. 중요한 결정 전에 반드시 전문가와 상담하세요.

## 🏗 프로젝트 구조

```
autojudge/
├── backend/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 설정 (Pydantic)
│   ├── models/              # 데이터 모델
│   │   ├── case.py
│   │   └── whatif.py
│   ├── routers/             # API 라우터
│   │   ├── cases.py
│   │   ├── scenarios.py
│   │   ├── search.py
│   │   └── whatif.py
│   ├── services/            # 비즈니스 로직
│   │   ├── scenario.py      # 시나리오 생성
│   │   └── search.py        # 법률/판례 검색
│   ├── scripts/             # 데이터 수집 스크립트
│   │   ├── collect_laws.py
│   │   ├── collect_precedents.py
│   │   └── convert_to_md.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # 페이지 컴포넌트
│   │   │   ├── CaseInput.vue
│   │   │   ├── ScenarioResult.vue
│   │   │   └── WhatIf.vue
│   │   ├── components/      # 재사용 컴포넌트
│   │   │   ├── CaseForm.vue
│   │   │   └── ScenarioCard.vue
│   │   ├── api/             # API 클라이언트
│   │   │   ├── client.ts
│   │   │   ├── cases.ts
│   │   │   ├── scenarios.ts
│   │   │   └── whatif.ts
│   │   └── stores/          # Pinia 스토어
│   └── package.json
└── README.md
```

## 🤝 기여

이 프로젝트는 개인적인 학습 및 MVP 개발을 위한 것입니다. 버그 리포트 및 개선 제안은 Issues에 남겨주세요.

## 📜 라이선스

MIT License

## 🙏 감사의 글

- [국가법령정보센터](https://www.law.go.kr/) - 법률/판례 데이터 제공
- [OpenRouter](https://openrouter.ai/) - LLM API 제공
- [korean-law-mcp](https://github.com/SeoNaRu/korean-law-mcp) - 법률 데이터 수집 도구

---

<div align="center">
  <sub>Built with ❤️ for legal tech exploration</sub>
</div>
