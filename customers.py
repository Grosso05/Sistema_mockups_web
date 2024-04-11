from flask import Blueprint, jsonify, render_template, request, redirect, url_for,flash,session
from flask_login import login_required, login_user,current_user
from models import Customers, Users, db  # Importa las clases de modelos y la configuración de la base de datos
import bcrypt
from utils import roles_required
customers_blueprint = Blueprint('customers', __name__)

@customers_blueprint.route('/customers.listar_clientes', methods=['DELETE','GET', 'POST'])
@login_required
@roles_required(1)
def listar_clientes():
    clientes = Customers.query.all()  # Obtener todos los usuarios de la base de datos
    return render_template('listar_clientes.html', clientes=clientes)  # Renderizar la plantilla HTML con la lista de usuarios

#ruta para listar clientes desde el lado de vendedores

@customers_blueprint.route('/customers.listar_clientes_v', methods=['DELETE','GET', 'POST'])
@login_required
def listar_clientes_v():
    clientes = Customers.query.outerjoin(Users, Customers.user == Users.user_id).all()
    return render_template('listar_clientes_usuarios.html', clientes=clientes)  # Renderizar la plantilla HTML con la lista de usuarios


# Ruta para eliminar clientes
@customers_blueprint.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
@login_required
@roles_required(1)
def delete_customer(customer_id):
    customer = Customers.query.get(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Cliente eliminado exitosamente'}), 200


# Ruta para cambiar el estado del cliente
@customers_blueprint.route('/contactar_cliente/<int:customer_id>', methods=['POST'])
@login_required
def contactar_cliente(customer_id):
    cliente = Customers.query.get(customer_id)
    if cliente:
        cliente.user = current_user.user_id
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404