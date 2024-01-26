# models.py
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sqlalchemy import text 
from flask_login import UserMixin  # Importa la clase UserMixin de flask_login
db = SQLAlchemy()

class UsersRol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(20), nullable=False)

class Users(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), nullable=False)
    user_last_name = db.Column(db.String(30), nullable=False)
    user_email = db.Column(db.String(30), nullable=False)
    user_password = db.Column(db.String(12), nullable=False)
    user_rol = db.Column(db.Integer, db.ForeignKey('users_rol.id'), nullable=False)
    users_rol = db.relationship('UsersRol', backref='users', lazy=True)
    session_token = db.Column(db.String(50), unique=True)

    def get_id(self):
        return str(self.user_id)

def configure_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/software_innova'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

def test_db_connection(app):
    with app.app_context():
        with db.engine.connect() as connection:
            try:
                # Imprimir en consola el contenido de la tabla users
                result = connection.execute(Users.query.statement)
                for row in result.fetchall():
                    print(row)
                print("Conexión a la base de datos exitosa.")
            except Exception as e:
                print(f"Error al conectar a la base de datos: {str(e)}")
