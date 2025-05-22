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
import logging

# importing own modules out of project
import pandas as pd

from .extractor import Extractor
from . import utils
from . import extractors
from . import exceptions

from .extractors_generic import determine_extractor_auto

logger = logging.getLogger()
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


def sberbankPDFtext2Excel(input_txt_file_name: str,
                          output_file_name: str | None = None,
                          format='auto',
                          perform_balance_check=True,
                          output_file_type='xlsx',
                          reversed_transaction_order=False) -> str:
    """ Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF в Excel или CSV форматы
        Если output_file_name не задан, то он создаётся из input_txt_file_name путём удаления расширения

    Args:
        input_txt_file_name (str): имя входного текстового файла
        output_file_name (str, optional): имя выходного файла. Defaults to None.
        format (str, optional): формат входного файла. Defaults to 'auto'.
        perform_balance_check (bool, optional): Проводить сверку баланса по трансакциям и по шапке. Defaults to True.
        output_file_type (str, optional): Тип выходного файла. Defaults to 'xlsx'.
        reversed_transaction_order (bool, optional): Изменить порядок трансакций на обратный. Defaults to False.

    Raises:
        exceptions.UserInputError: 

    Returns:
        str: file name of the created file
    """
    
    logger.debug(f"reversed_transaction_order = {reversed_transaction_order}")

    # creating output file name for Excel file, if not provided
    if not output_file_name:
        pre, ext = os.path.splitext(input_txt_file_name)
        output_file_name = pre

    # считываем входной файл в текст
    with open(input_txt_file_name, encoding="utf8") as file:
        file_text = file.read()

    extractor_type: type

    if format=='auto':
        extractor_type = determine_extractor_auto(file_text)
        print(r"Формат файла определён как " + extractor_type.__name__)

    # checking whether format is one of the known formats
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
    actual_extractor: Extractor = extractor_type(file_text)

    # extracting entries (operations) from big text to list of dictionaries
    individual_entries = actual_extractor.get_entries()

    # converting list of dictionaries to pandas dataframe
    df = pd.DataFrame(data = individual_entries,
                      columns=actual_extractor.get_columns_info().keys())
    
    logger.debug(f"Dataframe created from text file {input_txt_file_name}")
    logger.debug(df)

    # getting balance, written in the bank statement
    extracted_balance = actual_extractor.get_period_balance()

    # checking, if balance, extracted from text file is equal to the balance, found by summing column in Pandas dataframe

    error = ""

    try:
        utils.check_transactions_balance(input_pd=df,
                                         balance=extracted_balance,
                                         column_name_for_balance_calculation=actual_extractor.get_column_name_for_balance_calculation())

    except exceptions.BalanceVerificationError as e:
        if perform_balance_check:
            raise
        else:
            print(bcolors.FAIL + str(e) + bcolors.ENDC)
            error = str(e)


    df = utils.rename_sort_df(df = df,
                              columns_info=actual_extractor.get_columns_info())
    
    if reversed_transaction_order:
        df = df.iloc[::-1]  # reversing the order of transactions

    utils.write_df_to_file(df, output_file_name,
                            extractor_name=extractor_type.__name__,
                            errors=error,
                            output_file_format=output_file_type)

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
    parser.add_argument('-r', '--reverse', action='store_true', default=False, dest='reversed_transaction_order', help='Изменить порядок транзакций на обратный')

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
                          output_file_type=args.output_file_type,
                          reversed_transaction_order=args.reversed_transaction_order)


if __name__=='__main__':
    # root_logger = logging.getLogger()
    # root_logger.setLevel(logging.DEBUG)
    # # Adding file handler
    # file_handler = logging.FileHandler("sberbankPDFtext2Excel.log", encoding="utf-8")
    # # Creating formatter, which displays time, level, module name, line number and message
    # file_handler_formatter = logging.Formatter('%(levelname)s -%(name)s- %(module)s - %(lineno)d - %(funcName)s - %(message)s')
    
    # # Adding formatter to file handler
    # file_handler.setFormatter(file_handler_formatter)
    # root_logger.addHandler(file_handler)
    # logger = logging.getLogger(__name__)

    # logger.debug( "\n************** Starting  testing*******************")
    
    main()