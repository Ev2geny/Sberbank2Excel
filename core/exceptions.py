
class SberbankPDF2ExcelError(Exception):
    #TODO: replace usage of this generic error for more spesific
    pass

class InputFileStructureError(SberbankPDF2ExcelError):
    pass

class BalanceVerificationError(SberbankPDF2ExcelError):
    pass

class UserInputError(SberbankPDF2ExcelError):
    pass