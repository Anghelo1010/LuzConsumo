<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold text-center mb-4">📊 Dashboard de Series Matemáticas</h1>

    <!-- Selector de Series -->
    <div class="flex justify-center mb-6">
      <label for="tipoSerie" class="mr-2 text-lg font-semibold">Selecciona una serie:</label>
      <select v-model="tipoSeleccionado" @change="cargarSeries" class="border rounded px-3 py-1">
        <option value="coseno">Coseno</option>
        <option value="exp">e^x</option>
        <option value="onda_cuadrada">Onda Cuadrada</option>
      </select>
    </div>

    <!-- Tarjetas de Estadísticas -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-white">
      <div class="bg-blue-500 p-4 rounded-lg shadow-lg">
        <h3 class="text-lg font-semibold">📌 Total de Datos</h3>
        <p class="text-2xl">{{ series.length }}</p>
      </div>
      <div class="bg-green-500 p-4 rounded-lg shadow-lg">
        <h3 class="text-lg font-semibold">📈 Promedio de Valores</h3>
        <p class="text-2xl">{{ promedioValores.toFixed(3) }}</p>
      </div>
      <div class="bg-red-500 p-4 rounded-lg shadow-lg">
        <h3 class="text-lg font-semibold">⚠️ Error Máximo</h3>
        <p class="text-2xl">{{ errorMaximo.toFixed(3) }}</p>
      </div>
    </div>

    <!-- Contenedor de tabla y gráfico -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <!-- Tabla de Datos -->
      <div class="overflow-x-auto">
        <h2 class="text-xl font-semibold mb-2">📋 Datos de la Serie</h2>
        <table class="table-auto border-collapse border border-gray-500 w-full">
          <thead>
            <tr class="bg-gray-200">
              <th class="border px-4 py-2">ID</th>
              <th class="border px-4 py-2">Índice</th>
              <th class="border px-4 py-2">X</th>
              <th class="border px-4 py-2">Valor</th>
              <th class="border px-4 py-2">Error</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="serie in seriesPaginadas" :key="serie[0]" class="text-center">
              <td class="border px-4 py-2">{{ serie[0] }}</td>
              <td class="border px-4 py-2">{{ serie[1] }}</td>
              <td class="border px-4 py-2">{{ serie[2] }}</td>
              <td class="border px-4 py-2">{{ serie[3] }}</td>
              <td class="border px-4 py-2">{{ serie[4] }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Controles de paginación -->
        <div class="flex justify-between items-center mt-4">
          <button @click="paginaActual--" :disabled="paginaActual === 1" class="px-3 py-1 bg-gray-300 rounded">⬅️ Anterior</button>
          <span class="text-lg">Página {{ paginaActual }} de {{ totalPaginas }}</span>
          <button @click="paginaActual++" :disabled="paginaActual >= totalPaginas" class="px-3 py-1 bg-gray-300 rounded">Siguiente ➡️</button>
        </div>
      </div>

      <!-- Gráfico -->
      <div>
        <h2 class="text-xl font-semibold mb-2">📊 Gráfico de la Serie</h2>
        <canvas ref="chartCanvas" class="w-full h-96"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import obtenerSeries from "../services/api.js";

export default {
  data() {
    return {
      series: [],
      tipoSeleccionado: "coseno",
      chart: null,
      paginaActual: 1,
      elementosPorPagina: 10,
    };
  },
  computed: {
    seriesPaginadas() {
      const inicio = (this.paginaActual - 1) * this.elementosPorPagina;
      return this.series.slice(inicio, inicio + this.elementosPorPagina);
    },
    totalPaginas() {
      return Math.ceil(this.series.length / this.elementosPorPagina);
    },
    promedioValores() {
      if (this.series.length === 0) return 0;
      const suma = this.series.reduce((acc, serie) => acc + serie[3], 0);
      return suma / this.series.length;
    },
    errorMaximo() {
      if (this.series.length === 0) return 0;
      return Math.max(...this.series.map(serie => serie[4]));
    }
  },
  methods: {
    async cargarSeries() {
      this.series = await obtenerSeries(this.tipoSeleccionado);
      this.paginaActual = 1;
      this.actualizarGrafico();
    },
    actualizarGrafico() {
      if (this.chart) {
        this.chart.destroy(); // Eliminar gráfico anterior
      }

      const ctx = this.$refs.chartCanvas.getContext("2d");
      const xValores = this.series.map(serie => serie[2]);
      const yValores = this.series.map(serie => serie[3]);

      this.chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: xValores,
          datasets: [
            {
              label: `Serie ${this.tipoSeleccionado}`,
              data: yValores,
              borderColor: "blue",
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    }
  },
  async created() {
    await this.cargarSeries();
  }
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 8px;
  border: 1px solid black;
}
canvas {
  max-width: 100%;
  height: 400px;
  margin-top: 20px;
}
</style>
