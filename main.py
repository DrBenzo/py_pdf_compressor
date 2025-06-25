import os
import shutil
import tempfile
from pdf_utils import find_pdfs, is_scanned_pdf
from compress import compress_text_pdf, compress_scanned_pdf
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from tkinter import Tk, filedialog
from pathlib import Path
import sys
from rich.progress import Progress

console = Console()

def ask_quality():
    console.print("\n[bold]Выберите уровень сжатия изображений (для сканов):[/bold]")
    console.print("1. Высокое качество (90%)")
    console.print("2. Среднее (70%)")
    console.print("3. Сильное сжатие (50%)")
    console.print("4. Максимальное (30%)")

    choice = input("Ваш выбор [1-4]: ").strip()

    mapping = {
        "1": 90,
        "2": 70,
        "3": 50,
        "4": 30
    }

    return mapping.get(choice, 70)  # По умолчанию 70

def get_file_size(path):
    return os.path.getsize(path) if os.path.exists(path) else 0

def choose_directory():
    """
    Открывает диалог выбора папки и возвращает путь к выбранной папке.
    """
    root = Tk()
    root.withdraw()  # Скрыть главное окно
    root.attributes('-topmost', True)  # Установить окно поверх других
    folder = filedialog.askdirectory(title="Выберите папку с PDF файлами")
    root.destroy()  # Закрыть диалоговое окно
    return folder

def run_pipeline(source_dir, scale_percent):
    # Создаем копию каталога
    dest_dir = f"{source_dir}_compressed"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    pdf_files = find_pdfs(source_dir)
    if not pdf_files:
        console.print("[red]В выбранной папке не найдено PDF файлов![/red]")
        return
    
    total_original_size = 0
    total_compressed_size = 0

    with tempfile.TemporaryDirectory() as temp_dir, Progress() as progress:
        task = progress.add_task("[cyan]Обработка PDF файлов...", total=len(pdf_files))

        for pdf_path in pdf_files:
            console.print(f"[cyan]Обработка файла: {pdf_path}[/cyan] {pdf_path}")
            relative_path = Path(pdf_path).relative_to(source_dir)
            output_path = Path(dest_dir) / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            original_size = get_file_size(pdf_path)

            if is_scanned_pdf(pdf_path):
                compress_scanned_pdf(pdf_path, output_path, temp_dir, scale_percent)
            else:
                compress_text_pdf(pdf_path, output_path)

            compressed_size = get_file_size(output_path)

            total_original_size += original_size
            total_compressed_size += compressed_size

            progress.update(task, advance=1)

    console.rule("[bold green]Готово")
    console.print(f"[bold]Обработано файлов:[/bold] {len(pdf_files)}")
    console.print(f"[bold]Исходный объём:[/bold] {total_original_size / 1024 / 1024:.2f} MB")
    console.print(f"[bold]Сжатый объём:[/bold] {total_compressed_size / 1024 / 1024:.2f} MB")

    if total_original_size > 0:
        saved_percent = 100 - (total_compressed_size / total_original_size * 100)
        console.print(f"[bold]Экономия:[/bold] {saved_percent:.2f}%")

def main():
    console.print(Panel.fit("[bold green]PDF Compressor[/bold green]", title="Добро пожаловать", border_style="green"))

    source_dir = choose_directory()
    if not source_dir:
        console.print("[red]Вы не выбрали папку![/red]")
        sys.exit(1)

    scale_percent = ask_quality()
    run_pipeline(source_dir, scale_percent)

if __name__ == "__main__":
    main()
