from email.mime.image import MIMEImage
from reportlab.lib.pagesizes import letter
import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import os
from random import choice
import smtplib
from smtplib import SMTP
import tempfile
from reportlab.pdfgen import canvas
from flask import Blueprint, flash, redirect, request, send_file, url_for,session
from flask_login import login_required
from PyPDF2 import PdfReader, PdfWriter
from calculate import get_white_presence
from models import Customers, Users, db
from routes import user
from set_logo import set_logo
from reportlab.lib import colors
import PyPDF2
import tempfile
from io import BytesIO
from flask import send_file
logos_blueprint = Blueprint('logos', __name__)
import fitz  # PyMuPDF
from flask import send_file
import io

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

        pdf_final_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        output_buffer = set_logo(image_temp_file, pdf_path, watermark_positions)  # Genera el PDF final
        print("pdf generado")
        with open(pdf_final_path, 'wb') as f:
            f.write(output_buffer.getvalue())

        # Comprimir el PDF
        pdf_final_path_comprimido = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        comprimir_pdf(pdf_final_path, pdf_final_path_comprimido)
        print("pdf comprimido")
        

        image_temp_file.close()
        os.remove(image_temp_file.name)


        # Obtener solo los IDs de los usuarios con rol 2
        eligible_user_ids = [user.user_id for user in Users.query.filter_by(user_rol=2).all()]

        # Seleccionar aleatoriamente un ID de usuario
        selected_user_id = choice(eligible_user_ids)

        # Obtener el objeto de usuario completo utilizando el ID seleccionado
        selected_user = Users.query.get(selected_user_id)

        print(f"usuario elegido {selected_user}")

        # Obtener el correo electrónico del formulario
        customer_email = request.form['customer_email']
        print(f"correo del cliente: {customer_email}")

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

        print("cliente creado")
       # Acceder al correo electrónico del usuario seleccionado
        selected_user_email = selected_user.user_email
        print("Correo del usuario seleccionadoo:", selected_user_email)

        selected_user_name = selected_user.user_name
        selected_user_last_name = selected_user.user_last_name
        # Llamar a la función enviar_correo para enviar el PDF por correo
        enviar_correo(pdf_final_path_comprimido, request.form['customer_email'], selected_user_email,selected_user_name,selected_user_last_name)
        print("Correo del cliente obtenido:", request.form['customer_email'])
        print("Correo del usuario seleccionado:", selected_user_email)

        # Llamar a la función enviar_correo para enviar el PDF por correo
        print("Antes de llamar a enviar_correo")
        enviar_correo(pdf_final_path_comprimido, request.form['customer_email'], selected_user.email)
        print("Después de llamar a enviar_correo")
        print("Correo del cliente:", request.form['customer_email'])
        print("Correo del usuario seleccionado:", selected_user.email)


        return redirect(url_for('routes.index'))
    except Exception as e:
        return f"Error: {str(e)}"
    
def comprimir_pdf(pdf_path, output_path):
    pdf_document = fitz.open(pdf_path)  # Abrir el documento PDF
    pdf_document.save(output_path, garbage=4, deflate=True)  # Guardar el documento con compresión
    pdf_document.close()  # Cerrar el documento


#ruta para el envio automatico de correos

