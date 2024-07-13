# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL, Column, Date, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy import Index

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
    user_link = db.Column(db.String(100), nullable=True)

    def get_id(self):
        return str(self.user_id)

class UnidadesNegocio(db.Model):
    """
    Esta clase representa la tabla 'unidades_negocio' en la base de datos.
    """
    unidad_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<UnidadesNegocio {self.nombre}>"

class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_email = db.Column(db.String(80), nullable=False)
    customer_date = db.Column(db.Date, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user_rel = db.relationship('Users', backref='customers', lazy=True)
    contactado = db.Column(db.Boolean, default=False, server_default=text('0'))

class Categoria(db.Model):
  """
  This class represents the Categoria table in the database.
  """
  CATEGORIA_ID = Column(Integer, primary_key=True, autoincrement=True)
  CATEGORIA_NOMBRE = Column(String(50), nullable=False)

  def __repr__(self):
    return f"<Categoria {self.CATEGORIA_NOMBRE}>"

class Cotizacion(db.Model):
  """
  This class represents the Cotizacion table in the database.
  """
  ID_COTIZACION = Column(Integer, primary_key=True, autoincrement=True)
  NEGOCIACION = Column(Integer, nullable=False)
  FECHA_COTIZACION = Column(Date, nullable=False)
  CLIENTE_COTIZACION = Column(String(150))
  CONTACTO_COTIZACION = Column(String(100))
  PROYECTO_COTIZACION = Column(String(150))
  PORCENTAJE_DESCUENTO = Column(Integer)
  PERSONA_RECIBE = Column(String(100))
  NUMERO_CONTACTO = Column(String(50))
  DIRECCION = Column(String(200))

  def __repr__(self):
    return f"<Cotizacion {self.ID_COTIZACION}>"

# The Customers model already exists, so we don't need to create it again

class Items(db.Model):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categoria.CATEGORIA_ID'))
    unidad = Column(String(255))
    tipo = Column(String(255))

    categoria = relationship("Categoria", backref="items")

    __table_args__ = (Index('idx_nombre', 'nombre'),)

    def __repr__(self):
        return f"<Items {self.nombre}>"
  
class ItemsPorProducto(db.Model):
  """
  This class represents the Items_por_producto table in the database.
  It represents the many-to-many relationship between Items and Productos tables.
  """
  item_producto_id = Column(Integer, primary_key=True, autoincrement=True)
  producto_idFK = Column(Integer, ForeignKey('productos.producto_id'), nullable=False)
  item_idFK = Column(Integer, ForeignKey('items.item_id'), nullable=False)

  producto = relationship("Productos", backref="items_por_producto")
  item = relationship("Items", backref="items_por_producto")

  def __repr__(self):
    return f"<ItemsPorProducto item_id: {self.item_idFK}, producto_id: {self.producto_idFK}>"
  
class ItemProveedores(db.Model):
    """
    This class represents the itemproveedores table in the database.
    It represents the many-to-many relationship between Items and Proveedores tables
    with additional attributes for tipo_proveedor, precio, and fecha.

    """
    __tablename__ = 'itemproveedores'

    item_id = Column(Integer, ForeignKey('items.item_id'), primary_key=True, nullable=False)
    id_proveedor = Column(Integer, ForeignKey('proveedores.ID_PROVEEDOR'), primary_key=True, nullable=False)  # Added ForeignKey constraint
    tipo_proveedor = Column(Integer, nullable=False)
    precio = Column(DECIMAL(10, 2))
    fecha = Column(Date)

    # Define relationships with foreign keys
    item = relationship("Items", backref="itemproveedores")
    proveedor = relationship("Proveedores", backref="itemproveedores")

    def __repr__(self):
        return f"<ItemProveedor item_id: {self.item_id}, id_proveedor: {self.id_proveedor}, tipo_proveedor: {self.tipo_proveedor}>"



  
class Lineas(db.Model):
  """
  This class represents the Lineas table in the database.
  """
  linea_id = Column(Integer, primary_key=True, autoincrement=True)
  unidad_idFK = Column(Integer, ForeignKey('unidades_negocio.unidad_id'), nullable=False)
  nombre = Column(String(100), nullable=False)

  unidad_negocio = relationship("UnidadesNegocio", backref="lineas")  # Relationship definition

  def __repr__(self):
    return f"<Lineas {self.nombre}>"

  
class Productos(db.Model):
  """
  This class represents the Productos table in the database.
  """
  producto_id = Column(Integer, primary_key=True, autoincrement=True)
  linea_idFK = Column(Integer, ForeignKey('lineas.linea_id'), nullable=False)
  nombre = Column(String(200), nullable=False)

  linea = relationship("Lineas", backref="productos")

  def __repr__(self):
    return f"<Productos {self.nombre}>"
  
class Proveedores(db.Model):
  """
  This class represents the Proveedores table in the database.
  """
  ID_PROVEEDOR = Column(Integer, primary_key=True, autoincrement=True)
  NOMBRE_PROVEEDOR = Column(String(100), nullable=False, default='0')
  TELEFONO_PROVEEDOR = Column(String(100), nullable=False, default='0')
  DIRECCION_PROVEEDOR = Column(String(100), nullable=False, default='0')
  CELULAR_PROVEEDOR = Column(String(100), nullable=False, default='0')
  CONTACTO_PROVEEDOR = Column(String(100), nullable=False, default='0')
  WEB_PROVEEDOR = Column(String(100), nullable=False, default='0')
  EMAIL_PROVEEDOR = Column(String(100), nullable=False, default='0')
  NIT_PROVEEDOR = Column(String(20), nullable=False, default='0')
  MATERIALES_PRINCIPALES = Column(String(100), nullable=False, default='0')

  def __repr__(self):
    return f"<Proveedores {self.NOMBRE_PROVEEDOR}>"


    

def configure_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://AdminDb:M52eqEhiH3@127.0.0.1/software_innova'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

def test_db_connection(app):
    with app.app_context():
        with db.engine.connect() as connection:
            try:
                print("----------------------------------")
                print("Conexión a la base de datos exitosa.")
                print("----------------------------------")
            except Exception as e:
                print("----------------------------------")
                print(f"Error al conectar a la base de datos: {str(e)}")
                print("----------------------------------")

