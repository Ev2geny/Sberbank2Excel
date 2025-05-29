"""
Графический интерфейс для для конвертации выписки Сбербанка по карте из формата PDF в формат Excel.
"""

# sources used:
# https://likegeeks.com/python-gui-examples-tkinter-tutorial/



from tkinter import *
import tkinter.filedialog
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox, ttk
import traceback
import sys
import logging

from .sberbankPDF2Excel import sberbankPDF2Excel
from . import version_info


# defining global variable, which will hold files tuple
files = ()
leave_intermediate_txt_file = 0
no_balance_check = 0
output_file_type = "xlsx"

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

    SelectedFiles_ScrolledText.configure(state=DISABLED)
    

def btn_convertFiles_clicked():
    """
    main function, which performs functionality by calling calls ProjectExpenditure2Excel.ProjectExpenditure2Excel(file)
     and converts file to Excel
    """
    # empty scrollText widget
    print("Версия "+version_info.VERSION)
    created_excel_files_scrollText.delete('1.0',END)

    qnt_files = len(files)
    qnt_files_converted = 0
    
    converted_file_name = ''
    
    for file in files:
        try:
            converted_file_name = sberbankPDF2Excel(file,
                                                    leave_intermediate_txt_file=leave_intermediate_txt_file.get(),
                                                    perform_balance_check=not no_balance_check.get(),
                                                    reversed_transaction_order=reversed_transaction_order.get(),
                                                    output_file_type=output_file_type.get())
            
            created_excel_files_scrollText.insert(INSERT,
                                        converted_file_name + '\n')
            
            qnt_files_converted = qnt_files_converted + 1         
        
        except:
            print(f"Произошла ошибка при конвертации файла {file} \n{sys.exc_info()[0]}")
            print(traceback.format_exc())
            print('Пропускаем конвертацию этого файла')
            

    if qnt_files == qnt_files_converted:
        print('Все файлы успешно сконвертированы')
    else:
        print(f'!!!!!!! {qnt_files-qnt_files_converted} файл(а) из {qnt_files} не были сконвертированы')

window = Tk()
menu = Menu(window)
help_about=Menu(menu)

def help_about_clicked():

    info_string = f'{version_info.NAME}\nВерсия={version_info.VERSION}\nАвтор={version_info.AUTHOR}\nГде скачать={version_info.PERMANENT_LOCATION}'
    print(info_string)
    messagebox.showinfo('', info_string)

help_about.add_command(label='About',command=help_about_clicked)

menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)
 
window.title(f'{version_info.NAME} Версия={version_info.VERSION}')
 
window.geometry('720x430')
 
Label(window, text="""
Шаг 1: Выберите один или несколько файлов в формате PDF
""",justify=LEFT).grid(column=0, row=0,sticky="W")
 
Button(window, text="Выбрать файлы", command=btn_selectFiles_clicked).grid(column=0, row=2)
 

Label(window, text='Выбранные файлы:').grid(column=0,row=3,sticky="W")
SelectedFiles_ScrolledText = scrolledtext.ScrolledText(window,width=80,height=4,state=DISABLED)
SelectedFiles_ScrolledText.grid(column=0,row=4)

frame = Frame(window)

frame.grid(column=0,row=5,sticky="W")

label_type_file_select = Label(frame, text="Шаг 2. Сконвертируйте файлы в выбранный формат")

type_files = ("xlsx", "csv")
output_file_type = StringVar()
output_file_type.set(type_files[0])
combobox = ttk.Combobox(frame, textvariable=output_file_type, state="readonly", values=type_files)

label_type_file_select.pack(side="left", padx=5, pady=5)
combobox.pack(side="right", padx=5, pady=5)

Button(window,text="Сконвертировать \n выбранные файлы", command=btn_convertFiles_clicked).grid(column=0,row=6)

Label(window, text='Созданные файлы в формате Excel:').grid(column=0,row=7,sticky="W")
created_excel_files_scrollText = scrolledtext.ScrolledText(window,width=80,height=4)
created_excel_files_scrollText.grid(column=0,row=8)

Label(window, text="Опции:").grid(column=0,row=9,sticky="W")
leave_intermediate_txt_file = IntVar()
Checkbutton(window, text="Не удалять промежуточный текстовый файл", variable=leave_intermediate_txt_file).grid(row=10, sticky=W)

no_balance_check = IntVar()
Checkbutton(window, text="Игнорировать результаты сверки баланса по трансакциям и в шапке выписки", variable=no_balance_check).grid(row=11, sticky=W)

reversed_transaction_order = IntVar()
Checkbutton(window, text="Изменить порядок трансакций на обратный", variable=reversed_transaction_order).grid(row=12, sticky=W)

if __name__ == '__main__':
    
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

