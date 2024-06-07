from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, login_user, current_user
from models import Categoria, Items, ItemsPorProducto, Lineas, Productos, Users, ItemProveedores
from utils import roles_required


routes_blueprint = Blueprint('routes', __name__)

#ruta principal (index), ruta para generar catalogo del lado del cliente
@routes_blueprint.route('/')
def index():
    mensaje = request.args.get('mensaje', '')  # Obtener el mensaje de la URL
    return render_template('index.html', mensaje=mensaje)


#ruta para el dashboard de administrador
@routes_blueprint.route('/routes.admin')
@login_required
@roles_required(1)
def admin():
    if current_user.user_rol != 1:  # Verifica si el rol del usuario es igual a 1 (ID del rol de administrador)
        return redirect(url_for('users.login'))  # Redirige a la página de inicio de sesión u otra página según lo que prefieras
    return render_template('/dashboard_admin.html')


#ruta para el dashboard de usuario
@routes_blueprint.route('/routes.user')
@login_required
@roles_required(2)
def user():
    if current_user.user_rol !=2:
        return render_template(url_for('users.login'))
    return render_template('dashboard_user.html')

#Ruta para generar catalogo del lado del admin
@routes_blueprint.route('/routes.generar_catalogo')
@login_required
@roles_required(1)
def generar_catalogo():
    return render_template('generar_catalogoregistrado.html')

#ruta para generar catalogo del lado del usuario
@routes_blueprint.route('/routes.generar_catalogouser')
@login_required
@roles_required(2)
def generar_catalogouser():
    return render_template('generarcatalogouserregistrado.html')

@routes_blueprint.route('/generar_cotizacion')
def generar_cotizacion():
    lineas = Lineas.query.all()
    productos = Productos.query.all()
    return render_template('generar_cotizacion.html', lineas=lineas, productos=productos)

@routes_blueprint.route('/productos_por_linea/<int:linea_id>')
def productos_por_linea(linea_id):
    productos = Productos.query.filter_by(linea_idFK=linea_id).all()
    productos_json = []
    for producto in productos:
        items = Items.query.join(ItemsPorProducto, ItemsPorProducto.item_idFK == Items.item_id)\
                            .filter(ItemsPorProducto.producto_idFK == producto.producto_id)\
                            .all()
        items_json = [{'id': item.item_id, 'descripcion': item.nombre} for item in items]
        productos_json.append({
            'id': producto.producto_id,
            'nombre': producto.nombre,
            'items': items_json
        })
    return jsonify(productos_json)

@routes_blueprint.route('/items_por_producto/<int:producto_id>')
def items_por_producto(producto_id):
    items_por_producto = ItemsPorProducto.query.filter_by(producto_idFK=producto_id).all()
    items = []
    for item_por_producto in items_por_producto:
        item = Items.query.get(item_por_producto.item_idFK)
        categoria = Categoria.query.get(item.categoria_id)  # Obtener el nombre de la categoría
        if item and categoria:
            items.append({
                'id': item.item_id,
                'descripcion': item.nombre,
                'categoria_id': item.categoria_id,
                'categoria_nombre': categoria.CATEGORIA_NOMBRE,
                'unidad': item.unidad,
                'tipo': item.tipo
            })
    return jsonify(items)







