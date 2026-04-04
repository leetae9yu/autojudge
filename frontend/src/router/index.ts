import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { defineComponent, h } from 'vue'

const makePage = (title: string, description: string) =>
  defineComponent({
    name: title.replace(/\s+/g, '') + 'Page',
    props: {
      id: {
        type: String,
        default: '',
      },
    },
    setup: props => () =>
      h('section', { class: 'page-shell' }, [
        h('h1', title),
        h('p', description),
        props.id ? h('p', `ID: ${props.id}`) : null,
      ]),
  })

const HomePage = makePage('홈', '사건과 시나리오를 시작하세요.')
const CasePage = makePage('사건 입력', '새 사건을 등록하거나 기존 사건을 확인합니다.')
const CaseDetailPage = makePage('사건 상세', '사건 상세 정보를 보여줍니다.')
const ResultPage = makePage('결과', '시나리오와 판정 결과를 확인합니다.')
const ScenarioResultPage = makePage('시나리오 결과', '시나리오별 결과를 확인합니다.')
const WhatIfPage = makePage('What-If', '대안 시나리오를 검토합니다.')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/case', name: 'case', component: CasePage },
    { path: '/case/new', name: 'case-new', component: CasePage },
    {
      path: '/case/:id',
      name: 'case-detail',
      component: CaseDetailPage,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
    { path: '/result', name: 'result', component: ResultPage },
    {
      path: '/scenarios/:id',
      name: 'scenario-result',
      component: ScenarioResultPage,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
    {
      path: '/whatif/:id',
      name: 'whatif',
      component: WhatIfPage,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
  ] satisfies RouteRecordRaw[],
})

export default router
