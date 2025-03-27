<template>
  <div class="container">
    <h1>📊 Serie de Fourier</h1>

    <canvas ref="chartCanvas"></canvas>

    <h2>📋 Últimos 10 Datos</h2>
    <table>
      <thead>
        <tr>
          <th>Índice</th>
          <th>X</th>
          <th>Valor Aproximado</th>
          <th>Error</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dato in datos" :key="dato.indice">
          <td>{{ dato.indice }}</td>
          <td>{{ dato.x.toFixed(3) }}</td>
          <td>{{ dato.valor.toFixed(3) }}</td>
          <td>{{ dato.error.toFixed(3) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  data() {
    return {
      datos: [],
      chart: null,
    };
  },
  methods: {
    async obtenerDatos() {
      try {
        const response = await axios.get("http://localhost:5000/datos_grafico");
        const data = response.data.data;

        this.datos = data[0].x.map((_, i) => ({
          indice: data[0].x[i],
          x: data[1].y[i],
          valor: data[0].y[i],
          error: data[2].y[i],
        })).slice(-10);

        this.actualizarGrafico();
      } catch (error) {
        console.error("Error al obtener datos:", error);
      }
    },
    actualizarGrafico() {
      if (this.chart) {
        this.chart.destroy();
      }

      const ctx = this.$refs.chartCanvas.getContext("2d");
      const xValores = this.datos.map(d => d.x);
      const yValores = this.datos.map(d => d.valor);

      this.chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: xValores,
          datasets: [
            {
              label: "Serie de Fourier",
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
  async mounted() {
    await this.obtenerDatos();
    setInterval(this.obtenerDatos, 5000); // Actualiza cada 5 segundos
  },
};
</script>

<style scoped>
.container {
  width: 80%;
  margin: auto;
  text-align: center;
}
table {
  width: 100%;
  margin-top: 20px;
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
