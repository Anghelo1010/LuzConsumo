export default async function obtenerSeries(tipo) {
  try {
    const response = await fetch(`http://localhost:5000/series/${tipo}`);
    return await response.json();
  } catch (error) {
    console.error("Error obteniendo series:", error);
    return [];
  }
}


export async function insertarDatos(n, numTerminos, tipoSerie) {
  const response = await axios.post(`http://localhost:5000/insertar`, {
    n,
    num_terminos: numTerminos,
    tipo_serie: tipoSerie
  });
  return response.data;
}

import axios from 'axios';

const API_URL = 'http://localhost:5000';

export async function obtenerDatosGrafico(serie) {
  try {
    const response = await axios.get(`${API_URL}/datos_grafico`, {
      params: { serie },
      timeout: 5000,
    });
    console.log('Datos recibidos del servidor en api.js:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error al obtener datos del gráfico:', error.message);
    if (error.response) {
      console.error('Respuesta del servidor:', error.response.data);
    }
    return { grafico_datos: [], grafico_config: {}, serie_indices: [], serie_puntos_x: [], serie_valores: [], serie_diferencias: [], serie_tipos: [] };
  }
}