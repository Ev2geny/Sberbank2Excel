"""
Модуль экстрактора информации из текстового файла выписки типа SBER_SAVING_2407

Для отладки модуля сделать следующее:

ШАГ 1: Сконвертировать выписку из формата .pdf в формат .txt используя либо sberbankPDF2ExcelGUI.py либо непосредственно
pdf2txtev.py

ШАГ 2: Запустить этот файл из командной строки:

    py extractor_SBER_PAYMENT_2212.py <test_text_file_name>

ШАГ 3: Убедиться, что модуль закончит работу без ошибок

ШАГ 4: Проанализировать WARNINGS, которые будут напечатаны в конце

"""


import re
from datetime import datetime
import sys
from decimal import Decimal

from typing import Any

from Sberbank2Excel import exceptions
from Sberbank2Excel.utils import get_decimal_from_money, split_Sberbank_line
from Sberbank2Excel.extractor import Extractor
from Sberbank2Excel import extractors_generic

class SBER_SAVING_2604(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test_individualnaya_vipiska_po_schetu = re.search(r'Индивидуальная выписка по счёту «[^\n]+»', self.bank_text, re.IGNORECASE)
        
        test_dop_filtry = re.search(r'Дополнительно заполненные фильтры', self.bank_text, re.IGNORECASE)
        
        test_dergunova = re.search(r'Дергунова', self.bank_text, re.IGNORECASE)
        
        if test_individualnaya_vipiska_po_schetu and test_dop_filtry and not test_dergunova:
            return
        else:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self) -> Decimal:
        """
        """
            
        res_popolneniy = re.search(r'Пополнение\t(.+)', self.bank_text)
        
        if not res_popolneniy:
            raise exceptions.InputFileStructureError(
                'Не найдена структура с пополнениями')
        
        summa_popolneniy = res_popolneniy.group(1) 
        
        
        res_spisaniy = re.search(r'Списание\t(.+)', self.bank_text)
        
        if not res_spisaniy:
            raise exceptions.InputFileStructureError(
                'Не найдена структура сo списаниями')
        
        summa_spisaniy = res_spisaniy.group(1)
        

        summa_popolneniy = get_decimal_from_money(summa_popolneniy)
        summa_spisaniy = get_decimal_from_money(summa_spisaniy)

        return summa_popolneniy - summa_spisaniy

    def split_text_on_entries(self)->list[str]:
        """
        Function splits the text on indovidual entries
        If no entries are found, the exceptions.InputFileStructureError() is raised

        разделяет текстовый файл на отдельные записи

        пример одной записи
        ---------------------------------------------
        27.07.2022	Списание	3, № 12345678-90	-230,00	10,00
        к/с 12345678901234567890
        --------------------------------------------
        """
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\t.+\n    # Date  '06.07.2021 15:46'  
            к/с.+\t?.+\n                       #к/с 12345678901234567890
            """, self.bank_text, re.VERBOSE)

        if len(individual_entries) == 0:
            raise exceptions.InputFileStructureError(
                "Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

        # for entry in individual_entries:
        #     print(entry)

        return individual_entries

    def decompose_entry_to_dict(self, entry:str)->dict:
        """
        Function decomposes individual entry text to an information structure in a form of dictionary
        If something unexpected is found, exception exceptions.InputFileStructureError() is raised
        Naming of the dictionary keys is not hard fixed, but shall correspond to what is returned by the function get_columns_info(self)

        All numerical fields shall be returned as Decimal

        All dates / dates and times shall be returned as python datetime.datetime

        """
        lines = entry.split('\n')
        lines = list(filter(None, lines))

        if len(lines) < 2 or len(lines) >2:
            raise exceptions.InputFileStructureError(
                "Трансакция должна состоять из 2 строк\n" + str(entry))

        result: dict = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        if not len(line_parts) == 4:
            raise exceptions.InputFileStructureError(
                "Первая строка трансакции должна состоять из 4 частей")

        result['operation_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y').date()

        result['description'] = line_parts[1]

        code_part = line_parts[2]
        if ',' in code_part:
            code_parts = code_part.split(',')
            result['code'] = code_parts[0].strip()
            result['document_number'] = code_parts[1].strip()
        else:
            result['code'] = code_part

        result['value'] = get_decimal_from_money(line_parts[3])
        # result['remaining_value'] = get_decimal_from_money(line_parts[4])
        # result['remainder_account_currency'] = get_decimal_from_money(line_parts[4])

        # ************** looking at the 2nd line
        line_parts = split_Sberbank_line(lines[1])

        if not len(line_parts) > 0:
            raise exceptions.InputFileStructureError(
                "вторая строка трансакции должна состоять минимум из 1 части")

        # print(line_parts[0])

        result['offsetting_account'] = line_parts[0]
        if len(line_parts) > 1:
            result['document_number'] = line_parts[1]

        return result

    def get_column_name_for_balance_calculation(self)->str:
        """
        Retrun name of the transaction field, which later can be used to calculate a complete balance of the period
        E.g. 'value_account_currency'
        """
        return 'value'

    def get_columns_info(self)->dict:
        """
        Returns full column names in the order and in the form they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """
        return {'operation_date': 'ДАТА ОПЕРАЦИИ',
                'description': 'НАИМЕНОВАНИЕ ОПЕРАЦИИ',
                'offsetting_account':'№ корреспондирующего счёта',
                'code': 'ШИФР',
                'document_number':'№ документа',
                'value': 'СУММА ОПЕРАЦИИ',
                'remaining_value': 'ОСТАТОК НА СЧЁТЕ'}


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_SAVING_2604,
                                           test_text_file_name=sys.argv[1])



