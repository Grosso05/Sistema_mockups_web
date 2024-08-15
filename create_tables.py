from flask import Flask
from models import db, configure_db

app = Flask(__name__)
configure_db(app)

with app.app_context():
    db.create_all()  # Esto creará todas las tablas en la base de datos
    print("Tablas creadas exitosamente.")
