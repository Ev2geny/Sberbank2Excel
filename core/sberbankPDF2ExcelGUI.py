"""
Графический интерфейс для для конвертации выписки Сбербанка по карте из формата PDF в формат Excel.
"""

# sources used:
# https://likegeeks.com/python-gui-examples-tkinter-tutorial/


import tkinter as tk
# Not sure, whay this is needed, seems to be a bug in tkinter https://stackoverflow.com/a/72321743
from tkinter import scrolledtext, ttk, filedialog, messagebox
# from tkinter import Menu
# from tkinter import ttk
import traceback
import sys
# import logging

from sberbankPDF2Excel import sberbankPDF2Excel
import version_info

WIDTH = 100 

# defining global variable, which will hold files tuple
files = ()
leave_intermediate_txt_file = 0
no_balance_check = 0


# *************  GUI logic *************

def btn_select_files_clicked():
    global files

    files = tk.filedialog.askopenfilenames(parent=window,
                                                title='Выберете файл(ы)',
                                                filetypes =(("PDF файл", "*.pdf"),("All Files","*.*")) )

    SelectedFiles_ScrolledText.configure(state=tk.NORMAL)
    # empty scrollText widget
    SelectedFiles_ScrolledText.delete('1.0', tk.END)
    created_excel_files_scrollText.delete('1.0', tk.END)

    # Populating SelectedFiles_ScrolledText widget
    for file in files:
        SelectedFiles_ScrolledText.insert(tk.INSERT, file+'\n')

    SelectedFiles_ScrolledText.configure(state=tk.DISABLED)
    

def btn_convert_files_clicked():
    """
    main function, which performs functionality by calling calls ProjectExpenditure2Excel.ProjectExpenditure2Excel(file)
     and converts file to Excel
    """
    # empty scrollText widget
    print(f"Версия {version_info.VERSION}")
    created_excel_files_scrollText.delete('1.0',tk.END)

    qntFiles=len(files)
    qntFilesConverted=0
    for file in files:
        try:
            created_file_name = sberbankPDF2Excel(file,
                                                leave_intermediate_txt_file = leave_intermediate_txt_file.get(),
                                                perform_balance_check = not no_balance_check.get() )
            
            created_excel_files_scrollText.insert(tk.INSERT,
                                                  created_file_name + '\n')
            qntFilesConverted=qntFilesConverted + 1
        except:
            print(f'Произошла ошибка при конвертации файла {file} {sys.exc_info()[0]}')
            print(traceback.format_exc())
            print('Пропускаем конвертацию этого файла')

    
    if qntFiles==qntFilesConverted:
        print('Все файлы успешно сконвертированы')
    else:
        print(f'!!!!!!! {qntFiles-qntFilesConverted} файл(а) из {qntFiles} не были сконвертированы')
        
def btn_output_folder_clicked():
    global output_folder_txt
    folder = tk.filedialog.askdirectory(parent=window,
                                                title='Выберете папку для сохранения файлов')
    
    output_folder_txt.delete(1.0, tk.END)
    output_folder_txt.insert(tk.END, folder)

def help_about_clicked():

    info_string = f'{version_info.NAME}\nВерсия={version_info.VERSION}\nАвтор={version_info.AUTHOR}\nГде скачать={version_info.PERMANENT_LOCATION}'
    print(info_string)
    tk.messagebox.showinfo('', info_string)



# *************  GUI  *************


window = tk.Tk()
menu = tk.Menu(window)
help_about=tk.Menu(menu)

help_about.add_command(label='About',command=help_about_clicked)

menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)
 
window.title(f'{version_info.NAME} Версия={version_info.VERSION}')
 
window.geometry('850x540')
 
tk.Label(window, text="""
Шаг 1: Выберите один или несколько файлов в формате PDF
""",justify=tk.LEFT).grid(column=0, row=0,sticky="W")
 
tk.Button(window, text="Выбрать файлы", command=btn_select_files_clicked).grid(column=0, row=2)
 

tk.Label(window, text='Выбранные файлы:').grid(column=0,row=3,sticky="W")
SelectedFiles_ScrolledText = tk.scrolledtext.ScrolledText(window,width=WIDTH,height=4,state=tk.DISABLED)
SelectedFiles_ScrolledText.grid(column=0,row=4)

tk.Label(window, text="Шаг 2. Сконвертируйте файлы в формат Excel").grid(column=0,row=5,sticky="W")

tk.Button(window,text="Сконвертировать \n выбранные файлы", command=btn_convert_files_clicked).grid(column=0,row=6)

tk.Label(window, text='Созданные файлы в формате Excel:').grid(column=0,row=7,sticky="W")
created_excel_files_scrollText = tk.scrolledtext.ScrolledText(window,width=WIDTH,height=4)
created_excel_files_scrollText.grid(column=0,row=8)

# Label(window, text="\n").grid(column=0,row=9,sticky="W" )

window.rowconfigure(9, minsize=2)
# separator = ttk.Separator(window, orient='horizontal')
separator = tk.ttk.Frame(window, relief='raised', height=8)
separator.grid(column=0,row=9,sticky="WE", rowspan=1, pady=20)

tk.Label(window, text="Опции:").grid(column=0,row=10,sticky="W" )
leave_intermediate_txt_file = tk.IntVar()
tk.Checkbutton(window, text="Не удалять промежуточный текстовый файл", variable=leave_intermediate_txt_file).grid(row=11, sticky='W')

no_balance_check = tk.IntVar()
tk.Checkbutton(window, text="Игнорировать результаты сверки баланса по трансакциям и в шапке выписки", variable=no_balance_check).grid(row=12, sticky='W')

reversed_transaction_order = tk.IntVar()
tk.Checkbutton(window, text="Изменить порядок трансакций на обратный", variable=reversed_transaction_order).grid(row=13, sticky='W')

tk.Label(window, text='Папка для созданных файлов Excel:').grid(column=0,row=14,sticky="W")
output_folder_txt = tk.Text(window,width=WIDTH, height=1)
output_folder_txt.grid(column=0,row=15)
# output_folder_txt.pack()
tk.Button(window,text="Найти папку", command=btn_output_folder_clicked).grid(column=0,row=16)

window.mainloop()

