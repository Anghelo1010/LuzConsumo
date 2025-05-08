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
    return psycopg2.connect(**DB_CONFIG)

# ---------------------- SERIES FOURIER ----------------------

def generar_datos(cantidad):
    conn = conectar_bd()
    cursor = conn.cursor()

    for i in range(cantidad):
        x_value = float(i)
        valor = (
            1.0 * math.sin(x_value) +
            0.5 * math.sin(2 * x_value) +
            0.25 * math.sin(3 * x_value) +
            random.uniform(-0.1, 0.1)
        )
        error = abs(valor - math.sin(x_value))
        tipo_serie = "Fourier"

        cursor.execute("""
            INSERT INTO series_fourier (indice, x_value, valor, error, tipo_serie, fecha)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (i, x_value, valor, error, tipo_serie))

    conn.commit()
    cursor.close()
    conn.close()

@app.route("/generar_datos", methods=["POST"])
def generar_datos_endpoint():
    data = request.json
    cantidad = int(data.get("cantidad", 5))
    generar_datos(cantidad)
    return jsonify({"message": f"Se agregaron {cantidad} datos"}), 200

@app.route("/datos_grafico", methods=["GET"])
def datos_grafico():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT indice, x_value, valor, error FROM series_fourier ORDER BY indice DESC LIMIT 10")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    indices = [r[0] for r in resultados]
    x_values = [r[1] for r in resultados]
    valores = [r[2] for r in resultados]
    errores = [r[3] for r in resultados]

    return jsonify({
        "data": [
            {"x": indices, "y": valores},
            {"x": indices, "y": x_values},
            {"x": indices, "y": errores},
        ],
        "layout": {"title": "Serie de Fourier en tiempo real"}
    })

# ---------------------- PACIENTES + LECTURAS ----------------------

@app.route("/pacientes", methods=["POST"])
def registrar_paciente():
    data = request.json
    nombre = data.get("nombre")
    edad = data.get("edad")
    peso = data.get("peso")
    altura = data.get("altura")

    conn = conectar_bd()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO pacientes (nombre, edad, peso, altura) VALUES (%s, %s, %s, %s) RETURNING id",
            (nombre, edad, peso, altura)
        )
        paciente_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"paciente_id": paciente_id}), 201
    except Exception as e:
        conn.rollback()
        print("Error al registrar paciente:", e)
        return jsonify({"error": "No se pudo registrar el paciente"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/guardar_lectura", methods=["POST"])
def guardar_lectura():
    data = request.json
    print("Datos recibidos:", data)  # Verificar los datos que llegan
    nombre = data.get("nombre")
    edad = data.get("edad")
    peso = data.get("peso")
    altura = data.get("altura")
    red = data.get("red")
    ir = data.get("ir")

    conn = conectar_bd()
    cursor = conn.cursor()

    try:
        # Buscar paciente
        cursor.execute("SELECT id FROM pacientes WHERE nombre = %s AND edad = %s", (nombre, edad))
        paciente = cursor.fetchone()

        # Insertar si no existe
        if paciente:
            paciente_id = paciente[0]
        else:
            cursor.execute(
                "INSERT INTO pacientes (nombre, edad, peso, altura) VALUES (%s, %s, %s, %s) RETURNING id",
                (nombre, edad, peso, altura)
            )
            paciente_id = cursor.fetchone()[0]

        # Guardar lectura
        cursor.execute(
            "INSERT INTO lecturas_sensor (paciente_id, red, ir, fecha) VALUES (%s, %s, %s, NOW())",
            (paciente_id, red, ir)
        )

        conn.commit()
        return jsonify({"message": "Lectura guardada correctamente"}), 201

    except Exception as e:
        conn.rollback()
        print("Error al guardar lectura:", e)
        return jsonify({"error": "Error al guardar la lectura"}), 500

    finally:
        cursor.close()
        conn.close()


# ---------------------- MAIN ----------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
