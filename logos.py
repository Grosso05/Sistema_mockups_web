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
            [{'x': 5.41, 'y': 09.48, 'width': 120, 'height': 100, 'rotation': 359, 'opacity': 0.8}],
            # Coordinates for page 2
            [{'x': 6.48, 'y': 11.53, 'width': 40, 'height': 20, 'rotation': -5, 'opacity': 0.7}],
            # Coordinates for page 3
            [{'x': 8.56, 'y': 10.80, 'width': 30, 'height': 25, 'rotation': 0, 'opacity': 0.7}]
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
            # Coordinates for page 1
            [{'x': 5.41, 'y': 09.48, 'width': 120, 'height': 100, 'rotation': 359, 'opacity': 0.8}],
            # Coordinates for page 2
            [{'x': 6.48, 'y': 11.53, 'width': 40, 'height': 20, 'rotation': -5, 'opacity': 0.7}],
            # Coordinates for page 3
            [{'x': 8.56, 'y': 10.80, 'width': 30, 'height': 25, 'rotation': 0, 'opacity': 0.7}]
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
    can.setFillColor(colors.white)  # Set text color to white
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