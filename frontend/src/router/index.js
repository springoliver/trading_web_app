import { setupLayouts } from 'virtual:generated-layouts'
import { createRouter, createWebHistory } from 'vue-router'
import routes from '~pages'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...setupLayouts(routes),
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' })
  }
  if (to.name === 'login' && token) {
    return next({ name: 'trade' })
  }
  return next()
})


// Docs: https://router.vuejs.org/guide/advanced/navigation-guards.html#global-before-guards
export default router
