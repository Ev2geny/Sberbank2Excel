#coding=utf-8
'''
Разные отдельностоящие функции, которые используются в других модулях
'''

import unidecode
import re
import pandas as pd
import logging
from pprint import pprint

from typing import *

from core import exceptions



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
    Разделяем Сбербанковсую строчку на кусочки данных. Разделяем используя пять пробелов в качестве разделителя
    """
    line_parts=re.split(r'\s\s\s\s\s',line)
    line_parts=list(filter(None,line_parts))
    return line_parts

#************ split_text_on_entries

def split_text_on_entries_2005_Moscow(PDF_text:str)->List[str]:
    """
    разделяет текстовый файл на отдельные записи

    пример одной записи
    ---------------------------------------------------------------------------------------------------------
    29.08.2019 10:04     GETT     1 189,40     8 087,13
    29.08.2019 / 278484     Отдых и развлечения
    ----------------------------------------------------------------------------------------------------------

    ещё один пример (с 3 линиями)
    ---------------------------------------------------------------------------------------------------------
    26.07.2019 02:04      ПЛАТА ЗА ОБСЛУЖИВАНИЕ БАНКОВСКОЙ     750,00     -750,00
    КАРТЫ  (ЗА ПЕРВЫЙ ГОД)
    05.08.2019 / -     Прочие операции
    ---------------------------------------------------------------------------------------------------------

    """
    # extracting entries (operations) from text file on
    individual_entries=re.findall(r"""
    \d\d\.\d\d\.\d\d\d\d\s\d\d:\d\d               # Date and time like 25.04.1991 18:31                                        
    [\s\S]*?                                      # any character, including new line. !!None-greedy!! See URL why [\s\S] is used https://stackoverflow.com/a/33312193
    \d\d\.\d\d\.\d\d\d\d\s/                       # date with forward stash like '25.12.2019 /' 
    .*?\n                                         # everything till end of the line
    """,
    PDF_text, re.VERBOSE)

    if len(individual_entries) == 0:
        raise exceptions.InputFileStructureError("Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

    return individual_entries

def split_text_on_entries_2107_Stavropol(PDF_text:str)->List[str]:
    """
    разделяет текстовый файл формата 2107_Stavropol на отдельные записи

    пример одной записи
------------------------------------------------------------------------------------------------------
    03.07.2021     12:52     Перевод с карты     3 500,00     28 655,30
    03.07.2021     123456     SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
