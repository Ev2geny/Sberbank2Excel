import sys
import os

from typing import Union

from core.pdf2txtev import pdf_2_txt_file
from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel



def sberbankPDF2Excel(input_pdf_file_name:str, output_excel_file_name:Union[str, None] =None, format='2005_Moscow') ->str:

    tmp_txt_file_name = os.path.splitext(input_pdf_file_name)[0] + ".txt"

    if not output_excel_file_name:
        output_excel_file_name = os.path.splitext(input_pdf_file_name)[0]+".xlsx"

    pdf_2_txt_file(input_pdf_file_name, tmp_txt_file_name)

    result=sberbankPDFtext2Excel(tmp_txt_file_name, output_excel_file_name, format=format)

    os.remove(tmp_txt_file_name)

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