# Created-By: FazziCLAY (fazziclay@gmail.com)
# SPDX-FileContributor: Tool: DeepSeek
# Конвертирует выписку по счёту дебетовой карты банка ВТБ, работает ТОЛЬКО с текстом библиотеки pypdf

import re
from datetime import datetime
import sys
from decimal import Decimal
from typing import List

from Sberbank2Excel import exceptions
from Sberbank2Excel.utils import get_decimal_from_money
from Sberbank2Excel.extractor import Extractor
from Sberbank2Excel import extractors_generic


class VTB_PAYMENT_DEBIT_0000F(Extractor):

    def check_pdf_lib_support(self, pdf_lib: str):
        if pdf_lib != "pypdf":
            raise exceptions.PdfLibNotSupported(
                "Для конвертации ЭТОЙ выписки переключите pdflib на [pypdf]"
            )

    def check_specific_signatures(self):
        """
        Проверяет наличие характерных для выписки ВТБ фрагментов.
        """
        test_vtb = re.search(r'Банк ВТБ \(ПАО\)', self.bank_text, re.IGNORECASE)
        test_operations = re.search(r'Операции по счёту', self.bank_text, re.IGNORECASE)
        if test_vtb and test_operations:
            return
        raise exceptions.InputFileStructureError(
            "Не найдены паттерны, соответствующие выписке ВТБ"
        )

    def get_period_balance(self) -> Decimal:
        """
        Извлекает итоговый баланс на конец периода.
        """
        match = re.search(
            r'Баланс на конец периода\s+([\d\s]+\.\d{2})\s+RUB',
            self.bank_text
        )
        if not match:
            raise exceptions.InputFileStructureError(
                'Не найдена строка "Баланс на конец периода"'
            )
        return get_decimal_from_money(match.group(1))

    def split_text_on_entries(self) -> List[str]:
        """
        Разбирает текст (выгрузка pypdf), где транзакция состоит из:
        - одной строки с датой операции,
        - строки с временем, датой обработки, суммой в валюте, валютой и приходом,
        - двух строк RUB и расхода,
        - строки RUB и комиссии,
        - произвольного количества строк описания.
        Удаляет повторяющиеся заголовки, разделители страниц и номера страниц.
        """
        start_marker = 'Операции по счёту'
        start_idx = self.bank_text.find(start_marker)
        if start_idx == -1:
            raise exceptions.InputFileStructureError(
                'Не найден раздел "Операции по счёту"'
            )
        end_marker = 'Спасибо, что Вы с нами!'
        end_idx = self.bank_text.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(self.bank_text)
        text = self.bank_text[start_idx:end_idx]

        lines = text.split('\n')
        cleaned = []
        # шаблоны строк, которые нужно полностью игнорировать
        skip_patterns = [
            r'^\s*$',                          # пустые
            r'^\s*\d+\s*$',                    # номера страниц
            r'^\-+\s*PAGE\s*DEVIDER\s*\-+',   # разделители
            r'^Дата\s+и\s+время',
            r'^операции',
            r'^Дата\s+обработки',
            r'^банком',
            r'^Сумма\s+операции\s+в',
            r'^валюте\s+операции',
            r'^счета/карты',
            r'^Комиссия\s+Описание\s+операции',
            r'^Приход\s+Расход',
        ]
        for line in lines:
            s = line.strip()
            if any(re.match(p, s) for p in skip_patterns):
                continue
            cleaned.append(s)

        # Паттерн даты на отдельной строке (ДД.ММ.ГГГГ)
        date_line_re = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
        # Паттерн второй строки: время, дата обработки, сумма в валюте, валюта, приход
        second_line_re = re.compile(
            r'^(\d{2}:\d{2}:\d{2})\s+'
            r'(\d{2}\.\d{2}\.\d{4})\s+'
            r'(-?[\d\s,]+\.\d{2})\s+'
            r'([A-Z]{3})\s+'
            r'(-?\d[\d\s,]*(?:\.\d{2})?)$'
        )

        entries = []
        i = 0
        while i < len(cleaned):
            # ищем начало блока: дата на строке i И минимум 6 строк впереди
            if date_line_re.match(cleaned[i]) and i + 6 <= len(cleaned):
                if second_line_re.match(cleaned[i + 1]):
                    block_start = i
                    # блок включает все строки с i до следующей даты (или конца)
                    j = i + 6  # минимум 6 строк
                    while j < len(cleaned) and not date_line_re.match(cleaned[j]):
                        j += 1
                    block = '\n'.join(cleaned[block_start:j])
                    entries.append(block)
                    i = j
                    continue
            i += 1

        if not entries:
            raise exceptions.InputFileStructureError(
                "Не найдено ни одной транзакции в формате ВТБ (pypdf)"
            )
        return entries

    def decompose_entry_to_dict(self, entry: str) -> dict:
        """
        Разбирает блок транзакции.
        Структура (может быть нарушена артефактами pypdf):
        0: дата операции
        1: время дата_обработки сумма_в_валюте валюта приход
        2.. : последовательность RUB / число / RUB / число, затем описание
        """
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if len(lines) < 4:
            raise exceptions.InputFileStructureError(
                f"Ожидалось минимум 4 строки в блоке:\n{entry}"
            )

        def parse_amount(text: str) -> Decimal:
            cleaned = text.replace(' ', '').replace(',', '')
            return Decimal(cleaned)

        # строка 0: дата
        operation_date_str = lines[0]

        # строка 1: время, дата обработки, сумма в валюте, валюта, приход
        m = re.match(
            r'^(\d{2}:\d{2}:\d{2})\s+'
            r'(\d{2}\.\d{2}\.\d{4})\s+'
            r'(-?[\d\s,]+\.\d{2})\s+'
            r'([A-Z]{3})\s+'
            r'(-?\d[\d\s,]*(?:\.\d{2})?)$',
            lines[1]
        )
        if not m:
            raise exceptions.InputFileStructureError(
                f"Ошибка разбора второй строки блока:\n{lines[1]}"
            )
        time_str = m.group(1)
        processing_date_str = m.group(2)
        oper_amount = parse_amount(m.group(3))
        oper_currency = m.group(4)
        income = parse_amount(m.group(5))

        # Обрабатываем оставшиеся строки (со 2-й и дальше)
        tail = lines[2:]
        expense = Decimal('0')
        commission = Decimal('0')
        description_lines = []

        # Ищем последовательность: RUB, число, RUB, число (любое может быть пропущено)
        idx = 0
        # Первый RUB (может отсутствовать, если строка уже число)
        if idx < len(tail) and re.fullmatch(r'RUB', tail[idx], re.IGNORECASE):
            idx += 1
        # Число расхода (или RUB, если число пропущено)
        if idx < len(tail):
            if re.fullmatch(r'RUB', tail[idx], re.IGNORECASE):
                idx += 1
                # расход остаётся 0
            else:
                # пробуем распарсить число
                try:
                    expense = parse_amount(tail[idx])
                    idx += 1
                except Exception:
                    # если не число и не RUB – это уже описание
                    pass
        # Второй RUB
        if idx < len(tail) and re.fullmatch(r'RUB', tail[idx], re.IGNORECASE):
            idx += 1
        # Число комиссии (или RUB, если число пропущено)
        if idx < len(tail):
            if re.fullmatch(r'RUB', tail[idx], re.IGNORECASE):
                idx += 1
                # комиссия остаётся 0
            else:
                try:
                    commission = parse_amount(tail[idx])
                    idx += 1
                except Exception:
                    pass

        # Всё, что осталось – описание
        description_lines = tail[idx:]
        description = ' '.join(description_lines)

        full_operation_date = datetime.strptime(
            f"{operation_date_str} {time_str}", '%d.%m.%Y %H:%M:%S'
        )
        processing_date = datetime.strptime(processing_date_str, '%d.%m.%Y').date()

        value_account_currency = income - expense

        category = ''
        if description and '. ' in description:
            category = description.split('. ')[0].strip()
        elif description:
            words = description.split()
            category = ' '.join(words[:3]) if words else ''

        return {
            'operation_date': full_operation_date,
            'processing_date': processing_date,
            'value_operational_currency': oper_amount,
            'operational_currency': oper_currency,
            'commission': commission,
            'value_account_currency': value_account_currency,
            'category': category,
            'description': description,
        }

    def get_column_name_for_balance_calculation(self) -> str:
        return 'value_account_currency'

    def get_columns_info(self) -> dict:
        return {
            'operation_date': 'Дата и время операции',
            'processing_date': 'Дата обработки банком',
            'value_operational_currency': 'Сумма в валюте операции',
            'operational_currency': 'Валюта операции',
            'commission': 'Комиссия',
            'value_account_currency': 'Сумма в валюте счёта',
            'category': 'Категория',
            'description': 'Описание операции',
        }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Укажите имя текстового файла для проверки экстрактора')
        print(__doc__)
    else:
        extractors_generic.debug_extractor(
            VTB_PAYMENT_DEBIT_0000F,
            test_text_file_name=sys.argv[1]
        )