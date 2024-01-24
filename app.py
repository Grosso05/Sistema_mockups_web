# app.py
from flask import Flask, request, redirect, url_for, send_file, render_template
from calculate import get_white_presence
from set_logo import set_logo
import tempfile
import os
from models import configure_db, test_db_connection, Users, UsersRol  


app = Flask(__name__)

configure_db(app)  # Configura la base de datos

# Comprueba la conexión a la base de datos
test_db_connection(app)


FIXED_PDF_FILE_PATH = "./Catalogo_white.pdf"
ANOTHER_PDF_FILE_PATH = "./Catalogo_black.pdf"

@app.route('/')
def index():
    return render_template('index.html')

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
