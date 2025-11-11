from flask_pymongo import PyMongo

def init_mongo(app):
    mongo = PyMongo(app)
    return mongo