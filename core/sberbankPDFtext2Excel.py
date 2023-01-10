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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def sberbankPDFtext2Excel(input_txt_file_name:str,
                          output_file_name:str = None,
                          format = 'auto',
                          perform_balance_check = True,
                          output_file_type='xlsx') -> str:
    """
    Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF в Excel или CSV форматы
    Если output_file_name не задан, то он создаётся из input_txt_file_name путём удаления расширения
    return: file name of the created file
    """

    # creating output file name for Excel file, if not provided
    if not output_file_name:
        pre, ext = os.path.splitext(input_txt_file_name)
        output_file_name = pre

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

    error = ""

    try:
        utils.check_transactions_balance(input_pd=df,
                                         balance=extracted_balance,
                                         column_name_for_balance_calculation=extractor.get_column_name_for_balance_calculation())

    except exceptions.BalanceVerificationError as e:
        if perform_balance_check:
            raise
        else:
            print(bcolors.FAIL + str(e) + bcolors.ENDC)
            error = str(e)


    df = utils.rename_sort_df(df = df,
                              columns_info=extractor.get_columns_info())

    utils.write_df_to_file(df, output_file_name,
                            extractor_name = extractor_type.__name__,
                            errors=error,
                            output_file_format=output_file_type)


    # writer = pd.ExcelWriter(output_excel_file_name,
    #                         engine='xlsxwriter',
    #                         datetime_format='dd.mm.yyyy HH:MM')
    #
    # df.to_excel(writer, sheet_name='data', index=False)
    #
    # writer.save()
    # writer.close()

    # print(f"Создан файл {output_file_name}")

    return output_file_name

def genarate_PDFtext2Excel_argparser()->argparse.ArgumentParser:
    """
    The function generates the argparser object. It is used in this module and later on as a parent in other module
    """
    
    # parser = argparse.ArgumentParser(description='Конвертация выписки банка из текстового формата в формат Excel или CSV. Для конвертации в текстовый формат, нужно воспользоваться утилитой pdf2txtev')
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('input_file_name', type=str, help='Файла для конвертации')
    parser.add_argument('-o','--output', type=str, default=None, dest='output_Excel_file_name', help='Имя файла (без расшмрения) который будет создан в формате Excel или CSV')
    parser.add_argument('-b','--balcheck', action='store_false', default=True, dest='perform_balance_check', help='Игнорировать результаты сверки баланса по транзакциям и в шапке выписки')
    parser.add_argument('-f', '--format', type=str,default='auto', dest='format', choices = extractors.get_list_extractors_in_text(),help = 'Формат выписки. Если не указан, определяется автоматически' )
    parser.add_argument('-t', '--type', type=str,default='xlsx', dest='output_file_type', choices = ["xlsx","csv"],help = 'Тип создаваемого файла' )

    return parser

def main():

    # print(extractors.get_list_extractors_in_text())
    parser = argparse.ArgumentParser(description='Конвертация выписки банка из текстового формата в формат Excel или CSV',
                                     parents=[genarate_PDFtext2Excel_argparser()])
    args = parser.parse_args()

    print(args)

    sberbankPDFtext2Excel(input_txt_file_name=args.input_file_name,
                          output_file_name = args.output_Excel_file_name,
                          format=args.format,
                          perform_balance_check = args.perform_balance_check,
                          output_file_type=args.output_file_type)


if __name__=='__main__':
    main()