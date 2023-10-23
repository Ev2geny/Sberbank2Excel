import sys
import os
from typing import Union
import argparse

import exceptions
import extractors
from pdf2txtev import pdf_2_txt_file
from sberbankPDFtext2Excel import sberbankPDFtext2Excel, genarate_PDFtext2Excel_argparser





def sberbankPDF2Excel(input_file_name:str,
                      output_file_name:Union[str, None] =None,
                      format:str= 'auto',
                      leave_intermediate_txt_file:str = False,
                      perform_balance_check = True,
                      output_file_type:str="xlsx",
                      reversed_transaction_order=True,
                      output_directory_name:Union[str, None] =None) ->str:
    """function converts pdf or text file with Sperbank extract to Excel or CSV format

    Args:
        input_file_name (str): Input file name
        output_file_name (Union[str, None], optional):Defaults to None.
        format (str, optional): Defaults to 'auto'.
        leave_intermediate_txt_file (str, optional): Defaults to False.
        perform_balance_check (bool, optional): Defaults to True.
        output_file_type (str, optional): Defaults to "xlsx".
        reversed_transaction_order (bool, optional): Defaults to True.
        output_directory_name (Union[str, None], optional): Defaults to None. If None, then output file is created in the same directory as input file
            if output_file_name is not None, then output_directory_name is ignored

    Raises:
        exceptions.InputFileStructureError: _description_

    Returns:
        str: file name of the created file
    """

    print(f"{format=}")

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


    if not output_file_name:
        output_file_name = path 

    try:
        if extension == ".pdf":
            pdf_2_txt_file(input_file_name, tmp_txt_file_name)

        created_file_name = sberbankPDFtext2Excel(tmp_txt_file_name,
                                                  output_file_name,
                                                  format=format,
                                                  perform_balance_check = perform_balance_check,
                                                  output_file_type=output_file_type,
                                                  reversed_transaction_order=reversed_transaction_order)

        if (not leave_intermediate_txt_file) and (not extension == ".txt"):
            os.remove(tmp_txt_file_name)

    except:
        raise


    return created_file_name


def main():

    parser = argparse.ArgumentParser(description='Конвертация выписки банка из формата PDF или из промежуточного текстового файла в формат Excel или CSV.',
                                        parents=[genarate_PDFtext2Excel_argparser()])
   
    parser.add_argument('-i','--interm', action='store_true', default=False, dest='leave_intermediate_txt_file', help='Не удалять промежуточный текстовый файт')

    args = parser.parse_args()

    print(args)

    sberbankPDF2Excel(input_file_name = args.input_file_name,
                      output_file_name = args.output_Excel_file_name,
                      format = args.format,
                      leave_intermediate_txt_file = args.leave_intermediate_txt_file,
                      perform_balance_check = args.perform_balance_check,
                      output_file_type=args.output_file_type,
                      reversed_transaction_order=args.reversed_transaction_order)

if __name__ == '__main__':
    main()