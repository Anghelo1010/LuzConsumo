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
import math
import time

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

# Función para calcular Fibonacci exacto
def fibonacci_exacto(n):
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return round((math.pow(phi, n) - math.pow(psi, n)) / math.sqrt(5))

# Función para aproximar Fibonacci usando coseno
def fibonacci_coseno(n, theta=0.5):
    phi = (1 + math.sqrt(5)) / 2
    return (math.cos(n * theta) / math.sqrt(5)) * math.pow(phi, n)


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


# ✅ Endpoint para recibir datos de Pydroid 3
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

# Nuevo endpoint para Fibonacci con coseno
@app.route("/enviar_fibonacci_coseno", methods=["POST"])
@jwt_required()
def enviar_fibonacci_coseno():
    usuario_id = get_jwt_identity()
    data = request.json
    n = data.get("n", 10)  # Número de término de Fibonacci
    theta = data.get("theta", 0.5)  # Ángulo theta por defecto
    iteraciones = data.get("iteraciones", 1)
    precision = data.get("precision", 0.0001)

    # Calcular Fibonacci exacto y aproximado
    start_time = time.time()
    fib_exacto = fibonacci_exacto(n)
    fib_coseno = fibonacci_coseno(n, theta)
    error = abs(fib_exacto - fib_coseno)
    tiempo_calculo = time.time() - start_time

    nueva_serie = SeriesMatematicas(
        usuario_id=usuario_id,
        tipo_serie="fibonacci_coseno",
        parametros={"n": n, "theta": theta},
        resultado=fib_coseno,
        error=error,
        iteraciones=iteraciones,
        precision=precision,
        tiempo_calculo=tiempo_calculo,
        dispositivo=data.get("dispositivo", "Desconocido"),
    )
    db.session.add(nueva_serie)
    db.session.commit()

    socketio.emit("nueva_serie", {
        "tipo_serie": "fibonacci_coseno",
        "resultado": float(fib_coseno),
        "error": float(error),
        "fecha": nueva_serie.fecha.strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"mensaje": "Fibonacci con coseno almacenado correctamente"})


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