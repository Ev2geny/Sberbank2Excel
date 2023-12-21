import pytest
import exceptions
from sberbankPDF2Excel import sberbankPDF2Excel


import no_github_module
"""
no_github_module.py contains information, which is not shared via github due to confidential nature

Its structure is following:

SBER_DEBIT_old_not_supported_pdf = r"Path to some file on the drive"

SBER_DEBIT_2005_pdf = r"Path to some other file on the drive"
...

"""

def test_correctly_converts_SBER_CREDIT_2110_txt():
    sberbankPDF2Excel(no_github_module.SBER_CREDIT_2110_file_name_text)

def test_correctly_converts_SBER_DEBIT_2107_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2107_pdf)

def test_correctly_converts_SBER_DEBIT_2107_Tinkoff_problem_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2107_Tinkoff_problem_pdf)

def test_correctly_balance_error_SBER_DEBIT_2107_pdf():
    with pytest.raises(exceptions.BalanceVerificationError):
        sberbankPDF2Excel(no_github_module.SBER_DEBIT_2107_wrong_balance_txt)

def test_correctly_converts_SBER_DEBIT_2005_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2005_pdf)

def test_correctly_does_not_convert_SBER_DEBIT_old_not_supported():
    with pytest.raises(exceptions.InputFileStructureError):
        sberbankPDF2Excel(no_github_module.SBER_DEBIT_old_not_supported_pdf)

def test_correctly_converts_SBER_PAYMENT_2208_txt():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2208_txt)

def test_correctly_converts_SBER_PAYMENT_2212_pdf():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2212_pdf)

def test_correctly_converts_SBER_DEBIT_2212_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_pdf)

def test_correctly_converts_SBER_SAVING_2303_EURO_pdf():
    sberbankPDF2Excel(no_github_module.SBER_SAVING_2303_EURO_pdf)
    
def test_correctly_converts_SBER_DEBIT_2303_CHELYABINSK_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2303_CHELYABINSK_pdf)

def test_correctly_converts_SBER_PAYMENT_2212_issue_31_simulation_txt():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2212_issue_31_simulation_txt)
    
def test_correctly_converts_SBER_DEBIT_2212_issue_33_txt():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_issue_33_txt)

# SBER_DEBIT_2303_CHELYABINSK_pdf

# SBER_SAVING_2303_EURO_pdf