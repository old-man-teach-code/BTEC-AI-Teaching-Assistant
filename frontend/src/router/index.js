import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import { useAuthStore } from '../stores/auth' 
import Authen from '../views/Authen.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/auth'
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/auth',
      name: 'authen',
      component: Authen,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/logout',
      name: 'logout',
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore()
        authStore.logout()
        next({ name: 'authen' }) // Redirect to /auth after logout
      }
    },
    {
      path: '/:catchAll(.*)',
      name: 'not-found',
      component: NotFoundView // Catch-all route for 404 Not Found
    }
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const token = authStore.jwt; 
  const publicPages = ['/auth'];
  const authRequired = !publicPages.includes(to.path);

  if (authRequired && !token) {
    return next({ name: 'authen' });
  }
  if (to.path === '/auth' && token) {
    return next({ path: '/home' });
  }
  next();
})

export default router
