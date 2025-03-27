import { createRouter, createWebHistory } from "vue-router";
import { auth } from "../firebase";
import DashboardView from "../view/DashboardView.vue";
import HomeView from "../view/HomeView.vue";
import LoginView from "../view/LoginView.vue";
import FourierView from "@/view/Fourier.vue";
import SeriesFormView from "../view/SeriesFormView.vue";

const routes = [
  { path: "/", component: LoginView, meta: { requiresNavbar: false } },
  {
    path: "/home",
    component: HomeView,
    meta: { requiresAuth: true, requiresNavbar: true },
  },
  {
    path: "/dashboard",
    component: DashboardView,
    meta: { requiresAuth: true, requiresNavbar: true },
  },
  {
    path: "/seriesform",
    component: SeriesFormView,
    meta: { requiresAuth: true, requiresNavbar: true },
  },
  {
    path: "/fourier",
    component: FourierView,
    meta: { requiresAuth: true, requiresNavbar: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Middleware de autenticación optimizado
router.beforeEach(async (to, from, next) => {
  const user = auth.currentUser; // Obtener usuario autenticado

  if (to.meta.requiresAuth && !user) {
    next("/"); // Redirige si no está autenticado
  } else {
    next();
  }
});

export default router;
