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

def test_correctly_converts_SBER_SAVING_2303_USD_pdf():
    sberbankPDF2Excel(no_github_module.SBER_SAVING_2303_USD_pdf)
    
def test_correctly_converts_SBER_DEBIT_2303_CHELYABINSK_pdf():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2303_CHELYABINSK_pdf)

def test_correctly_converts_SBER_PAYMENT_2212_issue_31_simulation_txt():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2212_issue_31_simulation_txt)
    
def test_correctly_converts_SBER_DEBIT_2212_issue_33_txt():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_issue_33_txt)

def test_correctly_converts_SBER_SAVING_2303_Activnoe_dolgolitie_issue_35_txt():
    sberbankPDF2Excel(no_github_module.SBER_SAVING_2303_Activnoe_dolgolitie_issue_35_txt)
    
def test_correctly_converts_SBER_DEBIT_2212_issue_36_txt():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_issue_36_txt)
    
def test_correctly_converts_SBER_DEBIT_2212_theoretical_case_for_issue_36_manually_created_line_22_txt():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_issue_36_theoretical_case_txt)
    
def test_correctly_converts_SBER_DEBIT_2212_v20240413_issue_39():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2212_v20240413_issue_39)
    
def test_correctly_converts_SBER_PAYMENT_2406_20231001_20240628_issue_42():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2406_20231001_20240628_issue_42)

# SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44

def test_correctly_converts_SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44():
    sberbankPDF2Excel(no_github_module.SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44)
    
def test_correctly_converts_SBER_SAVING2407_issue47():
    sberbankPDF2Excel(no_github_module.SBER_SAVING_2407_issue47)
    
def test_correctly_converts_SBER_DEBIT_2408_issue_48():
    sberbankPDF2Excel(no_github_module.SBER_DEBIT_2408_issue_48)