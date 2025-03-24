// api.js
import axios from "axios";

const API_URL = "http://localhost:5000";

const obtenerSeries = async () => {
  try {
    const response = await axios.get(`${API_URL}/series`);
    return response.data;
  } catch (error) {
    console.error("Error obteniendo datos:", error);
    return [];
  }
};

export default obtenerSeries; // Exportación por defecto