------------------------------------------------------------------------------------------------------

    ещё один пример (с 3 линиями)
    ---------------------------------------------------------------------------------------------------------
    03.07.2021     11:54     Перевод с карты     4 720,00     45 155,30
    03.07.2021     258077     SBOL перевод 1234****5678 А. ВАЛЕРИЯ
    ИГОРЕВНА
    ----------------------------------------------------------------------------------------------------------

    """
    # extracting entries (operations) from text file on
    individual_entries=re.findall(r"""
    \d\d\.\d\d\.\d\d\d\d\s{5}\d\d:\d\d                                            # Date and time like '06.07.2021     15:46'                                        
    .*?\n                                                                         # Anything till end of the line including a line break
    \d\d\.\d\d\.\d\d\d\d\s{5}\d{3,8}                                              # дата обработки и через 5 пробелов код авторизации. Код авторизациии который я видел всегда состоит и 6 цифр, но на всякий случай укажим с 3 до 8
    [\s\S]*?                                                                      # any character, including new line. !!None-greedy!!
    (?=Продолжение\sна\sследующей\sстранице|\d\d\.\d\d\.\d\d\d\d\s{5}\d\d:\d\d)   # lookahead at the end of the page or a start of a next transaction
    """,
    PDF_text, re.VERBOSE)

    if len(individual_entries) == 0:
        raise exceptions.InputFileStructureError("Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

    return individual_entries

def split_text_on_entries(PDF_text:str, format:str='2005_Moscow')->List[str]:
    format_dependent_func={'2005_Moscow':split_text_on_entries_2005_Moscow,
                           '2107_Stavropol':split_text_on_entries_2107_Stavropol}

    return format_dependent_func[format](PDF_text)

#************ split_text_on_entries END

#************ decompose_entry_to_dict

def decompose_entry_to_dict_2005_Moscow(entry:str)-> Dict:
    """
    Выделяем данные из одной записи в dictionary

    пример одной записи
    ---------------------------------------------------------------------------------------------------------
    29.08.2019 10:04     GETT     1 189,40     8 087,13
    29.08.2019 / 278484     Отдых и развлечения
    ----------------------------------------------------------------------------------------------------------

    ещё один пример (с 3 линиями)
    ---------------------------------------------------------------------------------------------------------
    26.07.2019 02:04      ПЛАТА ЗА ОБСЛУЖИВАНИЕ БАНКОВСКОЙ     750,00     -750,00
    КАРТЫ  (ЗА ПЕРВЫЙ ГОД)
    05.08.2019 / -     Прочие операции
    ---------------------------------------------------------------------------------------------------------
    В этом примере:

    result['operation_date'] = '26.07.2019 02:04'
    result['description'] = 'ПЛАТА ЗА ОБСЛУЖИВАНИЕ БАНКОВСКОЙ КАРТЫ  (ЗА ПЕРВЫЙ ГОД)'
    result['value_account_currency'] = -750.00
    result['remainder_account_currency'] = - 750.00
    result['processing_date'] = '05.08.2019'
    result['authorisation_code'] = '-'
    """
    lines=entry.split('\n')
    lines=list(filter(None,lines))

    result={}
    #************** looking at the 1st line
    line_parts=split_Sberbank_line(lines[0])
    result['operation_date']=line_parts[0]
    result['description']=line_parts[1]
    result['value_account_currency']=get_float_from_money(line_parts[2],True)
    result['remainder_account_currency']=get_float_from_money(line_parts[3])

    #************* looking at lines between 1st and the last
    sublines=lines[1:-1]
    for line in sublines:
        line_parts=split_Sberbank_line(line)
        if len(line_parts)!=1:
            raise exceptions.SberbankPDFtext2ExcelError("Line is expected to have only one part :" + line)
        result['description']=result['description']+' '+line_parts[0]

    #************* looking at the last line
    line_parts=split_Sberbank_line(lines[-1])

    if len(line_parts) <2 or len(line_parts)>3:
        raise exceptions.SberbankPDFtext2ExcelError("Line is expected to 2 or parts :" + line)

    result['processing_date']=line_parts[0][0:10]
    result['authorisation_code']=line_parts[0][13:]
    result['category']=line_parts[1]

    if len(line_parts)==3:
        found=re.search(r'[(](.*?)(\w\w\w)[)]',line_parts[2])  #processing string like (33,31 EUR)
        if found:
            result['value_operational_currency']=get_float_from_money(found.group(1),True)
            result['operational_currency']=found.group(2)
        else:
            raise exceptions.InputFileStructureError("Ошибка в обработке текста. Ожидалась струтура типа (33,31 EUR), получено: " + line)

    return result

def decompose_entry_to_dict_2107_Stavropol(entry:str)-> Dict:
    """
    Выделяем данные из одной записи в dictionary

    ------------------------------------------------------------------------------------------------------
    03.07.2021     12:52     Перевод с карты     3 500,00     28 655,30
    03.07.2021     123456     SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
------------------------------------------------------------------------------------------------------

    ещё один пример (с 3 линиями)
    ---------------------------------------------------------------------------------------------------------
    03.07.2021     11:54     Перевод с карты     4 720,00     45 155,30
    03.07.2021     258077     SBOL перевод 1234****5678 А. ВАЛЕРИЯ
    ИГОРЕВНА
    ----------------------------------------------------------------------------------------------------------

    В этом примере:

