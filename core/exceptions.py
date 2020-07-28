
class SberbankPDFtext2ExcelError(Exception):
    #TODO: replace usage of this generic error for more spesific
    pass

class InputFileStructureError(SberbankPDFtext2ExcelError):
    pass

class BalanceVerificationError(SberbankPDFtext2ExcelError):
    pass