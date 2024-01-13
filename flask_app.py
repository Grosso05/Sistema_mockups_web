from flask import Flask, request, redirect, url_for, send_file, render_template
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
import math

app = Flask(__name__)

# Set the constant PDF file path
FIXED_PDF_FILE_PATH = "./CATALOGO DE PRUEBA2pag.pdf"

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

        # Create a BytesIO buffer to store the modified PDF
        output_buffer = BytesIO()

        # Read the fixed PDF and create a PdfReader object
        pdf_reader = PdfReader(FIXED_PDF_FILE_PATH)

        # Create a temporary file for the image
        image_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image_file.save(image_temp_file.name)

        pdf_writer = PdfWriter()

        # Define the list of watermark positions, dimensions, rotation, and opacity for each page
        watermark_positions = [
            [
                {'x': 7.15, 'y': 12.50, 'width': 120, 'height': 100, 'rotation': 359, 'opacity': 0.8},
            ],
            # Define positions for the second page
            [
                {'x': 9.72, 'y': 5.60, 'width': 30, 'height': 30, 'rotation': 0, 'opacity': 1.0},
                {'x': 10.50, 'y': 21.00, 'width': 30, 'height': 30, 'rotation': 4, 'opacity': 1.0},
                # Add more positions as needed
            ],
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
