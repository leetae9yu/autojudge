import './assets/main.css'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'autojudge',
    themes: {
      autojudge: {
        dark: false,
        colors: {
          primary: '#2f5d62',
          secondary: '#8b4b3e',
          background: '#efe4d2',
          surface: '#fffaf2',
          error: '#9f3434',
          success: '#356b4a',
          warning: '#9a6620',
        },
      },
    },
  },
})

app.use(createPinia())
app.use(vuetify)
app.use(router)

app.mount('#app')
