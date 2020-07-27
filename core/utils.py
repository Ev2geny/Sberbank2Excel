#coding=utf-8
'''
Разные отдельностоящие функции, которые используются в других модулях
'''

import unidecode
import re
import pandas as pd

from typing import *

from core import exceptions


def get_float_from_money(money_str: str, process_no_sign_as_negative=False) -> float:
    """
    Converts string, representing money to a float.
    If process_no_sign_as_negative is set to True, then a number will be negative in case no leading sign is available
    """
    
    money_str = unidecode.unidecode(money_str)
    money_str = money_str.replace(' ','')
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
    Разделяем Сбербанковсую строчку на кусочки данных. Разделяем используя три и более пробела в качестве разделителя
    """
    line_parts=re.split(r'\s\s\s+',line)
    line_parts=list(filter(None,line_parts))
    return line_parts

def split_text_on_entries(PDF_text:str)->List[str]:
    """
    разделяет текстовый файл на отдельные записи
    """
    # extracting entries (operations) from text file on
    individual_entries=re.findall(r"""
    \s{40}                                        # 44 white speces 
    \d\d\.\d\d\.\d\d\d\d\s\d\d:\d\d               # Date and time like 25.04.1991 18:31                                     
    \s{8,12}                                     # 8-12 white speces (the amount of white speces in different places of the document is different
    [\s\S]*?                                      # any character, including new line. !!None-greedy!! See URL why [\s\S] is used https://stackoverflow.com/a/33312193
    \s{40}\d\d\.\d\d\.\d\d\d\d\s/                 # Again 44 white spaces, followed by like '25.12.2019 /' 
    .*?\n                                         # everything till end of the line
    """,
    PDF_text, re.VERBOSE)
    return individual_entries

def decompose_entry_to_dict(entry:str)-> Dict:
    """
    Выделяем данные из одной записи в dictionary
    
    Example of individual entry
    ---------------------------------------------------------------------------------------------------------
                                                 29.08.2019                GETT                                                             1 189,40             8 087,13 



                                                29.08.2019 / 278484       Отдых и развлечения 
    ----------------------------------------------------------------------------------------------------------
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

    result['processing_date']=line_parts[0][0:11]
    result['authorisation_code']=line_parts[0][13:]
    result['category']=line_parts[1]

    if len(line_parts)==3:
        found=re.search(r'[(](.*?)(\w\w\w)[)]',line_parts[2])  #processing string like (33,31 EUR)
        if found:
            result['value_operational_currency']=get_float_from_money(found.group(1),True)
            result['operational_currency']=found.group(2)
        else:
            raise exceptions.SberbankPDFtext2ExcelError("Could not process string. Expected something like (33,31 EUR):" + line)

    return result

def entries_to_pandas(individual_entries:List[str])->pd.DataFrame:

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
        """
        print('================================================================================================================================')
        print(entry)
        print('--------------------------------------------------------------------------------------------------------------------------------')
        """
        dict_result=decompose_entry_to_dict(entry)

        # print(result)
        df=df.append(dict_result,ignore_index=True)

    # convert to date https://stackoverflow.com/questions/41514173/change-multiple-columns-in-pandas-dataframe-to-datetime
    df['operation_date']=pd.to_datetime(df['operation_date'])
    df['processing_date']=pd.to_datetime(df['processing_date'])

    return df

def pd_to_Excel(pd_dataframe:pd.DataFrame,russian_headers:List[str],output_Excel_file_name:str):
    
    # Saving pandas dataframe to Excel
    writer = pd.ExcelWriter(output_Excel_file_name,
                            engine='xlsxwriter',
                            datetime_format='dd.mm.yyyy')
    
    pd_dataframe.to_excel(writer,header=russian_headers,sheet_name='Sheet1',index=False)
    
    writer.close()

def get_period_balance(PDF_text: str) -> float:
    """
    функция ищет в тексте значения "СУММА ПОПОЛНЕНИЙ" и "СУММА СПИСАНИЙ" и возвращает заницу
    используется для контрольной проверки вычислений

    :param PDF_text:
    :return:
    """

    if( res:= re.search(r'СУММА ПОПОЛНЕНИЙ \s{5,}(\d[\d\s]*\,\d\d)', PDF_text, re.MULTILINE) ):
        summa_popolneniy = res.group(1)
    else:
        raise exceptions.SberbankPDFtext2ExcelError('Не найдено значение "СУММА ПОПОЛНЕНИЙ"')

    if( res:= re.search(r'СУММА СПИСАНИЙ  \s{5,}(\d[\d\s]*\,\d\d)', PDF_text, re.MULTILINE) ):
        summa_spisaniy = res.group(1)
    else:
        raise exceptions.SberbankPDFtext2ExcelError('Не найдено значение "СУММА СПИСАНИЙ "')

    summa_popolneniy = get_float_from_money(summa_popolneniy)
    summa_spisaniy = get_float_from_money(summa_spisaniy)

    return summa_popolneniy - summa_spisaniy

def check_transactions_balance(input_pd: pd.DataFrame, balance: float):
    calculated_balance = input_pd['value_account_currency'].sum()
    if (abs(balance-calculated_balance) > 0.01):
        raise exceptions.SberbankPDFtext2ExcelError("Failed verification of balance")


def main():
    print('this manual is not designed to work standalone')

if __name__=='__main__':
    main()
    
        
    
    
    


