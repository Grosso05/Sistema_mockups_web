from flask import Flask, request, redirect, url_for, send_file, render_template
from flask_login import LoginManager,login_required
from calculate import get_white_presence
from set_logo import set_logo
import tempfile
import os
from models import configure_db, test_db_connection, Users, UsersRol, db

from flask_login import login_user
import secrets


FIXED_PDF_FILE_PATH = "./Catalogo_white.pdf"
ANOTHER_PDF_FILE_PATH = "./Catalogo_black.pdf"

app = Flask(__name__)

# Genera una clave secreta aleatoria de 24 bytes (192 bits)
app.config['SECRET_KEY'] = secrets.token_hex(24)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Vista de inicio de sesión

configure_db(app)  # Configura la base de datos


# Comprueba la conexión a la base de datos
test_db_connection(app)


@login_manager.user_loader
def load_user(user_id):
    # Retorna el usuario correspondiente al ID de usuario
    return db.session.get(Users, int(user_id))




@app.route('/')
def index():
    return render_template('index.html')

#ruta para el dashboard de administrador
@app.route('/admin')
def admin():
    return render_template('dashboard_admin.html')

@app.route('/generar_catalogo')
def generar_catalogo():
    return render_template('generar_catalogoregistrado.html')

#ruta para el dashboard de usuario
@app.route('/user')
def user():
    return render_template('dashboard_user.html')

# Ruta para mostrar la lista de usuarios
@app.route('/listar_usuarios', methods=['DELETE','GET', 'POST'])
def listar_usuarios():
    usuarios = Users.query.all()  # Obtener todos los usuarios de la base de datos
    return render_template('listar_usuarios.html', usuarios=usuarios)  # Renderizar la plantilla HTML con la lista de usuarios

#ruta del formulario para crear usuarios
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_last_name = request.form['user_last_name']
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        user_rol = request.form['user_rol']  # Asegúrate de tener un campo en el formulario para el rol del usuario

        # Crear una instancia del modelo Users con los datos del formulario
        new_user = Users(user_name=user_name, user_last_name=user_last_name, user_email=user_email, user_password=user_password, user_rol=user_rol)

        # Agregar la nueva instancia a la sesión y hacer commit para guardarla en la base de datos
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('listar_usuarios'))  # Redirigir a la página principal después de registrar al usuario

    return render_template('crear_usuario.html')

#ruta para editar el formulario de usuarios

@app.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    user = Users.query.get(user_id)
    if request.method == 'POST':
        user.user_name = request.form['user_name']
        user.user_last_name = request.form['user_last_name']
        user.user_email = request.form['user_email']
        user.user_password = request.form['user_password']
        user.user_rol = request.form['user_rol']
        db.session.commit()
        return redirect(url_for('listar_usuarios'))
    return render_template('editar_usuario.html', user=user)


#ruta para eliminar usuarios
@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('listar_usuarios'))

#ruta para el inicio de sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')

        # Verifica las credenciales del usuario
        user = Users.query.filter_by(user_email=user_email, user_password=user_password).first()

        if user:
            login_user(user)  # Inicia sesión
            if user.user_rol == 1:
                return redirect(url_for('admin'))  # Redirige al panel de administrador si el rol es 1
            elif user.user_rol == 2:
                return redirect(url_for('user'))  # Redirige al panel de usuario si el rol es 2
            else:
                return redirect(url_for('index'))  # Redirige a otra página si el rol no es 1 ni 2
        else:
            # Credenciales inválidas, muestra un mensaje de error
            return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Cierra la sesión
    return redirect(url_for('index'))



@app.route('/add_watermark', methods=['POST'])
def add_watermark():
    try:
        if 'image_file' not in request.files:
            return redirect(url_for('index'))

        image_file = request.files['image_file']

        if image_file.filename == '':
            return redirect(url_for('index'))

        image_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image_file.save(image_temp_file.name)

        white_percentage = get_white_presence(image_temp_file.name)

        if white_percentage >= 10:  
            pdf_path = ANOTHER_PDF_FILE_PATH
        else:
            pdf_path = FIXED_PDF_FILE_PATH

        watermark_positions = [
            # Coordinates for page 1
            [{'x': 5.41, 'y': 09.48, 'width': 120, 'height': 100, 'rotation': 359, 'opacity': 0.8}],
            # Coordinates for page 2
            [{'x': 6.48, 'y': 11.53, 'width': 40, 'height': 20, 'rotation': -5, 'opacity': 0.7}],
            # Coordinates for page 3
            [{'x': 8.56, 'y': 10.80, 'width': 30, 'height': 25, 'rotation': 0, 'opacity': 0.7}]
        ]

        output_buffer = set_logo(image_temp_file, pdf_path, watermark_positions)

        image_temp_file.close()
        os.remove(image_temp_file.name)

        return send_file(output_buffer, as_attachment=True, download_name="modified_pdf.pdf")

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
