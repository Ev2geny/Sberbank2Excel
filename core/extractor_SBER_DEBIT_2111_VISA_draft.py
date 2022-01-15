"""
Это незаконченный модуль, не интегрированный в extractors.py
Незаконченность определяется тем, что мне был выслан *.pdf без первой страницы
"""


import exceptions
import re
from datetime import datetime
import sys

from utils import get_float_from_money
from utils import split_Sberbank_line

from extractor import Extractor

import extractors_generic

class SBER_DEBIT_2111_VISA(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test1 = re.search(r'www.sberbank.ru', self.pdf_text, re.IGNORECASE)
        # print(f"{test1=}")

        if not test1:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self)->str:
        test1 = re.search(r'www.sberbank.ru', self.pdf_text, re.IGNORECASE)
        # print(f"{test1=}")

        if not test1:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

        return 0.0

    def split_text_on_entries(self)->list[str]:
        """
        Function splits the text on individual entries
        If no entries are found, the exceptions.InputFileStructureError() is raised

        """
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d                                              # Date like '02.06.21' Дата операции 
            \t                                                            # tab    
            \d\d\.\d\d\.\d\d                                              # Date like '02.06.21' Дата обработки
            [\s\S]*?                                                      # any character, including new line. !!None-greedy!!
            (?=\d\d\.\d\d\.\d\d|                                           # Lookahead Start of new transaction
            117997,\sМосква,\sул\.\sВавилова,\sд\.\s19|                    # or till "117997, Москва, ул. Вавилова, д. 19"
             ___EOF)                                                       # or till artificial __EOF
            """,
            self.pdf_text, re.VERBOSE)

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

        result = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        result['operation_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%y')

        result['processing_date'] = line_parts[1]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%y')

        if re.match(r'\d{6}', line_parts[2]): # checking presence of aithorisation code
            result['authorisation_code'] = line_parts[2]

            result['description'] = line_parts[3]

        else:
            result['authorisation_code'] = ''

            result['description'] = line_parts[2]

        result['value_account_currency'] = get_float_from_money(line_parts[-1], True)

        #TODO: Add support for transaction in different currency

        # ************** looking at the line from 2nd till the end
        result['description'] = result['description'] + " " + " ".join(lines[1:])

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
        return {'operation_date': 'Дата операции',
                'processing_date': 'Дата обработки',
                'authorisation_code': 'Код авторизации',
                'description': 'Описание операции',
                # 'category': 'Категория',
                'value_account_currency': 'Сумма в валюте счёта',
                # 'value_operational_currency': 'Сумма в валюте операции',
                # 'operational_currency': 'Валюта операции',
                # 'remainder_account_currency': 'Остаток по счёту в валюте счёта'
                }


if __name__ == '__main__':


    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_DEBIT_2111_VISA,
                                           test_text_file_name=sys.argv[1])



