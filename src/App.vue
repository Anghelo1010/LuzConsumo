<script setup>
import { ref, watchEffect } from "vue"; // Importar watchEffect para reaccionar a cambios en la ruta
import { useRoute } from "vue-router"; // Importar useRoute
import NavBar from './components/NavBar.vue'; // Importar el componente Navbar

// Obtener la ruta actual
const route = useRoute();

// Variable reactiva para controlar si se debe mostrar el navbar
const showNavbar = ref(false);

// Usar watchEffect para verificar si la ruta actual tiene meta.requiresNavbar
watchEffect(() => {
  showNavbar.value = route.meta.requiresNavbar ?? false;
});
</script>

<template>
  <!-- Mostrar el navbar solo si showNavbar es true -->
  <NavBar v-if="showNavbar" />
  
  <main>
    <!-- Aquí se renderizan las vistas según la ruta activa -->
    <RouterView />
  </main>
</template>

<style>
/* Estilos globales */
body {
  margin: 0;
  font-family: 'Arial', sans-serif;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
