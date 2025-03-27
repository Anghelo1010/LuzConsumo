<template>
  <div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold text-center mb-4">📊 Serie de Onda Cuadrada</h1>

    <!-- Formulario -->
    <div class="form-container p-6 max-w-sm mx-auto bg-white rounded-lg shadow-lg">
      <form @submit.prevent="calcularSerie">
        <div class="mb-4">
          <label for="valorX" class="block text-gray-700">Valor X</label>
          <input type="number" v-model="valorX" id="valorX" class="w-full p-2 mt-2 border rounded" required />
        </div>
        <div class="mb-4">
          <label for="valorY" class="block text-gray-700">Valor Y</label>
          <input type="number" v-model="valorY" id="valorY" class="w-full p-2 mt-2 border rounded" required />
        </div>
        <button type="submit" class="w-full p-2 bg-blue-500 text-white rounded">Calcular</button>
      </form>
    </div>

    <!-- Tabla de Series -->
    <div class="mt-6">
      <table class="w-full border-collapse border border-gray-400">
        <thead>
          <tr class="bg-gray-200">
            <th class="border p-2">ID</th>
            <th class="border p-2">Índice</th>
            <th class="border p-2">X</th>
            <th class="border p-2">Valor</th>
            <th class="border p-2">Error</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="serie in series" :key="serie[0]" class="text-center">
            <td class="border p-2">{{ serie[0] }}</td>
            <td class="border p-2">{{ serie[1] }}</td>
            <td class="border p-2">{{ serie[2] }}</td>
            <td class="border p-2">{{ serie[3] }}</td>
            <td class="border p-2">{{ serie[4] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Gráfico -->
    <div class="mt-6">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import obtenerSeries from "../services/api.js";

export default {
  data() {
    return {
      valorX: "",
      valorY: "",
      series: [],
      chart: null,
    };
  },
  methods: {
    async cargarSeries() {
      this.series = await obtenerSeries("onda_cuadrada");
      this.actualizarGrafico();
    },
    calcularSerie() {
      console.log(`Valor X: ${this.valorX}, Valor Y: ${this.valorY}`);
      // Aquí puedes agregar la lógica para enviar los datos al backend
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
              label: "Serie Onda Cuadrada",
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
.container {
  max-width: 800px;
  margin: auto;
}
.form-container {
  text-align: center;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 8px;
  border: 1px solid gray;
}
canvas {
  max-width: 600px;
  max-height: 400px;
  margin-top: 20px;
}
</style>
