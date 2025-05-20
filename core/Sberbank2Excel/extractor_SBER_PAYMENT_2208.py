"""
Модуль экстрактора информации из текстового файла выписки типа SBER_PAYMENT_2208

Для отладки модуля сделать следующее:

ШАГ 1: Сконвертировать выписку из формата .pdf в формат .txt используя либо sberbankPDF2ExcelGUI.py либо непосредственно pdf2txtev.py

ШАГ 2: Запустить этот файл из командной строки:

    py extractor_SBER_CREDIT_2110.py <test_text_file_name>

ШАГ 3: Убедиться, что модуль закончит работу без ошибок

ШАГ 4: Проанализировать WARNINGS, которые будут напечатаны в конце

"""


from . import exceptions
import re
from datetime import datetime
import sys

from .utils import get_float_from_money
from .utils import split_Sberbank_line

from .extractor import Extractor

from . import extractors_generic

class SBER_PAYMENT_2208(Extractor):

    def check_specific_signatures(self):
        """
        Function tries to find some spesific signatures in the text (e.g. sberbank)
        If these signatures are not found, then exceptions.InputFileStructureError() is raised
        """

        test1 = re.search(r'сбербанк', self.bank_text, re.IGNORECASE)
        # print(f"{test1=}")

        test2 = re.search(r'Выписка по платёжному счёту', self.bank_text, re.IGNORECASE)
        # print(f"{test2=}")

        test_ostatok_po_schetu = re.search(r'ОСТАТОК ПО СЧЁТУ', self.bank_text, re.IGNORECASE)
        # print(f"{test2=}")

        if not test1  or not test2 or not test_ostatok_po_schetu:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self)-> float:
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

        res = re.search(r'ОСТАТОК\sНА.*ВСЕГО\sСПИСАНИЙ\tВСЕГО\sПОПОЛНЕНИЙ.*\n(.*?)\n', self.bank_text, re.MULTILINE)
        if not res:
            pass
            raise exceptions.InputFileStructureError('Не найдена структура с пополнениями и списаниями')

        line_parts = res.group(1).split('\t')

        summa_popolneniy = get_float_from_money(line_parts[3])
        summa_spisaniy = get_float_from_money(line_parts[2])

        balance = summa_popolneniy - summa_spisaniy

        ostatok_start_of_period = get_float_from_money(line_parts[0])
        ostatok_end_of_period = get_float_from_money(line_parts[1])

        if not abs(balance - (ostatok_end_of_period - ostatok_start_of_period))<0.01:
            raise exceptions.InputFileStructureError(f'Что-то пошло не так:\n[ ВСЕГО ПОПОЛНЕНИЙ ({summa_popolneniy}) - ВСЕГО СПИСАНИЙ ({summa_spisaniy}) ] != [ОСТАТОК В КОНЦЕ ({ostatok_end_of_period}) - ОСТАТОК В НАЧАЛЕ ({ostatok_start_of_period})]  ')

        return balance

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
        # extracting entries (operations) from text file on
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\s{1}\d\d:\d\d                             # Date and time like '06.07.2021 15:46'                                        
            .*?\n                                                          # Anything till end of the line including a line break
            \d\d\.\d\d\.\d\d\d\d\s{1}                                      # дата обработки и 1 пробел 
            (?=\d{3,8}|-)                                                  # код авторизации либо "-". Код авторизациии который я видел всегда состоит и 6 цифр, но на всякий случай укажим с 3 до 8
            [\s\S]*?                                                       # any character, including new line. !!None-greedy!!
            (?=Продолжение\sна\sследующей\sстранице|                       # lookahead до "Продолжение на следующей странице"
             \d\d\.\d\d\.\d\d\d\d\s{1}\d\d:\d\d|                           # Либо до начала новой страницы
              Реквизиты\sдля\sперевода)                                    # Либо да конца выписки
            """,
                                        self.bank_text, re.VERBOSE)

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

        if len(lines) < 2 or len(lines) > 3:
            raise exceptions.InputFileStructureError(
                "entry is expected to have from 2 to 3 lines\n" + str(entry))

        result: dict = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        result['operation_date'] = line_parts[0] + " " + line_parts[1]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y %H:%M')

        result['description'] = line_parts[2]
        result['value_account_currency'] = get_float_from_money(line_parts[3])
        result['remainder_account_currency'] = get_float_from_money(line_parts[4])

        # ************** looking at the 2nd line
        line_parts = split_Sberbank_line(lines[1])

        if len(line_parts) < 3 or len(line_parts) > 4:
            raise exceptions.Bank2ExcelError(
                "Line is expected to have 3 or 4 parts :" + str(lines[1]))

        # print(line_parts[0])

        # processing_date__authorisation_code = re.search(r'(dd\.dd\.dddd)\s(.*)', line_parts[0])
        result['processing_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%Y')

        result['authorisation_code'] = line_parts[1]
        result['category'] = line_parts[2]

        # Выделяем сумму в валюте оперции, если присуиствует
        if len(line_parts) == 4:
            found = re.search(r'(.*?)\s(\S*)',
                              line_parts[3])  # processing string like '6,79 €'
            if found:
                result['value_operational_currency'] = get_float_from_money(found.group(1))
                result['operational_currency'] = found.group(2)
            else:
                raise exceptions.InputFileStructureError(
                    "Ошибка в обработке текста. Ожидалась структура типа '6,79 €', получено: " +
                    line_parts[3])

        # ************** looking at the 3rd line
        if len(lines) == 3:
            line_parts = split_Sberbank_line(lines[2])
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
                'description': 'НАЗВАНИЕ ОПЕРАЦИИ',
                'category': 'Категория',
                'value_account_currency': 'СУММА В ВАЛЮТЕ СЧЁТА',
                'value_operational_currency': 'Сумма в валюте операции',
                'operational_currency': 'Валюта операции',
                'remainder_account_currency': 'Остаток по счёту в валюте счёта'
                }


if __name__ == '__main__':


    if len(sys.argv) < 2:
        print('Не указано имя текстового файла для проверки экстрактора')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(SBER_PAYMENT_2208,
                                           test_text_file_name=sys.argv[1])



