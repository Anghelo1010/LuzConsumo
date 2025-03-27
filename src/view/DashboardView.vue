<template>
  <div>
    <h1>📊 Dashboard: Series Matemáticas</h1>

    <!-- Selector de serie -->
    <div class="selector">
      <label for="serie-select">Seleccionar Serie: </label>
      <select id="serie-select" v-model="selectedSerie" @change="actualizarDatos">
        <option value="" disabled>Elige una serie</option>
        <option v-for="serie in seriesDisponibles" :key="serie" :value="serie">
          {{ serie }}
        </option>
      </select>
    </div>

    <div v-if="series.length === 0" class="no-data">
      No hay datos disponibles para mostrar. Selecciona una serie o inserta datos.
    </div>

    <table v-else>
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

    <canvas ref="chartCanvas" v-if="series.length > 0"></canvas>
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
      selectedSerie: '', // Serie seleccionada por el usuario
      seriesDisponibles: ['coseno', 'exp', 'onda_cuadrada', 'fibonacci_coseno'], // Opciones de series
    };
  },
  methods: {
    async actualizarDatos() {
      // No hacer nada si no se ha seleccionado una serie
      if (!this.selectedSerie) {
        this.series = [];
        if (this.chart) {
          this.chart.destroy();
          this.chart = null;
        }
        return;
      }

      try {
        // Pasar la serie seleccionada como parámetro en la solicitud
        const datosGrafico = await obtenerDatosGrafico(this.selectedSerie);
        
        console.log('Datos recibidos en actualizarDatos:', datosGrafico);

        if (
          !datosGrafico ||
          !datosGrafico.indices ||
          !Array.isArray(datosGrafico.indices) ||
          !datosGrafico.x_vals ||
          !datosGrafico.valores ||
          !datosGrafico.errores ||
          !datosGrafico.tipos
        ) {
          console.warn('Datos incompletos recibidos del servidor:', datosGrafico);
          this.series = [];
          if (this.chart) {
            this.chart.destroy();
            this.chart = null;
          }
          return;
        }

        if (datosGrafico.indices.length === 0) {
          console.warn('No hay datos para mostrar (arreglos vacíos)');
          this.series = [];
          if (this.chart) {
            this.chart.destroy();
            this.chart = null;
          }
          return;
        }

        this.series = datosGrafico.indices.map((indice, i) => {
          return {
            indice,
            x_value: datosGrafico.x_vals[i],
            valor: datosGrafico.valores[i],
            error: datosGrafico.errores[i],
            tipo_serie: datosGrafico.tipos[i],
          };
        });

        console.log('Series mapeadas para la tabla:', this.series);

        this.actualizarGrafico(datosGrafico);
      } catch (error) {
        console.error('Error en actualizarDatos:', error);
        this.series = [];
        if (this.chart) {
          this.chart.destroy();
          this.chart = null;
        }
      }
    },
    actualizarGrafico(datosGrafico) {
      if (this.chart) {
        this.chart.destroy();
      }

      const canvas = this.$refs.chartCanvas;
      if (!canvas) {
        console.error('No se encontró el elemento canvas para el gráfico');
        return;
      }

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.error('No se pudo obtener el contexto 2D del canvas');
        return;
      }

      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: datosGrafico.x_vals.map(val => val.toFixed(2)),
          datasets: [
            {
              label: 'Valor Aproximado',
              data: datosGrafico.valores,
              borderColor: 'blue',
              fill: false,
              tension: 0.1,
            },
            {
              label: 'Error',
              data: datosGrafico.errores,
              borderColor: 'red',
              borderDash: [5, 5],
              fill: false,
              tension: 0.1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: { display: true, text: 'x' },
            },
            y: {
              title: { display: true, text: 'Valor / Error' },
            },
          },
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: `Aproximaciones de la Serie ${this.selectedSerie} y Error`,
            },
          },
        },
      });

      console.log('Gráfico actualizado con éxito');
    },
  },
  created() {
    console.log('Componente DashboardView creado, iniciando actualización de datos');
    // No llamamos a actualizarDatos aquí porque queremos que el usuario seleccione una serie primero
    setInterval(() => {
      if (this.selectedSerie) {
        console.log('Actualizando datos en tiempo real...');
        this.actualizarDatos();
      }
    }, 2000);
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
};
</script>

<style scoped>
.selector {
  text-align: center;
  margin: 20px 0;
}
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
  display: block;
}
.no-data {
  text-align: center;
  color: #888;
  margin: 20px;
}
</style>