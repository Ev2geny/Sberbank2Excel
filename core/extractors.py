"""
This module lists all extractor calsses available
It shall be edited with every new extractor class created
"""

extractors_list = []

from extractor_SBER_DEBIT_2107 import SBER_DEBIT_2107
extractors_list.append(SBER_DEBIT_2107)

from extractor_SBER_DEBIT_2005 import SBER_DEBIT_2005
extractors_list.append(SBER_DEBIT_2005)