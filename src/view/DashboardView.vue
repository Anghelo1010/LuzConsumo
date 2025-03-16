<template>
  <div class="dashboard-container">
    <h2>Historial de Series Matemáticas 📈</h2>

    <div v-if="mensaje" class="error">{{ mensaje }}</div>

    <table v-if="series.length">
      <thead>
        <tr>
          <th>Tipo de Serie</th>
          <th>Resultado</th>
          <th>Error</th>
          <th>Fecha</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="serie in series" :key="serie.fecha">
          <td>{{ serie.tipo_serie }}</td>
          <td>{{ serie.resultado }}</td>
          <td>{{ serie.error }}</td>
          <td>{{ formatoFecha(serie.fecha) }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else class="loading">Cargando datos... ⏳</p>

    <!-- Gráfico de Líneas -->
    <div v-if="chartData.labels.length" class="chart-container">
      <LineChart :chart-data="chartData" :chart-options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import api from "@/api";
import { io } from "socket.io-client";
import { computed, onMounted, ref } from "vue";
import { LineChart } from "vue-chart-3";

// 📌 Registrar Chart.js con `LineController`
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  LineController // ✅ Agregado al registro
);

// Variables reactivas
const series = ref([]);
const mensaje = ref("");

// Configurar WebSocket
const socket = io("http://localhost:5000");

// Función para obtener datos
const obtenerDatos = async () => {
  const token = localStorage.getItem("token");

  if (!token) {
    mensaje.value = "⚠ No hay token. Inicia sesión.";
    console.error("Error: No hay token en localStorage");
    return;
  }

  try {
    const response = await api.get("/obtener_datos", {
      headers: { Authorization: `Bearer ${token}` },
    });
    series.value = response.data;
    console.log("✅ Datos obtenidos correctamente:", response.data);
  } catch (error) {
    if (error.response) {
      mensaje.value = error.response.data?.error || "❌ Error al obtener datos.";
      console.error("📌 Error en la respuesta del servidor:", error.response);
    } else if (error.request) {
      mensaje.value = "❌ No se pudo conectar con el servidor.";
      console.error("📌 Error en la solicitud: No hay respuesta del servidor.", error.request);
    } else {
      mensaje.value = "❌ Ocurrió un error desconocido.";
      console.error("📌 Error desconocido:", error.message);
    }
  }
};

// WebSocket: recibir datos en tiempo real
socket.on("nueva_serie", (nuevaSerie) => {
  series.value.unshift(nuevaSerie);
  console.log("🟢 Nueva serie matemática recibida:", nuevaSerie);
});

// Formato de fecha
const formatoFecha = (fecha) => new Date(fecha).toLocaleString();

// Datos del gráfico
const chartData = computed(() => {
  if (!series.value.length) return { labels: [], datasets: [] };

  return {
    labels: series.value.map((s) => formatoFecha(s.fecha)),
    datasets: [
      {
        label: "Resultado",
        data: series.value.map((s) => s.resultado),
        borderColor: "#36A2EB",
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        fill: true,
        tension: 0.4,
      },
      {
        label: "Error",
        data: series.value.map((s) => s.error),
        borderColor: "#FF6384",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        fill: true,
        tension: 0.4,
      },
    ],
  };
});

// Opciones del gráfico
const chartOptions = {
  responsive: true,
  plugins: { legend: { position: "top" } },
  scales: { y: { beginAtZero: true } },
};

// Cargar datos al iniciar
onMounted(obtenerDatos);
</script>

<style scoped>
.dashboard-container {
  width: 90%;
  margin: 20px auto;
  text-align: center;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
}

th {
  background-color: #007bff;
  color: white;
}

.chart-container {
  margin-top: 30px;
  width: 80%;
  margin-left: auto;
  margin-right: auto;
}

.error {
  color: red;
  margin-top: 10px;
}

.loading {
  font-size: 18px;
  font-weight: bold;
  color: #555;
}
</style>
