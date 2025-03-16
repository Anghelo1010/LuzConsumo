from flask import Flask, render_template, jsonify
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",  # Predeterminado en XAMPP
            password="",  # Sin contraseña por defecto en XAMPP
            database="fibonacci_trigonometric"
        )
        print("Conexión a la base de datos exitosa")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

def obtener_datos():
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        sql = "SELECT id, tipo_serie, resultado, cos_fib, error, fecha FROM fibonacci_cos ORDER BY id"
        cursor.execute(sql)
        resultados = cursor.fetchall()
        print(f"Datos recuperados: {len(resultados)} filas")

        tabla_datos = []
        ids = []
        resultados_vals = []
        cos_fib_vals = []
        errors = []

        for fila in resultados:
            ids.append(fila[0])
            resultados_vals.append(fila[2])
            cos_fib_vals.append(fila[3])
            errors.append(fila[4])
            tabla_datos.append({
                "id": fila[0],
                "tipo_serie": fila[1],
                "resultado": fila[2],
                "error": fila[4],
                "fecha": fila[5].strftime("%Y-%m-%d %H:%M:%S")
            })

        cursor.close()
        conexion.close()

        return ids, resultados_vals, cos_fib_vals, errors, tabla_datos
    except Exception as e:
        print(f"Error en obtener_datos: {e}")
        raise

@app.route('/')
def index():
    print("Renderizando index.html")
    return render_template('index.html')

@app.route('/datos_grafico', methods=['GET'])
def datos_grafico():
    try:
        ids, resultados, cos_fib, errors, tabla_datos = obtener_datos()

        trace1 = go.Scatter(x=ids, y=resultados, mode='lines+markers', name='Fibonacci')
        trace2 = go.Scatter(x=ids, y=cos_fib, mode='lines+markers', name='Coseno(Fibonacci)')
        trace3 = go.Scatter(x=ids, y=errors, mode='lines', name='Error', line=dict(color='red', dash='dash'))

        layout = go.Layout(
            title=f'Gráfico en tiempo real - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            xaxis_title='ID',
            yaxis_title='Valores',
            legend=dict(x=0, y=1),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
        graph_json = pio.to_json(fig)

        response = {
            "grafico": graph_json,
            "tabla": tabla_datos
        }
        print("Datos enviados al cliente")
        return jsonify(response)
    except Exception as e:
        print(f"Error en datos_grafico: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Iniciando servidor Flask...")
    app.run(debug=True, use_reloader=False)
#Para instalar
#.\.venv\Scripts\Activate.ps1
#pip install mysql-connector-python
#pip install flask plotly mysql-connector-python