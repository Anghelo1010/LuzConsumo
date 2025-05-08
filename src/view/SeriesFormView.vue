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
      <p><strong>Frecuencia cardíaca estimada:</strong> {{ bpm }} BPM</p>
      <p v-if="esperandoDatos">⏳ Esperando datos del sensor...</p>
      <p v-if="errorConexion" style="color: red;">❌ Error de conexión con el ESP32</p>

      <!-- Gráfica en tiempo real -->
      <canvas ref="chartCanvas" width="700" height="400"></canvas>
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
const bpm = ref(0)
const esperandoDatos = ref(true)
const errorConexion = ref(false)

const ipESP = 'http://192.168.1.108:8080/datos'
const apiBackend = 'http://localhost:5000/guardar_lectura'

let intervalo = null
const chartCanvas = ref(null)
let chartInstance = null
const maxPuntos = 100

// Arrays normales para almacenar los datos, sin ser reactivos
let dataIR = []
let dataRED = []

// Para el cálculo de BPM
let tiemposPicos = []

function enviarFormulario() {
  formEnviado.value = true

  if (!intervalo) {
    intervalo = setInterval(obtenerDatos, 1500)
  }
}

async function obtenerDatos() {
  try {
    const res = await fetch(ipESP)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()

    if (typeof data.red === 'number' && typeof data.ir === 'number') {
      red.value = data.red
      ir.value = data.ir
      esperandoDatos.value = false
      errorConexion.value = false

      // Añadir los valores al array para el gráfico
      dataIR.push(ir.value)
      dataRED.push(red.value)

      if (dataIR.length > maxPuntos) dataIR.shift()
      if (dataRED.length > maxPuntos) dataRED.shift()

      detectarPicosYCalcularBPM()

      // Esperar que el DOM se haya actualizado y luego actualizar el gráfico
      await nextTick()
      actualizarGrafico()

      // Enviar los datos al backend
      const requestData = {
        nombre: paciente.value.nombre,
        edad: paciente.value.edad,
        peso: paciente.value.peso,
        altura: paciente.value.altura,
        red: red.value,
        ir: ir.value,
        bpm: bpm.value
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

function detectarPicosYCalcularBPM() {
  const umbral = 50000 // Ajustar según valores reales del sensor
  const ahora = Date.now()
  const valorActual = ir.value
  const anterior = dataIR[dataIR.length - 2] || 0

  if (valorActual > umbral && anterior <= umbral) {
    tiemposPicos.push(ahora)
    if (tiemposPicos.length > 10) tiemposPicos.shift()

    if (tiemposPicos.length >= 2) {
      const intervalos = []
      for (let i = 1; i < tiemposPicos.length; i++) {
        intervalos.push(tiemposPicos[i] - tiemposPicos[i - 1])
      }

      const promedioIntervalo = intervalos.reduce((a, b) => a + b, 0) / intervalos.length
      bpm.value = Math.round(60000 / promedioIntervalo)
    }
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
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76,175,80,0.3)',
            data: [],
            fill: true,
            tension: 0.4
          },
          {
            label: 'RED',
            borderColor: '#FF5722',
            backgroundColor: 'rgba(255,87,34,0.3)',
            data: [],
            fill: true,
            tension: 0.4
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
        },
        plugins: {
          legend: {
            labels: {
              font: {
                size: 14
              }
            }
          }
        }
      }
    })
  }
}

function actualizarGrafico() {
  if (chartInstance) {
    chartInstance.data.labels = Array.from({ length: dataIR.length }, (_, i) => i + 1)
    chartInstance.data.datasets[0].data = dataIR
    chartInstance.data.datasets[1].data = dataRED
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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 800px;
  margin: auto;
  color: #2c3e50;
}

.card {
  border: 1px solid #ddd;
  padding: 1.5rem;
  border-radius: 1rem;
  margin-top: 1rem;
  background: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

label {
  display: block;
  margin-top: 1rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.6rem;
  margin-top: 0.2rem;
  border-radius: 0.5rem;
  border: 1px solid #ccc;
  font-size: 1rem;
}

button {
  margin-top: 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:hover {
  background: #0056b3;
}

canvas {
  margin-top: 2rem;
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
}
</style>
