from flask import Flask, request, redirect, url_for, send_file, render_template
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
import math
import cv2
import numpy as np

app = Flask(__name__)

# Set the constant PDF file path
FIXED_PDF_FILE_PATH = "./Catalogo_white.pdf"
ANOTHER_PDF_FILE_PATH = "./Catalogo_black.pdf"


@app.route('/')
def index():
    return render_template('index.html')

def get_white_presence(image_path):
    # Lee la imagen utilizando OpenCV
    image = cv2.imread(image_path)

    # Convierte la imagen de BGR a escala de grises
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplica un umbral para identificar píxeles blancos
    _, thresholded = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)

    # Calcula el porcentaje de píxeles blancos en la imagen
    white_percentage = (np.sum(thresholded == 255) / thresholded.size) * 100

    # Imprime el porcentaje de presencia de blanco
    print(f"El color blanco se encuentra en un : {white_percentage:.2f}%")
    
    # Return the white percentage
    return white_percentage

@app.route('/add_watermark', methods=['POST'])
def add_watermark():
    try:
        if 'image_file' not in request.files:
            return redirect(url_for('index'))

        image_file = request.files['image_file']

        if image_file.filename == '':
            return redirect(url_for('index'))

        # Create a BytesIO buffer to store the modified PDF
        output_buffer = BytesIO()

        # Create a temporary file for the image
        image_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image_file.save(image_temp_file.name)

        # Get white presence from the image and print it
        white_percentage = get_white_presence(image_temp_file.name)

        # Conditionally choose the PDF file based on white presence percentage
        if white_percentage >= 10:  
            pdf_path = ANOTHER_PDF_FILE_PATH  # Specify the path to the alternate PDF
        else:
            pdf_path = FIXED_PDF_FILE_PATH

        # Read the PDF and create a PdfReader object
        pdf_reader = PdfReader(pdf_path)

        # Create a PdfWriter object for the modified PDF
        pdf_writer = PdfWriter()

        # Define the list of watermark positions, dimensions, rotation, and opacity for each page
        watermark_positions = [
                #coordenadas pagina #1
            [
                {'x': 5.41, 'y': 09.48, 'width': 120, 'height': 100, 'rotation': 359, 'opacity': 0.8},
            ],
            # Coordenadas paginas #2
            [
                {'x': 6.48, 'y': 11.53, 'width': 40, 'height': 20, 'rotation': -5, 'opacity': 0.7},
                # Add more positions as needed
            ],
                #coordenadas pagina #3
            [ 
                {'x': 8.56, 'y': 10.80, 'width': 30, 'height': 25, 'rotation': 0, 'opacity': 0.7},
            ]
            # Add more pages as needed
        ]

        # Iterate through each page of the PDF
        for page_num in range(len(pdf_reader.pages)):
            # Get the page
            page = pdf_reader.pages[page_num]

            # Create a new canvas for each page
            watermark_page = BytesIO()

            # Create a single canvas for all positions on each page
            watermark_canvas = canvas.Canvas(watermark_page, pagesize=letter)

            for position in watermark_positions[page_num]:
                img_reader = ImageReader(image_temp_file.name)

                # Draw the image with specified position, dimensions, rotation, and opacity
                watermark_canvas.saveState()
                watermark_canvas.translate(position['x'] * 72 / 2.54, position['y'] * 72 / 2.54)
                watermark_canvas.rotate(position.get('rotation', 0))
                watermark_canvas.setFillAlpha(position.get('opacity', 1.0))  # Use 1.0 if opacity is not specified
                watermark_canvas.drawImage(
                    img_reader,
                    0,
                    0,
                    width=position['width'],
                    height=position['height'],
                    mask='auto',
                    preserveAspectRatio=True
                )
                watermark_canvas.restoreState()

            # Save the watermark canvas after all positions have been drawn
            watermark_canvas.showPage()
            watermark_canvas.save()

            # Set the watermark page to the beginning
            watermark_page.seek(0)

            # Merge the watermark with the original page
            page.merge_page(PdfReader(watermark_page).pages[0])

            # Add the modified page to the PdfWriter
            pdf_writer.add_page(page)

        # Write the modified PDF to the BytesIO buffer
            pdf_writer.write(output_buffer)

        # Set the buffer position to the beginning for reading
        output_buffer.seek(0)

        # Close and remove the temporary image file
        image_temp_file.close()
        os.remove(image_temp_file.name)

        # Return the file for download
        return send_file(output_buffer, as_attachment=True, download_name="modified_pdf.pdf")

    except Exception as e:
        # Handle any exception that may occur
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
