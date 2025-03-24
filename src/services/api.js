export default async function obtenerSeries(tipo) {
  try {
    const response = await fetch(`http://localhost:5000/series/${tipo}`);
    return await response.json();
  } catch (error) {
    console.error("Error obteniendo series:", error);
    return [];
  }
}
