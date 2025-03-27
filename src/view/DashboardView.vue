<template>
  <div>
    <h1>📊 Series Matemáticas</h1>

    <label for="tipoSerie">Selecciona una serie:</label>
    <select v-model="tipoSeleccionado" @change="cargarSeries">
      <option value="coseno">Coseno</option>
      <option value="exp">e^x</option>
      <option value="onda_cuadrada">Onda Cuadrada</option>
    </select>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Índice</th>
          <th>X</th>
          <th>Valor</th>
          <th>Error</th>
          <th>Tipo</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="serie in series" :key="serie[0]">
          <td>{{ serie[0] }}</td>
          <td>{{ serie[1] }}</td>
          <td>{{ serie[2] }}</td>
          <td>{{ serie[3] }}</td>
          <td>{{ serie[4] }}</td>
          <td>{{ serie[5] }}</td>
        </tr>
      </tbody>
    </table>

    <canvas ref="chartCanvas"></canvas>
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
  max-width: 600px;
  max-height: 400px;
  margin-top: 20px;
}
</style>
