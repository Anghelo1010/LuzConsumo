from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Importa CORS correctamente
import datetime

# Inicializa Flask solo UNA vez
app = Flask(__name__)

# Configuración de la base de datos y JWT
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@localhost:5432/iot"
app.config["JWT_SECRET_KEY"] = "supersecretkey"

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


# Endpoint para autenticación y generación de token
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    usuario = Usuario.query.filter_by(email=data["email"]).first()
    if usuario and usuario.clave == data["clave"]:  # Debe usarse hashing en producción
        token = create_access_token(identity=str(usuario.id))
        return jsonify({"token": token})
    return jsonify({"error": "Credenciales inválidas"}), 401


# Endpoint para recibir datos de Pydroid 3
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


# Endpoint para obtener datos históricos del usuario autenticado
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


# Nuevo endpoint para obtener TODAS las series matemáticas
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
