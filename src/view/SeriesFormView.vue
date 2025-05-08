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
      <p v-if="esperandoDatos">⏳ Esperando datos del sensor...</p>

      <!-- Gráfica en tiempo real -->
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

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

const ipESP = 'http://192.168.1.108:8080/datos' // IP del ESP32
const apiBackend = 'http://localhost:5000/guardar_lectura' // Backend Flask

let intervalo = null
const chartCanvas = ref(null)
let chartInstance = null
const maxPuntos = 20

const dataIR = ref([])
const dataRED = ref([])

function enviarFormulario() {
  formEnviado.value = true

  if (!intervalo) {
    intervalo = setInterval(obtenerDatos, 1500) // cada 1.5 segundos
  }
}

async function obtenerDatos() {
  try {
    const res = await fetch(ipESP)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()
    console.log("Datos obtenidos:", data)

    if (typeof data.red === 'number' && typeof data.ir === 'number') {
      red.value = data.red
      ir.value = data.ir
      esperandoDatos.value = false
      errorConexion.value = false

      // Actualizar arrays sin causar recursión infinita
      const newIR = [...dataIR.value, ir.value]
      const newRED = [...dataRED.value, red.value]

      if (newIR.length > maxPuntos) newIR.shift()
      if (newRED.length > maxPuntos) newRED.shift()

      dataIR.value = newIR
      dataRED.value = newRED

      nextTick(() => {
        actualizarGrafico()
      })

      // Enviar al backend
      const requestData = {
        nombre: paciente.value.nombre,
        edad: paciente.value.edad,
        peso: paciente.value.peso,
        altura: paciente.value.altura,
        red: red.value,
        ir: ir.value
      }

      await fetch(apiBackend, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      })
    } else {
      console.error('Datos inválidos recibidos:', data)
    }
  } catch (e) {
    console.error('Error al obtener datos:', e)
    errorConexion.value = true
  }
}

function inicializarGrafico() {
  if (chartCanvas.value && !chartInstance) {
    chartInstance = new Chart(chartCanvas.value, {
      type: 'line',
      data: {
        labels: Array.from({ length: maxPuntos }, (_, i) => i + 1),
        datasets: [
          {
            label: 'IR',
            borderColor: 'blue',
            data: [],
            fill: false
          },
          {
            label: 'RED',
            borderColor: 'red',
            data: [],
            fill: false
          }
        ]
      },
      options: {
        animation: false,
        responsive: true,
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    })
  }
}

function actualizarGrafico() {
  if (chartInstance) {
    chartInstance.data.labels = Array.from({ length: dataIR.value.length }, (_, i) => i + 1)
    chartInstance.data.datasets[0].data = dataIR.value
    chartInstance.data.datasets[1].data = dataRED.value
    chartInstance.update()
  } else {
    inicializarGrafico()
  }
}

onMounted(async () => {
  await nextTick()
  setTimeout(() => {
    inicializarGrafico()
  }, 200)
})
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

canvas {
  margin-top: 1rem;
  width: 100%;
  height: 300px;
}
</style>
