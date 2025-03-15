<template>
  <nav v-if="user" class="navbar">
    <div class="container">
      <!-- Enlaces de navegación -->
      <router-link to="/home" class="nav-link">Inicio</router-link>
      <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
      <router-link to="/informacion" class="nav-link">Información</router-link>
      <router-link to="/SobreNosotros" class="nav-link">Sobre Nosotros</router-link>
    </div>
  </nav>
</template>

<script setup>
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { onMounted, ref } from "vue";

const auth = getAuth();
const user = ref(null);

// Verificar el estado de autenticación
onMounted(() => {
  onAuthStateChanged(auth, (currentUser) => {
    user.value = currentUser;
  });
});
</script>

<style scoped>
.navbar {
  background-color: #2c3e50; /* Fondo oscuro */
  padding: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Sombra sutil */
}

.container {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.nav-link:hover {
  background-color: #34495e; /* Fondo gris oscuro al para el cursor */
}

.nav-link.router-link-exact-active {
  background-color: #42b883; /* Fondo verde cuando el enlace es activo */
  color: white;
}
</style>
