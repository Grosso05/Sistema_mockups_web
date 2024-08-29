# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL, TIMESTAMP, Boolean, Column, Date, Float, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from datetime import datetime

from flask_login import UserMixin  
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





# The Customers model already exists, so we don't need to create it again

class Items(db.Model):
    __tablename__ = 'items'  # Nombre correcto de la tabla
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False, index= True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.CATEGORIA_ID'))
    unidad = db.Column(db.String(255))
    tipo = db.Column(db.String(255))

    categoria = db.relationship("Categoria", backref="items")

    __table_args__ = (db.Index('idx_nombre', 'nombre'),)

    def __repr__(self):
        return f"<Items {self.nombre}>"
    


class ItemTemporal(db.Model):
    __tablename__ = 'itemtemporal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)  # Actualizado a 'descripcion'
    precio = db.Column(db.Float, nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    aprobado = db.Column(db.Boolean, default=False)

    # Definir la relación con Users
    creado_por_usuario = db.relationship('Users', backref='items_temporales')

    def __repr__(self):
        return f"<ItemTemporal {self.descripcion}>"

  
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
    __tablename__ = 'productos'
    producto_id = Column(Integer, primary_key=True, autoincrement=True)
    linea_idFK = Column(Integer, ForeignKey('lineas.linea_id'), nullable=False)
    nombre = Column(String(200), nullable=False)

    linea = relationship("Lineas", backref="productos")
    porcentajes = relationship("PorcentajesProducto", uselist=False, back_populates="producto")

    def __repr__(self):
        return f"<Productos {self.nombre}>"
  
class PorcentajesProducto(db.Model):
    """
    This class represents the PorcentajesProducto table in the database.
    """
    __tablename__ = 'porcentajes_productos'
    id_producto = Column(Integer, ForeignKey('productos.producto_id'), primary_key=True)
    administracion = Column(Integer, nullable=False)
    imprevistos = Column(Integer, nullable=False)
    utilidad = Column(Integer, nullable=False)

    producto = relationship("Productos", back_populates="porcentajes")

    def __repr__(self):
        return f"<PorcentajesProducto {self.id_producto}>"
  
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
  
class Cotizacion(db.Model):
    __tablename__ = 'cotizacion'
    id_cotizacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_cotizacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cliente_cotizacion = db.Column(db.String(255), nullable=False)
    contacto_cotizacion = db.Column(db.String(255), nullable=False)
    proyecto_cotizacion = db.Column(db.String(255), nullable=False)
    vendedor_cotizacion = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    negociacion = db.Column(db.String(255), nullable=False)
    forma_de_pago_cotizacion = db.Column(db.String(255), nullable=True)
    validez_cotizacion = db.Column(db.String(255), nullable=True)
    descuento_cotizacion = db.Column(db.String(255), nullable=True)
    recibe_cotizacion = db.Column(db.String(255), nullable=True)
    numero_contacto_cotizacion = db.Column(db.String(255), nullable=True)
    direccion_cotizacion = db.Column(db.String(255), nullable=True)
    iva_seleccionado = db.Column(db.String(10), nullable=False)  # Nuevo campo para IVA

    vendedor = db.relationship('Users', backref='cotizaciones')

    def to_dict(self):
        return {
            'id_cotizacion': self.id_cotizacion,
            'fecha_cotizacion': self.fecha_cotizacion.isoformat(),
            'cliente_cotizacion': self.cliente_cotizacion,
            'contacto_cotizacion': self.contacto_cotizacion,
            'proyecto_cotizacion': self.proyecto_cotizacion,
            'vendedor_cotizacion': self.vendedor_cotizacion,
            'negociacion': self.negociacion,
            'forma_de_pago_cotizacion': self.forma_de_pago_cotizacion,
            'validez_cotizacion': self.validez_cotizacion,
            'descuento_cotizacion': self.descuento_cotizacion,
            'recibe_cotizacion': self.recibe_cotizacion,
            'numero_contacto_cotizacion': self.numero_contacto_cotizacion,
            'direccion_cotizacion': self.direccion_cotizacion,
            'iva_seleccionado': self.iva_seleccionado,
        }

class ProductoCotizado(db.Model):
    __tablename__ = 'producto_cotizado'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    linea_id = db.Column(db.Integer, db.ForeignKey('lineas.linea_id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=True)  # Mantener este campo
    producto_seleccionado_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=True)  # Nuevo campo
    alto = db.Column(db.Float)
    ancho = db.Column(db.Float)
    fondo = db.Column(db.Float)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.id_cotizacion'), nullable=False)
    cantidades = db.Column(db.String(255), nullable=False)  # Nuevo campo para almacenar cantidades

    linea = db.relationship("Lineas", backref="productos_cotizados")
    producto = db.relationship("Productos", foreign_keys=[producto_seleccionado_id], backref="productos_cotizados")
    cotizacion = db.relationship("Cotizacion", backref="productos_cotizados")

    def __repr__(self):
        return f"<ProductoCotizado {self.descripcion}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'linea_id': self.linea_id,
            'producto_id': self.producto_id,
            'producto_seleccionado_id': self.producto_seleccionado_id,
            'alto': self.alto,
            'ancho': self.ancho,
            'fondo': self.fondo,
            'cotizacion_id': self.cotizacion_id,
            'cantidades': self.cantidades,
        }

class ItemCotizado(db.Model):
    __tablename__ = 'items_cotizados'
    id = db.Column(db.Integer, primary_key=True)
    producto_cotizado_id = db.Column(db.Integer, db.ForeignKey('producto_cotizado.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    temporal = db.Column(db.Boolean, default=False, nullable=False)
    total_item = db.Column(db.Float, nullable=False)

    producto = db.relationship('ProductoCotizado', backref='items')
    item = db.relationship('Items', backref='cotizaciones')

    def to_dict(self):
        return {
            'id': self.id,
            'producto_cotizado_id': self.producto_cotizado_id,
            'item_id': self.item_id,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'temporal': self.temporal,
            'total_item': self.total_item,
        }

class ResumenDeCostos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    costo_directo = db.Column(db.Float, nullable=False)
    administracion = db.Column(db.Float, nullable=False)
    imprevistos = db.Column(db.Float, nullable=False)
    utilidad = db.Column(db.Float, nullable=False)
    oferta_antes_iva = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, nullable=False)
    valor_oferta = db.Column(db.Float, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto_cotizado.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'costo_directo': self.costo_directo,
            'administracion': self.administracion,
            'imprevistos': self.imprevistos,
            'utilidad': self.utilidad,
            'oferta_antes_iva': self.oferta_antes_iva,
            'iva': self.iva,
            'valor_oferta': self.valor_oferta,
            'producto_id': self.producto_id,
        }

    

def configure_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/software_innova'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

def test_db_connection(app):
    with app.app_context():
        with db.engine.connect() as connection:
            try:
                print("----------------------------------")
                print("Conexion a Db Exitosa")
                print("----------------------------------")
            except Exception as e:
                print("----------------------------------")
                print(f"Error al conectar a la base de datos: {str(e)}")
                print("----------------------------------")

