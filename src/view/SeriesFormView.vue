<template>
    <div class="form-container">
      <h2>Calcular Nueva Serie</h2>
      <form @submit.prevent="calcularSerie">
        <div class="input-group">
          <label for="valorX">Valor X</label>
          <input type="number" v-model="valorX" id="valorX" required />
        </div>
        <div class="input-group">
          <label for="valorY">Valor Y</label>
          <input type="number" v-model="valorY" id="valorY" required />
        </div>
        <button type="submit">Calcular</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        valorX: "",
        valorY: "",
      };
    },
    methods: {
      calcularSerie() {
        // Lógica para calcular la nueva serie
        // Por ejemplo, puedes enviar los valores al backend o simplemente mostrarlos en la consola
        console.log(`Valor X: ${this.valorX}, Valor Y: ${this.valorY}`);
        // Aquí puedes agregar la lógica para añadir la nueva serie a la base de datos o al gráfico.
      },
    },
  };
  </script>
  
  <style scoped>
  .form-container {
    width: 300px;
    margin: 50px auto;
    text-align: center;
  }
  .input-group {
    margin-bottom: 15px;
  }
  label {
    display: block;
    margin-bottom: 5px;
  }
  input {
    width: 100%;
    padding: 8px;
    margin-top: 5px;
  }
  button {
    width: 100%;
    padding: 10px;
    background-color: blue;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>
  