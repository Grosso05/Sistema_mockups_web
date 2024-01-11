from flask import Flask, request, redirect, url_for, send_file, render_template
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_watermark', methods=['POST'])
def add_watermark():
    try:
        if 'pdf_file' not in request.files or 'image_file' not in request.files:
            return redirect(url_for('index'))

        pdf_file = request.files['pdf_file']
        image_file = request.files['image_file']

        if pdf_file.filename == '' or image_file.filename == '':
            return redirect(url_for('index'))

        # Create a BytesIO buffer to store the modified PDF
        output_buffer = BytesIO()

        # Read the PDF and create a PdfReader object
        pdf_reader = PdfReader(pdf_file)

        # Create a temporary file for the image
        image_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image_file.save(image_temp_file.name)

        pdf_writer = PdfWriter()

        # Define the list of watermark positions and dimensions
        watermark_positions = [
            {'x': 4.3, 'y': 13.50, 'width': 100, 'height': 100,},
            {'x': 15.51, 'y': 15.96, 'width': 35, 'height': 35},
            {'x': 10.41, 'y': 4.79, 'width': 25, 'height': 25},
            # Add more positions as needed
        ]

        # Iterate through each page of the PDF
        for page_num in range(len(pdf_reader.pages)):
            # Get the page
            page = pdf_reader.pages[page_num]

            # Create a new canvas for each page
            watermark_page = BytesIO()
            
            # Create a single canvas for all positions on each page
            watermark_canvas = canvas.Canvas(watermark_page, pagesize=letter)

            for position in watermark_positions:
                img_reader = ImageReader(image_temp_file.name)

                # Draw the image with specified position and dimensions
                watermark_canvas.drawImage(
                    img_reader,
                    position['x'] * 72 / 2.54,  # Convert coordinates to points
                    position['y'] * 72 / 2.54,
                    width=position['width'],
                    height=position['height'],
                    mask='auto',
                    preserveAspectRatio=True
                )

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