{'authorisation_code': '258077',
 'category': 'Перевод с карты',
 'description': 'BOL перевод 1234****5678 А. ВАЛЕРИЯ ИГОРЕВНА',
 'operation_date': '03.07.2021 11:54',
 'processing_date': '03.07.2021',
 'remainder_account_currency': 45155.30,
 'value_account_currency': -4720.00}
    """
    lines=entry.split('\n')
    lines=list(filter(None,lines))

    if len(lines) <2 or len(lines) >3:
        raise exceptions.InputFileStructureError("entry is expected to have from 2 to 3 lines\n" + str(entry))

    result={}
    #************** looking at the 1st line
    line_parts=split_Sberbank_line(lines[0])
    result['operation_date']=line_parts[0]+" "+line_parts[1]
    result['category']=line_parts[2]
    result['value_account_currency']=get_float_from_money(line_parts[3],True)
    result['remainder_account_currency']=get_float_from_money(line_parts[4])

    # ************** looking at the 2nd line
    line_parts = split_Sberbank_line(lines[1])

    if len(line_parts) <3 or len(line_parts)>4:
        raise exceptions.SberbankPDFtext2ExcelError("Line is expected to 3 or 4 parts :" + str(lines[1]))

    result['processing_date']=line_parts[0]
    result['authorisation_code']=line_parts[1]
    result['description']=line_parts[2]

    # TODO: Ev2geny добавить выделение суммы в валюте операции

    # ************** looking at the 3rd line
    if len(lines) == 3:
        line_parts = split_Sberbank_line(lines[2])
        result['description'] = result['description']+' '+line_parts[0]

    return result

def decompose_entry_to_dict(entry:str, format:str='2005_Moscow')-> Dict:
    format_dependent_func={'2005_Moscow':decompose_entry_to_dict_2005_Moscow,
                           '2107_Stavropol':decompose_entry_to_dict_2107_Stavropol}

    return format_dependent_func[format](entry)

#************ decompose_entry_to_dict END

def entries_to_pandas(individual_entries:List[str], format:str='2005_Moscow')->pd.DataFrame:

    """
    converting list of individual entries to pandas dataframe
    """
    df=pd.DataFrame(columns=['operation_date',
                             'processing_date',
                             'authorisation_code',
                             'description',
                             'category',
                             'value_account_currency',
                             'value_operational_currency',
                             'operational_currency',
                             'remainder_account_currency'])

    for entry in individual_entries:

        dict_result=decompose_entry_to_dict(entry, format)

        # print(result)
        df=df.append(dict_result,ignore_index=True)

    # convert to date https://stackoverflow.com/questions/41514173/change-multiple-columns-in-pandas-dataframe-to-datetime
    # strftime() and strptime() Format Codes   https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    df['operation_date']=pd.to_datetime(df['operation_date'], format="%d.%m.%Y %H:%M")
    df['processing_date']=pd.to_datetime(df['processing_date'], format="%d.%m.%Y")

    return df

def pd_to_Excel(pd_dataframe:pd.DataFrame,russian_headers:List[str],output_Excel_file_name:str):
    
    # Saving pandas dataframe to Excel
    writer = pd.ExcelWriter(output_Excel_file_name,
                            engine='xlsxwriter',
                            datetime_format='dd.mm.yyyy HH:MM')
    
    pd_dataframe.to_excel(writer,header=russian_headers,sheet_name='Sheet1',index=False)
    
    writer.close()

#************ get_period_balance

def get_period_balance_2005_Moscow(PDF_text: str) -> float:
    """
    функция ищет в тексте значения "СУММА ПОПОЛНЕНИЙ" и "СУММА СПИСАНИЙ" и возвращает раницу
    используется для контрольной проверки вычислений

    :param PDF_text:
    :return:
    """

    if( res:= re.search(r'СУММА ПОПОЛНЕНИЙ\s{5}(\d[\d\s]*\,\d\d)', PDF_text, re.MULTILINE) ):
        summa_popolneniy = res.group(1)
    else:
        raise exceptions.InputFileStructureError('Не найдено значение "СУММА ПОПОЛНЕНИЙ"')

    if( res:= re.search(r'СУММА СПИСАНИЙ\s{5}(\d[\d\s]*\,\d\d)', PDF_text, re.MULTILINE) ):
        summa_spisaniy = res.group(1)
    else:
        raise exceptions.InputFileStructureError('Не найдено значение "СУММА СПИСАНИЙ "')

    summa_popolneniy = get_float_from_money(summa_popolneniy)
    summa_spisaniy = get_float_from_money(summa_spisaniy)

    return summa_popolneniy - summa_spisaniy

def get_period_balance_2107_Stavropol(PDF_text: str) -> float:
    """
    функция ищет в тексте значения "ВСЕГО СПИСАНИЙ" и "ВСЕГО ПОПОЛНЕНИЙ" и возвращает разницу
    используется для контрольной проверки вычислений

    Пример текста
    ----------------------------------------------------------
    ОСТАТОК НА 30.06.2021     ОСТАТОК НА 06.07.2021     ВСЕГО СПИСАНИЙ     ВСЕГО ПОПОЛНЕНИЙ
    28 542,83     12 064,34     248 822,49     232 344,00
    ----------------------------------------------------------

    :param PDF_text:
    :return:
    """

    res= re.search(r'ОСТАТОК НА.*(?=Расшифровка операций)',PDF_text, re.MULTILINE|re.DOTALL)
    if not res:
        raise exceptions.InputFileStructureError('Не найдена структура с остатками и пополнениями')

    lines = res.group(0).split('\n')

    line_parts = split_Sberbank_line(lines[1])

    # print(lines)

    lines = list(filter(None,lines))

    summa_spisaniy = line_parts[2]
    summa_popolneniy = line_parts[3]

    # print('summa_spisaniy ='+summa_spisaniy)
    # print('summa_popolneniy =' + summa_popolneniy)

    summa_popolneniy = get_float_from_money(summa_popolneniy)
    summa_spisaniy = get_float_from_money(summa_spisaniy)

    return summa_popolneniy - summa_spisaniy

def get_period_balance(PDF_text: str, format:str='2005_Moscow') -> float:
    format_dependent_func={'2005_Moscow':get_period_balance_2005_Moscow,
                           '2107_Stavropol':get_period_balance_2107_Stavropol}

    return format_dependent_func[format](PDF_text)


#************ get_period_balance END

def check_transactions_balance(input_pd: pd.DataFrame, balance: float):
    """
    сравниваем вычисленный баланс периода (get_period_balance) и баланс периода, полученный сложением всех трансакций в
    pandas dataframe.

    Если разница одна копейка или больше, то выдаётся ошибка
    """
    calculated_balance = input_pd['value_account_currency'].sum()
    if (abs(balance-calculated_balance) >= 0.01):
        raise exceptions.BalanceVerificationError(f"""
            Ошибка проверки балланса по трансакциям: 
                СУММА НАЧИСЛЕНИЙ - СУММА СПИСАНИЙ = {balance}
                Вычисленный баланс по всем трансакциям = {calculated_balance}
        """)

def detect_format(PDF_text: str)->str:
    """
    Function detects format of the pdf file, converted to txt
    If no known format is detected, an exception will be raised
    """
    pdf_format=set()

    try:
        get_period_balance_2005_Moscow(PDF_text)
        pdf_format.add("2005_Moscow")
    except exceptions.InputFileStructureError:
        pass

    try:
        get_period_balance_2107_Stavropol(PDF_text)
        pdf_format.add("2107_Stavropol")
    except exceptions.InputFileStructureError:
        pass

    # As a result we shall have excetly one dected format
    if len(pdf_format) != 1:
        raise exceptions.InputFileStructureError("Неизвестная структура файла")

    return pdf_format.pop()





def main():
    print('this module is not designed to work standalone')

if __name__=='__main__':
    main()
    
        
    
    
    


