"""
Утилита для конвертации выписки Сбербанка по карте из формата PDF в формат Excel.
Для использования утилиты сначала надо сконвертировать выписку PDF в текстовый формат используя 

foxit PDF reader  https://www.foxitsoftware.com/pdf-reader/
"""


NAME='Конвертер выписки Сбербанка из PDF в Excel'
AUTHOR='ev2geny@gmail.com'
PERMANENT_LOCATION='https://github.com/Ev2geny/Sberbank2Excel/releases/latest'
VERSION='1.3'


# sources used:
# https://likegeeks.com/python-gui-examples-tkinter-tutorial/



from tkinter import *
import tkinter.filedialog
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox
import traceback
import logging

from core import sberbankPDFtext2Excel



# defining global variable, which will hold files tuple
files = ()


def btn_selectFiles_clicked():
    global files

    files = tkinter.filedialog.askopenfilenames(parent=window,title='Выберете файл(ы)',filetypes =(("Текстовый файл", "*.txt"),("All Files","*.*")) ) 

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
    main function, which performs functionality by calling calls ProjectExpenditure2Excel.ProjectExpenditure2Excel(file) and converts file to Excel
    """
    # empty scrollText widget
    created_excel_files_scrollText.delete('1.0',END)

    qntFiles=len(files)
    qntFilesConverted=0
    for file in files:
        try:
            created_excel_files_scrollText.insert(INSERT, sberbankPDFtext2Excel.sberbankPDFtext2Excel(file) + '\n')
            qntFilesConverted=qntFilesConverted+1
        except:
            print('Error occured, when converting file "'+'file'+'" '+ str(sys.exc_info()[0]))
            print(traceback.format_exc())
            print('Skipping this file conversion')

    
    if qntFiles==qntFilesConverted:
        print('Все файлы успешно сконвертированы')
    else:
        print(f'!!!!!!! {qntFiles-qntFilesConverted} файл(а) из {qntFiles} не были сконвертированы')

window = Tk()
menu = Menu(window)
help_about=Menu(menu)

def help_about_clicked():

    messagebox.showinfo('',f'{NAME}\nВерсия={VERSION}\nАвтор={AUTHOR}\nГде скачать={PERMANENT_LOCATION}\n{__doc__}')

help_about.add_command(label='About',command=help_about_clicked)

menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)
 
window.title(f'{NAME} Версия={VERSION}')
 
window.geometry('600x380')
 
Label(window, text="""
Шаг 1: Сконвертируйты выписку по карте Сбербанка из формата PDF
        в текстовый формат, использую foxit PDF reader 
        https://www.foxitsoftware.com/pdf-reader/ 

Шаг 2: Выберите один или несколько сконвертированных текстовых файлов
""",justify=LEFT).grid(column=0, row=0,sticky="W")
 
Button(window, text="Выбрать файлы", command=btn_selectFiles_clicked).grid(column=0, row=2)
 

Label(window, text='Выбранные файлы:').grid(column=0,row=3,sticky="W")
SelectedFiles_ScrolledText = scrolledtext.ScrolledText(window,width=60,height=4,state=DISABLED)
SelectedFiles_ScrolledText.grid(column=0,row=4)

Label(window, text="Шаг 3. Сконвертируйте файлы в формат Excel").grid(column=0,row=5,sticky="W")

Button(window,text="Сконвертировать \n выбранные файлы", command=btn_convertFiles_clicked).grid(column=0,row=6)

Label(window, text='Созданные файлы в формате Excel:').grid(column=0,row=7,sticky="W")
created_excel_files_scrollText = scrolledtext.ScrolledText(window,width=60,height=4)
created_excel_files_scrollText.grid(column=0,row=8)
 
window.mainloop()

