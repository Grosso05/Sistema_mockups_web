from reportlab.lib.pagesizes import letter
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import os
from random import choice
import smtplib
import tempfile
from reportlab.pdfgen import canvas
from flask import Blueprint, flash, redirect, request, send_file, url_for,session
from flask_login import login_required
from PyPDF2 import PdfReader, PdfWriter
from calculate import get_white_presence
from models import Customers, Users, db
from set_logo import set_logo
from reportlab.lib import colors

logos_blueprint = Blueprint('logos', __name__)

FIXED_PDF_FILE_PATH = "./Catalogo_white.pdf"
ANOTHER_PDF_FILE_PATH = "./Catalogo_black.pdf"

#funcion para ubicar el logo
@logos_blueprint.route('/add_watermark', methods=['POST'])
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
            [{'x': 5.41, 'y': 09.48, 'width': 0, 'height': 0, 'rotation': 359, 'opacity': 0.8}],
            # Coordinates for page 2 VALLA NUMERO
            [{'x': 8.13, 'y': 5.80, 'width': 1.91, 'height': 0.61, 'rotation': 352.88, 'opacity': 0.7}],
            # Coordinates for page 3 IMPRESORA - CAMISETA 
            [
                {'x': 9.90, 'y': 18.32, 'width': 1.88, 'height':0.64 , 'rotation': 0, 'opacity': 0.7},
                {'x': 8.99, 'y': 5.29, 'width': 0.86, 'height': 0.43, 'rotation': 0, 'opacity': 0.7}
             ],

            #PAGE 4 - FOLLETO
            [{'x': 5.91, 'y': 2.40, 'width': 2.02, 'height': 1.37, 'rotation': 22.42, 'opacity': 0.7}],
            #PAGE 5 CAMISETA
            [{'x': 8.64, 'y': 5.53, 'width': 2.85, 'height': 1.42, 'rotation': 0, 'opacity': 0.7}],
            #PAGE 6 CAMISETA - circulo
            [
                {'x': 6.05, 'y': 14.57, 'width': 2.15, 'height': 1.78, 'rotation': 326.56, 'opacity': 0.8},
                {'x': 8.99, 'y': 6.53, 'width': 2.67, 'height': 1.33, 'rotation': 0, 'opacity': 0.8}
             
             ],
            #pagina 7 valla
            [{'x': 9.9, 'y': 5.9, 'width': 2.2, 'height': 2.11, 'rotation': 19.97, 'opacity': 0.8}],
            #pagina 8 cerramientos

            [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
            #ak
                        [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],
                         [
                {'x': 11.14, 'y': 14.48, 'width': 2.70, 'height': 1.04, 'rotation': 0, 'opacity': 0.6},
                {'x': 4.38, 'y': 2.75, 'width': 1.40, 'height': 0.58, 'rotation': 2.91, 'opacity': 0.6}

             ],

            #pagina9
            [
                {'x': 2.62, 'y': 14.61, 'width': 2.37, 'height': 0.88, 'rotation': 0, 'opacity': 0.7},
                {'x': 2.61, 'y': 3.22, 'width': 3.15, 'height': 1.38, 'rotation': 0, 'opacity': 0.7}

             ]
        ]

        pdf_final_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        output_buffer = set_logo(image_temp_file, pdf_path, watermark_positions)  # Genera el PDF final
        with open(pdf_final_path, 'wb') as f:
            f.write(output_buffer.getvalue())

        image_temp_file.close()
        os.remove(image_temp_file.name)


# Obtener una lista de usuarios con rol 2
        eligible_users = Users.query.filter_by(user_rol=2).all()

        # Seleccionar aleatoriamente un usuario de la lista
        selected_user = choice(eligible_users)

        # Obtener el correo electrónico del formulario
        customer_email = request.form['customer_email']

        # Obtener la fecha actual
        current_date = datetime.datetime.now()

        # Crear una nueva instancia de Customers
        new_customer = Customers(
        customer_email=customer_email,
        customer_date=current_date,
        user=selected_user.user_id  # Asignar el usuario seleccionado al cliente
)

        db.session.add(new_customer)
        db.session.commit()

         # Llamar a la función enviar_correo para enviar el PDF por correo
        enviar_correo(pdf_final_path, request.form['customer_email'])

        return redirect(url_for('routes.index'))
    except Exception as e:
        return f"Error: {str(e)}"


#ruta para el envio automatico de correos

