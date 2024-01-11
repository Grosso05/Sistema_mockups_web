from flask import Flask, request, redirect, url_for, send_file
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
        <body>
            <h1>PDF Watermark</h1>
            <form action="/add_watermark" method="post" enctype="multipart/form-data">
                <input type="file" name="pdf_file" accept=".pdf"><br>
                <input type="file" name="image_file" accept=".png"><br>
                <input type="submit" value="Add Watermark">
            </form>
        </body>
    </html>
    '''

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

        # Create a watermark page from the PNG image
        watermark_page = BytesIO()
        watermark_canvas = canvas.Canvas(watermark_page, pagesize=letter)
        watermark_canvas.drawImage(image_temp_file.name, 100, 100, width=200, height=200)
        watermark_canvas.showPage()
        watermark_canvas.save()

        # Iterate through each page of the PDF
        for page_num in range(len(pdf_reader.pages)):
            # Get the page
            page = pdf_reader.pages[page_num]

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
