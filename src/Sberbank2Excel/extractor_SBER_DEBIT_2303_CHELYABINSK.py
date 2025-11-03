import re
from datetime import datetime
import sys
from decimal import Decimal

from typing import Any

from Sberbank2Excel import exceptions
from Sberbank2Excel.utils import get_decimal_from_money, split_Sberbank_line
from Sberbank2Excel.extractor import Extractor
from Sberbank2Excel import extractors_generic

class SBER_DEBIT_2303_CHELYABINSK(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test1 = re.search(r'История операций по дебетовой карте за период', self.bank_text, re.IGNORECASE)
        # print(f"{test1=}")

        if not test1:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self) -> Decimal:
        """
        Function gets information about transaction balance from the header of the banlk extract
        This balance is then returned as a Decimal


        ---------------------------------------------------
        Безналичные	.....................................	245 424,56
        Наличные	...........................................	354 745,00
        Пополнение карты	..........................	+603 201,00
        -------------------------------------------------------
        :param :
        :return:
        """

        beznalichniye = re.search(r'Безналичные\t[.]{5,}\t(.*)', self.bank_text)
        # print(beznalichniye.group(1))
        if not beznalichniye:
            raise exceptions.InputFileStructureError('Не найдена структура с безналинными')

        nalichniye = re.search(r'Наличные\t[.]{5,}\t(.*)', self.bank_text)
        # print(nalichniye.group(1))
        if not nalichniye:
            raise exceptions.InputFileStructureError('Не найдена структура с наличными')

        popolneniye_karty = re.search(r'Пополнение карты\t[.]{5,}\t(.*)', self.bank_text)
        if not popolneniye_karty:
            raise exceptions.InputFileStructureError('Не найдена структура с пополнением карты')

        beznalichniye_num = get_decimal_from_money(beznalichniye.group(1))
        # print(beznalichniye_num)

        nalichniye_num = get_decimal_from_money(nalichniye.group(1))
        # print(nalichniye_num)

        popolneniye_karty_num = get_decimal_from_money(popolneniye_karty.group(1))
        # print(popolneniye_karty_num)

        balance = popolneniye_karty_num - beznalichniye_num - nalichniye_num

        return balance

    def split_text_on_entries(self)->list[str]:
        """
        Выделяем записи типа
        ----------------------------------------------
        24.07.21	24.07.21	290467	RUS Moscow SBOL перевод	+1 500,00
        1234****5678 Р. ИРИНА
        ГРИГОРЬЕВНА
        ------------------------------------------------
        
        Либо такие 
        
        ----------------------------------------------
        15.01.21	16.01.21	RUS Moscow  MOBILE FEE	60,00
        --------------------------------------------------
        
        """
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
        \d\d\.\d\d\.\d\d\t\d\d\.\d\d\.\d\d            # 19.09.21	21.09.21                                        
        [\s\S]*?                                      # any character, including new line. !!None-greedy!! See URL why [\s\S] is used https://stackoverflow.com/a/33312193
        (?=\d\d\.\d\d\.\d\d\t\d\d\.\d\d\.\d\d|        # lookahead до начала следующей трансакции
        117997,\sМосква,\sул\.\sВавилова,\sд\.\s19|   # либо до верхнего колонтитула следующей страницы (117997, Москва, ул. Вавилова, д. 19)' 
        \Z)                                           # либо до конца файла
        """,
        self.bank_text, re.VERBOSE)

        if len(individual_entries) == 0:
            raise exceptions.InputFileStructureError(
                "Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

        return individual_entries

    def decompose_entry_to_dict(self, entry:str)->dict:
        """
        Выделяем данные из одной записи в dictionary

        пример одной записи
        ----------------------------------------------
        24.07.21	24.07.21	290467	RUS Moscow SBOL перевод	+1 500,00
        1234****5678 Р. ИРИНА
        ГРИГОРЬЕВНА
        ------------------------------------------------

        Либо такие 
        
        ----------------------------------------------
        15.01.21	16.01.21	RUS Moscow  MOBILE FEE	60,00
        --------------------------------------------------
        """
        lines = entry.split('\n')
        lines = list(filter(None, lines))

        result: dict = {}
        # ************** looking at the 1st line

        line_parts = split_Sberbank_line(lines[0])

        result['operation_date'] = line_parts[0]
        result['processing_date'] = line_parts[1]
        
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%y').date()
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%y').date()
        
        
        # result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%Y')
        
        
        # checking if line contains authrisation code
        if re.match(r'\d{6}', line_parts[2]):
            result['authorisation_code'] = line_parts[2]
            result['description'] = line_parts[3]
        
        # otherwise this is this type of line with ow autherisation code
            """
            ----------------------------------------------
            15.01.21	16.01.21	RUS Moscow  MOBILE FEE	60,00
            --------------------------------------------------
            """
        else:
            result['authorisation_code'] = None
            result['description'] = line_parts[2]

        # Т.к. нет примера выписки, где присутствует сумма в валюте операции, то не будем извлекать эту информацию
        result['value_account_currency'] = get_decimal_from_money(line_parts[-1],True)

        # ************* looking at lines after the 1st
        sublines = lines[1:]
        for line in sublines:
            line_parts = split_Sberbank_line(line)
            if len(line_parts) != 1:
                raise exceptions.Bank2ExcelError(
                    f"Line '{line}' is expected to have only one part :" + line)
            result['description'] = result['description'] + " " +line_parts[0]

        return result

    def get_column_name_for_balance_calculation(self)->str:
        return 'value_account_currency'

    def get_columns_info(self)->dict:
        """
        Returns full column names in the order they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """
        return {'operation_date': 'Дата операции',
                'processing_date': 'Дата обработки',
                'authorisation_code': 'Код авторизации',
                'description': 'Описание операции',
                # 'category': 'Категория',
                # 'value_operational_currency': 'Сумма в валюте операции',
                'value_account_currency': 'Сумма в валюте счёта',
                # 'operational_currency': 'Валюта операции',
                # 'remainder_account_currency': 'Остаток по счёту в валюте счёта'
                }


if __name__ == '__main__':


    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_DEBIT_2303_CHELYABINSK,
                                           test_text_file_name=sys.argv[1])