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
import random
import math

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
    resultado_seno = db.Column(db.Numeric, nullable=False)
    resultado_coseno = db.Column(db.Numeric, nullable=False)
    resultado_tangente = db.Column(db.Numeric, nullable=False)
    error_seno = db.Column(db.Numeric, nullable=False)
    error_coseno = db.Column(db.Numeric, nullable=False)
    error_tangente = db.Column(db.Numeric, nullable=False)


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
    
    valor = float(data["resultado"])
    resultado_seno = math.sin(valor)
    resultado_coseno = math.cos(valor)
    resultado_tangente = math.tan(valor)
    
    error_seno = abs(resultado_seno - math.sin(valor))
    error_coseno = abs(resultado_coseno - math.cos(valor))
    error_tangente = abs(resultado_tangente - math.tan(valor))

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
        resultado_seno=resultado_seno,
        resultado_coseno=resultado_coseno,
        resultado_tangente=resultado_tangente,
        error_seno=error_seno,
        error_coseno=error_coseno,
        error_tangente=error_tangente,
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
            "resultado_seno": resultado_seno,
            "resultado_coseno": resultado_coseno,
            "resultado_tangente": resultado_tangente,
            "error_seno": error_seno,
            "error_coseno": error_coseno,
            "error_tangente": error_tangente,
        },
    )

    return jsonify({"mensaje": "Datos almacenados correctamente"})


@app.route("/")  # Verifica que esta ruta esté definida
def home():
    return "API funcionando correctamente 🚀"


if __name__ == "__main__":
    app.run(debug=True)
