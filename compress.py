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
        '-dPDFSETTINGS=/screen',
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

def compress_images(image_paths, quality=50, scale_percent=70):
    """
    Сжимает изображения JPEG с указанным качеством.
    Возвращает список путей к сжатым изображениям.
    """
    compressed_paths = []

    for img_path in image_paths:
        image = Image.open(img_path)
        width, height = image.size

        # Вычисляем новые размеры
        new_width = int(width * scale_percent / 100)
        new_height = int(height * scale_percent / 100)

        # Изменяем размер
        image = image.resize((new_width, new_height), Image.LANCZOS)

        compressed_path = img_path.replace(".jpg", "_compressed.jpg")
        image.save(compressed_path, "JPEG", quality=quality, optimize=True)
        compressed_paths.append(compressed_path)

    return compressed_paths

def create_pdf_from_images(image_paths, output_pdf_path):
    """
    Создаёт PDF из изображений, автоматически выбирая ориентацию A4 и сохраняя пропорции.
    """
    pdf = FPDF(unit="mm")
    dpi = 96  # Предполагаемое DPI изображений

    for img_path in image_paths:
        image = Image.open(img_path)
        img_width_px, img_height_px = image.size

        img_width_mm = img_width_px * 25.4 / dpi
        img_height_mm = img_height_px * 25.4 / dpi

        # Определяем ориентацию страницы
        if img_width_mm > img_height_mm:
            # Альбомная ориентация
            page_width, page_height = 297, 210
            pdf.add_page(orientation='L')  # Landscape
        else:
            # Книжная ориентация
            page_width, page_height = 210, 297
            pdf.add_page(orientation='P')  # Portrait

        # Масштабирование с сохранением пропорций
        scale = min(page_width / img_width_mm, page_height / img_height_mm)
        new_width = img_width_mm * scale
        new_height = img_height_mm * scale

        # Центрирование
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        pdf.image(img_path, x=x, y=y, w=new_width, h=new_height)

    pdf.output(output_pdf_path)

def compress_scanned_pdf(input_pdf_path, output_pdf_path, temp_folder, scale_percent=70):
    """
    Полный цикл сжатия сканированного PDF:
    1) Извлечение изображений
    2) Сжатие изображений
    3) Сборка нового PDF
    """
    extracted_images = extract_images_from_pdf(input_pdf_path, temp_folder)
    compressed_images = compress_images(extracted_images, scale_percent=scale_percent)
    create_pdf_from_images(compressed_images, output_pdf_path)
