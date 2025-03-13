<script setup>
import NavBar from './components/NavBar.vue';
</script>

<template>
  <NavBar />
  <main>
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