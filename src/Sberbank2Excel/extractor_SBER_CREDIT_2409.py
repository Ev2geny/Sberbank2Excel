"""
Модуль экстрактора информации из текстового файла выписки типа SBER_CREDIT_2409

Для отладки модуля сделать следующее:

ШАГ 1: Сконвертировать выписку из формата .pdf в формат .txt используя либо sberbankPDF2ExcelGUI.py либо непосредственно pdf2txtev.py

ШАГ 2: Запустить этот файл из командной строки:

    py extractor_SBER_CREDIT_2409.py <test_text_file_name>

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


class SBER_CREDIT_2409(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test_SberBank = re.search(r'сбербанк', self.bank_text, re.IGNORECASE)
        # print(f"{test1=}")

        test_Vipiska_po_schetu = re.search(r'Выписка по счёту кредитной карты', self.bank_text, re.IGNORECASE)
        # print(f"{test2=}")
        
        test_OSTATOK_SREDSTV = re.search(r'ОСТАТОК СРЕДСТВ', self.bank_text, re.IGNORECASE)

        if not (test_SberBank and test_Vipiska_po_schetu and test_OSTATOK_SREDSTV):
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self) -> Decimal:
        """
        Function gets information about transaction balance from the header of the banl extract
        This balance is then returned as a float


        ---------------------------------------------------
        СУММА ПОПОЛНЕНИЙ -> СУММА СПИСАНИЙ -> СУММА СПИСАНИЙ БАНКА
        1 040,00 -> 601,80 -> 437,46
        -------------------------------------------------------
        :param :
        :return:
        """

        res = re.search(r'ОСТАТОК ПО СЧЁТУ НА \d\d\.\d\d\.\d\d\d\d\tОСТАТОК ПО СЧЁТУ НА \d\d\.\d\d\.\d\d\d\d\n(.*?)\n', self.bank_text, re.MULTILINE)
 
        if not res:
            pass
            raise exceptions.InputFileStructureError('Не найдена структура с пополнениями и списаниями')

        line_parts = res.group(1).split('\t')

        summa_beginning = get_decimal_from_money(line_parts[0])
        summa_end = get_decimal_from_money(line_parts[1])


        return summa_end - summa_beginning

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
        # Удаляем куски текста, которые являются разделами между страницами PDF, не несущими информации
        cleaned_text = re.sub(r'Продолжение на следующей странице[\s\S]*?Сумма в валюте операции²\n', '', self.bank_text)
        
        # print("*********** cleaned_text ***********")
        # print(cleaned_text)
        
        
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\t\d\d:\d\d\t\d{3,8}                       # Structure like '02.09.2024	09:28	097626'  
            [\s\S]*?                                                       # any character, including new line. !!None-greedy!!
            (?=\d\d\.\d\d\.\d\d\d\d\s{1}\d\d:\d\d|                         # lookahead до начала следующей транзакции
            Дергунова)                                                     # Либо да конца выписки
            """,
                                        cleaned_text, re.VERBOSE)

        if len(individual_entries) == 0:
            raise exceptions.InputFileStructureError(
                "Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

        # for entry in individual_entries:
        #     print(entry)

        return individual_entries

    @staticmethod
    def process_line_data_obrabotki(line: str, result: dict) -> dict:
        """
        Обрабатывает строку с датой обработки
        Типа:
            а) Без валюты операции
            
            26.09.2024 -> Kurgan OICO WEB
            
            б) С валютой операции
            
            26.09.2024 -> Kurgan OICO WEB -> 6,79 €
        
        """

        line_parts = split_Sberbank_line(line)

        if len(line_parts) < 2 or len(line_parts) > 3 and not re.search(r'^\d{2}\.\d{2}\.\d{4}', line_parts[1]):
            raise exceptions.Bank2ExcelError(
                "Ожидалась строка из 2 или 3 частей и начинающаяся с дд.мм.гггг. получено:\n" + line)

        # print(line_parts[0])

        # processing_date__authorisation_code = re.search(r'(dd\.dd\.dddd)\s(.*)', line_parts[0])
        result['processing_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%Y')

        
        result['description'] = line_parts[1]

        # Выделяем сумму в валюте оперции, если присуиствует
        if len(line_parts) == 3:
            found = re.search(r'(.*?)\s(\S*)',
                              line_parts[2])  # processing string like '6,79 €'
            if found:
                result['value_operational_currency'] = get_decimal_from_money(found.group(1), True)
                result['operational_currency'] = found.group(2)
            else:
                raise exceptions.InputFileStructureError(
                    "Ошибка в обработке текста. Ожидалась структура типа '6,79 €', получено: " +
                    line_parts[2])
                
        return result
                

    def decompose_entry_to_dict(self, entry: str) -> dict | list[dict]:
        """
        Function decomposes individual entry text to an information structure in a form of dictionary
        If something unexpected is found, exception exceptions.InputFileStructureError() is raised
        Naming of the dictionary keys is not hard fixed, but shall correspond to what is returned by the function get_columns_info(self)

        All numerical fields shall be returned as float

        All dates / dates and times shall be returned as python datetime.datetime


        Выделяем данные из одной записи в dictionary

    ------------------------------------------------------------------------------------------------------
        03.07.2021 12:52 -> Перевод с карты -> 3 500,00
        03.07.2021 123456 -> SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
    ------------------------------------------------------------------------------------------------------

        либо такой
    --------------------------------------------------------------------------------------------------
        28.06.2021 00:00 -> Неизвестная категория(+)     +21107,75
        28.06.2021 - -> Прочие выплаты
    ----------------------------------------------------------------------------------------------------

        ещё один пример (с 3 линиями)
        ---------------------------------------------------------------------------------------------------------
        03.07.2021 11:54 -> Перевод с карты -> 4 720,00
        03.07.2021 258077 -> SBOL перевод 1234****5678 А. ВАЛЕРИЯ
        ИГОРЕВНА
        ----------------------------------------------------------------------------------------------------------

        либо такой с иностранной вылютой
    ---------------------------------------------------------------------------------------------------------
        08.07.2021 18:27 -> Все для дома -> 193,91
        09.07.2021 -> 254718 -> XXXXX XXXXX -> 2,09 €
    ---------------------------------------------------------------------------------------------------------

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

        if len(lines) < 2:
            raise exceptions.InputFileStructureError(
                "Ожидается, что в трансакция будет состоять не менее чем из 2 строк.\n" + str(entry))

        result: dict = dict()
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        result['operation_date'] = line_parts[0] + " " + line_parts[1]
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y %H:%M')
        
        result['authorisation_code'] = line_parts[2]

        result['category'] = line_parts[3]
        result['value_rubles'] = get_decimal_from_money(line_parts[4], True)
        result['remainder_account_currency'] = get_decimal_from_money(line_parts[5], True)

        # ************** looking at the 2nd line and 3rd line in case of issue 56 
        line_parts = split_Sberbank_line(lines[1])
        
        next_line = None
        
        if len(line_parts) == 1 and  not re.search(r'^\d{2}\.\d{2}\.\d{4}', line_parts[0]):
            # this must be this case: https://github.com/Ev2geny/Sberbank2Excel/issues/56
            result['category'] += ' ' + line_parts[0]
            
            # Looking at the 3rd line in this case
            result = self.process_line_data_obrabotki(lines[2], result)
            
            next_line = 3
            
        else:
            result = self.process_line_data_obrabotki(lines[1], result)
            next_line = 2

        # **********  Обрабатываем строки, следующие за строкой с датой обработки
        # sub_transactions будет хранить вложенные транзакции, если они есть. 
        # См. https://github.com/Ev2geny/Sberbank2Excel/issues/54
        sub_transactions: list[dict] = []
                
        
        for line in lines[next_line:]:
            line_parts = split_Sberbank_line(line)
            
            if len(line_parts) > 2:
                raise exceptions.InputFileStructureError("Ожидалась строка с 1-2 частями, получено: \n" + line)
            
            if len(line_parts) == 1:
                # Если строка содержит только одну часть, то значит это не может быть форматом "Описание -> сумма"
                # проверяем, была ли уже найдена хотя бы одна вложенная транзакция
                if len(sub_transactions) > 0:
                    # Ожидаем, что если была найдена хотя бы одна вложенная транзакция, то все последующие строки должны 
                    # быть также вложенными транзакциями формата "Описание -> сумма"
                    raise exceptions.InputFileStructureError("Ожидалась строка с описанием и суммой, получено: \n" + line)
                
                result['description'] = result['description'] + ' ' + line_parts[0]
                # continue
            
            else:
            
                sub_transaction = dict()
                sub_transaction['operation_date'] = result['operation_date']
                sub_transaction['processing_date'] = result['processing_date']
                sub_transaction['category'] = result['category']
                sub_transaction['authorisation_code'] = result['authorisation_code']
                sub_transaction['description'] = line_parts[0]
                sub_transaction['value_rubles'] = get_decimal_from_money(line_parts[1], True)
                
                sub_transactions.append(sub_transaction)
                
        # In this case return only dictionary
        if len(sub_transactions) == 0:
            return result        
        
        # In this case return list of dictionaries
        else:
            return [result] + sub_transactions



    def get_column_name_for_balance_calculation(self)->str:
        """
        Returns the name of the transaction field, which later can be used to calculate a complete balance of the period
        E.g. 'value_account_currency'
        """
        return 'value_rubles'

    def get_columns_info(self) -> dict:
        """
        Returns full column names in the order and in the form they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """
        return {'operation_date': 'ДАТА ОПЕРАЦИИ',
                'processing_date': 'Дата обработки',
                'authorisation_code': 'Код авторизации',
                'description': 'Описание операции',
                'category': 'КАТЕГОРИЯ',
                'value_rubles': 'СУММА В РУБЛЯХ',
                'value_operational_currency': 'Сумма в валюте операции',
                'operational_currency': 'Валюта операции',
                'remainder_account_currency': 'ОСТАТОК СРЕДСТВ'
                }


if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_CREDIT_2409,
                                           test_text_file_name=sys.argv[1])



