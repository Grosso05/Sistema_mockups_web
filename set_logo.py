# set_logo.py
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile  # ¡Asegúrate de que esta línea esté presente!

def set_logo(image_temp_file, pdf_path, watermark_positions):
    output_buffer = BytesIO()
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        watermark_page = BytesIO()
        watermark_canvas = canvas.Canvas(watermark_page, pagesize=letter)

        for position in watermark_positions[page_num]:
            img_reader = ImageReader(image_temp_file.name)

            watermark_canvas.saveState()
            watermark_canvas.translate(position['x'] * 72 / 2.54, position['y'] * 72 / 2.54)
            watermark_canvas.rotate(position.get('rotation', 0))
            watermark_canvas.setFillAlpha(position.get('opacity', 1.0))
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

        watermark_canvas.showPage()
        watermark_canvas.save()

        watermark_page.seek(0)
        page.merge_page(PdfReader(watermark_page).pages[0])
        pdf_writer.add_page(page)

    pdf_writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer
