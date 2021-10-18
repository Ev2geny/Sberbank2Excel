"""
Code, generic for extractors functionality
"""
import logging
from pprint import pprint

from extractors import extractors_list
import exceptions

from extractor import Extractor

def determine_extractor_auto(pdf_text:str) -> type:
    """
    Function determines which extractor to use with this particular text representation of PDF extract

    pdf_text:str: text representation of PDF extract

    returns:
        reference to a calss of a supported extractor
    """
    global extractors_list # type list[Extractor]

    supported_extractors = [extractor for extractor in extractors_list if extractor(pdf_text).check_support()]

    if len(supported_extractors) == 0:
        raise exceptions.InputFileStructureError("Неизвecтный формат выписки, ни один из экстракторов не подходят")

    if len(supported_extractors) > 1 :
        raise exceptions.InputFileStructureError(f"Непонятный формат выписки. Больше чем один экстрактор говорят, что понимают его")

    # If only one supported extractor if found - then all OK
    return supported_extractors[0]

def determine_extractor_by_name(extractor_name:str) -> type:
    """
    Checks if the is an Extractor class available, which has a name, iqual to the 'extractor_name' string
    If such extractor is available, then this class is returned, otherwise an exception is raised
    """
    extractor_names_set = set()

    global extractors_list # type list[Extractor]

    for extractor in extractors_list:
        if extractor.__name__ == extractor_name:
            return extractor

        extractor_names_set.add(extractor.__name__ )

    raise exceptions.UserInputError(f'Указанный формат файла "{extractor_name}" Неизвестен.\n См. смписок известных форматов \n {extractor_names_set}')

def debug_extractor(extractor_type_object:type, test_text_file_name:str):
    """
    This is helper function, which helps to debug a new extractor. It is not used in the operational code
    """

    all_actually_returned_fields_set=set()

    with open(test_text_file_name, encoding='utf-8') as f:
        txt_file_content = f.read()

    # Initializing an extractor with the type extractor_type_object and passing txt_file_content to it
    extractor = extractor_type_object(txt_file_content)

    print('-'*20)
    print("Checking 'check_specific_signatures()'. If code continues further, then everything is OK")
    extractor.check_specific_signatures()

    print('-' * 20)
    print("Testing 'get_period_balance()'")
    print(f"period_balance = {extractor.get_period_balance()}")
    assert isinstance(extractor.get_period_balance(), float)

    print('-' * 20)
    print("Testing split_text_on_entries()'")
    for text_entry in extractor.split_text_on_entries():
        print('*'*20)
        print(text_entry)

    print('-' * 20)
    print("Testing 'get_entries()'")
    for entry in extractor.get_entries():
        print('*'*20)
        pprint(entry)
        assert isinstance(entry,dict)
        all_actually_returned_fields_set = all_actually_returned_fields_set | set(entry.keys())

    print('-' * 20)
    print("Testing 'check_support()'")
    print(f"check_support = {extractor.check_support()}")

    print('-' * 20)
    print(f"Testing get_columns_info()")
    columns_info_dic = extractor.get_columns_info()
    pprint(columns_info_dic)

    undefined_fiels_set = all_actually_returned_fields_set - set(columns_info_dic.keys())

    print(f"{undefined_fiels_set=}")

    if len(undefined_fiels_set)>0:
        raise ValueError(f"""
Some of the fields, returned by the function 'get_entries()' are not retured by the function 'get_columns_info()'
Specifically the following fields are missing {undefined_fiels_set}""")

    print('-' * 20)
    print(f"Testing 'get_column_name_for_balance_calculation()'")
    column_name_for_balance_calculation = extractor.get_column_name_for_balance_calculation()
    print(f"get_column_name_for_balance_calculation = {column_name_for_balance_calculation}")

    if not column_name_for_balance_calculation in all_actually_returned_fields_set:
        raise ValueError(f"""
Function 'get_column_name_for_balance_calculation()' returns value '{column_name_for_balance_calculation}' which is not one of the actually
returned fiels 
{all_actually_returned_fields_set}
""")


    print('\n'*2)
    print("#"*10 + " Warnings! " + "#"*10)

    defined_but_not_used_fiels_set = set(columns_info_dic.keys()) - all_actually_returned_fields_set

    if len(defined_but_not_used_fiels_set)>0:
        print(f"""
Some of the fields, returned by the function 'get_columns_info()'  are not retured by the function 'get_entries()''
Specifically the following fields are missing {defined_but_not_used_fiels_set}
This may be due to an input file, used for testing. Make sure you test this fucntion on another input file""")

if __name__ == '__main__':
    """
    Some testing code
    """

    txt_file = r'C:\_code\py\Sberbank2Excel_no_github\20210724_20210720_20210724_2107_Stavropol_.txt'

    with open(txt_file, encoding='utf-8') as f:
        txt_file_content = f.read()

    extractor = determine_extractor_auto(txt_file_content)

    print(extractor)

    print(extractor.__name__)

    print(determine_extractor_by_name('SBER_CREDIT_2107'))
    print(determine_extractor_by_name('SBER_CREDIT_2108'))