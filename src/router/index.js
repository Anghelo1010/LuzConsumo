import { createRouter, createWebHistory } from "vue-router";
import { auth } from "../firebase";
import DashboardView from "../view/DashboardView.vue"; // Importamos la nueva vista
import HomeView from "../view/HomeView.vue";
import LoginView from "../view/LoginView.vue";

const routes = [
  { path: "/", component: LoginView, meta: { requiresNavbar: false } },
  {
    path: "/home",
    component: HomeView,
    meta: { requiresAuth: true, requiresNavbar: true },
  },
  {
    path: "/dashboard", // Nueva ruta
    component: DashboardView,
    meta: { requiresAuth: true, requiresNavbar: true }, // Requiere autenticación y navbar
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Middleware de autenticación
router.beforeEach((to, from, next) => {
  auth.onAuthStateChanged((user) => {
    if (to.meta.requiresAuth && !user) {
      next("/"); // Redirigir si no está autenticado
    } else {
      next();
    }
  });
});

export default router;
