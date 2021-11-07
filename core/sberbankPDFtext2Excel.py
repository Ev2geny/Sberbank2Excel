"""
Утилита для ковертации в Excel текстового файла, сгенерированного из PDF модулем pdf2txtev.py

*********************************************
при использовании из командной строки
*********************************************

запустить утилиту без аргументов и прочитать help


*********************************************
при использовании в качестве модуля
*********************************************
использовать функцию sberbankPDFtext2Excel()
"""

import sys
import os
import argparse

# importing own modules out of project
import pandas as pd

import utils
import extractors
import exceptions

from extractors_generic import determine_extractor_auto

def sberbankPDFtext2Excel(input_txt_file_name:str,
                          output_excel_file_name:str = None,
                          format = 'auto',
                          perform_balance_check = True) -> str:
    """
    Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF помощью конвертации Foxit PDF reader в Excel формат
    Если output_excel_file_name не задан, то он создаётся из input_txt_file_name путём замены расширения файла на xlsx
    """

    # creating output file name for Excel file, if not provided
    if not output_excel_file_name:
        pre, ext = os.path.splitext(input_txt_file_name)
        output_excel_file_name = pre+'.xlsx'

    # считываем входной файл в текст
    with open(input_txt_file_name, encoding="utf8") as file:
        file_text = file.read()

    extractor_type = None

    if format=='auto':
        extractor_type = determine_extractor_auto(file_text)
        print(r"Формат файла определён как " + extractor_type.__name__)

    else:
        for extractor in extractors.extractors_list:
            if extractor.__name__ == format:
                extractor_type = extractor
                break
        else:
            raise exceptions.UserInputError(f"Задан неизвестный формат {format}")

        print(r"Конвертируем файл как формат " + format)


    # in this case extractor_type is not a function, but a class
    # if you call it like this extractor_type() it returns an object with the type of extractor_type
    extractor = extractor_type(file_text)

    # extracting entries (operations) from big text to list of dictionaries
    individual_entries = extractor.get_entries()

    # converting list of dictionaries to pandas dataframe
    df = pd.DataFrame(individual_entries,
                      columns=extractor.get_columns_info().keys())

    # getting balance, written in the bank statement
    extracted_balance = extractor.get_period_balance()

    # checking, if balance, extracted from text file is equal to the balance, found by summing column in Pandas dataframe
    if perform_balance_check:
        utils.check_transactions_balance(input_pd=df,
                                         balance=extracted_balance,
                                         column_name_for_balance_calculation=extractor.get_column_name_for_balance_calculation())

    df = utils.rename_sort_df(df = df,
                              columns_info=extractor.get_columns_info())

    utils.write_df_to_excel(df, output_excel_file_name, extractor_name = extractor_type.__name__)


    # writer = pd.ExcelWriter(output_excel_file_name,
    #                         engine='xlsxwriter',
    #                         datetime_format='dd.mm.yyyy HH:MM')
    #
    # df.to_excel(writer, sheet_name='data', index=False)
    #
    # writer.save()
    # writer.close()

    print(f"Создан файл {output_excel_file_name}")

    return output_excel_file_name

# TODO: Add menu to be able to provide several arguments
def main():

    # print(extractors.get_list_extractors_in_text())

    parser = argparse.ArgumentParser(description='Конвертация выписки банка из текстового формата в формат Excel. Для конвертации в текстовый формат, нужно воспользоваться утилитой pdf2txtev')
    parser.add_argument('input_txt_file_name', type=str, help='Имя текстового файла для конвертации')
    parser.add_argument('-o','--output', type=str, default=None, dest='output_Excel_file_name', help='Имя файла в формате Excel, который будет создан')
    parser.add_argument('-b','--balcheck', action='store_false', default=True, dest='perform_balance_check', help='Не выполнять сверку баланса по трансакциям и в шапке выписки')
    parser.add_argument('-f', '--format', type=str,default='auto', dest='format', choices = extractors.get_list_extractors_in_text(),help = 'Формат выписки. Если не указан, определяется автоматически' )
    args = parser.parse_args()


    sberbankPDFtext2Excel(input_txt_file_name=args.input_txt_file_name,
                          output_excel_file_name = args.output_Excel_file_name,
                          format=args.format,
                          perform_balance_check = args.perform_balance_check)


if __name__=='__main__':
    main()