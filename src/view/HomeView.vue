<template>
  <div class="container">
    <!-- Contenedor dividido en dos columnas -->
    <div class="content">
      <div class="text-section">
        <h1>Gráfica de Series</h1>

        <h2>Introducción</h2>
        <p>
          Las gráficas de series son representaciones visuales de datos que muestran una o más series de puntos a lo largo de los ejes horizontal y vertical.
        </p>

        <h3>Características</h3>
        <ul>
          <li>Los puntos de datos se representan en el eje X y están unidos por una línea continua.</li>
          <li>Los datos que faltan se muestran con una línea discontinua.</li>
          <li>El eje X se denomina <strong>eje de tiempo</strong> y la unidad es una medida de tiempo.</li>
          <li>El eje Y corresponde a la variable que se está midiendo.</li>
        </ul>

        <h3>Usos</h3>
        <ul>
          <li>Visualizar tendencias de valores numéricos o recuentos a lo largo del tiempo.</li>
          <li>Comparar los valores de una variable en distintos períodos.</li>
          <li>Mostrar vacíos en un conjunto de datos.</li>
        </ul>

        <h3>Aplicaciones</h3>
        <ul>
          <li>En cuadros de mando interactivos, un gráfico de serie puede ser el origen o el destino de una acción.</li>
          <li>En estadísticas básicas, los gráficos de tiempo generan información útil antes de crear modelos.</li>
        </ul>

        <h3>Métodos de Análisis</h3>
        <ul>
          <li>Descomposición</li>
          <li>Prueba Dickey-Fuller aumentada (ADF)</li>
          <li>Correlaciones (ACF/PACF)</li>
          <li>Análisis espectral</li>
        </ul>

        <h2>Gráfica de Ejercicios</h2>
      </div>

      <!-- Cuadro para la imagen -->
      <div class="image-section">
        <div class="image-box">
          <img src="../images/series.png" alt="Gráfica de series">
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 3000px;
  margin: 0 auto;
  padding: 10px;
}

/* Layout en dos columnas */
.content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

/* Sección de texto a la izquierda */
.text-section {
  width: 60%;
  text-align: left;
}

h1 {
  font-size: 2rem;
  margin-bottom: 10px;
}

h2 {
  font-size: 1.5rem;
  margin-top: 20px;
}

h3 {
  font-size: 1.3rem;
  margin-top: 15px;
  color: #333;
}

p {
  font-size: 1rem;
  color: #555;
  margin-bottom: 10px;
}

ul {
  padding-left: 20px;
}

li {
  font-size: 1rem;
  color: #444;
  margin-bottom: 5px;
}

/* Cuadro de imagen a la derecha */
.image-section {
  width: 35%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-box img {
  width: 100%; /* La imagen ocupará todo el ancho disponible */
  height: 100%; /* La imagen ocupará todo el alto disponible */
  object-fit: cover; /* Ajusta la imagen manteniendo su proporción y recortando si es necesario */
  border-radius: 5px; /* Opcional: Bordes redondeados para una mejor apariencia */
}

</style>