def enviar_correo(pdf_final_path, customer_email, user_email,user_name,user_last_name):

    print("Iniciado enviar_correo")
    # Configurar los detalles del correo electrónico
    sender_email = 'info@innovapublicidad.com.co'
    receiver_emails = [customer_email, user_email]
    subject = 'Catálogo Innova'
    body_paragraphs = [
        "Reciba un cordial saludo por parte de Innova Publicidad Visual S.A.S.\n",
        "Adjunto encontrará nuestro catálogo personalizado con su logo suministrado.\n",
        f"Agradecemos su interés, y esperamos generar pronto un contacto con usted. \n",
        "\n",
        "Nota: Este correo se envía automáticamente y con su previa autorización. Lo invitamos a no responderlo, y en caso de consultas realizarlas a su asesor asignado.\n"
    ]

    body_text = "\n\n".join(body_paragraphs)

    # Crear el mensaje
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ', '.join(receiver_emails)
    message['Subject'] = subject

    # Crear el cuerpo del mensaje en formato HTML
    body_html = """
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f2f2f2;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .content {{
                padding-bottom: 50px; /* Espacio para el pie de página */
            }}
            .footer {{
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #ccc;
                padding: 10px 20px;
                text-align: center;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <p>Reciba un cordial saludo por parte de Innova Publicidad Visual S.A.S.</p>
                <p>Adjunto encontrará nuestro catálogo personalizado con su logo suministrado.</p>
                <p>Agradecemos su interés, y esperamos generar pronto un contacto con usted.</p>
                <p></p>
                <p>Nota: Este correo se envía automáticamente. Lo invitamos a comunicarse con nosotros por los medios indicados</p>
            </div>
            <div class="footer">
                <img src="cid:image1" style="max-width: 100%; height: auto;">
            </div>
        </div>
    </body>
    </html>
    """.format("\n".join(body_paragraphs))

    # Adjuntar el texto del cuerpo del mensaje
    message.attach(MIMEText(body_html, 'html'))

    # Adjuntar la imagen como parte del mensaje
    image_path = 'static/images/FIRMA_CORREO.png'  # Ruta de la imagen en tu sistema
    with open(image_path, 'rb') as img_file:
        img = MIMEImage(img_file.read())
    img.add_header('Content-Disposition', 'inline', filename='pie_de_pagina.png')
    img.add_header('Content-ID', '<image1>')
    message.attach(img)

    # Adjuntar el archivo PDF al mensaje
    with open(pdf_final_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename=Catalogo_Innova.pdf')
    message.attach(part)

    # Enviar el correo electrónico a través de un servidor SMTP
    smtp_server = 'mail.innovapublicidad.com.co'
    smtp_port = 587
    smtp_username = 'info@innovapublicidad.com.co'
    smtp_password = 'R5LyN3EFayWx%DYxED&!RY'

    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Activar STARTTLS
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        flash('Correo enviado correctamente', 'success')
    except Exception as e:
        flash(f'Error al enviar el correo electrónico: {str(e)}', 'error')

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

        def compress_pdf(output_buffer_final):
            input_pdf = fitz.open("pdf", output_buffer_final)
            output_buffer_compressed = io.BytesIO()
#
            # Comprimir el PDF con PyMuPDF
            input_pdf.save(output_buffer_compressed, deflate=True)

            output_buffer_compressed.seek(0)
            return output_buffer_compressed

        # Luego, llamar a la función compress_pdf para comprimir el PDF final
        output_buffer_compressed = compress_pdf(output_buffer_final)

        # Verificar el tamaño del PDF comprimido
        print(f"Tamaño del PDF comprimido: {len(output_buffer_compressed.getvalue())} bytes")

        # Finalmente, retornar el PDF comprimido
        return send_file(output_buffer_compressed, as_attachment=True, download_name="catalogo_innova.pdf")

    except Exception as e:
        return f"Error: {str(e)}"
    
#ruta para agregar el sello al pdf

def agregar_fecha_hora_usuario_a_pdf(pdf_path):
    output_buffer = BytesIO()
    packet = BytesIO()

    # create a new PDF with Reportlab   
    can = canvas.Canvas(packet, pagesize=letter)
    
    username = session.get('username')
    user_last_name = session.get('userlastname')
    user_email = session.get('usermail')
    user_link = session.get('userlink')

    
    if username and user_last_name and user_email and user_link:
        usuario_text = f"Generado por: {username} {user_last_name}"
        fecha_hora_text = f"Fecha y hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        email_text = f"Correo: {user_email}"
        link_text = f"Whatsapp: {user_link}"
        
        can.setFillColor(colors.black)
        can.setFont("Helvetica", 7)
        # x - y
        can.drawString(350, 45, usuario_text)
        can.drawString(342, 35, fecha_hora_text)
        can.drawString(330, 25, email_text)
        can.drawString(342, 15, link_text)
    else:
       print("algun dato no se obtuvo")

    can.showPage()  # Mostrar la página actual antes de guardar el lienzo
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    print(len(new_pdf.pages))  # Verificar la cantidad de páginas en el PDF

    existing_pdf = PdfReader(pdf_path)
    output = PdfWriter()

    for page_number in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[page_number]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    output.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer
