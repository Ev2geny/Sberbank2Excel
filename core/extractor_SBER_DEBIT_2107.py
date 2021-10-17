import exceptions
import re
from datetime import datetime
from pprint import pprint


from utils import get_float_from_money
from utils import split_Sberbank_line

from extractor import Extractor

class SBER_DEBIT_2107(Extractor):

    def check_specific_signatures(self):

        test1 = re.search(r'сбербанк', self.pdf_text, re.IGNORECASE)
        # print(f"{test1=}")

        test2 = re.search(r'Выписка по счёту дебетовой карты', self.pdf_text, re.IGNORECASE)
        # print(f"{test2=}")

        if not test1  or not test2:
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")

    def get_period_balance(self)->str:
        """
        функция ищет в тексте значения "ВСЕГО СПИСАНИЙ" и "ВСЕГО ПОПОЛНЕНИЙ" и возвращает разницу
        используется для контрольной проверки вычислений

        Пример текста
        ----------------------------------------------------------
        ОСТАТОК НА 30.06.2021     ОСТАТОК НА 06.07.2021     ВСЕГО СПИСАНИЙ     ВСЕГО ПОПОЛНЕНИЙ
        28 542,83->12 064,34->248 822,49->232 344,00
        ----------------------------------------------------------

        :param PDF_text:
        :return:
        """

        res = re.search(r'ОСТАТОК НА.*?ОСТАТОК НА.*?ВСЕГО СПИСАНИЙ.*?ВСЕГО ПОПОЛНЕНИЙ.*?\n(.*?)\n', self.pdf_text, re.MULTILINE)
        if not res:
            raise exceptions.InputFileStructureError(
                'Не найдена структура с остатками и пополнениями')

        line_parts = res.group(1).split('\t')

        summa_spisaniy = line_parts[2]
        summa_popolneniy = line_parts[3]

        # print('summa_spisaniy ='+summa_spisaniy)
        # print('summa_popolneniy =' + summa_popolneniy)

        summa_popolneniy = get_float_from_money(summa_popolneniy)
        summa_spisaniy = get_float_from_money(summa_spisaniy)

        return summa_popolneniy - summa_spisaniy

    def split_text_on_entries(self)->list[str]:
        """
        разделяет текстовый файл формата 2107_Stavropol на отдельные записи

        пример одной записи
    ------------------------------------------------------------------------------------------------------
        03.07.2021 12:52 -> Перевод с карты -> 3 500,00 -> 28 655,30
        03.07.2021 123456 -> SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
    ------------------------------------------------------------------------------------------------------

        либо такой
    --------------------------------------------------------------------------------------------------
        28.06.2021 00:00 -> Неизвестная категория(+) -> +21107,75 -> 22113,73
        28.06.2021 - -> Прочие выплаты
    ----------------------------------------------------------------------------------------------------

        либо такой с иностранной вылютой
    ---------------------------------------------------------------------------------------------------------
        08.07.2021 18:27 -> Все для дома     193,91     14593,30
        09.07.2021 254718 -> XXXXX XXXXX -> 2,09 €
    ---------------------------------------------------------------------------------------------------------

        ещё один пример (с 3 линиями)
        ---------------------------------------------------------------------------------------------------------
        03.07.2021 11:54 -> Перевод с карты -> 4 720,00 -> 45 155,30
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
                                        self.pdf_text, re.VERBOSE)

        if len(individual_entries) == 0:
            raise exceptions.InputFileStructureError(
                "Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")

        # for entry in individual_entries:
        #     print(entry)

        return individual_entries

    def decompose_entry_to_dict(self, entry:str)->dict:
        """
        Выделяем данные из одной записи в dictionary

    ------------------------------------------------------------------------------------------------------
        03.07.2021 12:52 -> Перевод с карты -> 3 500,00 -> 28 655,30
        03.07.2021 123456 -> SBOL перевод 1234****1234 Н. ИГОРЬ РОМАНОВИЧ
    ------------------------------------------------------------------------------------------------------

        либо такой
    --------------------------------------------------------------------------------------------------
        28.06.2021 00:00 -> Неизвестная категория(+)     +21107,75     22113,73
        28.06.2021 - -> Прочие выплаты
    ----------------------------------------------------------------------------------------------------

        ещё один пример (с 3 линиями)
        ---------------------------------------------------------------------------------------------------------
        03.07.2021 11:54 -> Перевод с карты -> 4 720,00 -> 45 155,30
        03.07.2021 258077 -> SBOL перевод 1234****5678 А. ВАЛЕРИЯ
        ИГОРЕВНА
        ----------------------------------------------------------------------------------------------------------

        либо такой с иностранной вылютой
    ---------------------------------------------------------------------------------------------------------
        08.07.2021 18:27 -> Все для дома -> 193,91 -> 14593,30
        09.07.2021 -> 254718 -> XXXXX XXXXX -> 2,09 €
    ---------------------------------------------------------------------------------------------------------

        В последнем примере:

    {'authorisation_code': '254718',
     'category': 'Все для дома',
     'description': 'XXXXX XXXXX',
     'operation_date': '08.07.2021 18:27',
     'processing_date': '09.07.2021',
     'remainder_account_currency': 14593.30,
     'value_account_currency': -193.91б
     'operational_currency': '€'
     }
        """
        lines = entry.split('\n')
        lines = list(filter(None, lines))

        if len(lines) < 2 or len(lines) > 3:
            raise exceptions.InputFileStructureError(
                "entry is expected to have from 2 to 3 lines\n" + str(entry))

        result = {}
        # ************** looking at the 1st line
        line_parts = split_Sberbank_line(lines[0])

        # print( f"1st line line_parts {line_parts}")

        result['operation_date'] = line_parts[0] + " " + line_parts[1]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['operation_date'] = datetime.strptime(result['operation_date'], '%d.%m.%Y %H:%M')

        result['category'] = line_parts[2]
        result['value_account_currency'] = get_float_from_money(line_parts[3],
                                                                True)
        result['remainder_account_currency'] = get_float_from_money(
            line_parts[4])

        # ************** looking at the 2nd line
        line_parts = split_Sberbank_line(lines[1])

        if len(line_parts) < 3 or len(line_parts) > 4:
            raise exceptions.SberbankPDF2ExcelError(
                "Line is expected to have 3 or 4 parts :" + str(lines[1]))

        # print(line_parts[0])

        # processing_date__authorisation_code = re.search(r'(dd\.dd\.dddd)\s(.*)', line_parts[0])
        result['processing_date'] = line_parts[0]
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        result['processing_date'] = datetime.strptime(result['processing_date'], '%d.%m.%Y')

        result['authorisation_code'] = line_parts[1]
        result['description'] = line_parts[2]

        # Выделяем сумму в валюте оперции, если присуиствует
        if len(line_parts) == 4:
            found = re.search(r'(.*?)\s(\S*)',
                              line_parts[3])  # processing string like '6,79 €'
            if found:
                result['value_operational_currency'] = get_float_from_money(
                    found.group(1), True)
                result['operational_currency'] = found.group(2)
            else:
                raise exceptions.InputFileStructureError(
                    "Ошибка в обработке текста. Ожидалась струтура типа '6,79 €', получено: " +
                    line_parts[3])

        # ************** looking at the 3rd line
        if len(lines) == 3:
            line_parts = split_Sberbank_line(lines[2])
            result['description'] = result['description'] + ' ' + line_parts[0]

        # print(result)

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
                'category': 'Категория',
                'value_account_currency': 'Сумма в валюте счёта',
                'value_operational_currency': 'Сумма в валюте операции',
                'operational_currency': 'Валюта операции',
                'remainder_account_currency': 'Остаток по счёту в валюте счёта'}


if __name__ == '__main__':

    txt_file = r'C:\_code\py\Sberbank2Excel_no_github\20210724_20210720_20210724_2107_Stavropol_.txt'

    with open(txt_file, encoding='utf-8') as f:
        txt_file_content = f.read()

    converter = SBER_DEBIT_2107(txt_file_content)

    converter.check_specific_signatures()

    print(f"period_balance = {converter.get_period_balance()}")

    for entry in converter.get_entries():
        print('*'*20)
        pprint(entry)

    print(f"check_support = {converter.check_support()}")