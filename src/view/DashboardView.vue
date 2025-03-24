<template>
  <div>
    <h1>📊 Series Matemáticas</h1>
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
  </div>
</template>

<script>
import obtenerSeries from "../services/api.js"; // Importación por defecto

export default {
  data() {
    return {
      series: [],
    };
  },
  async created() {
    this.series = await obtenerSeries();
  },
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
</style>
