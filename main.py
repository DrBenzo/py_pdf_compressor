import os
import shutil
import tempfile
from pdf_utils import find_pdfs, is_scanned_pdf
from compress import compress_text_pdf, compress_scanned_pdf

def recreate_directory_structure(source_dir, dest_dir):
    """
    Воссоздаёт структуру каталогов из source_dir в dest_dir.
    """
    for dirpath, dirnames, filenames in os.walk(source_dir):
        relative_path = os.path.relpath(dirpath, source_dir)
        target_path = os.path.join(dest_dir, relative_path)
        os.makedirs(target_path, exist_ok=True)

def process_pdfs(input_directory, output_directory, temp_folder):
    """
    Обрабатывает все PDF файлы:
    Сжимает текстовые и сканы, воссоздаёт структуру каталогов.
    """
    pdf_files = find_pdfs(input_directory)
    print(f"Найдено PDF файлов: {len(pdf_files)}")

    for pdf_path in pdf_files:
        relative_path = os.path.relpath(pdf_path, input_directory)
        output_path = os.path.join(output_directory, relative_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if is_scanned_pdf(pdf_path):
            print(f"{relative_path} — это скан. Сжатие как изображений.")
            compress_scanned_pdf(pdf_path, output_path, temp_folder)
        else:
            print(f"{relative_path} — текстовый PDF. Сжатие Ghostscript.")
            compress_text_pdf(pdf_path, output_path)

if __name__ == "__main__":
    input_dir = r"test"  # Укажи реальный путь здесь
    output_dir = input_dir + "_compressed"

    temp_dir = tempfile.mkdtemp()  # временная директория
    print(f"Создана временная папка: {temp_dir}")

    try:
        recreate_directory_structure(input_dir, output_dir)
        process_pdfs(input_dir, output_dir, temp_dir)
    finally:
        shutil.rmtree(temp_dir)  # очистка временных файлов
        print("Временная папка удалена.")
