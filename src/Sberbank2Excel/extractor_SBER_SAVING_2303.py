"""
Модуль экстрактора информации из текстового файла выписки типа SBER_SAVING_2303

Для отладки модуля сделать следующее:

ШАГ 1: Сконвертировать выписку из формата .pdf в формат .txt используя либо sberbankPDF2ExcelGUI.py либо непосредственно pdf2txtev.py

ШАГ 2: Запустить этот файл из командной строки:

    py extractor_SBER_PAYMENT_2212.py <test_text_file_name>

ШАГ 3: Убедиться, что модуль закончит работу без ошибок

ШАГ 4: Проанализировать WARNINGS, которые будут напечатаны в конце

"""


import re
from datetime import datetime
import sys

from typing import Any

from Sberbank2Excel import exceptions
from Sberbank2Excel.utils import get_float_from_money, split_Sberbank_line
from Sberbank2Excel.extractor import Extractor
from Sberbank2Excel import extractors_generic

class SBER_SAVING_2303(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test1 = re.search(r'Выписка из лицевого счёта по вкладу «[^\n]+»', self.bank_text, re.IGNORECASE)
        # print(f"{test1=}")

        # Специфический паттерн, характерный для SBER_SAVING_2407, но который не должен присутствовать здесь
        spesific_pattern_SBER_SAVING_2407 = re.search(r'Дата предыдущей операции по счёту', self.bank_text, re.IGNORECASE)

        if (not test1 ) or spesific_pattern_SBER_SAVING_2407:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self)->float:
        """
        Function gets information about transaction balance from the header of the banl extract
        This balance is then returned as a float


        ---------------------------------------------------
        Пополнение	621,18	Списание	621,18
        -------------------------------------------------------
        :param :
        :return:
        """

        popolnenie_spisanie_re = re.search(r'Пополнение\t([\d,\s]*)\tСписание\t([\d,\s]*)', self.bank_text)
        if not popolnenie_spisanie_re:
            raise exceptions.InputFileStructureError('Не найдена структура с пополнениями и списаниями')

        # line_parts = res.group(1).split('\t')

        summa_popolneniy = get_float_from_money(popolnenie_spisanie_re.group(1))
        # print(f"summa_popolneniy = {summa_popolneniy}")
        summa_spisaniy = get_float_from_money(popolnenie_spisanie_re.group(2))
        # print(f"summa_spisaniy = {summa_spisaniy}")

        balance = summa_popolneniy - summa_spisaniy
        # print(f"balance = {balance}")

        """
        ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД  09.03.2020 - 23.02.2023
        Остаток средств	0,00	Остаток средств	100,00
        """
        ostatok_sredstv_re = re.search(r'ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД.+\nОстаток\sсредств\t([\d,\s]*)\tОстаток средств\t([\d,\s]*)', self.bank_text)
        if not ostatok_sredstv_re:
            raise exceptions.InputFileStructureError('Не найдена структура с остатками средств на начало и конец периода')

        # print(f"ostatok_sredstv_re.group(1) = {ostatok_sredstv_re.group(1)}")

        ostatok_start_of_period = get_float_from_money(ostatok_sredstv_re.group(1))
        ostatok_end_of_period = get_float_from_money(ostatok_sredstv_re.group(2))

        if not abs(balance - (ostatok_end_of_period - ostatok_start_of_period))<0.01:
            raise exceptions.InputFileStructureError(f'Что-то пошло не так:\n[ ВСЕГО ПОПОЛНЕНИЙ ({summa_popolneniy}) - ВСЕГО СПИСАНИЙ ({summa_spisaniy}) ] != [ОСТАТОК В КОНЦЕ ({ostatok_end_of_period}) - ОСТАТОК В НАЧАЛЕ ({ostatok_start_of_period})]  ')

        return balance

    def split_text_on_entries(self)->list[str]:
        """
        Function splits the text on indovidual entries
        If no entries are found, the exceptions.InputFileStructureError() is raised

        разделяет текстовый файл на отдельные записи

        пример одной записи
        ---------------------------------------------
        27.07.2022	Списание	3	-230,00	10,00
        к/с 12345678901234567890	№ 12345678-90
        --------------------------------------------
        """
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\t.+\n    # Date  '06.07.2021 15:46'  
            к/с.+\t.+\n                       #к/с 12345678901234567890	№ 12345678-90               
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

        All numerical fields shall be returned as float

        All dates / dates and times shall be returned as python datetime.datetime


        Выделяем данные из одной записи в dictionary

        ---------------------------------------------
        27.07.2022	Списание	3	-230,00	10,00
        к/с 12345678901234567890	№ 12345678-90
        --------------------------------------------


        В последнем примере:

    {'authorisation_code': '254718',
     'category': 'Все для дома',
     'description': 'XXXXX XXXXX',
     'operation_date': datetime.datetime(2021,7,8,18,27),
     'processing_date': datetime.datetime(2021,7,9,0,0),
     'value_account_currency': -193.91б
     'operational_currency': '€'
     }
        """
        lines = entry.split('\n')
        lines = list(filter(None, lines))

        if len(lines) < 2 or len(lines) >2:
            raise exceptions.InputFileStructureError(
                "Трансакция должна состоять из 2 строк\n" + str(entry))

        result: dict = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        if not len(line_parts) == 5:
            raise exceptions.InputFileStructureError(
                "Первая строка трансакции должна состоять из 5 частей")

        result['operation_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y').date()

        result['description'] = line_parts[1]
        result['code'] = line_parts[2]
        result['value'] = get_float_from_money(line_parts[3])
        result['remaining_value'] = get_float_from_money(line_parts[4])
        # result['remainder_account_currency'] = get_float_from_money(line_parts[4])

        # ************** looking at the 2nd line
        line_parts = split_Sberbank_line(lines[1])

        if not len(line_parts) == 2:
            raise exceptions.InputFileStructureError(
                "вторая строка трансакции должна состоять из 2 частей")

        # print(line_parts[0])

        result['offsetting_account'] = line_parts[0]
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
        extractors_generic.debug_extractor(SBER_SAVING_2303,
                                           test_text_file_name=sys.argv[1])



