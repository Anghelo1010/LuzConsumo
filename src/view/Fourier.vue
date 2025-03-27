<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold">¿Qué es la Serie de Fourier?</h1>
    <p>
      La Serie de Fourier es una forma de representar una función periódica como una suma infinita de funciones seno y coseno.
    </p>

    <h2 class="text-xl font-semibold mt-4">Gráfico en Tiempo Real</h2>
    <div id="grafico" class="w-full h-96"></div>

    <h2 class="text-xl font-semibold mt-4">Últimos 10 Datos</h2>
    <table class="table-auto border-collapse border border-gray-500 w-full mt-2">
      <thead>
        <tr class="bg-gray-200">
          <th class="border px-4 py-2">Índice</th>
          <th class="border px-4 py-2">X Value</th>
          <th class="border px-4 py-2">Valor Aproximado</th>
          <th class="border px-4 py-2">Error</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(dato, index) in datos" :key="index">
          <td class="border px-4 py-2">{{ dato.indice }}</td>
          <td class="border px-4 py-2">{{ dato.x_value?.toFixed(3) ?? 'N/A' }}</td>
          <td class="border px-4 py-2">{{ dato.valor?.toFixed(3) ?? 'N/A' }}</td>
          <td class="border px-4 py-2">{{ dato.error?.toFixed(3) ?? 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Plotly from "plotly.js-dist";
import axios from "axios";

const datos = ref([]);

const actualizarGrafico = async () => {
  try {
    const response = await axios.get("http://localhost:5000/datos_grafico");
    const data = response.data;

    // Mapear los datos para mostrarlos correctamente
    datos.value = data.data[0].x.map((_, i) => ({
      indice: data.data[0].x[i],
      x_value: data.data[1].y[i],
      valor: data.data[0].y[i],
      error: data.data[2].y[i],
    })).slice(-10); // Tomamos solo los últimos 10 elementos

    const trace1 = {
      x: data.data[0].x,
      y: data.data[0].y,
      mode: "lines+markers",
      name: "Fourier Aproximado",
      line: { color: "blue", width: 2 },
      marker: { opacity: 0.7 },
    };

    const trace2 = {
      x: data.data[0].x,
      y: data.data[1].y,
      mode: "lines+markers",
      name: "Fourier Real",
      line: { color: "green", width: 2 },
      marker: { opacity: 0.7 },
    };

    const trace3 = {
      x: data.data[0].x,
      y: data.data[2].y,
      mode: "lines+markers",
      name: "Error",
      line: { color: "red", dash: "dot", width: 2 },
      marker: { opacity: 0.6 },
      yaxis: "y2",
    };

    const layout = {
      title: "Serie de Fourier en Tiempo Real",
      xaxis: { title: "Índice" },
      yaxis: { title: "Valor de Fourier" },
      yaxis2: {
        title: "Error",
        overlaying: "y",
        side: "right",
        showgrid: false,
      },
      legend: { x: 0, y: 1 },
    };

    Plotly.react("grafico", [trace1, trace2, trace3], layout);
  } catch (error) {
    console.error("Error al obtener datos:", error);
  }
};

onMounted(() => {
  actualizarGrafico();
  setInterval(actualizarGrafico, 3000); // Actualiza cada 3 segundos
});
</script>
