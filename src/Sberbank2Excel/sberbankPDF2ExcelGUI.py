"""
Графический интерфейс для для конвертации выписки Сбербанка по карте из формата PDF в формат Excel.
"""

# sources used:
# https://likegeeks.com/python-gui-examples-tkinter-tutorial/



# https://github.com/Ev2geny/Sberbank2Excel/issues/74
try:
    import tkinter
except ImportError as e:
    raise RuntimeError(
        "Tkinter не установлен. "
        "На Ubuntu: sudo apt-get install python3.XX-tk или используйте интерпретатор Python, собранный с Tcl/Tk."
    ) from e

import os
from tkinter import *
import tkinter.filedialog
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox, ttk
import traceback
import sys
import logging

from Sberbank2Excel.sberbankPDF2Excel import sberbankPDF2Excel
from Sberbank2Excel import version_info


# defining global variable, which will hold files tuple
files = ()
leave_intermediate_txt_file = 0
no_balance_check = 0
output_file_type = "xlsx"
pdf_library = "pdfminer"


def log_message(text):
    """Выводит сообщение в панель логов и в консоль."""
    log_scrolledtext.configure(state=NORMAL)
    log_scrolledtext.insert(END, text + '\n')
    log_scrolledtext.see(END)
    log_scrolledtext.configure(state=DISABLED)
    print(text)

def btn_selectFiles_clicked():
    global files

    files = tkinter.filedialog.askopenfilenames(parent=window,
                                                title='Выберете файл(ы)',
                                                filetypes =(("PDF файл", "*.pdf"),("All Files","*.*")) )

    SelectedFiles_ScrolledText.configure(state=NORMAL)
    # empty scrollText widget
    SelectedFiles_ScrolledText.delete('1.0', END)
    created_excel_files_scrollText.delete('1.0', END)

    # Populating SelectedFiles_ScrolledText widget
    for file in files:
        SelectedFiles_ScrolledText.insert(INSERT, file+'\n')

    SelectedFiles_ScrolledText.configure(state = DISABLED)
    

def btn_convertFiles_clicked():
    """
    Конвертирует выбранные файлы, выводя информацию в лог.
    """
    log_message("Версия " + version_info.VERSION)
    created_excel_files_scrollText.delete('1.0', END)

    qnt_files = len(files)
    qnt_files_converted = 0
    
    converted_file_name = ''
    
    for file in files:
        try:
            converted_file_name = sberbankPDF2Excel(
                file,
                leave_intermediate_txt_file=leave_intermediate_txt_file.get(),
                perform_balance_check=not no_balance_check.get(),
                reversed_transaction_order=reversed_transaction_order.get(),
                output_file_type=output_file_type.get(),
                pdf_lib=pdf_library.get()
            )
            created_excel_files_scrollText.insert(INSERT, converted_file_name + '\n')
            qnt_files_converted += 1
            log_message(f"Успешно: {file} -> {converted_file_name}")
        except Exception as e:
            f = file.split("/")[-1]
            err_msg = f"Ошибка при конвертации файла:\n{f}\n\n{e}"
            log_message(err_msg)
            messagebox.showerror("Ошибка конвертации", err_msg)
            log_message("Пропускаем конвертацию этого файла")
            continue

    if qnt_files == qnt_files_converted:
        log_message("Все файлы успешно сконвертированы")
    else:
        log_message(f"!!!!!!! {qnt_files - qnt_files_converted} файл(а) из {qnt_files} не были сконвертированы")


# --- Основное окно ---
window = Tk()
menu = Menu(window)
help_about = Menu(menu)

def help_about_clicked():
    info_string = f'{version_info.NAME}\nВерсия={version_info.VERSION}\nАвтор={version_info.AUTHOR}\nГде скачать={version_info.HOMEPAGE}'
    log_message(info_string)
    messagebox.showinfo('', info_string)

help_about.add_command(label='About', command=help_about_clicked)
menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)

window.title(f'{version_info.NAME} Версия={version_info.VERSION}')
window.geometry('720x600')   # чуть выше для логов

