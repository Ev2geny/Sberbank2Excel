
class Bank2ExcelError(Exception):
    #TODO: replace usage of this generic error for more spesific
    pass

class InputFileStructureError(Bank2ExcelError):
    pass

class BalanceVerificationError(Bank2ExcelError):
    pass

class UserInputError(Bank2ExcelError):
    pass

class TestingError(Bank2ExcelError):
    pass

class InternalLogicError(Bank2ExcelError):
    pass