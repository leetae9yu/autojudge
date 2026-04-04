## 2026-04-04

- Used a dedicated Pinia store (`frontend/src/stores/case.ts`) to centralize form state, validation, loading state, and POST `/api/cases` submission instead of scattering fetch logic across the view and form component.
- Kept success navigation on the view layer (`CaseInput.vue`) so the reusable form component emits the created case record and stays focused on collection + submission UX.
- Matched the dropdown options to the backend enum (`손해배상`, `계약위반`, `부당이득`) so the form submits valid payloads to the existing FastAPI endpoint.
- Bound `/scenarios/:id` to a dedicated `ScenarioResult.vue` view instead of a placeholder route generator so the scenario result page can own mock Top3 presentation now and accept real API wiring later.
- Sent each What-If CTA to `/whatif/:id` using the current case id plus a `scenario` query parameter, which keeps compatibility with the current WhatIf page loader while preserving per-card origin context.
- Chose always-on amber `v-alert` banners in App/layout and page views rather than dismissible notices so the legal notice cannot be permanently hidden.
- Centralized backend access in `frontend/src/api/*` with an Axios client rooted at `VITE_API_BASE_URL`, then wired stores/views to those helpers so error handling stays consistent.
- Included the search and what-if routers in `backend/main.py` so the new client modules can actually reach the mounted FastAPI endpoints.
