from extractors import extractors_list
import exceptions

from extractor import Extractor

def determine_extractor(pdf_text:str) -> type:
    """
    Function determines which extractor to use with this particular text representation of PDF extract

    pdf_text:str: text representation of PDF extract

    returns:
        reference to a calss of a supported extractor
    """
    global extractors_list

    supported_extractors = [extractor for extractor in extractors_list if extractor(pdf_text).check_support()]
    # for extractor in extractors_list:
    #     if extractor(pdf_text).check_support():
    #         supported_extractors.append(extractor)

    if len(supported_extractors) == 0:
        exceptions.InputFileStructureError("Неизвecтный формат выписки")

    if len(supported_extractors) > 1 :
        exceptions.InputFileStructureError(f"Непонятный формат выписки. Больше чем один экстрактор говорят, что понимают его")

    return supported_extractors[0]

if __name__ == '__main__':
    """
    Some testing code
    """

    txt_file = r'C:\_code\py\Sberbank2Excel_no_github\20210724_20210720_20210724_2107_Stavropol_.txt'

    with open(txt_file, encoding='utf-8') as f:
        txt_file_content = f.read()

    extractor = determine_extractor(txt_file_content)

    print(extractor)

    print(extractor.__name__)