from venv import logger
from flask import Blueprint, Response, json, jsonify, make_response, render_template, request, redirect, url_for,flash,session
from flask_login import login_required, login_user,current_user
from sqlalchemy import update
from models import Customers, Users, db  # Importa las clases de modelos y la configuración de la base de datos
import bcrypt
from builtins import bool
from utils import roles_required
customers_blueprint = Blueprint('customers', __name__)
import logging
from sqlalchemy.orm.exc import NoResultFound

# Define la función bool_func aquí
def bool_func(value):
    return "Contactado" if value else "Sin Contactar"

@customers_blueprint.route('/customers.listar_clientes', methods=['GET'])
@login_required
@roles_required(1)
def listar_clientes():
    try:
        clientes = Customers.query.all()  # Obtener todos los clientes de la base de datos
        
        # Impresión de depuración para verificar el valor de cliente.contactado
        for cliente in clientes:
            print(f"Cliente ID: {cliente.customer_id}, Contactado: {cliente.contactado}")

        # Verificar la consulta SQL generada por SQLAlchemy
        consulta_sql = Customers.query.statement
        print("Consulta SQL generada por SQLAlchemy:")
        print(consulta_sql)

        return render_template('listar_clientes.html', clientes=clientes)

    except Exception as e:
        # Manejo de errores
        print(f"Error: {e}")
        return render_template('error.html', error=e)

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



@customers_blueprint.route('/cambiar_estado/<int:customer_id>', methods=['POST'])
def cambiar_estado_cliente(customer_id):
    try:
        print(f"Cambiar estado cliente: {customer_id}")  # Depuración

        # Construye la sentencia UPDATE usando SQLAlchemy
        update_stmt = update(Customers).where(Customers.customer_id == customer_id).values(contactado=True)

        # Ejecuta la sentencia UPDATE y guarda los cambios
        db.session.execute(update_stmt)
        db.session.commit()

        logger.info(f"Estado del cliente {customer_id} actualizado correctamente a 'Contactado'.")

        response = make_response(jsonify({'success': True}), 200)
        return response

    except NoResultFound as e:
        # Cliente no encontrado
        logger.error(f"Cliente no encontrado: {e}")
        response = make_response(jsonify({'error': 'Cliente no encontrado'}), 404)
        return response

    except Exception as e:
        # Otros errores
        db.session.rollback()  # Rollback cambios en caso de error
        logger.error(f"Error al actualizar el estado del cliente: {e}")
        response = make_response(jsonify({'error': str(e)}), 500)
        return response

