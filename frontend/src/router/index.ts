import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { defineComponent, h } from 'vue'

import CaseInputView from '../views/CaseInput.vue'
import ScenarioResultView from '../views/ScenarioResult.vue'
import WhatIfView from '../views/WhatIf.vue'

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

const CaseDetailPage = makePage('사건 상세', '사건 상세 정보를 보여줍니다.')
const ResultPage = makePage('결과', '시나리오와 판정 결과를 확인합니다.')
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: 'case-new' } },
    { path: '/case', name: 'case', component: CaseInputView },
    { path: '/case/new', name: 'case-new', component: CaseInputView },
    {
      path: '/case/:id',
      name: 'case-detail',
      component: CaseDetailPage,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
    {
      path: '/result',
      name: 'result',
      component: ResultPage,
      props: route => ({ id: String(route.query.caseId ?? '') }),
    },
    {
      path: '/scenarios/:id',
      name: 'scenario-result',
      component: ScenarioResultView,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
    {
      path: '/whatif/:id',
      name: 'whatif',
      component: WhatIfView,
      props: route => ({ id: String(route.params.id ?? '') }),
    },
  ] satisfies RouteRecordRaw[],
})

export default router
