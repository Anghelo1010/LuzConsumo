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

export async function obtenerDatosGrafico() {
  const response = await axios.get(`http://localhost:5000/datos_grafico`);
  return response.data;
}