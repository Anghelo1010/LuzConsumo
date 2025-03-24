from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import numpy as np
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
    return psycopg2.connect(**DB_CONFIG)


@app.route("/series", methods=["GET"])
def obtener_series():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM series ORDER BY id ASC;")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(datos)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
