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
    <div v-if="series.length" class="chart-container">
      <LineChart :chart-data="chartData" :chart-options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import api from "@/api";
import { CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from "chart.js";
import { computed, onMounted, ref } from "vue";
import { LineChart } from "vue-chart-3";

// Registrar componentes de Chart.js
ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);

const series = ref([]);
const mensaje = ref("");

// Cargar datos al montar el componente
onMounted(async () => {
  await obtenerDatos();
});

// Función para obtener datos
const obtenerDatos = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await api.get("/obtener_datos", {
      headers: { Authorization: `Bearer ${token}` },
    });
    series.value = response.data;
  } catch (error) {
    mensaje.value = "Error al obtener datos. Inténtalo de nuevo.";
  }
};

// Función para formatear fecha
const formatoFecha = (fecha) => {
  return new Date(fecha).toLocaleString();
};

// Datos del gráfico
const chartData = computed(() => ({
  labels: series.value.map((s) => formatoFecha(s.fecha)), // Usamos la fecha como etiqueta
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
}));

// Opciones del gráfico
const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};
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
