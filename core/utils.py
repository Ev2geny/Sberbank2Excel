#coding=utf-8
'''
Разные отдельностоящие функции, которые используются в других модулях
'''

import unidecode
import re
import pandas as pd
from typing import *

import exceptions
import version_info

def get_float_from_money(money_str: str, process_no_sign_as_negative=False) -> float:
    """
    Converts string, representing money to a float.
    If process_no_sign_as_negative is set to True, then a number will be negative in case no leading sign is available

    Example:
    get_float_from_money('1 189,40', True) -> -1189.4
    """
    
    money_str = unidecode.unidecode(money_str)
    # избавляемся от пробелов
    money_str = money_str.replace(' ','')
    # заменяем запятую на точку
    money_str = money_str.replace(',','.')

    leading_plus = False
    if money_str[0] == '+':
        leading_plus = True

    money_float = float(money_str)

    if (process_no_sign_as_negative and not leading_plus):
        money_float = -1*money_float

    return money_float

def split_Sberbank_line(line:str)->List[str]:
    """
    Разделяем Сбербанковсую строчку на кусочки данных. Разделяем используя symbol TAB
    """
    line_parts=re.split(r'\t',line)
    line_parts=list(filter(None,line_parts))
    return line_parts

def rename_sort_df(df:pd.DataFrame, columns_info:dict)->pd.DataFrame:

    # Reordering columns to follow the order of the keys in the columns_info
    df=df[list(columns_info.keys())]

    # renaming columns
    df = df.rename(columns = columns_info)
    return df

def check_transactions_balance(input_pd: pd.DataFrame, balance: float, column_name_for_balance_calculation:str)->None:
    """
    сравниваем вычисленный баланс периода (get_period_balance) и баланс периода, полученный сложением всех трансакций в
    pandas dataframe.

    Если разница одна копейка или больше, то выдаётся ошибка
    """
    calculated_balance = input_pd[column_name_for_balance_calculation].sum()
    if (abs(balance-calculated_balance) >= 0.01):
        raise exceptions.BalanceVerificationError(f"""
            Ошибка проверки балланса по трансакциям: 
                Вычисленный баланс по информации в шапке выписки = {balance}
                Вычисленный баланс по всем трансакциям = {calculated_balance}
        """)

def write_df_to_excel(df:pd.DataFrame, filename:str, extractor_name:str, errors:str = ""):
    """

    """

    global version_info

    writer = pd.ExcelWriter(filename,
                            engine='xlsxwriter',
                            datetime_format='dd.mm.yyyy HH:MM')

    df.to_excel(writer, sheet_name='data', index=False)

    workbook = writer.book
    info_worksheet = workbook.add_worksheet('Info')

    info_worksheet.write('A3', f'Файл создан утилитой "{version_info.NAME}", доступной для скачивания по ссылке {version_info.PERMANENT_LOCATION}')
    info_worksheet.write('A4', f'Версия утилиты "{version_info.VERSION}"')
    info_worksheet.write('A5', f'Для выделения информации был использован экстрактор типа "{extractor_name}"')
    info_worksheet.write('A6', f'Ошибки при конвертации: "{errors}"')

    writer.save()

def main():
    print('this module is not designed to work standalone')

if __name__=='__main__':
    main()
    
        
    
    
    


