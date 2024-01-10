from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfWriter, PdfReader, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.lib.utils import ImageReader
from PyPDF2.generic import createStringObject

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_watermark', methods=['POST'])
def add_watermark():
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
    pdf_writer = PdfWriter()

    # Load the watermark image using ImageReader
    watermark = ImageReader(image_file)

    # Iterate through each page of the PDF
    for page_num in range(len(pdf_reader.pages)):
        # Get the page and create a canvas
        page = pdf_reader.pages[page_num]
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Draw the watermark on the canvas
        can.drawImage(watermark, 100, 100, width=watermark._width, height=watermark._height)

        # Merge the watermark with the original page
        page2 = PageObject.create_blank_page(width=page.mediabox.width, height=page.mediabox.height)
        page2.merge_page(page)
        
        # Translate the page content
        page2.artbox.upper_left = (page2.artbox.upper_left[0] + 100, page2.artbox.upper_left[1] + 100)

    
        # Add the modified page to the PdfWriter
        pdf_writer.add_page(page2)

    # Write the modified PDF to the BytesIO buffer
    pdf_writer.write(output_buffer)

    # Set the buffer position to the beginning for reading
    output_buffer.seek(0)

    return output_buffer.read()

if __name__ == '__main__':
    app.run(debug=True)
