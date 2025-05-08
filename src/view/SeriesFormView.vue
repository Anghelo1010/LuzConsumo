<template>
  <div class="container">
    <h1 v-if="!formEnviado">Registro del Paciente</h1>
    <h1 v-else>Datos del MAX30102 (desde ESP32)</h1>

    <!-- Formulario del paciente -->
    <form v-if="!formEnviado" @submit.prevent="enviarFormulario" class="card">
      <label>Nombre:</label>
      <input v-model="paciente.nombre" required />

      <label>Edad:</label>
      <input type="number" v-model="paciente.edad" required />

      <label>Peso (kg):</label>
      <input type="number" v-model="paciente.peso" required />

      <label>Altura (cm):</label>
      <input type="number" v-model="paciente.altura" />

      <button type="submit">Iniciar monitoreo</button>
    </form>

    <!-- Lecturas del sensor -->
    <div v-if="formEnviado" class="card">
      <p><strong>Nombre:</strong> {{ paciente.nombre }}</p>
      <p><strong>IR:</strong> {{ ir }}</p>
      <p><strong>RED:</strong> {{ red }}</p>

      <!-- Estado de la conexión -->
      <p v-if="esperandoDatos">⏳ Esperando datos del sensor...</p>
      <p v-if="errorConexion">❌ No se pudo conectar al ESP32</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const paciente = ref({
  nombre: '',
  edad: '',
  peso: '',
  altura: ''
})

const formEnviado = ref(false)
const ir = ref(0)
const red = ref(0)
const esperandoDatos = ref(true)
const errorConexion = ref(false)

const ipESP = 'http://192.168.1.108:8080/datos' // IP del ESP32 directamente en el código
const apiBackend = 'http://localhost:5000/guardar_lectura' // Backend Flask

let intervalo = null

function enviarFormulario() {
  formEnviado.value = true

  if (!intervalo) {
    intervalo = setInterval(obtenerDatos, 1500) // cada segundo
  }
}

async function obtenerDatos() {
  try {
    const res = await fetch(ipESP);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    console.log("Datos obtenidos:", data);

    if (typeof data.red === 'number' && typeof data.ir === 'number') {
      red.value = data.red;
      ir.value = data.ir;
      esperandoDatos.value = false;
      errorConexion.value = false;

      // Verificar qué datos se envían al backend
      const requestData = {
        nombre: paciente.value.nombre,
        edad: paciente.value.edad,
        peso: paciente.value.peso,
        altura: paciente.value.altura,
        red: red.value,
        ir: ir.value
      };
      console.log("Datos enviados al backend:", requestData);

      const response = await fetch(apiBackend, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`Error al guardar la lectura: HTTP ${response.status}`);
      }

      const responseData = await response.json();
      console.log('Respuesta del servidor:', responseData);

    } else {
      console.error("Datos inválidos recibidos:", data);
    }

  } catch (e) {
    console.error("Error al obtener datos:", e);
    errorConexion.value = true;
  }
}

</script>

<style scoped>
.container {
  padding: 2rem;
  font-family: sans-serif;
  max-width: 500px;
  margin: auto;
}

.card {
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 1rem;
  margin-top: 1rem;
  background-color: #f8f8f8;
}

label {
  display: block;
  margin-top: 0.5rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.2rem;
  border-radius: 0.5rem;
  border: 1px solid #aaa;
}

button {
  margin-top: 1rem;
  background: #2c3e50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
}

button:hover {
  background: #1a252f;
}
</style>
