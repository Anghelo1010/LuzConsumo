from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
from datetime import timedelta
import numpy as np

# Inicializa Flask solo UNA vez
app = Flask(__name__)

# Configuración de la base de datos y JWT
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@localhost:5432/iot"
app.config["JWT_SECRET_KEY"] = "supersecretkey"

# ⏳ Token de acceso dura 7 días
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
# 🔄 Refresh token dura 30 días
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

db = SQLAlchemy(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Habilitar CORS correctamente después de inicializar Flask
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Modelo de Series Matemáticas
class SeriesMatematicas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    tipo_serie = db.Column(db.String(50), nullable=False)
    parametros = db.Column(db.JSON, nullable=False)
    resultado = db.Column(db.Numeric, nullable=False)
    error = db.Column(db.Numeric, nullable=False)
    iteraciones = db.Column(db.Integer, nullable=False)
    precision = db.Column(db.Numeric, nullable=False)
    tiempo_calculo = db.Column(db.Float, nullable=False)
    dispositivo = db.Column(db.String(100))
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Función para calcular la serie de Fourier (simplificada)
def calcular_fourier(n, frecuencias, amplitudes):
    t = np.linspace(0, 2 * np.pi, n)
    resultado = np.zeros(n)

    for f, a in zip(frecuencias, amplitudes):
        resultado += a * np.sin(f * t)

    # Calculamos el error como la diferencia entre el máximo y el mínimo
    error = np.max(resultado) - np.min(resultado)
    return resultado, error

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    usuario = Usuario.query.filter_by(email=data["email"]).first()
    if usuario and usuario.clave == data["clave"]:  # ¡Usa hashing en producción!
        access_token = create_access_token(
            identity=str(usuario.id), expires_delta=datetime.timedelta(days=7)
        )
        return jsonify(
            {"token": access_token}
        )  # 👈 Asegúrate de que el frontend busca "token"

    return jsonify({"error": "Credenciales inválidas"}), 401

# 🔄 Endpoint para renovar el token de acceso usando el refresh token
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    usuario_id = get_jwt_identity()
    nuevo_token = create_access_token(identity=usuario_id)
    return jsonify({"access_token": nuevo_token})

# ✅ Endpoint para recibir datos de Pydroid 3 (sería para cualquier otra serie también)
@app.route("/enviar_datos", methods=["POST"])
@jwt_required()
def recibir_datos():
    usuario_id = get_jwt_identity()
    data = request.json
    nueva_serie = SeriesMatematicas(
        usuario_id=usuario_id,
        tipo_serie=data["tipo_serie"],
        parametros=data["parametros"],
        resultado=data["resultado"],
        error=data["error"],
        iteraciones=data["iteraciones"],
        precision=data["precision"],
        tiempo_calculo=data["tiempo_calculo"],
        dispositivo=data.get("dispositivo", "Desconocido"),
    )
    db.session.add(nueva_serie)
    db.session.commit()

    # Enviar datos en tiempo real con WebSocket
    socketio.emit(
        "nueva_serie",
        {
            "tipo_serie": data["tipo_serie"],
            "resultado": data["resultado"],
            "error": data["error"],
        },
    )

    return jsonify({"mensaje": "Datos almacenados correctamente"})

# ✅ Nuevo endpoint para recibir datos de la serie de Fourier
@app.route("/enviar_datos_fourier", methods=["POST"])
@jwt_required()
def recibir_datos_fourier():
    usuario_id = get_jwt_identity()
    data = request.json
    
    # Obtenemos los parámetros de la serie de Fourier
    frecuencias = data["frecuencias"]  # [f1, f2, ...]
    amplitudes = data["amplitudes"]    # [a1, a2, ...]

    # Validación de que las frecuencias y amplitudes tengan la misma longitud
    if len(frecuencias) != len(amplitudes):
        return jsonify({"error": "Las frecuencias y amplitudes deben tener la misma longitud"}), 400

    n = data["n"]  # Número de puntos en la serie de Fourier
    resultado, error = calcular_fourier(n, frecuencias, amplitudes)

    # Crear un nuevo registro para la serie de Fourier en la base de datos
    nueva_serie = SeriesMatematicas(
        usuario_id=usuario_id,
        tipo_serie="Fourier",
        parametros={"frecuencias": frecuencias, "amplitudes": amplitudes, "n": n},
        resultado=resultado[-1],  # Último valor de la serie
        error=error,
        iteraciones=n,
        precision=data["precision"],  # Asegúrate de pasar la precisión
        tiempo_calculo=data["tiempo_calculo"],  # Asegúrate de pasar el tiempo de cálculo
        dispositivo=data.get("dispositivo", "Desconocido"),
    )
    db.session.add(nueva_serie)
    db.session.commit()

    # Enviar datos en tiempo real con WebSocket
    socketio.emit(
        "nueva_serie_fourier",
        {
            "tipo_serie": "Fourier",
            "resultado": resultado.tolist(),  # Convertimos el array a lista
            "error": error,
        },
    )

    return jsonify({"mensaje": "Datos de la serie de Fourier almacenados correctamente"})

# ✅ Endpoint para obtener datos históricos del usuario autenticado
@app.route("/obtener_datos", methods=["GET"])
@jwt_required()
def obtener_datos():
    usuario_id = get_jwt_identity()
    series = SeriesMatematicas.query.filter_by(usuario_id=usuario_id).all()

    if not series:
        return jsonify([]), 200  # Devuelve lista vacía en vez de error

    resultado = [
        {
            "tipo_serie": s.tipo_serie,
            "resultado": float(s.resultado),
            "error": float(s.error),
            "fecha": s.fecha.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for s in series
    ]
    return jsonify(resultado)

# ✅ Nuevo endpoint para obtener TODAS las series matemáticas
@app.route("/series", methods=["GET"])
@jwt_required()
def obtener_todas_las_series():
    series = SeriesMatematicas.query.all()
    resultado = [
        {
            "id": s.id,
            "usuario_id": s.usuario_id,
            "tipo_serie": s.tipo_serie,
            "parametros": s.parametros,
            "resultado": float(s.resultado),
            "error": float(s.error),
            "iteraciones": s.iteraciones,
            "precision": float(s.precision),
            "tiempo_calculo": s.tiempo_calculo,
            "dispositivo": s.dispositivo,
            "fecha": s.fecha.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for s in series
    ]
    return jsonify(resultado)

@app.route("/")  # Verifica que esta ruta esté definida
def home():
    return "API funcionando correctamente 🚀"

if __name__ == "__main__":
    app.run(debug=True)

