<template>
    <div>
      <canvas ref="chartCanvas"></canvas>
    </div>
  </template>
  
  <script setup>
  import { Chart, registerables } from "chart.js";
import { onMounted, ref, watch } from "vue";
  
  Chart.register(...registerables);
  
  const props = defineProps({
    chartData: Object,
    chartOptions: Object,
  });
  
  const chartCanvas = ref(null);
  let chartInstance = null;
  
  onMounted(() => {
    if (chartCanvas.value) {
      chartInstance = new Chart(chartCanvas.value, {
        type: "line",
        data: props.chartData,
        options: props.chartOptions,
      });
    }
  });
  
  // 🔄 Actualizar gráfico si los datos cambian
  watch(
    () => props.chartData,
    (newData) => {
      if (chartInstance) {
        chartInstance.data = newData;
        chartInstance.update();
      }
    },
    { deep: true }
  );
  </script>
  