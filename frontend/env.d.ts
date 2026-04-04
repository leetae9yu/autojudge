/// <reference types="vite/client" />

declare module 'vuetify/styles'
declare module '@mdi/font/css/materialdesignicons.css'

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<{}, {}, any>
  export default component
}
