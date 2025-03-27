<template>
  <div>
    <h1>📊 Dashboard: Series Matemáticas</h1>

    <table>
      <thead>
        <tr>
          <th>Índice</th>
          <th>X</th>
          <th>Valor Aproximado</th>
          <th>Error</th>
          <th>Tipo de Serie</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in series" :key="index">
          <td>{{ row.indice }}</td>
          <td>{{ row.x_value.toFixed(2) }}</td>
          <td>{{ row.valor.toFixed(4) }}</td>
          <td>{{ row.error.toFixed(4) }}</td>
          <td>{{ row.tipo_serie }}</td>
        </tr>
      </tbody>
    </table>

    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import { obtenerDatosGrafico } from '../services/api.js';

export default {
  data() {
    return {
      series: [],
      chart: null,
    };
  },
  methods: {
    async actualizarDatos() {
      const datosGrafico = await obtenerDatosGrafico();
      this.series = datosGrafico.indices.map((indice, i) => ({
        indice,
        x_value: datosGrafico.x_vals[i],
        valor: datosGrafico.valores[i],
        error: datosGrafico.errores[i],
        tipo_serie: datosGrafico.tipos[i],
      }));
      this.actualizarGrafico(datosGrafico);
    },
    actualizarGrafico(datosGrafico) {
      if (this.chart) {
        this.chart.destroy();
      }
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: datosGrafico.x_vals,
          datasets: [
            {
              label: 'Valor Aproximado',
              data: datosGrafico.valores,
              borderColor: 'blue',
              fill: false,
            },
            {
              label: 'Error',
              data: datosGrafico.errores,
              borderColor: 'red',
              borderDash: [5, 5],
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display: true, text: 'x' } },
            y: { title: { display: true, text: 'Valor / Error' } },
          },
        },
      });
    },
  },
  created() {
    this.actualizarDatos();
    setInterval(this.actualizarDatos, 2000); // Actualización en tiempo real
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
};
</script>

<style scoped>
table {
  width: 80%;
  border-collapse: collapse;
  margin: 20px auto;
}
th,
td {
  padding: 8px;
  border: 1px solid black;
  text-align: center;
}
th {
  background-color: #f2f2f2;
}
canvas {
  max-width: 80%;
  max-height: 500px;
  margin: 20px auto;
}
</style>