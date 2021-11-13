"""
this module simply imports information, defined in the module no_github_module.py

This module is only needed for testing

no_github_module.py contains information, which is not shared via github due to confidential nature

Its structure is following:

SBER_DEBIT_old_not_supported_pdf = r"Path to some file on the drive"

SBER_DEBIT_2005_pdf = r"Path to some other file on the drive"
...

"""
from no_github_module import SBER_DEBIT_old_not_supported_pdf

from no_github_module import SBER_DEBIT_2005_pdf

from no_github_module import SBER_DEBIT_2107_pdf
from no_github_module import SBER_DEBIT_2107_wrong_balance_txt
from no_github_module import SBER_DEBIT_2107_Tinkoff_problem_pdf

from no_github_module import SBER_CREDIT_2110_file_name_text