def enviar_correo(pdf_final_path, customer_email):
    # Configurar los detalles del correo electrónico
    sender_email = 'brayangrosso05@gmail.com'  
    receiver_email = customer_email
    subject = 'Catalogo Innova'
    body = MIMEText('Reciba un Cordial saludo por parte de Innova Publicidad Visual. Adjunto encontrará nuestro catalogo, esperamos que sea de su agrado.', 'plain', 'utf-8')

    # Crear el mensaje
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(body)  

    # Adjuntar el archivo PDF al mensaje
    with open(pdf_final_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename=Catalogo_Innova.pdf')
    message.attach(part)

    # Enviar el correo electrónico a través de un servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'brayangrosso05@gmail.com'  # Reemplazar con tu dirección de correo electrónico
    smtp_password = 'cubk rhdg yspy dvzz'  # Reemplazar con tu contraseña de correo electrónico

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)


    flash('Catalogo enviado correctamente', 'success')
    return redirect(url_for('routes.index'))

#ruta para generar catalogo del lado de los usuarios y admin

@logos_blueprint.route('/agregar_logo_user', methods=['POST'])
@login_required
def agregar_logo_user():
    
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
            #pagina1 - vacia
            [{'x': 8.65, 'y': 5.78, 'width': 0, 'height': 0, 'rotation': 353, 'opacity': 0.7}],
            #pagina2 - vacia
            [{'x': 8.65, 'y': 5.78, 'width': 0, 'height': 0, 'rotation': 353, 'opacity': 0.7}],
            #pagina 3 valla
            [{'x': 8.65, 'y': 5.78, 'width': 0.90, 'height': 0.54, 'rotation': 353, 'opacity': 0.7}],
            # Coordinates for page 4 camiseta 
            [{'x': 9.24, 'y': 5.36, 'width': 0.54, 'height': 0.28, 'rotation': 0, 'opacity': 0.7}],
            #PAGE 5 - FOLLETO
            [{'x': 6.19, 'y': 2.68, 'width': 1.66, 'height': 1.31, 'rotation': 24.25, 'opacity': 0.7}],
            #PAGE 6 CAMISETA
            [{'x': 8.64, 'y': 5.53, 'width': 2.85, 'height': 1.42, 'rotation': 0, 'opacity': 0.7}],
            #pagina 7

            [     #camiseta
                {'x': 6.69, 'y': 14.73, 'width': 1.66, 'height': 1.31, 'rotation': 335.225, 'opacity': 0.7},
                #circulo
                {'x': 9.18, 'y': 6.64, 'width': 2.18, 'height': 1.13, 'rotation': 0, 'opacity': 0.7}

             ],
            #pagina 8 valla
            
            [{'x': 9.81, 'y': 6.11, 'width': 2.28, 'height': 1.61, 'rotation': 21.87, 'opacity': 0.7}],

            #pagina 9

            [   #fachada
                {'x': 11.86, 'y': 14.64, 'width': 1.48, 'height': 0.76, 'rotation': 2, 'opacity': 0.6},
                #valla
                {'x': 4.56, 'y': 2.75, 'width': 1.00, 'height': 0.53, 'rotation': 3, 'opacity': 0.7}

             ],
            #pagina 10

            [     #valla1
                {'x': 3.07, 'y': 14.6, 'width': 1.64, 'height': 0.84, 'rotation': 359, 'opacity': 0.6},
                #valla 2
                {'x': 3.04, 'y': 3.23, 'width': 2.34, 'height': 1.25, 'rotation': 358.67, 'opacity': 0.6}

             ],
             #pagina 11

            [  #valla 1
                {'x': 11.09, 'y': 19.30, 'width': 1.00, 'height': 0.49, 'rotation': 354, 'opacity': 0.7},
                #valla 2
                {'x': 12.78, 'y': 7.30, 'width': 1.48, 'height': 0.76, 'rotation': 0, 'opacity': 0.7}

             ],
            #pagina 12
            [     #fachada1
                {'x': 8.01, 'y': 18.43, 'width': 1.55, 'height': 0.96, 'rotation': 351.28, 'opacity': 0.6},
                #acrilico
                {'x': 6.33, 'y': 5.92, 'width': 4.73, 'height': 3.17, 'rotation': 13.415, 'opacity': 0.7}

             ],
             #pagina 13 vacia
               [{'x': 11.14, 'y': 14.48, 'width': 0, 'height': 0, 'rotation': 0, 'opacity': 0.6}],

            #pagina 14 
            [   #vinilos1
                {'x': 7.98, 'y': 18.34, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                {'x': 9.61, 'y': 18.37, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                {'x': 11.08, 'y': 18.37, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                {'x': 12.76, 'y': 18.39, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                {'x': 14.65, 'y': 18.41, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                #vinilos2
                {'x': 4.61, 'y': 5.26, 'width': 0.53, 'height': 0.27, 'rotation': 0, 'opacity': 0.6},
                {'x': 6.50, 'y': 5.24, 'width': 0.64, 'height': 0.32, 'rotation': 0, 'opacity': 0.6},
                {'x': 9.21, 'y': 5.09, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 11.52, 'y': 5.09, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6}
             ],
             #pagina 15 
            [  #tropezon
                {'x': 10.88, 'y': 19.68, 'width': 1.28, 'height': 0.65, 'rotation': 0, 'opacity': 0.7},
                #aviso de pared
                {'x': 9.10, 'y': 6.86, 'width': 1.57, 'height': 0.80, 'rotation': 0, 'opacity': 0.6}
                ],
            #pagina 16
            [
                #decoracion pintura 
                {'x': 10.65, 'y': 17.63, 'width': 2.25, 'height': 1.23, 'rotation': 2.94, 'opacity': 0.7},
                #stand
                {'x': 7.21, 'y': 8.92, 'width': 1.55, 'height': 0.98, 'rotation': 10.67, 'opacity': 0.6}
             ],
             #pagina 17
             [ 
                 #modulo en lamina
                {'x': 11.43, 'y': 17.32, 'width': 1.85, 'height': 1.06, 'rotation': 5.43, 'opacity': 0.6},
                #modulo plano1
                {'x': 2.85, 'y': 7.27, 'width': 0.93, 'height': 0.48, 'rotation': 0.50, 'opacity': 0.6},
                #modulo plano2
                {'x': 13.74, 'y': 6.35, 'width': 1.19, 'height': 0.67, 'rotation': 4.13, 'opacity': 0.6}

             ],
             #pagina 18

            [   #modulo bastidor 1
                {'x': 8.97, 'y': 12.87, 'width': 1.33, 'height': 0.70, 'rotation': 1.37, 'opacity': 0.6},
                #modulo 2
                {'x': 11.21, 'y': 12.67, 'width': 1.20, 'height': 0.63, 'rotation': 0.96, 'opacity': 0.6}
             ],
            #pagina 19 - vacia
            [{'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}],

            #pagina 20 - decoracion vehicular 

            [{'x': 6.06, 'y': 17.22, 'width': 2.99, 'height': 1.52, 'rotation': 0, 'opacity': 0.7}],
            
            #pagina 21 decoracion vehicular
            
            [{'x': 9.54, 'y': 13.80, 'width': 3.35, 'height': 1.71, 'rotation': 2, 'opacity': 0.5}],

            #pagina 22 
            [
                #bandera metalica
                {'x': 10.42, 'y': 15.86, 'width': 2.25, 'height': 1.39, 'rotation': 9.08, 'opacity': 0.6},
                #tipo gota
                {'x': 3.75, 'y': 8.95, 'width': 1.48, 'height': 0.75, 'rotation': 0, 'opacity': 0.6}
            ],
            #pagina 23 - bandera de escritorio

            [
                {'x': 10.26, 'y': 17.87, 'width': 1.54, 'height': 0.78, 'rotation': 0, 'opacity': 0.6},

                {'x': 9.18, 'y': 7.38, 'width': 1.17, 'height': 0.60, 'rotation': 0, 'opacity': 0.5},
                {'x': 13.28, 'y': 6.99, 'width': 1.16, 'height': 0.59, 'rotation': 0, 'opacity': 0.5}  
            ],
               #pagina 24 
            [
                {'x': 8.52, 'y': 6.74, 'width': 1.44, 'height': 0.81, 'rotation': 4.30, 'opacity': 0.5}

             ],
               #pagina 25

            [ 
                {'x': 10.97, 'y': 16.86, 'width': 1.66, 'height': 0.85, 'rotation': 0, 'opacity': 0.5},
                {'x': 11.31, 'y': 4.27, 'width': 1.39, 'height': 0.75, 'rotation': 357.4, 'opacity': 0.6}

             ],
               #pagina 26
            [
                {'x': 6.98, 'y': 14.40, 'width': 1.46, 'height': 0.74, 'rotation': 0, 'opacity': 0.5},
                {'x': 4.42, 'y': 4.43, 'width': 1.47, 'height': 0.84, 'rotation': 4.87, 'opacity': 0.6}

             ],
             #pagina 27
            
            [
                {'x': 10.87, 'y': 18.53, 'width': 1.18, 'height': 0.60, 'rotation': 0, 'opacity': 0.5},
                {'x': 7.47, 'y': 5.61, 'width': 1.10, 'height': 0.56, 'rotation': 0, 'opacity': 0.6}

             ],

             #pagina 28

            [     #portapendones1
                {'x': 8.5, 'y': 17.26, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                #portapendones2
                {'x': 11.20, 'y': 13.82, 'width': 0.53, 'height': 0.85, 'rotation': 90, 'opacity': 0.6},

                #backing
                {'x': 6.68, 'y': 8.55, 'width': 0.80, 'height': 0.41, 'rotation': 0, 'opacity': 0.6},
                {'x': 8.5, 'y': 7.69, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 7.48, 'y': 6.70, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 7.15, 'y': 5.34, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 10.51, 'y': 8.31, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 10.13, 'y': 7.16, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 9.19, 'y': 5.89, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 10.97, 'y': 5.14, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6}
             ],

             #pagina 29
            [     
                {'x': 10.94, 'y': 19.56, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 8.04, 'y': 8.17, 'width': 0.53, 'height': 0.84, 'rotation': 90, 'opacity': 0.6},
                {'x': 8.80, 'y': 8.34, 'width': 0.51, 'height': 0.81, 'rotation': 90, 'opacity': 0.6}

             ],
             #pagina 30
            [
                {'x': 9.97, 'y': 17.69, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.5},
                {'x': 6.37, 'y': 6.60, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 9.71, 'y': 6.60, 'width': 0.93, 'height': 0.47, 'rotation': 0, 'opacity': 0.6},
                {'x': 12.02, 'y': 2.90, 'width': 1.29, 'height': 0.66, 'rotation': 0, 'opacity': 0.5}

             ],
             #pagina 31
             [
                {'x': 8.02, 'y': 8.43, 'width': 1.17, 'height': 0.59, 'rotation': 0, 'opacity': 0.5}

             ],
            #pagina 32 - vacia
            [
               {'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}
             ],
            #pagina 33
            [
                {'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}
             ],
             #pagina 34
            [
                {'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}
             ],
             #pagina 35
            [
                {'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}
             ],
             #pagina 36
            [
                {'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}
             ],
             #pagina 37
            [{'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}],
            #pagina 38
            [{'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}],

            #pagina39
            [{'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}],
            #pagina40
            [{'x': 4.38, 'y': 2.75, 'width': 0, 'height': 0, 'rotation': 2.91, 'opacity': 0.6}]
        ]

        # Después de llamar a agregar_fecha_hora_a_pdf, guardar el resultado en un archivo temporal
        output_buffer_fecha_hora = agregar_fecha_hora_usuario_a_pdf(pdf_path)
        temp_file_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(output_buffer_fecha_hora.getbuffer())

        # Luego, llamar a set_logo utilizando el archivo temporal como entrada
        output_buffer_final = set_logo(image_temp_file, temp_file_path, watermark_positions)

        # Finalmente, enviar el archivo final como respuesta
        return send_file(output_buffer_final, as_attachment=True, download_name="catalogo_innova.pdf")

    except Exception as e:
        return f"Error: {str(e)}"
    
#ruta para agregar el sello al pdf

def agregar_fecha_hora_usuario_a_pdf(pdf_path):

    output_buffer = BytesIO()
    packet = BytesIO()

    # create a new PDF with Reportlab   
    can = canvas.Canvas(packet, pagesize=letter)
    
    username = session['username']
    user_last_name = session['userlastname']
    user_email=session['usermail']
    usuario_text = f"Generado por: {username} {user_last_name}"  # Agregar tanto el nombre de usuario como el apellido
    fecha_hora_text = f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    email_text=f"Correo: {user_email}"
    can.setFillColor(colors.black)  # Set text color to white
    can.setFont("Helvetica", 8)  # Set font size
    
    can.drawString(245, 70, usuario_text)
    can.drawString(250, 60, fecha_hora_text)
    can.drawString(255, 50, email_text)
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(pdf_path)
    output = PdfWriter()

    for page_number in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[page_number]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    output.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer