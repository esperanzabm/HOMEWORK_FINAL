# mongo_test_connection.py
from flask import Flask
from dotenv import load_dotenv
import os
from app.utils.mongo_config import init_mongo

# Cargar variables del .env
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Inicializar Mongo
mongo = init_mongo(app)

# Probar conexión
try:
    mongo.db.command("ping")
    print("✅ Conexión a MongoDB OK")
except Exception as e:
    print("❌ Error de conexión:", e)
