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

def conectar_base_datos():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return None

def inicializar_base_datos():
    conexion = conectar_base_datos()
    if conexion is None:
        return
    try:
        cursor_db = conexion.cursor()
        series_tablas = {
            "series_coseno_datos": "coseno",
            "series_maclaurin_datos": "exp",
            "series_fourier_datos": "onda_cuadrada",
            "series_fibonacci_coseno_datos": "fibonacci_coseno"
        }
        for serie_tabla, serie_categoria in series_tablas.items():
            cursor_db.execute(f"""
                CREATE TABLE IF NOT EXISTS {serie_tabla} (
                    id SERIAL PRIMARY KEY, 
                    serie_indice INT, 
                    punto_x NUMERIC, 
                    valor_calculado NUMERIC, 
                    diferencia NUMERIC, 
                    serie_categoria TEXT, 
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor_db.execute(f"SELECT COUNT(*) FROM {serie_tabla}")
            if cursor_db.fetchone()[0] == 0:
                if serie_categoria == "coseno":
                    agregar_datos_base(serie_categoria, np.linspace(0, 2 * np.pi, 10), 5)
                elif serie_categoria == "exp":
                    agregar_datos_base(serie_categoria, np.linspace(-2, 2, 10), 5)
                elif serie_categoria == "onda_cuadrada":
                    agregar_datos_base(serie_categoria, np.linspace(-np.pi, np.pi, 10), 5)
                elif serie_categoria == "fibonacci_coseno":
                    agregar_datos_base(serie_categoria, np.linspace(0, 2 * np.pi, 10), 5)
        conexion.commit()
        cursor_db.close()
        print("✅ Tablas verificadas y datos iniciales creados correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
    finally:
        conexion.close()

def insertar_registros(serie_categoria, puntos_x, valores_calculados, diferencias):
    conexion = conectar_base_datos()
    if conexion is None:
        return
    serie_tabla = {
        "coseno": "series_coseno_datos",
        "exp": "series_maclaurin_datos",
        "onda_cuadrada": "series_fourier_datos",
        "fibonacci_coseno": "series_fibonacci_coseno_datos"
    }.get(serie_categoria, None)
    if not serie_tabla:
        return
    try:
        cursor_db = conexion.cursor()
        fecha_registro = datetime.now()
        registros = [(i, float(puntos_x[i]), float(valores_calculados[i]), float(diferencias[i]), serie_categoria, fecha_registro) 
                     for i in range(len(puntos_x))]
        cursor_db.executemany(f"""
            INSERT INTO {serie_tabla} (serie_indice, punto_x, valor_calculado, diferencia, serie_categoria, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, registros)
        conexion.commit()
        cursor_db.close()
        print(f"✅ Datos de '{serie_categoria}' insertados correctamente.")
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
    finally:
        conexion.close()

def calcular_cos_taylor(punto_x, total_terminos):
    return sum(((-1) ** iterador * punto_x ** (2 * iterador)) / math.factorial(2 * iterador) for iterador in range(total_terminos))

def calcular_exp_maclaurin(punto_x, total_terminos):
    return sum((punto_x ** iterador) / math.factorial(iterador) for iterador in range(total_terminos))

def calcular_onda_cuadrada(punto_x, total_terminos):
    return 4 / np.pi * sum((1 / (2 * iterador + 1)) * np.sin((2 * iterador + 1) * punto_x) for iterador in range(total_terminos))

def calcular_fibonacci_coseno(punto_x, total_terminos):
    fibonacci_nums = [0, 1]
    for i in range(2, total_terminos):
        fibonacci_nums.append(fibonacci_nums[i-1] + fibonacci_nums[i-2])
    fibonacci_max = max(fibonacci_nums[:total_terminos]) if total_terminos > 0 else 1
    return sum((fibonacci_nums[iterador] / fibonacci_max) * np.cos(iterador * punto_x) for iterador in range(min(total_terminos, len(fibonacci_nums))))

def agregar_datos_base(serie_categoria, puntos_x, total_terminos):
    if serie_categoria == "coseno":
        valores_aprox = [calcular_cos_taylor(px, total_terminos) for px in puntos_x]
        valores_reales = [np.cos(px) for px in puntos_x]
    elif serie_categoria == "exp":
        valores_aprox = [calcular_exp_maclaurin(px, total_terminos) for px in puntos_x]
        valores_reales = [np.exp(px) for px in puntos_x]
    elif serie_categoria == "onda_cuadrada":
        valores_aprox = [calcular_onda_cuadrada(px, total_terminos) for px in puntos_x]
        valores_reales = [np.sign(np.sin(px)) for px in puntos_x]
    elif serie_categoria == "fibonacci_coseno":
        valores_aprox = [calcular_fibonacci_coseno(px, total_terminos) for px in puntos_x]
        valores_reales = [np.cos(px) for px in puntos_x]
    diferencias = [abs(ap - real) for ap, real in zip(valores_aprox, valores_reales)]
    insertar_registros(serie_categoria, puntos_x, valores_aprox, diferencias)

@app.route('/insertar', methods=['POST'])
def insertar():
    try:
        datos_entrada = request.json
        if not datos_entrada:
            return jsonify({"status": "error", "message": "No se proporcionaron datos en el cuerpo de la solicitud"}), 400

        if 'n' not in datos_entrada or 'num_terminos' not in datos_entrada or 'tipo_serie' not in datos_entrada:
            return jsonify({"status": "error", "message": "Faltan parámetros: 'n', 'num_terminos' o 'tipo_serie'"}), 400

        cantidad_puntos = int(datos_entrada['n'])
        total_terminos = int(datos_entrada['num_terminos'])
        serie_categoria = datos_entrada['tipo_serie']

        if cantidad_puntos <= 0 or total_terminos <= 0:
            return jsonify({"status": "error", "message": "Los valores de 'n' y 'num_terminos' deben ser mayores que 0"}), 400

        if serie_categoria == "coseno":
            puntos_x = np.linspace(0, 2 * np.pi, cantidad_puntos)
        elif serie_categoria == "exp":
            puntos_x = np.linspace(-2, 2, cantidad_puntos)
        elif serie_categoria == "onda_cuadrada":
            puntos_x = np.linspace(-np.pi, np.pi, cantidad_puntos)
        elif serie_categoria == "fibonacci_coseno":
            puntos_x = np.linspace(0, 2 * np.pi, cantidad_puntos)
        else:
            return jsonify({"status": "error", "message": f"Tipo de serie no válido: {serie_categoria}"}), 400

        agregar_datos_base(serie_categoria, puntos_x, total_terminos)
        return jsonify({"status": "success", "message": f"Se agregaron {cantidad_puntos} datos para {serie_categoria}"})

    except ValueError as ve:
        return jsonify({"status": "error", "message": f"Error en los valores proporcionados: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno del servidor: {str(e)}"}), 500

@app.route('/datos_grafico')
def datos_grafico():
    serie_seleccionada = request.args.get('serie', default=None, type=str)
    
    conexion = conectar_base_datos()
    if conexion is None:
        print("❌ No se pudo conectar a la base de datos en /datos_grafico")
        return jsonify({"grafico_datos": [], "grafico_config": {}, "serie_indices": [], "serie_puntos_x": [], "serie_valores": [], "serie_diferencias": [], "serie_tipos": []})
    
    try:
        cursor_db = conexion.cursor()
        
        serie_tabla = {
            "coseno": "series_coseno_datos",
            "exp": "series_maclaurin_datos",
            "onda_cuadrada": "series_fourier_datos",
            "fibonacci_coseno": "series_fibonacci_coseno_datos"
        }.get(serie_seleccionada, None)

        if not serie_seleccionada or not serie_tabla:
            print(f"⚠️ Serie no especificada o no válida: {serie_seleccionada}")
            return jsonify({"grafico_datos": [], "grafico_config": {}, "serie_indices": [], "serie_puntos_x": [], "serie_valores": [], "serie_diferencias": [], "serie_tipos": []})

        cursor_db.execute(f"""
            SELECT serie_indice, punto_x, valor_calculado, diferencia, serie_categoria 
            FROM {serie_tabla}
            ORDER BY punto_x
        """)
        registros_db = cursor_db.fetchall()
        print(f"📊 Resultados crudos de la consulta para {serie_seleccionada}: {registros_db}")

        if not registros_db:
            print(f"⚠️ No se encontraron datos para la serie {serie_seleccionada}")
            return jsonify({"grafico_datos": [], "grafico_config": {}, "serie_indices": [], "serie_puntos_x": [], "serie_valores": [], "serie_diferencias": [], "serie_tipos": []})

        serie_indices = [row[0] for row in registros_db]
        serie_puntos_x = [float(row[1]) for row in registros_db]
        serie_valores = [float(row[2]) for row in registros_db]
        serie_diferencias = [float(row[3]) for row in registros_db]
        serie_tipos = [row[4] for row in registros_db]

        grafico_datos = [
            {"x": serie_puntos_x, "y": serie_valores, "type": "scatter", "name": "Valor Aproximado", "mode": "lines+markers"},
            {"x": serie_puntos_x, "y": serie_diferencias, "type": "scatter", "name": "Diferencia", "mode": "lines", "line": {"dash": "dash"}}
        ]
        grafico_config = {
            "title": f"Aproximaciones de la Serie {serie_seleccionada.capitalize()} y Diferencia",
            "xaxis": {"title": "x"},
            "yaxis": {"title": "Valor / Diferencia"},
            "legend": {"x": 1, "y": 1}
        }

        print(f"✅ Datos procesados para {serie_seleccionada}: {len(registros_db)} filas")
        print(f"Serie_indices: {serie_indices[:5]}...")
        print(f"Serie_puntos_x: {serie_puntos_x[:5]}...")
        print(f"Serie_valores: {serie_valores[:5]}...")
        print(f"Serie_diferencias: {serie_diferencias[:5]}...")
        print(f"Serie_tipos: {serie_tipos[:5]}...")

        return jsonify({
            "grafico_datos": grafico_datos,
            "grafico_config": grafico_config,
            "serie_tipos": serie_tipos,
            "serie_indices": serie_indices,
            "serie_puntos_x": serie_puntos_x,
            "serie_valores": serie_valores,
            "serie_diferencias": serie_diferencias
        })
    except Exception as e:
        print(f"❌ Error al obtener datos para el gráfico: {e}")
        return jsonify({"grafico_datos": [], "grafico_config": {}, "serie_indices": [], "serie_puntos_x": [], "serie_valores": [], "serie_diferencias": [], "serie_tipos": []})
    finally:
        if conexion:
            conexion.close()

@app.route("/series/<categoria>", methods=["GET"])
def obtener_datos_serie(categoria):
    conexion = conectar_base_datos()
    if conexion is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    try:
        cursor_db = conexion.cursor()
        serie_tabla = {
            "coseno": "series_coseno_datos",
            "exp": "series_maclaurin_datos",
            "onda_cuadrada": "series_fourier_datos",
            "fibonacci_coseno": "series_fibonacci_coseno_datos"
        }.get(categoria, None)
        if not serie_tabla:
            return jsonify({"error": "Tipo de serie no válido"}), 400
        cursor_db.execute(f"SELECT * FROM {serie_tabla} ORDER BY id ASC;")
        datos_serie = cursor_db.fetchall()
        cursor_db.close()
        conexion.close()
        return jsonify(datos_serie)
    except Exception as e:
        print(f"❌ Error al obtener series: {e}")
        return jsonify({"error": "Error al obtener datos"}), 500

if __name__ == "__main__":
    inicializar_base_datos()
    app.run(host='0.0.0.0', port=5000, debug=True)