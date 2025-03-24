<template>
  <div class="login-container">
    <h2>Iniciar Sesión</h2>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Correo electrónico" required />
      <input type="password" v-model="password" placeholder="Contraseña" required />
      <button type="submit">Ingresar</button>
      <p v-if="mensaje">{{ mensaje }}</p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      mensaje: "",
    };
  },
  methods: {
    login() {
      // Comprobamos las credenciales de manera local
      if (this.email === "usuario@example.com" && this.password === "contraseña123") {
        this.mensaje = "✅ Inicio de sesión exitoso 🚀";
        this.$router.push("/home"); // Redirigimos a la página principal
      } else {
        this.mensaje = "❌ Error: Credenciales incorrectas.";
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  width: 300px;
  margin: 100px auto;
  text-align: center;
}
input {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 10px;
}
button {
  width: 100%;
  padding: 10px;
  background-color: blue;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
