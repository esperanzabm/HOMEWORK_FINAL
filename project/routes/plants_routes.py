# ===============================================
# 🌿 Plants Routes - Proyecto SimpleFlaskHomework
# ===============================================
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from bson import ObjectId

# Definición del Blueprint
plants_bp = Blueprint("plants", __name__, url_prefix="/plants")


# -----------------------------------------------
# Función auxiliar para obtener la instancia de Mongo
# -----------------------------------------------
def get_mongo():
    """Obtiene la instancia de Mongo guardada en la app principal"""
    return current_app.config["mongo"]


# -----------------------------------------------
# Función auxiliar para formatear los documentos
# -----------------------------------------------
def plant_to_json(plant):
    """Convierte un documento Mongo en un JSON serializable"""
    return {
        "id": str(plant["_id"]),
        "name": plant.get("name"),
        "type": plant.get("type"),
        "care_level": plant.get("care_level", "unknown")
    }


# -----------------------------------------------
# POST → Crear una planta (requiere autenticación)
# -----------------------------------------------
@plants_bp.route("/", methods=["POST"])
@jwt_required()
def create_plant():
    mongo = get_mongo()
    data = request.get_json()

    # Validación de datos
    name = data.get("name")
    type_ = data.get("type")
    care_level = data.get("care_level", "medium")

    if not name or not type_:
        return jsonify({"msg": "Los campos 'name' y 'type' son requeridos"}), 400

    # Inserción en MongoDB
    plant_id = mongo.db.plants.insert_one({
        "name": name,
        "type": type_,
        "care_level": care_level
    }).inserted_id

    return jsonify({
        "msg": "🌱 Planta creada exitosamente",
        "id": str(plant_id),
        "data": {"name": name, "type": type_, "care_level": care_level}
    }), 201


# -----------------------------------------------
# GET → Obtener todas las plantas o filtradas
# -----------------------------------------------
@plants_bp.route("/", methods=["GET"])
def get_plants():
    mongo = get_mongo()
    care_filter = request.args.get("care_level")

    query = {}
    if care_filter:
        query["care_level"] = care_filter

    plants = list(mongo.db.plants.find(query))
    return jsonify([plant_to_json(p) for p in plants]), 200


# -----------------------------------------------
# GET → Obtener planta por ID
# -----------------------------------------------
@plants_bp.route("/<string:plant_id>", methods=["GET"])
def get_plant_by_id(plant_id):
    mongo = get_mongo()
    try:
        plant = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
        if not plant:
            return jsonify({"msg": "Planta no encontrada"}), 404
        return jsonify(plant_to_json(plant)), 200
    except Exception:
        return jsonify({"msg": "ID inválido"}), 400


# -----------------------------------------------
# DELETE → Eliminar una planta (solo admin)
# -----------------------------------------------
@plants_bp.route("/<string:plant_id>", methods=["DELETE"])
@jwt_required()
def delete_plant(plant_id):
    mongo = get_mongo()
    try:
        result = mongo.db.plants.delete_one({"_id": ObjectId(plant_id)})
        if result.deleted_count == 0:
            return jsonify({"msg": "Planta no encontrada"}), 404
        return jsonify({"msg": "🗑️ Planta eliminada exitosamente"}), 200
    except Exception:
        return jsonify({"msg": "ID inválido"}), 400


# -----------------------------------------------
# PUT → Actualizar una planta existente
# -----------------------------------------------
@plants_bp.route("/<string:plant_id>", methods=["PUT"])
@jwt_required()
def update_plant(plant_id):
    mongo = get_mongo()
    data = request.get_json()

    fields = {}
    for key in ["name", "type", "care_level"]:
        if key in data:
            fields[key] = data[key]

    if not fields:
        return jsonify({"msg": "Debe enviar al menos un campo para actualizar"}), 400

    try:
        result = mongo.db.plants.update_one(
            {"_id": ObjectId(plant_id)},
            {"$set": fields}
        )

        if result.matched_count == 0:
            return jsonify({"msg": "Planta no encontrada"}), 404

        updated = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
        return jsonify({
            "msg": "🌻 Planta actualizada exitosamente",
            "data": plant_to_json(updated)
        }), 200

    except Exception:
        return jsonify({"msg": "ID inválido"}), 400
