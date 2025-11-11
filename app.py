from flask import Flask, jsonify, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt
)
from functools import wraps
import datetime
from dotenv import load_dotenv
import os

from project.utils.mongo_config import init_mongo

# Importa el init_mongo 
from project.utils.mongo_config import init_mongo

app = Flask(__name__, template_folder="project/templates")

from project.routes.plants_routes import plants_bp
app.register_blueprint(plants_bp)

# .env
load_dotenv()
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)

# Mongo + JWT
mongo = init_mongo(app)
jwt = JWTManager(app)
app.config["mongo"] = mongo

# ------- Semilla de usuarios en MongoDB -------
def seed_users():
    users_col = mongo.db.users
    if users_col.count_documents({}) == 0:
        users_col.insert_many([
            {"username": "admin", "password": generate_password_hash("adminpass"), "roles": ["admin"]},
            {"username": "client", "password": generate_password_hash("clientpass"), "roles": ["client"]}
        ])
        print("✅ Usuarios de ejemplo creados en MongoDB")
    else:
        print("ℹ️ Usuarios ya existen en MongoDB")

seed_users()

# ------- Handlers JWT -------
@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return jsonify({"msg": "Token no proporcionado (Authorization header faltante)", "error": error_string}), 401

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"msg": "Token inválido", "error": reason}), 422

@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({"msg": "Token expirado"}), 401

# ------- Decorador de roles -------
def role_required(allowed_roles):
    """
    Uso:
    @role_required(['admin'])
    @role_required(['manager','admin'])
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            roles = claims.get("roles", [])
            if not any(r in roles for r in allowed_roles):
                return jsonify({"msg": "Rol no autorizado"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# ------- Endpoints -------
@app.route("/")
def index():
    return jsonify(message="Hola — Flask con JWT listo y control de roles"), 200

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "JSON esperado"}), 400

    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"msg": "username y password son requeridos"}), 400

    # Buscar usuario en MongoDB
    user = mongo.db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # Roles desde Mongo
    additional_claims = {"roles": user.get("roles", [])}
    access_token = create_access_token(identity=username, additional_claims=additional_claims)
    return jsonify(access_token=access_token), 200

@app.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    token_data = get_jwt()
    return jsonify({
        "msg": "Token válido",
        "identity": token_data.get("sub"),
        "token_claims": token_data
    }), 200

# Admin only
@app.route("/admin-only", methods=["GET"])
@role_required(['admin'])  # ya incluye @jwt_required dentro del decorador
def admin_only():
    return jsonify({"msg": "Área de administrador — acceso concedido ✅"}), 200

# Manager or admin
@app.route("/manager-area", methods=["GET"])
@role_required(['manager','admin'])
def manager_area():
    return jsonify({"msg": "Área de manager — acceso concedido"}), 200

# Crear usuario (solo admin)
@app.route("/users", methods=["POST"])
@role_required(['admin'])
def add_user():
    if not request.is_json:
        return jsonify({"msg": "JSON esperado"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    roles = data.get("roles", [])

    if not username or not password or not isinstance(roles, list):
        return jsonify({"msg": "username, password y roles (lista) son requeridos"}), 400

    users_col = mongo.db.users

    if users_col.find_one({"username": username}):
        return jsonify({"msg": "Usuario ya existe"}), 400

    users_col.insert_one({
        "username": username,
        "password": generate_password_hash(password),
        "roles": roles
    })

    return jsonify({
        "msg": "Usuario creado",
        "user": {"username": username, "roles": roles}
    }), 201

# Vista con render (admin/manager)
@app.route("/users-view", methods=["GET"])
@role_required(['admin', 'manager'])
def users_view():
    users = list(mongo.db.users.find({}, {"_id": 0, "username": 1, "roles": 1}))
    return render_template("users.html", users=users)

# Vista pública (sin JWT)
@app.route("/public-users")
def public_users():
    users = list(mongo.db.users.find({}, {"_id": 0, "username": 1, "roles": 1}))
    return render_template("users.html", users=users)

@app.get("/__routes__")
def _routes_debug():
    return jsonify(sorted([f"{r.methods} {r.rule}" for r in app.url_map.iter_rules()]))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)