"""
Графический интерфейс для конвертации выписки Сбербанка/ВТБ из PDF в Excel.
Поддерживается выбор библиотеки парсинга PDF (pdfminer / pypdf) и формата вывода (xlsx / csv).
"""

try:
    import tkinter
except ImportError as e:
    raise RuntimeError(
        "Tkinter не установлен. "
        "На Ubuntu: sudo apt-get install python3.XX-tk или используйте интерпретатор Python, собранный с Tcl/Tk."
    ) from e

import os
import threading
import traceback
import sys
import logging
from tkinter import *
from tkinter import filedialog, scrolledtext, Menu, messagebox, ttk

from Sberbank2Excel.sberbankPDF2Excel import sberbankPDF2Excel
from Sberbank2Excel import version_info

# ------------------------ Глобальные переменные ------------------------
files = ()                          # выбранные PDF-файлы
leave_intermediate_txt_file = 0     # не удалять промежуточный txt
no_balance_check = 0                # игнорировать сверку баланса
output_file_type = "xlsx"           # формат вывода
pdf_library = "pdfminer"            # библиотека парсинга PDF

conversion_running = False          # флаг, что конвертация уже идёт
conversion_thread = None            # поток конвертации

# ------------------------ Вспомогательные функции ------------------------
def log_message(text):
    """Выводит сообщение в панель логов и в консоль."""
    log_scrolledtext.configure(state=NORMAL)
    log_scrolledtext.insert(END, text + '\n')
    log_scrolledtext.see(END)
    log_scrolledtext.configure(state=DISABLED)
    print(text)

def set_ui_state(enabled):
    """Включает или отключает элементы интерфейса."""
    state = NORMAL if enabled else DISABLED
    btn_select_files.config(state=state)
    btn_convert.config(state=state)
    combobox_type.config(state='readonly' if enabled else DISABLED)
    combobox_pdf.config(state='readonly' if enabled else DISABLED)
    chk_leave_txt.config(state=state)
    chk_no_balance.config(state=state)
    chk_reverse.config(state=state)

def update_progress(percent, message):
    """Обновляет прогресс-бар и текстовую метку."""
    progress_bar['value'] = percent
    progress_label.config(text=message)

def finalize_conversion():
    """Восстанавливает интерфейс после завершения конвертации."""
    global conversion_running, conversion_thread
    conversion_running = False
    conversion_thread = None
    set_ui_state(enabled=True)
    progress_bar['value'] = 0
    progress_label.config(text="")

# ------------------------ Обработчики кнопок ------------------------
def btn_selectFiles_clicked():
    global files
    files = filedialog.askopenfilenames(
        parent=window,
        title='Выберите файл(ы)',
        filetypes=(("PDF файл", "*.pdf"), ("All Files", "*.*"))
    )
    SelectedFiles_ScrolledText.configure(state=NORMAL)
    SelectedFiles_ScrolledText.delete('1.0', END)
    created_excel_files_scrollText.delete('1.0', END)

    for file in files:
        SelectedFiles_ScrolledText.insert(INSERT, file + '\n')
    SelectedFiles_ScrolledText.configure(state=DISABLED)

def run_conversion_thread():
    """Выполняет конвертацию в фоновом потоке и обновляет GUI."""
    global conversion_running
    qnt_files = len(files)
    qnt_files_converted = 0

    window.after(0, update_progress, 0, "Конвертация началась...")

    for idx, file in enumerate(files):
        try:
            converted_file_name = sberbankPDF2Excel(
                file,
                leave_intermediate_txt_file=leave_intermediate_txt_file.get(),
                perform_balance_check=not no_balance_check.get(),
                reversed_transaction_order=reversed_transaction_order.get(),
                output_file_type=output_file_type.get(),
                pdf_lib=pdf_library.get()
            )
            # Успех – добавляем в список созданных файлов
            window.after(0, lambda f=converted_file_name: created_excel_files_scrollText.insert(INSERT, f + '\n'))
            qnt_files_converted += 1
            window.after(0, log_message, f"Успешно: {file} -> {converted_file_name}")
        except Exception as e:
            fname = os.path.basename(file)
            err_msg = f"Ошибка при конвертации файла:\n{fname}\n\n{e}"
            window.after(0, log_message, err_msg)
            window.after(0, messagebox.showerror, "Ошибка конвертации", err_msg)
            window.after(0, log_message, "Пропускаем конвертацию этого файла")

        progress = int(((idx + 1) / qnt_files) * 100)
        window.after(0, update_progress, progress, f"Обработано {idx + 1} из {qnt_files}")

    if qnt_files == qnt_files_converted:
        window.after(0, log_message, "Все файлы успешно сконвертированы")
    else:
        window.after(0, log_message,
                     f"!!!!!!! {qnt_files - qnt_files_converted} файл(а) из {qnt_files} не были сконвертированы")

    window.after(0, finalize_conversion)

