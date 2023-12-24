#coding=utf-8
'''
Разные отдельностоящие функции, которые используются в других модулях
'''

import unidecode
import re
from typing import *
from pathlib import Path

import pandas as pd

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

def write_df_to_file(df:pd.DataFrame, 
                        file:Path, 
                        extractor_name:str, 
                        errors:str="",
                        output_file_format:str="xlsx")->None:
    """
        file - Path object of the file with or without extension
        output_file_format - supported values xlsx, csv
    """

    global version_info

    if output_file_format not in ["xlsx", "csv"]:
        raise exceptions.UserInputError(f"not supported output file format '{output_file_format}' is given to the function 'write_df_to_file'")

    def print_message_about_file_creation(file_name:Any)->None:
        print(f"Создан файл {file_name}")

    filename = Path(file).with_suffix(f".{output_file_format}")

    if output_file_format == "xlsx":

        with pd.ExcelWriter(filename,
                                engine='xlsxwriter',
                                datetime_format='dd.mm.yyyy HH:MM') as writer:

            df.to_excel(writer, sheet_name='data', index=False)

            workbook = writer.book
            info_worksheet = workbook.add_worksheet('Info')

            info_worksheet.write('A3', f'Файл создан утилитой "{version_info.NAME}", доступной для скачивания по ссылке {version_info.PERMANENT_LOCATION}')
            info_worksheet.write('A4', f'Версия утилиты "{version_info.VERSION}"')
            info_worksheet.write('A5', f'Для выделения информации был использован экстрактор типа "{extractor_name}"')
            info_worksheet.write('A6', f'Ошибки при конвертации: "{errors}"')

            # writer.save()

        print_message_about_file_creation(filename)

    elif output_file_format == "csv":
        df.to_csv(filename,
                    sep=";",
                    index=False,
                    # date_format='dd.mm.yyyy HH:MM'
                    )

        print_message_about_file_creation(filename)
    else:
        raise exceptions.UserInputError(f"not supported output file format '{output_file_format}' is given to the function 'write_df_to_file'")
    
    
def get_output_extentionless_file_name(input_file_name:str|Path,
                                       output_file_name:str|Path|None = None,
                                        output_folder:str|Path|None = None,
                                        create_output_folder:bool=False)->Path:
    """Claculates the name of the output file based on the combilation of the input file name and output file name and output folder name

    Args:
        input_file_name (str | Path): _description_
        output_file_name (str | Path | None, optional): _description_. Defaults to None.
        output_folder (str | Path | None, optional): _description_. Defaults to None.
        create_output_folder (bool, optional): _description_. Defaults to False.

    Returns:
        absolute path to the output file
    """
    
    
    
    if not input_file_name:
        raise exceptions.UserInputError("input file name is not provided")
    
    
    input_file_name_path = Path(input_file_name).resolve(strict=True)
    
    if not input_file_name_path.exists():
        raise exceptions.UserInputError(f"input file '{input_file_name_path}' does not exist")
    
    
    if output_file_name:
        output_file_name_path = Path(output_file_name)
        
        if output_file_name_path.is_absolute():
            return output_file_name_path
        
        output_file_name_is_single_file =  output_file_name_path.name == output_file_name
        if not output_file_name_is_single_file:
            raise exceptions.UserInputError(f"output file name '{output_file_name}' is a relative path, but it should be a file name only or an absolute path")
        
    
    final_output_folder_path = None
    if output_folder:
        output_folder_path = Path(output_folder)
        output_folder_path_is_single_folder =  Path(output_folder_path.name) == output_folder_path
        if (not output_folder_path.is_absolute()) and  (not output_folder_path_is_single_folder):
            raise exceptions.UserInputError(f"output folder '{output_folder}' is a relative path, consisting of several folders, but it should be a folder name only or an absolute path")

        if not output_folder_path.is_absolute():
            final_output_folder_path = input_file_name_path.parent / output_folder_path
        else:
            final_output_folder_path = output_folder_path
            
        if not final_output_folder_path.is_dir():
            if create_output_folder:
                final_output_folder_path.mkdir()
            else:
                raise exceptions.UserInputError(f"output folder '{final_output_folder_path}' does not exist and it is not requested to create it")
    else:
        final_output_folder_path = input_file_name_path.parent
    
    
    
    output_file_name_path = None        
    if  output_file_name:
        output_file_name_path = Path(output_file_name)
        output_file_name_path_is_single_file =  Path(output_file_name_path.name) == output_file_name_path
        if not output_file_name_path.is_absolute() and not output_file_name_path_is_single_file:
            raise exceptions.UserInputError(f"output file name '{output_file_name}' is a relative path,  but it should be a file name only or an absolute path")  
    
        if  output_file_name_path.is_absolute() and output_folder_path:
            raise exceptions.UserInputError(f"output file name '{output_file_name}' is an absolute path, but output folder '{output_folder}' is also provided. It is not clear how to resolve this conflict")
        
        
    # Here starting with allowed combinations   
    if output_file_name_path and output_file_name_path.is_absolute():
        return output_file_name_path
    
    if output_file_name_path and not final_output_folder_path:
        return input_file_name_path.parent / output_file_name_path
       
    
    if not final_output_folder_path and not output_file_name_path:
        return input_file_name_path.parent / input_file_name_path.stem
    
    if output_file_name_path and final_output_folder_path:
        return final_output_folder_path / output_file_name_path
    
    
    if not output_file_name_path and final_output_folder_path:
        return final_output_folder_path / input_file_name_path.stem
    
    
    raise exceptions.InternalLogicError(f"unexpected combination of input parameters: input_file_name='{input_file_name}', output_file_name='{output_file_name}', output_folder='{output_folder}'")


def main():
    print('this module is not designed to work standalone')

if __name__=='__main__':
    print(get_output_extentionless_file_name('input_file.txt'))
    print(get_output_extentionless_file_name('C:\_code\py\Sberbank2Excel\Sberbank2Excel\core\input_file.txt'))
    print(get_output_extentionless_file_name('input_file.txt', output_file_name='output_file_changed.xlsx'))
    print(get_output_extentionless_file_name('input_file.txt', output_folder='output_folder'))
    print(get_output_extentionless_file_name('input_file.txt', output_folder='output_folder', create_output_folder=True))
    
    
        
    
    
    


