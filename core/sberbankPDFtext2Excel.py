"""
*********************************************
при использовании из командной строки
*********************************************

Программа для конфертации выписки по карте Сбербанка из формата Adobe PDF в формат Excel.

Программа не читает PDF файл непосредственно. Сначала надо скофертировать выписку Сбербанка в текстовый формат используя Foxit PDF reader



*********************************************
при использовании в качестве модуля
*********************************************
Надо использовать функцию sberbankPDFtext2Excel()
"""

import sys
import os

# importing own modules out of project
from core import utils

def sberbankPDFtext2Excel(input_txt_file_name:str,output_excel_file_name:str=None, format='auto') -> str:
    """
    Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF помощью конвертации Foxit PDF reader в Excel формат
    Если output_excel_file_name не задан, то он создаётся из input_txt_file_name путём замены расширения файла на xlsx
    """

    # creating output file name for Excel file, if not provided
    if not output_excel_file_name:
        pre, ext = os.path.splitext(input_txt_file_name)
        output_excel_file_name = pre+'.xlsx'

    # считываем входной файл в текст
    file = open(input_txt_file_name, encoding="utf8")
    file_text = file.read()
    file.close()

    if format=='auto':
        format = utils.detect_format(file_text)
        print(r"Формат файла определён как "+format)

    else:
        print(r"Конвертируем файл как формат "+format)

    # extracting entries (operations) from big text to list of dictionaries
    individual_entries = utils.split_text_on_entries(file_text, format= format)

    # converting list of dictionaries to pandas dataframe
    df = utils.entries_to_pandas(individual_entries, format= format)

    # calculating balance based on the data, extracted from the text file
    calculated_balance = utils.get_period_balance(file_text, format= format)

    # checking, if balance, extracted from text file is equal to the balance, found by summing column in Pandas dataframe
    utils.check_transactions_balance(df, calculated_balance)

    # Defining header in Russian.  
    russian_headers = [
        'Дата операции',
        'дата обработки',
        'код авторизации',
        'Описание операции',
        'категория',
        'Сумма в валюте счёта',
        'cумма в валюте операции',
        'валюта операции',
        'Остаток по счёту в валюте счёта']
   
    # Сохраняем pandas в Excel
    utils.pd_to_Excel(df, russian_headers, output_excel_file_name)

    return output_excel_file_name

# TODO: Add menu to be able to provide several arguments
def main():
    if len(sys.argv) < 2:
        print('Недостаточно аргументов')
        print(__doc__)
        return None
    
    elif len(sys.argv)==2:
        outputFileName = None

    elif len(sys.argv)==3:
        outputFileName=sys.argv[2]

    sberbankPDFtext2Excel(sys.argv[1], outputFileName)


if __name__=='__main__':
    main()