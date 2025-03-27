from flask import Flask, jsonify, request
 from flask_cors import CORS
 import psycopg2
 import random
 import math
 
 app = Flask(__name__)
 CORS(app)
 
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
 
 def generar_datos(cantidad):
     """Genera datos de Fourier en la base de datos."""
     conn = conectar_bd()
     cursor = conn.cursor()
 
     cursor.execute("SELECT valor FROM series_fourier ORDER BY indice DESC LIMIT 1")
     last_real = cursor.fetchone()
     last_real = last_real[0] if last_real else 0  # Si no hay datos previos, empezar en 0
 
     for i in range(cantidad):
         x_value = float(last_real) + random.uniform(-0.2, 0.2)
         valor = x_value + random.uniform(-0.5, 0.5) * (1 / (i + 1))  # Aproximación Fourier
         error = abs(valor - x_value)
         tipo_serie = "Fourier"
         fecha = "NOW()"
 
         cursor.execute("""
             INSERT INTO series_fourier (indice, x_value, valor, error, tipo_serie, fecha)
             VALUES (%s, %s, %s, %s, %s, %s)
         """, (i, x_value, valor, error, tipo_serie, fecha))
         last_real = x_value  # Actualizar último valor real
 
     conn.commit()
     cursor.close()
     conn.close()
 
 @app.route("/generar_datos", methods=["POST"])
 def generar_datos_endpoint():
     data = request.json
     cantidad = int(data.get("cantidad", 5))
     generar_datos(cantidad)
     return jsonify({"message": f"Se agregaron {cantidad} datos"}), 200
 
 def obtener_datos():
     """Obtiene los últimos 10 datos de la serie de Fourier."""
     conn = conectar_bd()
     cursor = conn.cursor()
     cursor.execute("SELECT indice, x_value, valor, error FROM series_fourier ORDER BY indice DESC LIMIT 10")
     resultados = cursor.fetchall()
 
     cursor.close()
     conn.close()
 
     return {
         "data": [
             {"x": [r[0] for r in resultados], "y": [r[2] for r in resultados]},  # Valores de la función
             {"x": [r[0] for r in resultados], "y": [r[1] for r in resultados]},  # X Values
             {"x": [r[0] for r in resultados], "y": [r[3] for r in resultados]},  # Error
         ],
         "layout": {"title": "Serie de Fourier en tiempo real"}
     }
 
 @app.route("/datos_grafico", methods=["GET"])
 def datos_grafico():
     """Retorna los datos en formato JSON para la visualización."""
     return jsonify(obtener_datos())
 
 if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
