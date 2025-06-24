import os
import fitz  # PyMuPDF

def find_pdfs(directory):
    """
    Рекурсивно ищет все PDF файлы в указанном каталоге.
    Возвращает список абсолютных путей к PDF файлам.
    """
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def is_scanned_pdf(pdf_path, image_threshold=0.5):
    """
    Определяет, является ли PDF сканом.
    Если доля страниц с изображениями >= image_threshold — считается сканом.
    """
    doc = fitz.open(pdf_path)
    image_pages = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        if images:
            image_pages += 1

    ratio = image_pages / len(doc)
    return ratio >= image_threshold
