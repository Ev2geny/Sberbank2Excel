from pathlib import Path

import pytest

from Sberbank2Excel import exceptions
from Sberbank2Excel.sberbankPDF2Excel import sberbankPDF2Excel


"""
no_github_module.py contains information, which is not shared via github due to confidential nature

Its structure is following:

SBER_DEBIT_old_not_supported_pdf = r"Path to some file on the drive"

SBER_DEBIT_2005_pdf = r"Path to some other file on the drive"
...

"""

HERE = Path(__file__).parent 

TEST_DATA: Path = HERE / "test_data" # A directory with test data files


@pytest.mark.private
def test_correctly_converts_SBER_CREDIT_2110_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2110_file_name_text)

class Test_SBER_DEBIT_2107:

    @pytest.mark.private
    def test_correctly_converts_SBER_DEBIT_2107_pdf(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2107_pdf)
        
    def test_correctly_converts_SBER_DEBIT_2107_txt_anonim(self):
        sberbankPDF2Excel(str(TEST_DATA / "_SBER_DEBIT_2107_anonymized_reduced.txt"))

    @pytest.mark.private
    def test_correctly_converts_SBER_DEBIT_2107_Tinkoff_problem_pdf(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2107_Tinkoff_problem_pdf)

@pytest.mark.private
def test_correctly_balance_error_SBER_DEBIT_2107_pdf():
    from . import no_github_module
    with pytest.raises(exceptions.BalanceVerificationError):
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2107_wrong_balance_txt)

@pytest.mark.private
def test_correctly_converts_SBER_DEBIT_2005_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2005_pdf)

@pytest.mark.private
def test_correctly_does_not_convert_SBER_DEBIT_old_not_supported():
    from . import no_github_module
    with pytest.raises(exceptions.InputFileStructureError):
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_old_not_supported_pdf)

@pytest.mark.private
def test_correctly_converts_SBER_PAYMENT_2208_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2208_txt)

@pytest.mark.private
def test_correctly_converts_SBER_PAYMENT_2212_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2212_pdf)

@pytest.mark.private
def test_correctly_converts_SBER_DEBIT_2212_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2212_pdf)

@pytest.mark.private
def test_correctly_converts_SBER_SAVING_2303_EURO_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_SAVING_2303_EURO_pdf)

@pytest.mark.private
def test_correctly_converts_SBER_SAVING_2303_USD_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_SAVING_2303_USD_pdf)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2303_CHELYABINSK_pdf():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2303_CHELYABINSK_pdf)

@pytest.mark.private
def test_correctly_converts_SBER_PAYMENT_2212_issue_31_simulation_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2212_issue_31_simulation_txt)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2212_issue_33_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2212_issue_33_txt)

@pytest.mark.private
def test_correctly_converts_SBER_SAVING_2303_Activnoe_dolgolitie_issue_35_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_SAVING_2303_Activnoe_dolgolitie_issue_35_txt)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2212_issue_36_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2212_issue_36_txt)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2212_theoretical_case_for_issue_36_manually_created_line_22_txt():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2212_issue_36_theoretical_case_txt)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2212_v20240413_issue_39():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2212_v20240413_issue_39)

@pytest.mark.private    
def test_correctly_converts_SBER_PAYMENT_2406_20231001_20240628_issue_42():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2406_20231001_20240628_issue_42)

# SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44

@pytest.mark.private
def test_correctly_converts_SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2407__MIR_20240803__20240101_20240801_issue_44)

@pytest.mark.private    
def test_correctly_converts_SBER_PAYMENT_2407_issue52():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2407_issue52)

@pytest.mark.private    
def test_correctly_converts_SBER_SAVING2407_issue47():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_SAVING_2407_issue47)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2408_issue_48():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2408_issue_48)
    
class Test_SBER_CREDIT_2409:    
    
    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2409_issue_50(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2409_issue_50)
    
    @pytest.mark.private    
    def test_correctly_converts_SBER_CREDIT_2409_issue_54(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2409_issue_54)
    
    @pytest.mark.private    
    def test_does_not_convert_wrong_SBER_CREDIT_2409_issue_54(self):
        from . import no_github_module
        with pytest.raises(RuntimeError) as excinfo:
            sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2409_issue_54_wrong)
            
        assert isinstance(excinfo.value.__cause__, exceptions.InputFileStructureError)

    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2409_issue_56_simulated_txt(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2409_issue_56_simulated_txt)

@pytest.mark.private    
def test_correctly_converts_SBER_DEBIT_2510_issue_69():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2510_issue_69)
    
@pytest.mark.private    
def test_correctly_converts_SBER_PAYMENT_2510():
    from . import no_github_module
    sberbankPDF2Excel(no_github_module.path2_SBER_PAYMENT_2510_issue70)
    
class Test_SBER_CREDIT_2511:
    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2511_pdf(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2511_pdf)
        
    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2511_simulate_local_currency(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2511_simulate_local_currency)
        
    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2511_simulate_more_lines(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2511_simulate_more_lines)
        
    @pytest.mark.private
    def test_correctly_converts_SBER_CREDIT_2511_issue_79(self):
        from . import no_github_module
        sberbankPDF2Excel(no_github_module.path2_SBER_CREDIT_2511_issue_79)

if __name__ == "__main__":
    print("Running tests")
