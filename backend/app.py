from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
DB_CONFIG = {
    "dbname": "series_matematicas",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432",
}

def conectar_bd():
    """Función para conectar a la base de datos PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

@app.route("/series/<tipo>", methods=["GET"])
def obtener_series(tipo):
    """Obtiene datos de diferentes series matemáticas según el tipo especificado."""
    conn = conectar_bd()
    cursor = conn.cursor()

    consultas = {
        "coseno": "SELECT * FROM series_coseno ORDER BY id ASC;",
        "exp": "SELECT * FROM series_maclaurin ORDER BY id ASC;",
        "onda_cuadrada": "SELECT * FROM series_fourier ORDER BY id ASC;",
    }

    if tipo not in consultas:
        return jsonify({"error": "Tipo de serie no válido"}), 400

    cursor.execute(consultas[tipo])
    datos = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return jsonify(datos)

def obtener_datos():
    """Obtiene los últimos 10 datos de la serie de Fourier."""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute("SELECT indice, x_value, valor, error FROM series_fourier ORDER BY indice DESC LIMIT 10")
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    # Construcción del JSON con los datos estructurados
    datos = {
        "data": [
            {"x": [r[0] for r in resultados], "y": [r[2] for r in resultados]},  # Valores de la función
            {"x": [r[0] for r in resultados], "y": [r[1] for r in resultados]},  # X Values
            {"x": [r[0] for r in resultados], "y": [r[3] for r in resultados]},  # Error
        ],
        "layout": {"title": "Serie de Fourier en tiempo real"}
    }
    return datos  # Devuelve un diccionario, no una cadena JSON

@app.route("/datos_grafico", methods=["GET"])
def datos_grafico():
    """Retorna datos en formato JSON para la visualización gráfica."""
    return jsonify(obtener_datos())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
