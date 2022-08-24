import pytest
import exceptions
from sberbankPDF2Excel import sberbankPDF2Excel


import no_github_module_import

def test_correctly_converts_SBER_CREDIT_2110_txt():
    sberbankPDF2Excel(no_github_module_import.SBER_CREDIT_2110_file_name_text)

def test_correctly_converts_SBER_DEBIT_2107_pdf():
    sberbankPDF2Excel(no_github_module_import.SBER_DEBIT_2107_pdf)

def test_correctly_converts_SBER_DEBIT_2107_Tinkoff_problem_pdf():
    sberbankPDF2Excel(no_github_module_import.SBER_DEBIT_2107_Tinkoff_problem_pdf)

def test_correctly_balance_error_SBER_DEBIT_2107_pdf():
    with pytest.raises(exceptions.BalanceVerificationError):
        sberbankPDF2Excel(no_github_module_import.SBER_DEBIT_2107_wrong_balance_txt)

def test_correctly_converts_SBER_DEBIT_2005_pdf():
    sberbankPDF2Excel(no_github_module_import.SBER_DEBIT_2005_pdf)

def test_correctly_does_not_convert_SBER_DEBIT_old_not_supported():
    with pytest.raises(exceptions.InputFileStructureError):
        sberbankPDF2Excel(no_github_module_import.SBER_DEBIT_old_not_supported_pdf)

def test_correctly_converts_SBER_PAYMENT_2208_txt():
    sberbankPDF2Excel(no_github_module_import.SBER_PAYMENT_2208_txt)