# Шаг 1
Label(window, text="Шаг 1: Выберите один или несколько файлов в формате PDF", justify=LEFT).grid(column=0, row=0, sticky="W")
Button(window, text="Выбрать файлы", command=btn_selectFiles_clicked).grid(column=0, row=2)

Label(window, text='Выбранные файлы:').grid(column=0, row=3, sticky="W")
SelectedFiles_ScrolledText = scrolledtext.ScrolledText(window, width=80, height=4, state=DISABLED)
SelectedFiles_ScrolledText.grid(column=0, row=4)

# Шаг 2: выбор формата
frame1 = Frame(window)
frame1.grid(column=0, row=5, sticky="W")
label_type_file_select = Label(frame1, text="Шаг 2. Сконвертируйте файлы в выбранный формат")
type_files = ("xlsx", "csv")
output_file_type = StringVar(value=type_files[0])
combobox_type = ttk.Combobox(frame1, textvariable=output_file_type, state="readonly", values=type_files)
label_type_file_select.pack(side="left", padx=5, pady=5)
#combobox_type.pack(side="right", padx=5, pady=5)

# Выбор библиотеки PDF (новый элемент)
frame_pdf = Frame(window)
frame_pdf.grid(column=0, row=5, pady=5, sticky="W")
frame1 = Frame(window)
frame1.grid(column=0, row=5, sticky="W")
Label(frame1, text="Формат:").pack(side="left", padx=5)
combobox_type = ttk.Combobox(frame1, textvariable=output_file_type, state="readonly", values=type_files, width=6)
combobox_type.pack(side="left", padx=5)

Label(frame1, text="PDF библиотека:").pack(side="left", padx=5)
pdf_libraries = ("pdfminer", "pypdf")
pdf_library = StringVar(value=pdf_libraries[0])
combobox_pdf = ttk.Combobox(frame1, textvariable=pdf_library, state="readonly", values=pdf_libraries, width=8)
combobox_pdf.pack(side="left", padx=5)

Button(window, text="Сконвертировать выбранные файлы", command=btn_convertFiles_clicked).grid(column=0, row=6)

Label(window, text='Созданные файлы:').grid(column=0, row=7, sticky="W")
created_excel_files_scrollText = scrolledtext.ScrolledText(window, width=80, height=4)
created_excel_files_scrollText.grid(column=0, row=8)

# Лог-панель (новый элемент)
Label(window, text='Лог выполнения:').grid(column=0, row=9, sticky="W")
log_scrolledtext = scrolledtext.ScrolledText(window, width=80, height=6, state=DISABLED)
log_scrolledtext.grid(column=0, row=10)

# Опции
Label(window, text="Опции:").grid(column=0, row=11, sticky="W")
leave_intermediate_txt_file = IntVar()
Checkbutton(window, text="Не удалять промежуточный текстовый файл", variable=leave_intermediate_txt_file).grid(row=12, sticky=W)

no_balance_check = IntVar()
Checkbutton(window, text="Игнорировать результаты сверки баланса", variable=no_balance_check).grid(row=13, sticky=W)

reversed_transaction_order = IntVar()
Checkbutton(window, text="Изменить порядок трансакций на обратный", variable=reversed_transaction_order).grid(row=14, sticky=W)


def main():
    # logging.getLogger('pdfminer').setLevel(logging.INFO)

    # root_logger = logging.getLogger()
    # root_logger.setLevel(logging.DEBUG)
    # # Adding file handler
    # file_handler = logging.FileHandler("sberbankPDF2ExcelGUI.log", encoding="utf-8")
    # # Creating formatter, which displays time, level, module name, line number and message
    # file_handler_formatter = logging.Formatter('%(levelname)s -%(name)s- %(module)s - %(lineno)d - %(funcName)s - %(message)s')

    # # Adding formatter to file handler
    # file_handler.setFormatter(file_handler_formatter)
    # root_logger.addHandler(file_handler)
    # logger = logging.getLogger(__name__)

    # logger.debug( "\n************** Starting  testing*******************")

    window.mainloop()

if __name__ == '__main__':
    main()
