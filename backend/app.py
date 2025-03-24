from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

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
    return psycopg2.connect(**DB_CONFIG)


@app.route("/series/<tipo>", methods=["GET"])
def obtener_series(tipo):
    conn = conectar_bd()
    cursor = conn.cursor()

    if tipo == "coseno":
        cursor.execute("SELECT * FROM series_coseno ORDER BY id ASC;")
    elif tipo == "exp":
        cursor.execute("SELECT * FROM series_maclaurin ORDER BY id ASC;")
    elif tipo == "onda_cuadrada":
        cursor.execute("SELECT * FROM series_fourier ORDER BY id ASC;")
    else:
        return jsonify({"error": "Tipo de serie no válido"}), 400

    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(datos)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
