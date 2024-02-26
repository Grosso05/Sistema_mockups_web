from flask import Blueprint, render_template, request, redirect, url_for


routes_blueprint = Blueprint('routes', __name__)

#ruta principal (index), ruta para generar catalogo del lado del cliente
@routes_blueprint.route('/')
def index():
    mensaje = request.args.get('mensaje', '')  # Obtener el mensaje de la URL
    return render_template('index.html', mensaje=mensaje)

#ruta para el dashboard de administrador
@routes_blueprint.route('/routes.admin')
def admin():
    return render_template('/dashboard_admin.html')


#ruta para el dashboard de usuario
@routes_blueprint.route('/routes.user')
def user():
    return render_template('dashboard_user.html')

#Ruta para generar catalogo del lado del admin
@routes_blueprint.route('/routes.generar_catalogo')
def generar_catalogo():
    return render_template('generar_catalogoregistrado.html')

#ruta para generar catalogo del lado del usuario
@routes_blueprint.route('/routes.generar_catalogouser')
def generar_catalogouser():
    return render_template('generarcatalogouserregistrado.html')

