"""
Модуль экстрактора информации из текстового файла выписки типа SBER_PAYMENT_2406

Для отладки модуля сделать следующее:

ШАГ 1: Сконвертировать выписку из формата .pdf в формат .txt используя либо sberbankPDF2ExcelGUI.py либо непосредственно pdf2txtev.py

ШАГ 2: Запустить этот файл из командной строки:

    py extractor_SBER_PAYMENT_2406.py <test_text_file_name>

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

class SBER_PAYMENT_2604b(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some specific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test1 = re.search(r'сбербанк', self.bank_text, re.IGNORECASE)
        # print(f"{test1=}")

        test2 = re.search(r'Выписка по платёжному счёту', self.bank_text, re.IGNORECASE)
        # print(f"{test2=}")

        test_ostatok_po_schetu = re.search(r'ОСТАТОК ПО СЧЁТУ', self.bank_text, re.IGNORECASE)
        # print(f"{test2=}")
        
        test_data_formirovania = re.search(r'Дата формирования', self.bank_text, re.IGNORECASE)
        
        test_dlya_proverki_podlinnosti = re.search(r'Для проверки подлинности документа', self.bank_text, re.IGNORECASE)
        
        test_dergunova_k_a = re.search(r'Дергунова К\. А\.', self.bank_text, re.IGNORECASE)

        if (test1 and 
            test2 and 
            test_dlya_proverki_podlinnosti and 
            test_data_formirovania) and not (test_ostatok_po_schetu or test_dergunova_k_a):
            
            return # All OK
        
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
    ------------------------------------------------------------------------------------------------------
        03.07.2021 12:52 -> Перевод с карты -> 3 500,00
        03.07.2021 123456 -> SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
    ------------------------------------------------------------------------------------------------------

        либо такой
    --------------------------------------------------------------------------------------------------
        28.06.2021 00:00 -> Неизвестная категория(+) -> +21107,75
        28.06.2021 - -> Прочие выплаты
    ----------------------------------------------------------------------------------------------------

        либо такой с иностранной вылютой
    ---------------------------------------------------------------------------------------------------------
        08.07.2021 18:27 -> Все для дома     193,91
        09.07.2021 254718 -> XXXXX XXXXX -> 2,09 €
    ---------------------------------------------------------------------------------------------------------

        ещё один пример (с 3 линиями)
        ---------------------------------------------------------------------------------------------------------
        03.07.2021 11:54 -> Перевод с карты -> 4 720,00
        03.07.2021 258077 -> SBOL перевод 1234****5678 А. ВАЛЕРИЯ
        ИГОРЕВНА
        ----------------------------------------------------------------------------------------------------------

        """
        
        # Removing the page breakes, which contain text like
        """
        Продолжение на следующей странице
        Выписка по платёжному счёту	Страница 3 из 8
        ДАТА ОПЕРАЦИИ (МСК)	КАТЕГОРИЯ	СУММА В ВАЛЮТЕ СЧЁТА	ОСТАТОК СРЕДСТВ
        В ВАЛЮТЕ СЧЁТА
        Дата обработки¹ и код авторизации	Описание операции	Сумма в валюте
        операции²
        """
        
        bank_text_cleaned = re.sub(r"""
                                   Продолжение\sна\sследующей\sстранице
                                   [\s\S]+?                                # Any character, including new line. !!None-greedy!!
                                   код\sавторизации\tоперации²
                                   """,
                                   repl='', 
                                   string=self.bank_text, 
                                   flags=re.VERBOSE)  
        
        # print("############## Cleaned text #################################")
        # print(bank_text_cleaned)
        
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\t\d\d:\d\d\t                             # Линия типа    29.06.2022	08:44	                             
            .*?\n                                                         # Anything till end of the line including a line break
            \d\d\.\d\d\.\d\d\d\d\t\d+                                     # дата обработки и и код авторизации типа 07.04.2026	310850
            [\s\S]*?                                                      # any character, including new line. !!None-greedy!!
            (?=\d\d\.\d\d\.\d\d\d\d\t\d\d:\d\d\t|                         # Либо до начала новой трансакции
            Дата\sформирования\sдокумента)                                # Либо да конца выписки
            """,
            bank_text_cleaned, re.VERBOSE)

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


        Выделяем данные из одной записи в dictionary

    ------------------------------------------------------------------------------------------------------
        06.04.2026	19:09	Транспорт	83,00	58 812,88
        07.04.2026	310850	Mos.Transport MOSKVA RUS. Операция по карте ****6118
    ------------------------------------------------------------------------------------------------------

        ещё один пример (с 3 линиями)
        ---------------------------------------------------------------------------------------------------------
        07.04.2026	13:48	Рестораны и кафе	523,40	58 978,88
        07.04.2026	224023	STOLOVAYA 2-J ETAZH MOSCOW RUS. Операция по карте
        ****6118
        ----------------------------------------------------------------------------------------------------------

        """
        lines = entry.split('\n')
        lines = list(filter(None, lines))

        if len(lines) < 2 or len(lines) > 4:
            raise exceptions.InputFileStructureError(
                "entry is expected to have from 2 to 4 lines\n" + str(entry))

        result: dict = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        result['operation_date'] = line_parts[0] + " " + line_parts[1]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y %H:%M')
        
        # result['authorisation_code'] = line_parts[2]

        result['category'] = line_parts[2]
        result['value_account_currency'] = get_decimal_from_money(line_parts[3], True)
        result['remainder_account_currency'] = get_decimal_from_money(line_parts[4])

        # ************** looking at the 2nd line
        line_parts = split_Sberbank_line(lines[1])

        if len(line_parts) < 3 or len(line_parts) > 4:
            raise exceptions.Bank2ExcelError(
                "Line 2 is expected to have 3 or 4 parts :\n" + str(lines[1]))

        result['processing_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%Y').date()

        result['authorisation_code'] = line_parts[1]

        result['description'] = line_parts[2]

        # Выделяем сумму в валюте оперции, если присуиствует
        if len(line_parts) == 4:
            found = re.search(r'(.*?)\s(\S*)',
                              line_parts[3])  # processing string like '6,79 €'
            if found:
                result['value_operational_currency'] = get_decimal_from_money(found.group(1))
                result['operational_currency'] = found.group(2)
            else:
                raise exceptions.InputFileStructureError(
                    "Ошибка в обработке текста. Ожидалась струтура типа '4,00 BYN', получено: " +
                    line_parts[3])

        # ************** looking at the 3rd line
        if len(lines) >= 3:
            line_parts = split_Sberbank_line(lines[2])
            result['description'] = result['description'] + ' ' + line_parts[0]
            
            
        # ************** looking at the 4th line
        if len(lines) == 4:
            line_parts = split_Sberbank_line(lines[3])
            result['description'] = result['description'] + ' ' + line_parts[0]

        # print(result)

        return result

    def get_column_name_for_balance_calculation(self)->str:
        """
        Retrun name of the transaction field, which later can be used to calculate a complete balance of the period
        E.g. 'value_account_currency'
        """
        return 'value_account_currency'

    def get_columns_info(self)->dict:
        """
        Returns full column names in the order and in the form they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """
        return {'operation_date': 'ДАТА ОПЕРАЦИИ (МСК)',
                'processing_date': 'Дата обработки',
                'authorisation_code': 'Код авторизации',
                'description': 'Описание операции',
                'category': 'КАТЕГОРИЯ',
                'value_account_currency': 'СУММА В ВАЛЮТЕ СЧЁТА',
                'value_operational_currency': 'Сумма в валюте операции',
                'operational_currency': 'Валюта операции',
                'remainder_account_currency': 'ОСТАТОК СРЕДСТВ В ВАЛЮТЕ СЧЁТА'
                }


if __name__ == '__main__':


    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_PAYMENT_2604b,
                                           test_text_file_name=sys.argv[1])



