import sys
import os
import exceptions

from typing import Union

from core.pdf2txtev import pdf_2_txt_file
from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel



def sberbankPDF2Excel(input_file_name:str,
                      output_excel_file_name:Union[str, None] =None,
                      format:str= 'auto',
                      leave_intermediate_txt_file:str = False) ->str:
    """
    function converts pdf or text file with Sperbank extract to Excel format
    input_file_name:
    output_excel_file_name:
    format: str - format of the Sberbank extract. If "auto" then tool tryes to work out the format itself
    leave_intermediate_txt_file: if True, does not delete intermediate txt file
    """

    print("*"*30)
    print("Конвертируем файл " + input_file_name)

    path, extension = os.path.splitext(input_file_name)

    extension = extension.lower()

    if extension == ".pdf":
        tmp_txt_file_name = os.path.splitext(input_file_name)[0] + ".txt"

    elif extension == ".txt":
        tmp_txt_file_name = input_file_name

    else:
        raise exceptions.InputFileStructureError("Неподдерживаемое расширение файла: "+ extension)


    if not output_excel_file_name:
        output_excel_file_name = path + ".xlsx"

    try:
        if extension == ".pdf":
            pdf_2_txt_file(input_file_name, tmp_txt_file_name)

        result = sberbankPDFtext2Excel(tmp_txt_file_name, output_excel_file_name, format=format)
        print("Создан файл "+result)

        if (not leave_intermediate_txt_file) and (not extension == ".txt"):
            os.remove(tmp_txt_file_name)

    except:
        raise


    return result


def main():
    if len(sys.argv) < 2:
        print('Недостаточно аргументов')
        print(__doc__)
        return None

    elif len(sys.argv) == 2:
        outputFileName = None

    elif len(sys.argv) == 3:
        outputFileName = sys.argv[2]

    sberbankPDF2Excel(sys.argv[1], outputFileName)


if __name__ == '__main__':
    main()