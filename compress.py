import os
import fitz  # PyMuPDF
from PIL import Image
from fpdf import FPDF
import subprocess

def compress_text_pdf(input_pdf_path, output_pdf_path):
    """
    Сжимает текстовый PDF с помощью Ghostscript.
    """
    gs_command = [
        'gswin64c',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_pdf_path}',
        input_pdf_path
    ]

    subprocess.run(gs_command, check=True)

def extract_images_from_pdf(pdf_path, output_folder):
    """
    Извлекает все изображения из PDF в указанную папку.
    Возвращает список путей к извлечённым изображениям.
    """
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            img_path = os.path.join(output_folder, f"page{page_number + 1}_{img_index + 1}.jpg")
            pix.save(img_path)
            image_paths.append(img_path)

    return image_paths

def compress_images(image_paths, quality=10):
    """
    Сжимает изображения JPEG с указанным качеством.
    Возвращает список путей к сжатым изображениям.
    """
    compressed_paths = []

    for img_path in image_paths:
        image = Image.open(img_path)
        compressed_path = img_path.replace(".jpg", "_compressed.jpg")
        image.save(compressed_path, "JPEG", quality=quality)
        compressed_paths.append(compressed_path)

    return compressed_paths

def create_pdf_from_images(image_paths, output_pdf_path):
    """
    Создаёт новый PDF из списка изображений.
    """
    pdf = FPDF()

    for img_path in image_paths:
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=210, h=297)  # формат A4

    pdf.output(output_pdf_path, "F")

def compress_scanned_pdf(input_pdf_path, output_pdf_path, temp_folder):
    """
    Полный цикл сжатия сканированного PDF:
    1) Извлечение изображений
    2) Сжатие изображений
    3) Сборка нового PDF
    """
    extracted_images = extract_images_from_pdf(input_pdf_path, temp_folder)
    compressed_images = compress_images(extracted_images, quality=50)
    create_pdf_from_images(compressed_images, output_pdf_path)
