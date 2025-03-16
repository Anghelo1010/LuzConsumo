from flask import Flask, render_template, jsonify, request
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

# Inicializar la aplicación Flask
app = Flask(__name__)

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",  # Cambia según la configuración de tu base de datos
        user="usuario0",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="aproxtaylor"  # Cambia por tu base de datos
    )
    return conexion

# Función para obtener los datos más recientes de la tabla coseno
def obtener_datos():
    conexion = conectar()
    cursor = conexion.cursor()

    # Consulta SQL para obtener los datos
    sql = "SELECT * FROM coseno ORDER BY nres"  # Limitamos los últimos 50 datos si es necesario
    cursor.execute(sql)
    resultados = cursor.fetchall()

    # Listas para almacenar los datos
    nres = []
    costaylor = []
    cosmath = []
    error = []

    for fila in resultados:
        nres.append(fila[0])
        costaylor.append(fila[1])
        cosmath.append(fila[2])
        error.append(fila[3])

    cursor.close()
    conexion.close()

    return nres, costaylor, cosmath, error

# Ruta principal que carga el dashboard
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para actualizar los datos del gráfico
@app.route('/datos_grafico', methods=['GET'])
def datos_grafico():
    nres, costaylor, cosmath, error = obtener_datos()

    # Crear la gráfica usando Plotly
    trace1 = go.Scatter(x=nres, y=costaylor, mode='lines+markers', name='Coseno (Taylor)')
    trace2 = go.Scatter(x=nres, y=cosmath, mode='lines+markers', name='Coseno (Math.cos)')
    trace3 = go.Scatter(x=nres, y=error, mode='lines', name='Error', line=dict(color='red', dash='dash'))

    layout = go.Layout(
        title=f'Gráfico en tiempo real - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        xaxis_title='ID (nres)',
        yaxis_title='Valores de Coseno',
        legend=dict(x=0, y=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

    # Convertir la gráfica a JSON
    graph_json = pio.to_json(fig)

    return jsonify(graph_json)

if __name__ == "__main__":
    # Cambiar el host a '0.0.0.0' para permitir conexiones desde otros dispositivos
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
