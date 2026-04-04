## 2026-04-04

- Task 12 UI is now routed through `/case` and `/case/new`, with `/` redirecting to the case intake flow so the structured form is the default landing experience.
- The frontend had only Vue/Vite starter styles, so a small token-based design system was introduced in `frontend/src/assets/base.css` and `main.css` to provide reusable color, spacing, radius, shadow, and typography primitives.
- Vuetify `v-combobox` with `multiple` chips works well for the evidence list because it preserves the backend payload shape (`string[]`) while satisfying the chip-based UX requirement.
- Task 13 scenario output works best as a three-card responsive grid with a shared `ScenarioCard` component so title, interpretation, basis chips, key factors, and CTA layout stay visually consistent.
- The existing token-based design system from Task 12 was sufficient for the result view, so the new scenario UI could reuse the same `font-display`, spacing, surface, border, and shadow primitives without introducing ad-hoc styles.
- Added a single Korean disclaimer string across frontend banners and backend API response models to keep copy consistent.
- Axios response interceptors are a clean place to normalize network, 422, and 500 errors into the exact Korean messages the UI needs (`연결 실패`, validation text, `서버 오류`).
- The scenario result view can stay card-based by converting backend citation strings into the existing `ScenarioCard` authority shape at the edge of the API layer.
