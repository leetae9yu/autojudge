# Learnings

- 프로젝트 루트는 이미 존재했으며, Git 저장소만 초기화하면 됐습니다.
- 초기 브랜치는 master로 생성되었습니다.
- 기본 구조는 backend/frontend/data/docs로 분리했습니다.
- frontend는 Vite 기본 스캐폴드 위에 Vuetify와 @mdi/font을 붙였고, dev 포트를 3000으로 고정했습니다.
- Vue Router는 /, /case, /case/new, /case/:id, /result, /scenarios/:id, /whatif/:id 로 정리했습니다.
- env.d.ts에 .vue 및 vuetify/styles 타입 선언을 추가해야 vue-tsc가 통과했습니다.
- backend 설정은 Pydantic Settings로 로드되도록 구성하고, `.env.example`로 검증 가능하게 했습니다.
- backend용 venv는 `--system-site-packages`로 만들면 기존 전역 패키지를 재사용해 빠르게 QA할 수 있습니다.
