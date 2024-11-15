from flask import Blueprint, render_template, request, redirect, url_for,flash,session
from flask_login import current_user, login_required, login_user
from models import Lineas, Productos, Users, UsersRol, db  # Importa las clases de modelos y la configuración de la base de datos
import bcrypt
from utils import roles_required
users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/users.listar_usuarios', methods=['GET'])
@login_required
@roles_required(1)
def listar_usuarios():
    # Obtener filtros desde la solicitud GET
    filter_name = request.args.get('filterName', '')
    filter_last_name = request.args.get('filterLastName', '')
    filter_email = request.args.get('filterEmail', '')
    filter_role = request.args.get('filterRole', '')
    filter_id_min = request.args.get('filterIdMin', '')
    filter_id_max = request.args.get('filterIdMax', '')

    # Construir la consulta con filtros
    usuarios = Users.query.join(UsersRol).add_columns(
        Users.user_id,
        Users.user_name,
        Users.user_last_name,
        Users.user_email,
        UsersRol.descripcion
    )
    
    if filter_name:
        usuarios = usuarios.filter(Users.user_name.ilike(f"%{filter_name}%"))
    if filter_last_name:
        usuarios = usuarios.filter(Users.user_last_name.ilike(f"%{filter_last_name}%"))
    if filter_email:
        usuarios = usuarios.filter(Users.user_email.ilike(f"%{filter_email}%"))
    if filter_role:
        usuarios = usuarios.filter(UsersRol.descripcion.ilike(f"%{filter_role}%"))
    if filter_id_min:
        usuarios = usuarios.filter(Users.user_id >= int(filter_id_min))
    if filter_id_max:
        usuarios = usuarios.filter(Users.user_id <= int(filter_id_max))

    usuarios = usuarios.all()

    # Obtener todos los roles para el select
    roles = UsersRol.query.all()
    
    return render_template('listar_usuarios.html', usuarios=usuarios, roles=roles, user_rol=current_user.user_rol)




#ruta del formulario para crear usuarios
@users_blueprint.route('/crear_usuario', methods=['GET', 'POST'])

def crear_usuario():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_last_name = request.form['user_last_name']
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        user_rol = request.form['user_rol']  # Asegúrate de tener un campo en el formulario para el rol del usuario

        # Encriptar la contraseña antes de guardarla en la base de datos
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
    

        # Crear una instancia del modelo Users con los datos del formulario
        new_user = Users(user_name=user_name, user_last_name=user_last_name, user_email=user_email, user_password=hashed_password, user_rol=user_rol)

        # Agregar la nueva instancia a la sesión y hacer commit para guardarla en la base de datos
        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado correctamente', 'success')

        return redirect(url_for('users.listar_usuarios'))  # Redirigir a la página principal después de registrar al usuario

    return render_template('crear_usuario.html',user_rol=current_user.user_rol)

#ruta para editar el formulario de usuarios

@users_blueprint.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required(1)
def editar_usuario(user_id):
    user = Users.query.get(user_id)
    
    # Obtener todos los roles
    roles = UsersRol.query.all()
    # 
    if request.method == 'POST':
        user.user_name = request.form['user_name']
        user.user_last_name = request.form['user_last_name']
        user.user_email = request.form['user_email']
        
        # Verificar si se ha proporcionado una nueva contraseña
        if 'user_password' in request.form:
            new_password = request.form['user_password']
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.user_password = hashed_password
        
        user.user_rol = request.form['user_rol']
        db.session.commit()
        return redirect(url_for('users.listar_usuarios'))
    
    return render_template('editar_usuario.html', user=user, roles=roles,user_rol=current_user.user_rol)



#ruta para eliminar usuarios
@users_blueprint.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
@roles_required(1)
def delete_user(user_id):
    user = Users.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users.listar_usuarios'))



#ruta para el inicio de sesion
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')

        # Busca al usuario por su correo electrónico
        user = Users.query.filter_by(user_email=user_email).first()

        if user and bcrypt.checkpw(user_password.encode('utf-8'), user.user_password.encode('utf-8')):
            login_user(user)  # Inicia sesión
            session['username'] = user.user_name
            session['userlastname'] = user.user_last_name
            session['usermail'] = user.user_email
            session['userlink'] = user.user_link
            session['user_id'] = user.user_id  # Guardar el ID del usuario en la sesión

            # Redirección según el rol del usuario
            if user.user_rol == 1:
                return redirect(url_for('routes.admin'))  # Redirige al panel de administrador si el rol es 1
            elif user.user_rol in [2, 3]:  # Permite acceso para roles 2 y 3
                return redirect(url_for('routes.user'))  # Redirige al panel de usuario si el rol es 2 o 3
        else:
            # Credenciales inválidas, muestra un mensaje de error
            return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')


#Ruta para la salida del usuario
@users_blueprint.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('routes.index'))

@users_blueprint.route('/generando_catalogod')

def Generandod():
    return render_template('generando_catalogod.html')

@users_blueprint.route('/generando_catalogoc')

def Generandoc():
    return render_template('generando_catalogoc.html')

@users_blueprint.route('/generando_catalogo_index')

def Generando_catalogo_index():
    return render_template('generando_catalogo_index.html')


