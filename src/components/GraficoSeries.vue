<template>
    <div>
      <canvas ref="grafico"></canvas>
    </div>
  </template>
  
  <script>
  import { Chart, registerables } from "chart.js";
  Chart.register(...registerables);
  
  export default {
    props: {
      datos: Array, // Recibirá los datos desde el padre
    },
    mounted() {
      this.renderChart();
    },
    watch: {
      datos() {
        this.renderChart(); // Vuelve a renderizar si los datos cambian
      },
    },
    methods: {
      renderChart() {
        if (this.chart) {
          this.chart.destroy(); // Destruye el gráfico anterior
        }
  
        const ctx = this.$refs.grafico.getContext("2d");
        this.chart = new Chart(ctx, {
          type: "line", // Tipo de gráfico
          data: {
            labels: this.datos.map((d) => d.fecha), // Fechas en el eje X
            datasets: [
              {
                label: "Resultados",
                data: this.datos.map((d) => d.resultado), // Valores en el eje Y
                borderColor: "blue",
                borderWidth: 2,
                fill: false,
              },
            ],
          },
        });
      },
    },
  };
  </script>
  