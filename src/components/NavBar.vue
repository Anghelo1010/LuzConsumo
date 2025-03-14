<template>
  <nav v-if="user" class="navbar">
    <router-link to="/home">Inicio</router-link>
    <router-link to="/mapa">Mapa</router-link>
    <router-link to="/informacion">Información</router-link>
    <router-link to="/SobreNosotros">Sobre Nosotros</router-link>
  </nav>
</template>

<script setup>
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { onMounted, ref } from "vue";

const auth = getAuth();
const user = ref(null);

// Verificar autenticación
onMounted(() => {
  onAuthStateChanged(auth, (currentUser) => {
    user.value = currentUser;
    console.log("Usuario autenticado:", user.value);
  });
});
</script>


<style scoped>
.navbar {
  background: #2c3e50;
  padding: 1rem;
  display: flex;
  justify-content: center;
  gap: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s;
}

.navbar a:hover {
  background: #34495e;
}

.navbar a.router-link-exact-active {
  background: #42b883;
  color: white;
}
</style>
