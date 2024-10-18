import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import os
import sys
import traceback

# Функция для создания PDF с текстом в памяти
def create_watermark(text, x, y, angle):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Times New Roman', 'TNR.ttf'))

    c.translate(x, y)  # Перемещение начала координат
    c.rotate(angle)  # Поворот текста на 270 градусов

    c.setFont('Times New Roman', 14)
    c.drawString(0, 0, text)
    c.save()
    packet.seek(0)
    return packet

# Функция для добавления текста в PDF
def add_text_to_pdf(input_pdf, output_pdf, text, x, y, angle):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Создаем водяной знак с текстом
    watermark_pdf = create_watermark(text, x, y, angle)
    watermark_reader = PdfReader(watermark_pdf)
    watermark_page = watermark_reader.pages[0]

    # Накладываем текст на каждую страницу PDF
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

# Функция для выбора нескольких PDF файлов
def choose_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if file_paths:
        root.selected_files = file_paths
        file_label.config(text=f"{len(file_paths)} файлов выбрано")  # Показываем количество выбранных файлов

# Функция для обработки и добавления текста
def process_pdfs():
    try:
        if not hasattr(root, 'selected_files'):
            messagebox.showwarning("Ошибка", "Выберите файлы PDF!")
            return

        text = text_entry.get()
        try:
            x = int(x_entry.get())
            y = int(y_entry.get())
            angle = int(angle_entry.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректные координаты!")
            return

        first_pdf_path = root.selected_files[0]
        input_dir = os.path.dirname(first_pdf_path)

        # Получаем имя текущей директории
        current_dir_name = os.path.basename(input_dir)

        # Создаем имя новой папки: <текущая директория> + <введённый текст>
        new_folder_name = f"{text}_{current_dir_name}"
        output_dir = os.path.join(input_dir, new_folder_name)

        # Создаем папку, если она не существует
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for input_pdf in root.selected_files:
            pdf_filename = os.path.basename(input_pdf)  # Имя исходного файла PDF
            output_pdf = os.path.join(output_dir, pdf_filename)  # Путь к новому файлу в новой папке

            # Добавляем текст в PDF
            add_text_to_pdf(input_pdf, output_pdf, text, x, y, angle)
            console_output(f"Обработан файл: {output_pdf}")

        messagebox.showinfo("Готово", f"Все файлы сохранены в папку: {output_dir}")

        # Очистка полей после завершения процесса
        text_entry.delete(0, tk.END)  # Очищаем поле ввода текста
        x_entry.delete(0, tk.END)  # Очищаем поле ввода координаты X
        y_entry.delete(0, tk.END)  # Очищаем поле ввода координаты Y
        angle_entry.delete(0, tk.END) # Очищаем поле ввода угла

    except Exception as e:
        # Перехватываем и выводим все ошибки
        error_message = traceback.format_exc()  # Получаем полную трассировку ошибки
        console_output(f"Ошибка в process_pdfs: {error_message}")
        messagebox.showerror("Ошибка в process_pdfs", f"Произошла ошибка: {str(e)}")

# Функция для вывода сообщений в текстбокс (консоль)
def console_output(message):
    console_textbox.config(state=tk.NORMAL)  # Делаем текстовое поле редактируемым временно
    console_textbox.insert(tk.END, message + '\n')  # Добавляем сообщение
    console_textbox.config(state=tk.DISABLED)  # Снова делаем поле нередактируемым
    console_textbox.see(tk.END)  # Скроллим к последнему сообщению

# Перенаправляем стандартный вывод в текстбокс
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, message)
        self.widget.config(state=tk.DISABLED)
        self.widget.see(tk.END)

    def flush(self):
        pass

# Основная функция, которая запускает GUI
def main():
    global root, text_entry, x_entry, y_entry, angle_entry, console_textbox, file_label

    # Создание графического интерфейса
    root = tk.Tk()
    root.title("Редактор PDF с текстом")
    root.geometry("700x700")

    # Кнопка выбора файлов
    choose_button = tk.Button(root, text="Выбрать PDF файлы", command=choose_files)
    choose_button.pack(pady=10)

    # Метка для отображения выбранных файлов
    file_label = tk.Label(root, text="Файлы не выбраны")
    file_label.pack()

    # Поле для ввода текста
    tk.Label(root, text="Введите текст:").pack(pady=5)
    text_entry = tk.Entry(root)
    text_entry.pack(pady=5)

    # Поля для ввода координат X и Y
    tk.Label(root, text="Координата X(14):").pack(pady=5)
    x_entry = tk.Entry(root)
    x_entry.pack(pady=5)

    tk.Label(root, text="Координата Y(10):").pack(pady=5)
    y_entry = tk.Entry(root)
    y_entry.pack(pady=5)

    tk.Label(root, text="Угол поворота:").pack(pady=5)
    angle_entry = tk.Entry(root)
    angle_entry.pack(pady=5)

    # Кнопка для запуска процесса
    process_button = tk.Button(root, text="Добавить текст в PDF", command=process_pdfs)
    process_button.pack(pady=20)

    # Текстовое поле для вывода сообщений
    console_textbox = tk.Text(root, height=10, state=tk.DISABLED)  # Поле нередактируемое
    console_textbox.pack(fill=tk.BOTH, pady=10, padx=10)

    # Перенаправляем stdout в текстовое поле
    sys.stdout = TextRedirector(console_textbox)

    root.mainloop()

# Если скрипт запущен напрямую, вызываем main()
if __name__ == "__main__":
    main()