def btn_convertFiles_clicked():
    """Запускает конвертацию, если она ещё не идёт."""
    global conversion_running, conversion_thread
    if conversion_running:
        messagebox.showwarning("Внимание", "Конвертация уже выполняется. Дождитесь завершения.")
        return
    if not files:
        messagebox.showwarning("Внимание", "Не выбрано ни одного файла.")
        return

    # Очищаем результаты и лог
    created_excel_files_scrollText.configure(state=NORMAL)
    created_excel_files_scrollText.delete('1.0', END)
    log_scrolledtext.configure(state=NORMAL)
    log_scrolledtext.delete('1.0', END)
    log_scrolledtext.configure(state=DISABLED)

    set_ui_state(enabled=False)
    conversion_running = True
    conversion_thread = threading.Thread(target=run_conversion_thread, daemon=True)
    conversion_thread.start()

# ------------------------ Построение интерфейса ------------------------
window = Tk()
menu = Menu(window)
help_about = Menu(menu)

def help_about_clicked():
    info_string = (f"{version_info.NAME}\n"
                   f"Версия={version_info.VERSION}\n"
                   f"Автор={version_info.AUTHOR}\n"
                   f"Где скачать={version_info.HOMEPAGE}")
    log_message(info_string)
    messagebox.showinfo('', info_string)

help_about.add_command(label='About', command=help_about_clicked)
menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)

window.title(f'{version_info.NAME} Версия={version_info.VERSION}')
window.geometry('720x720')
window.columnconfigure(0, weight=1)

# ------------------------ Шаг 1: выбор файлов ------------------------
step1_frame = LabelFrame(window, text="Шаг 1: Выбор PDF-файлов", padx=10, pady=5)
step1_frame.grid(column=0, row=0, padx=10, pady=(10, 5), sticky="EW")
step1_frame.columnconfigure(0, weight=1)

btn_select_files = Button(step1_frame, text="Выбрать файлы", command=btn_selectFiles_clicked)
btn_select_files.grid(row=0, column=0, padx=5, pady=5, sticky="W")

Label(step1_frame, text='Выбранные файлы:').grid(row=1, column=0, sticky="W")
SelectedFiles_ScrolledText = scrolledtext.ScrolledText(step1_frame, width=80, height=4, state=DISABLED)
SelectedFiles_ScrolledText.grid(row=2, column=0, padx=5, pady=5, sticky="EW")

# ------------------------ Шаг 2: настройки и конвертация ------------------------
step2_frame = LabelFrame(window, text="Шаг 2: Настройки конвертации", padx=10, pady=5)
step2_frame.grid(column=0, row=1, padx=10, pady=5, sticky="EW")

settings_frame = Frame(step2_frame)
settings_frame.pack(anchor="w", pady=5)

Label(settings_frame, text="Формат:").pack(side="left", padx=(0, 5))
output_file_type = StringVar(value="xlsx")
type_files = ("xlsx", "csv")
combobox_type = ttk.Combobox(settings_frame, textvariable=output_file_type, state="readonly", values=type_files, width=6)
combobox_type.pack(side="left", padx=(0, 20))

Label(settings_frame, text="PDF библиотека:").pack(side="left", padx=(0, 5))
pdf_libraries = ("auto", "pdfminer", "pypdf")
pdf_library = StringVar(value=pdf_libraries[0])
combobox_pdf = ttk.Combobox(settings_frame, textvariable=pdf_library, state="readonly", values=pdf_libraries, width=8)
combobox_pdf.pack(side="left")

btn_convert = Button(step2_frame, text="Сконвертировать выбранные файлы",
                     command=btn_convertFiles_clicked,
                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
btn_convert.pack(pady=10)

# Прогресс-бар
progress_label = Label(step2_frame, text="")
progress_label.pack(pady=(5, 0))
progress_bar = ttk.Progressbar(step2_frame, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=(0, 10))

# ------------------------ Созданные файлы ------------------------
output_frame = LabelFrame(window, text="Созданные файлы", padx=10, pady=5)
output_frame.grid(column=0, row=2, padx=10, pady=5, sticky="EW")
created_excel_files_scrollText = scrolledtext.ScrolledText(output_frame, width=80, height=4)
created_excel_files_scrollText.pack(fill="x", expand=True)

# ------------------------ Лог выполнения ------------------------
log_frame = LabelFrame(window, text="Лог выполнения", padx=10, pady=5)
log_frame.grid(column=0, row=3, padx=10, pady=5, sticky="EW")
log_scrolledtext = scrolledtext.ScrolledText(log_frame, width=80, height=6, state=DISABLED)
log_scrolledtext.pack(fill="x", expand=True)

# ------------------------ Опции ------------------------
options_frame = LabelFrame(window, text="Опции", padx=10, pady=5)
options_frame.grid(column=0, row=4, padx=10, pady=(5, 10), sticky="EW")

leave_intermediate_txt_file = IntVar()
chk_leave_txt = Checkbutton(options_frame, text="Не удалять промежуточный текстовый файл",
                            variable=leave_intermediate_txt_file)
chk_leave_txt.grid(row=0, sticky=W, pady=2)

no_balance_check = IntVar()
chk_no_balance = Checkbutton(options_frame, text="Игнорировать результаты сверки баланса",
                             variable=no_balance_check)
chk_no_balance.grid(row=1, sticky=W, pady=2)

reversed_transaction_order = IntVar()
chk_reverse = Checkbutton(options_frame, text="Изменить порядок трансакций на обратный",
                          variable=reversed_transaction_order)
chk_reverse.grid(row=2, sticky=W, pady=2)

# ------------------------ Запуск ------------------------
def main():
    window.mainloop()

if __name__ == '__main__':
    main()