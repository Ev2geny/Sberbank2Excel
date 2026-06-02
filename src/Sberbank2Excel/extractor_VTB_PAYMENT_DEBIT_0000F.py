import re
from datetime import datetime
import sys
from decimal import Decimal
from typing import Any, List, Dict, Optional

from Sberbank2Excel import exceptions
from Sberbank2Excel.utils import get_decimal_from_money
from Sberbank2Excel.extractor import Extractor
from Sberbank2Excel import extractors_generic


class VTB_PAYMENT_DEBIT_0000F(Extractor):

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

    def check_support(self) -> bool:
        return True

    def get_period_balance(self) -> Decimal:
        """
        Извлекает итоговый баланс на конец периода из строки "Баланс на конец периода".
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
        Разделяет текст выписки на отдельные транзакции.
        Каждая транзакция начинается со строки вида:
        ДД.ММ.ГГГГ   Приход   Расход   Комиссия   Описание...
        """
        # Находим начало блока операций
        start_marker = 'Операции по счёту'
        start_idx = self.bank_text.find(start_marker)
        if start_idx == -1:
            raise exceptions.InputFileStructureError(
                'Не найден раздел "Операции по счёту"'
            )
        # Конец выписки – последняя фраза
        end_marker = 'Спасибо, что Вы с нами!'
        end_idx = self.bank_text.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(self.bank_text)

        operations_text = self.bank_text[start_idx:end_idx]

        # Удаляем строки-заголовки таблицы, номера страниц и т.п.
        header_patterns = [
            r'Сумма операции в валюте\s*',
            r'счета/карты\s*',
            r'Дата и время\s+Дата обработки\s+Сумма операции в\s*',
            r'Комиссия\s+Описание операции\s*',
            r'операции\s+банком\s+валюте операции\s*',
            r'Приход\s+Расход\s*',
            r'Продолжение на следующей странице\s*',
            r'^[ ]*\d+[ ]*$',             # одинокие номера страниц (например, "1")
        ]
        for pat in header_patterns:
            operations_text = re.sub(pat, '', operations_text, flags=re.MULTILINE)

        # Паттерн начала транзакции: дата + три денежные суммы + начало описания
        # Суммы могут содержать разделители тысяч (пробелы/запятые)
        start_pattern = re.compile(
            r'^(\d{2}\.\d{2}\.\d{4})\s+'                 # дата операции (только дата, без времени)
            r'(\d[\d\s,]*\.\d{2})\s+'                    # Приход
            r'(\d[\d\s,]*\.\d{2})\s+'                    # Расход
            r'(\d[\d\s,]*\.\d{2})\s+'                    # Комиссия
            r'(.*)',                                     # начало описания
            re.MULTILINE
        )

        # Ищем все начала транзакций
        starts = list(start_pattern.finditer(operations_text))
        if not starts:
            raise exceptions.InputFileStructureError(
                "Не найдено ни одной транзакции в формате ВТБ"
            )

        entries = []
        for i, match in enumerate(starts):
            block_start = match.start()
            block_end = starts[i + 1].start() if i + 1 < len(starts) else len(operations_text)
            block = operations_text[block_start:block_end].strip()
            entries.append(block)

        return entries

    def decompose_entry_to_dict(self, entry: str) -> dict:
        """
        Разбирает блок одной транзакции в словарь.
        """
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if len(lines) < 3:
            raise exceptions.InputFileStructureError(
                f"Ожидалось минимум 3 строки в блоке транзакции:\n{entry}"
            )

        # ---- Первая строка: дата, приход, расход, комиссия, описание (начало) ----
        first_line = lines[0]
        m1 = re.match(
            r'^(\d{2}\.\d{2}\.\d{4})\s+'
            r'(\d[\d\s,]*\.\d{2})\s+'
            r'(\d[\d\s,]*\.\d{2})\s+'
            r'(\d[\d\s,]*\.\d{2})\s+'
            r'(.*)',
            first_line
        )
        if not m1:
            raise exceptions.InputFileStructureError(
                f"Не удалось разобрать первую строку транзакции:\n{first_line}"
            )
        operation_date_str = m1.group(1)  # только дата
        income = get_decimal_from_money(m1.group(2))
        expense = get_decimal_from_money(m1.group(3))
        commission = get_decimal_from_money(m1.group(4))
        description_start = m1.group(5).strip()

        # ---- Вторая строка: дата обработки, сумма в валюте операции ----
        second_line = lines[1]
        m2 = re.match(
            r'^(\d{2}\.\d{2}\.\d{4})\s+'
            r'(-?[\d\s,]+\.\d{2})\s+'
            r'([A-Z]{3})',
            second_line
        )
        if not m2:
            raise exceptions.InputFileStructureError(
                f"Не удалось разобрать вторую строку транзакции:\n{second_line}"
            )
        processing_date_str = m2.group(1)
        oper_amount = get_decimal_from_money(m2.group(2))
        oper_currency = m2.group(3)

        # ---- Третья строка: время, валютные коды (опционально), описание (продолжение) ----
        third_line = lines[2]
        m3 = re.match(
            r'^(\d{2}:\d{2}:\d{2})\s+'
            r'(?:[A-Z]{3}\s+[A-Z]{3}\s+)?'   # иногда "RUB RUB"
            r'(.*)',
            third_line
        )
        if not m3:
            raise exceptions.InputFileStructureError(
                f"Не удалось разобрать третью строку транзакции:\n{third_line}"
            )
        time_str = m3.group(1)
        description_cont = m3.group(2).strip()

        # Полная дата операции
        full_operation_date = datetime.strptime(
            f"{operation_date_str} {time_str}", '%d.%m.%Y %H:%M:%S'
        )
        processing_date = datetime.strptime(processing_date_str, '%d.%m.%Y').date()

        # Собираем описание
        description_parts = [description_start, description_cont]
        # Добавляем все оставшиеся строки (если есть)
        for extra_line in lines[3:]:
            description_parts.append(extra_line)
        full_description = ' '.join(filter(None, description_parts))

        # Вычисляем сумму в валюте счёта (приход – расход)
        value_account_currency = income - expense

        # Пытаемся выделить категорию (первая фраза до точки)
        category = ''
        if '. ' in full_description:
            category = full_description.split('. ')[0].strip()
        else:
            # если нет точки, берём первые несколько слов
            words = full_description.split()
            category = ' '.join(words[:3]) if words else ''

        return {
            'operation_date': full_operation_date,
            'processing_date': processing_date,
            'value_operational_currency': oper_amount,
            'operational_currency': oper_currency,
            'commission': commission,
            'value_account_currency': value_account_currency,
            'category': category,
            'description': full_description,
        }

    def get_column_name_for_balance_calculation(self) -> str:
        """
        Имя поля, используемое для вычисления итогового баланса периода.
        """
        return 'value_account_currency'

    def get_columns_info(self) -> dict:
        """
        Возвращает сопоставление внутренних ключей → названия колонок для Excel.
        """
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