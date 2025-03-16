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
import api from "@/api"; // Importamos la API configurada con Axios

export default {
  data() {
    return {
      email: "",
      password: "",
      mensaje: "",
    };
  },
  methods: {
    async login() {
      try {
        const response = await api.post("/login", {
          email: this.email,
          clave: this.password, // Flask espera "clave"
        });

        console.log("✅ Respuesta del servidor:", response.data); // Verifica la respuesta en consola
        const token = response.data.token; // Recibimos el token del backend

        if (!token) {
          this.mensaje = "❌ Error: No se recibió el token.";
          console.error("❌ Error: No se recibió un token del servidor.");
          return;
        }

        // Guardar el token en Local Storage
        localStorage.setItem("token", token);
        console.log("🔒 Token guardado en localStorage:", token);

        this.mensaje = "✅ Inicio de sesión exitoso 🚀";
        this.$router.push("/home"); // Redirigimos a la página principal
      } catch (error) {
        this.mensaje = "❌ Error al iniciar sesión. Verifica tus credenciales.";
        console.error("📌 Error en la autenticación:", error.response || error.message);
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
