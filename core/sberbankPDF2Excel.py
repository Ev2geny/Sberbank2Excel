import sys
import os
from typing import Union
import argparse
from pathlib import Path

import exceptions
import extractors
from pdf2txtev import pdf_2_txt_file
from sberbankPDFtext2Excel import sberbankPDFtext2Excel, genarate_PDFtext2Excel_argparser
from utils import get_output_extentionless_file_name





def sberbankPDF2Excel(input_file_name:str|Path,
                      output_file_name:str|Path|None =None,
                      format:str= 'auto',
                      leave_intermediate_txt_file:bool = False,
                      perform_balance_check = True,
                      output_file_type:str="xlsx",
                      reversed_transaction_order=True,
                      output_dir:str|Path|None = None,
                      create_output_dir:bool=False) ->str:
    """function converts pdf or text file with Sperbank extract to Excel or CSV format

    Args:
        input_file_name (str): _description_
        output_file_name (Union[str, None], optional): _description_. Defaults to None.
        format (str, optional): _description_. Defaults to 'auto'.
        leave_intermediate_txt_file (str, optional): _description_. Defaults to False.
        perform_balance_check (bool, optional): _description_. Defaults to True.
        output_file_type (str, optional): _description_. Defaults to "xlsx".
        reversed_transaction_order (bool, optional): _description_. Defaults to True.
        ouput_folder: 
        create_output_folder

    Raises:
        exceptions.InputFileStructureError: _description_

    Returns:
        str: file name of the created file
    """

    print(f"{format=}")

    print("*"*30)
    print(f"Конвертируем файл  {input_file_name}")

    input_file_name = Path(str(input_file_name))

    extension = input_file_name.suffix.lower()
    
    if extension not in [".pdf", ".txt"]:
        raise exceptions.InputFileStructureError(f"Расширение файла {extension} не поддерживается")

    if extension == ".txt":
        tmp_txt_file_name = input_file_name
    else:
        tmp_txt_file_name = get_output_extentionless_file_name(input_file_name).with_suffix(".txt")

    output_file_name = get_output_extentionless_file_name(input_file_name, 
                                                          output_file_name=output_file_name,  
                                                          output_dir=output_dir, 
                                                          create_output_dir=create_output_dir)

    # if not output_file_name:
    #     output_file_name = path 

    try:
        if extension == ".pdf":
            pdf_2_txt_file(input_file_name, tmp_txt_file_name)

        created_file_name = sberbankPDFtext2Excel(tmp_txt_file_name,
                                                  output_file_name=output_file_name,
                                                  format=format,
                                                  perform_balance_check = perform_balance_check,
                                                  output_file_type=output_file_type,
                                                  reversed_transaction_order=reversed_transaction_order)

        if (not leave_intermediate_txt_file) and (not extension == ".txt"):
            os.remove(tmp_txt_file_name)

    except:
        raise


    return str(created_file_name)


def main():

    parser = argparse.ArgumentParser(description='Конвертация выписки банка из формата PDF или из промежуточного текстового файла в формат Excel или CSV.',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    parents=[genarate_PDFtext2Excel_argparser()])
   
    parser.add_argument('-i','--interm', action='store_true', default=False, dest='leave_intermediate_txt_file', help='Не удалять промежуточный текстовый файт')
    parser.add_argument('-d','--dir', type=str, default=None, dest='output_dir', help='Имя директории, в которой будет создан файл. Может быть ли абсолютным путём, либо названием папки в директории конвертируемого файла. Если не указана, то файл будет создан в директории, в которой находится конвертируемый файл, либо в папке "_output_" в этой директории, если таковая существует.')
    parser.add_argument('-c','--create', action='store_true', default=False, dest='create_output_dir', help="Создать директорию, указанную в аргументе '-d' '--dir', если она не существует")

    args = parser.parse_args()

    print(args)

    sberbankPDF2Excel(input_file_name = args.input_file_name,
                      output_file_name = args.output_Excel_file_name,
                      format = args.format,
                      leave_intermediate_txt_file = args.leave_intermediate_txt_file,
                      perform_balance_check = args.perform_balance_check,
                      output_file_type=args.output_file_type,
                      reversed_transaction_order=args.reversed_transaction_order,
                      output_dir=args.output_dir,
                      create_output_dir=args.create_output_dir)

if __name__ == '__main__':
    main()