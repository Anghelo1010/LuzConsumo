from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import math
import psycopg2
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

DB_CONFIG = {
    "dbname": "series_matematicas",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432",
    "options": "-c client_encoding=UTF8"
}

def conectar_bd():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return None

def inicializar_bd():
    conn = conectar_bd()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        tablas = {
            "series_coseno": "coseno",
            "series_maclaurin": "exp",
            "series_fourier": "onda_cuadrada",
            "series_fibonacci_coseno": "fibonacci_coseno"
        }
        for tabla, tipo_serie in tablas.items():
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {tabla} (
                    id SERIAL PRIMARY KEY, indice INT, x_value NUMERIC, valor NUMERIC, error NUMERIC, tipo_serie TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            if cursor.fetchone()[0] == 0:
                if tipo_serie == "coseno":
                    agregar_datos_iniciales(tipo_serie, np.linspace(0, 2 * np.pi, 10), 5)
                elif tipo_serie == "exp":
                    agregar_datos_iniciales(tipo_serie, np.linspace(-2, 2, 10), 5)
                elif tipo_serie == "onda_cuadrada":
                    agregar_datos_iniciales(tipo_serie, np.linspace(-np.pi, np.pi, 10), 5)
                elif tipo_serie == "fibonacci_coseno":
                    agregar_datos_iniciales(tipo_serie, np.linspace(0, 2 * np.pi, 10), 5)
        conn.commit()
        cursor.close()
        print("✅ Tablas verificadas y datos iniciales creados correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

def insertar_datos(tipo_serie, x_vals, valores, errores):
    conn = conectar_bd()
    if conn is None:
        return
    tabla = {
        "coseno": "series_coseno",
        "exp": "series_maclaurin",
        "onda_cuadrada": "series_fourier",
        "fibonacci_coseno": "series_fibonacci_coseno"
    }.get(tipo_serie, None)
    if not tabla:
        return
    try:
        cursor = conn.cursor()
        fecha_actual = datetime.now()
        datos = [(i, float(x_vals[i]), float(valores[i]), float(errores[i]), tipo_serie, fecha_actual) 
                 for i in range(len(x_vals))]
        cursor.executemany(f"""
            INSERT INTO {tabla} (indice, x_value, valor, error, tipo_serie, fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, datos)
        conn.commit()
        cursor.close()
        print(f"✅ Datos de '{tipo_serie}' insertados correctamente.")
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
    finally:
        conn.close()

def aproximacion_cos_taylor(x, num_terminos):
    return sum(((-1) ** n * x ** (2 * n)) / math.factorial(2 * n) for n in range(num_terminos))

def aproximacion_exp_maclaurin(x, num_terminos):
    return sum((x**n) / math.factorial(n) for n in range(num_terminos))

def aproximacion_onda_cuadrada(x, num_terminos):
    return 4 / np.pi * sum((1 / (2 * n + 1)) * np.sin((2 * n + 1) * x) for n in range(num_terminos))

def aproximacion_fibonacci_coseno(x, num_terminos):
    fib = [0, 1]
    for i in range(2, num_terminos):
        fib.append(fib[i-1] + fib[i-2])
    max_fib = max(fib[:num_terminos]) if num_terminos > 0 else 1
    return sum((fib[n] / max_fib) * np.cos(n * x) for n in range(min(num_terminos, len(fib))))

def agregar_datos_iniciales(tipo_serie, x_vals, num_terminos):
    if tipo_serie == "coseno":
        valores_aprox = [aproximacion_cos_taylor(x, num_terminos) for x in x_vals]
        valores_reales = [np.cos(x) for x in x_vals]
    elif tipo_serie == "exp":
        valores_aprox = [aproximacion_exp_maclaurin(x, num_terminos) for x in x_vals]
        valores_reales = [np.exp(x) for x in x_vals]
    elif tipo_serie == "onda_cuadrada":
        valores_aprox = [aproximacion_onda_cuadrada(x, num_terminos) for x in x_vals]
        valores_reales = [np.sign(np.sin(x)) for x in x_vals]
    elif tipo_serie == "fibonacci_coseno":
        valores_aprox = [aproximacion_fibonacci_coseno(x, num_terminos) for x in x_vals]
        valores_reales = [np.cos(x) for x in x_vals]
    errores = [abs(a - r) for a, r in zip(valores_aprox, valores_reales)]
    insertar_datos(tipo_serie, x_vals, valores_aprox, errores)

@app.route('/insertar', methods=['POST'])
def insertar():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No se proporcionaron datos en el cuerpo de la solicitud"}), 400

        if 'n' not in data or 'num_terminos' not in data or 'tipo_serie' not in data:
            return jsonify({"status": "error", "message": "Faltan parámetros: 'n', 'num_terminos' o 'tipo_serie'"}), 400

        n = int(data['n'])
        num_terminos = int(data['num_terminos'])
        tipo_serie = data['tipo_serie']

        if n <= 0 or num_terminos <= 0:
            return jsonify({"status": "error", "message": "Los valores de 'n' y 'num_terminos' deben ser mayores que 0"}), 400

        if tipo_serie == "coseno":
            x_vals = np.linspace(0, 2 * np.pi, n)
        elif tipo_serie == "exp":
            x_vals = np.linspace(-2, 2, n)
        elif tipo_serie == "onda_cuadrada":
            x_vals = np.linspace(-np.pi, np.pi, n)
        elif tipo_serie == "fibonacci_coseno":
            x_vals = np.linspace(0, 2 * np.pi, n)
        else:
            return jsonify({"status": "error", "message": f"Tipo de serie no válido: {tipo_serie}"}), 400

        agregar_datos_iniciales(tipo_serie, x_vals, num_terminos)
        return jsonify({"status": "success", "message": f"Se agregaron {n} datos para {tipo_serie}"})

    except ValueError as ve:
        return jsonify({"status": "error", "message": f"Error en los valores proporcionados: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno del servidor: {str(e)}"}), 500

@app.route('/datos_grafico')
def datos_grafico():
    # Obtener el parámetro 'serie' de la query string
    serie = request.args.get('serie', default=None, type=str)
    
    conn = conectar_bd()
    if conn is None:
        print("❌ No se pudo conectar a la base de datos en /datos_grafico")
        return jsonify({"data": [], "layout": {}, "indices": [], "x_vals": [], "valores": [], "errores": [], "tipos": []})
    
    try:
        cursor = conn.cursor()
        
        # Mapear el tipo de serie a la tabla correspondiente
        tabla = {
            "coseno": "series_coseno",
            "exp": "series_maclaurin",
            "onda_cuadrada": "series_fourier",
            "fibonacci_coseno": "series_fibonacci_coseno"
        }.get(serie, None)

        if not serie or not tabla:
            # Si no se especifica una serie válida, devolver datos vacíos
            print(f"⚠️ Serie no especificada o no válida: {serie}")
            return jsonify({"data": [], "layout": {}, "indices": [], "x_vals": [], "valores": [], "errores": [], "tipos": []})

        # Consultar solo los datos de la tabla correspondiente a la serie seleccionada
        cursor.execute(f"""
            SELECT indice, x_value, valor, error, tipo_serie 
            FROM {tabla}
            ORDER BY x_value
        """)
        resultados = cursor.fetchall()
        print(f"📊 Resultados crudos de la consulta para {serie}: {resultados}")

        if not resultados:
            print(f"⚠️ No se encontraron datos para la serie {serie}")
            return jsonify({"data": [], "layout": {}, "indices": [], "x_vals": [], "valores": [], "errores": [], "tipos": []})

        indices = [row[0] for row in resultados]
        x_vals = [float(row[1]) for row in resultados]
        valores = [float(row[2]) for row in resultados]
        errores = [float(row[3]) for row in resultados]
        tipos = [row[4] for row in resultados]

        data = [
            {"x": x_vals, "y": valores, "type": "scatter", "name": "Valor Aproximado", "mode": "lines+markers"},
            {"x": x_vals, "y": errores, "type": "scatter", "name": "Error", "mode": "lines", "line": {"dash": "dash"}}
        ]
        layout = {
            "title": f"Aproximaciones de la Serie {serie.capitalize()} y Error",
            "xaxis": {"title": "x"},
            "yaxis": {"title": "Valor / Error"},
            "legend": {"x": 1, "y": 1}
        }

        print(f"✅ Datos procesados para {serie}: {len(resultados)} filas")
        print(f"Índices: {indices[:5]}...")
        print(f"X_vals: {x_vals[:5]}...")
        print(f"Valores: {valores[:5]}...")
        print(f"Errores: {errores[:5]}...")
        print(f"Tipos: {tipos[:5]}...")

        return jsonify({
            "data": data,
            "layout": layout,
            "tipos": tipos,
            "indices": indices,
            "x_vals": x_vals,
            "valores": valores,
            "errores": errores
        })
    except Exception as e:
        print(f"❌ Error al obtener datos para el gráfico: {e}")
        return jsonify({"data": [], "layout": {}, "indices": [], "x_vals": [], "valores": [], "errores": [], "tipos": []})
    finally:
        if conn:
            conn.close()

@app.route("/series/<tipo>", methods=["GET"])
def obtener_series(tipo):
    conn = conectar_bd()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        tabla = {
            "coseno": "series_coseno",
            "exp": "series_maclaurin",
            "onda_cuadrada": "series_fourier",
            "fibonacci_coseno": "series_fibonacci_coseno"
        }.get(tipo, None)
        if not tabla:
            return jsonify({"error": "Tipo de serie no válido"}), 400
        cursor.execute(f"SELECT * FROM {tabla} ORDER BY id ASC;")
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(datos)
    except Exception as e:
        print(f"❌ Error al obtener series: {e}")
        return jsonify({"error": "Error al obtener datos"}), 500

if __name__ == "__main__":
    inicializar_bd()
    app.run(host='0.0.0.0', port=5000, debug=True)