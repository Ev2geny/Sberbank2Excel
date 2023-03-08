"""
This module lists all extractor calsses available
It shall be edited with every new extractor class created
"""

extractors_list = []

from extractor_SBER_DEBIT_2107 import SBER_DEBIT_2107
extractors_list.append(SBER_DEBIT_2107)

from extractor_SBER_DEBIT_2005 import SBER_DEBIT_2005
extractors_list.append(SBER_DEBIT_2005)

from extractor_SBER_CREDIT_2110 import SBER_CREDIT_2107
extractors_list.append(SBER_CREDIT_2107)

# from core.extractor_SBER_DEBIT_2111_VISA_draft import  SBER_DEBIT_2111_VISA
# extractors_list.append(SBER_DEBIT_2111_VISA)

from extractor_SBER_PAYMENT_2212 import SBER_PAYMENT_2212
extractors_list.append(SBER_PAYMENT_2212)

from extractor_SBER_PAYMENT_2208 import SBER_PAYMENT_2208
extractors_list.append(SBER_PAYMENT_2208)

from extractor_SBER_DEBIT_2212 import SBER_DEBIT_2212
extractors_list.append(SBER_DEBIT_2212)

from extractor_SBER_SAVING_2303 import SBER_SAVING_2303
extractors_list.append(SBER_SAVING_2303)


def get_list_extractors_in_text():
    return [extractor.__name__ for extractor in extractors_list]

