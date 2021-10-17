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

def debug_extractor(extractor_type_object, test_text_file_name:str):
    """
    This is helper function, which helps to debug a new extractor
    """

    all_fields_dict=dict()

    with open(test_text_file_name, encoding='utf-8') as f:
        txt_file_content = f.read()


    extractor = extractor_type_object(txt_file_content)

    print('-'*20)
    print("Checking 'check_specific_signatures()'. If code continues further, then everything is OK")
    extractor.check_specific_signatures()

    print('-' * 20)
    print(f"period_balance = {extractor.get_period_balance()}")

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
        all_fields_dict = all_fields_dict | entry.keys()

    print('-' * 20)
    print(f"check_support = {extractor.check_support()}")

    pprint(all_fields_dict)

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