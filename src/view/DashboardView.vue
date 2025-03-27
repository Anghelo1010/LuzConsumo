<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold text-center">📊 Series Matemáticas</h1>

    <!-- Selector de Series -->
    <div class="flex justify-center my-4">
      <label for="tipoSerie" class="mr-2 text-lg">Selecciona una serie:</label>
      <select v-model="tipoSeleccionado" @change="cargarSeries" class="border rounded px-2 py-1">
        <option value="coseno">Coseno</option>
        <option value="exp">e^x</option>
        <option value="onda_cuadrada">Onda Cuadrada</option>
      </select>
    </div>

    <!-- Contenedor de tabla y gráfico -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Tabla de Datos -->
      <div class="overflow-x-auto">
        <h2 class="text-xl font-semibold mb-2">Datos de la Serie</h2>
        <table class="table-auto border-collapse border border-gray-500 w-full">
          <thead>
            <tr class="bg-gray-200">
              <th class="border px-4 py-2">ID</th>
              <th class="border px-4 py-2">Índice</th>
              <th class="border px-4 py-2">X</th>
              <th class="border px-4 py-2">Valor</th>
              <th class="border px-4 py-2">Error</th>
              <th class="border px-4 py-2">Tipo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="serie in series" :key="serie[0]" class="text-center">
              <td class="border px-4 py-2">{{ serie[0] }}</td>
              <td class="border px-4 py-2">{{ serie[1] }}</td>
              <td class="border px-4 py-2">{{ serie[2] }}</td>
              <td class="border px-4 py-2">{{ serie[3] }}</td>
              <td class="border px-4 py-2">{{ serie[4] }}</td>
              <td class="border px-4 py-2">{{ serie[5] }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Gráfico -->
      <div>
        <h2 class="text-xl font-semibold mb-2">Gráfico de la Serie</h2>
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
    };
  },
  methods: {
    async cargarSeries() {
      this.series = await obtenerSeries(this.tipoSeleccionado);
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
