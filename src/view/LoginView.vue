<template>
  <div class="login-container">
    <h2>Iniciar Sesión</h2>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Correo electrónico" required />
      <input type="password" v-model="password" placeholder="Contraseña" required />
      <button type="submit">Ingresar</button>
    </form>
  </div>
</template>

<script>
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";

export default {
  data() {
    return {
      email: "",
      password: "",
    };
  },
  methods: {
    async login() {
      try {
        const userCredential = await signInWithEmailAndPassword(auth, this.email, this.password);
        localStorage.setItem("user", userCredential.user.uid);
        this.$router.push("/home");
      } catch (error) {
        alert("Error al iniciar sesión: " + error.message);
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
