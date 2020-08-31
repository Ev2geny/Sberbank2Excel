"""
This module provides approximately the same functionality as pdfminer.six => pdfminer.high_level
https://github.com/pdfminer/pdfminer.six/blob/develop/pdfminer/high_level.py
But it allows to provide conversion of Sberbank statement without mixing lines.
The issue it works around is described here: https://github.com/pdfminer/pdfminer.six/issues/466

Usage:
======

from command line: py pdf2txtev.py <pdf_file_name> [<Excel_file_name>]
    where:
        pdf_file_name - file name of the PDF file to be converted
        Excel_file_name - optional name of the resulting Excel file

as a module programmaticatty:
      pdf_2_text - to get text as an output
      pdf_2_txt_file - to convert pdf to text
"""


import os
import sys

from typing import List, Union

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import open_filename
from pdfminer.layout import LTTextBoxHorizontal


def _list_LTTextBoxHorizontal_2_matrix(list_LTTextBoxHorizontal:List[LTTextBoxHorizontal])\
        ->List[List[LTTextBoxHorizontal]]:
    """
    Converts a list of LTTextBoxHorizontal on the page to a matrix, based on their coordinates
    This matrix is meant to simulate how elements are located on the page

    Keyword arguments:
        list_LTTextBoxHorizontal - list of LTTextBoxHorizontal elements of a page
    """

    # Sorting input list in reverse order by bottom Y coordinate of the horizontal text box : LTTextBoxHorizontal.y0]
    list_LTTextBoxHorizontal = sorted(list_LTTextBoxHorizontal, key = lambda box:box.y0,reverse= True)

    # Initialising matrix with the 1st most top element on the page
    matrix= [
                [ list_LTTextBoxHorizontal[0] ]
                                                ]
    # if there was only one LTTextBoxHorizontal, then resulting matrix matrix will contain only this element
    if len(list_LTTextBoxHorizontal) == 1:
        return matrix

    """ 
    If the LTTextBoxHorizontal top side (y1) is higher then the vertical middle of the previose 
    LTTextBoxHorizontal ([i-1]), then both current and previous LTTextBoxHorizontal are considered to be on the same 
    line/ row. In this case current LTTextBoxHorizontal element is added as the next element of the current row
    Otherwise current LTTextBoxHorizontal is added to a new line / row of the matrix
    """
    for i in range(1, len(list_LTTextBoxHorizontal)):
        vert_middle_prev_box = (list_LTTextBoxHorizontal[i-1].y0 + list_LTTextBoxHorizontal[i-1].y1)/2
        if list_LTTextBoxHorizontal[i].y1 > vert_middle_prev_box:
            matrix[-1].append(list_LTTextBoxHorizontal[i])
        else:
            matrix.append([
                list_LTTextBoxHorizontal[i]
            ])

    matrix = [sorted(row, key=lambda box:box.x0) for row in matrix]

    return matrix


def _matrix_2_txt(matrix:List[List[LTTextBoxHorizontal]], qnt_spaces = 1)->str:
    """
    Converting a matrix of elements LTTextBoxHorizontal to a string
    Withing a matrix row all elements are separated by amount of spaces, equal to qnt_spaces
    Each new row in a matrix represents a new line in  a string
    """
    result = ""
    for row in matrix:
        # concatinating all elements together, separating them with amount of spaces, equal to qnt_spaces
        last_row_element = len(row)-1
        for row_element in row:
            result= result + row_element.get_text().strip()

            # adding amount of spaces, equal to qnt_spaces for all elements, except the last one
            if row.index(row_element) != last_row_element:
                result = result + " " * qnt_spaces

        # Adding line break at the end of the row
        result = result + "\n"

    return result


def _PDFpage2txt(page:PDFPage, laparams = None) -> str:
    """
    Converting PDFPage to text
    """
    if laparams is None:
        laparams = LAParams(char_margin=1000, line_margin=0.001, boxes_flow=None, qnt_spaces=5)

    # Some preparations to get layout
    resource_manager = PDFResourceManager()
    device = PDFPageAggregator(resource_manager, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)
    interpreter.process_page(page)
    layout = device.get_result()

    # Creating a list of LTTextBoxHorizontal elements of the page, filtering all other elements out
    list_LTTextBoxHorizontal = [element for element in layout if isinstance(element, LTTextBoxHorizontal)]

    # converting list of LTTextBoxHorizontal to a 2-dimentional matrix
    matrix_of_LTTextBoxHorizontal = _list_LTTextBoxHorizontal_2_matrix(list_LTTextBoxHorizontal)

    return(_matrix_2_txt(matrix_of_LTTextBoxHorizontal, laparams.qnt_spaces))


def pdf_2_text(pdf_file_name:str,
               password='',
               page_numbers=None,
               maxpages=0,
               caching=True,
               laparams=None)->str:
    """
    This is a re-write of the function pdfminer.high_level.extract_text
    https://github.com/pdfminer/pdfminer.six/blob/0b44f7771462363528c109f263276eb254c4fcd0/pdfminer/high_level.py#L90
    It produces result, which does not have this issue: https://github.com/pdfminer/pdfminer.six/issues/466

    : pdf_file_name - name of the input PDF file
    : password: For encrypted PDFs, the password to decrypt.
    : page_numbers: zero-indexed page numbers to operate on
    : maxpages: How many pages to stop parsing after
    :
    """
    result = ""
    with open_filename(pdf_file_name, "rb") as pdf_file_object:
        for page in PDFPage.get_pages(pdf_file_object,
                                      page_numbers,
                                      maxpages=maxpages,
                                      password=password,
                                      caching=caching,
        ):
            result = result + _PDFpage2txt(page, laparams)

    return result


def pdf_2_txt_file(pdf_file_name:str,
                   txt_output_file_name: Union[None, str] = None,
                   password='',
                   page_numbers=None,
                   maxpages=0,
                   caching=True,
                   laparams=None):
    """
    Converts pdf file to text and creates a text file with this text
    : pdf_file_name - name of the input PDF file
    : txt_output_file_name - output text file name. If not provided file name will be constructed by ramaning
        *.pdf file to *.txt file
    : password: For encrypted PDFs, the password to decrypt.
    : page_numbers: zero-indexed page numbers to operate on
    : maxpages: How many pages to stop parsing after
    """
    if not txt_output_file_name:
        txt_output_file_name = os.path.splitext(pdf_file_name)[0]+".txt"

    pdf_text= pdf_2_text(pdf_file_name,
                         password,
                         page_numbers,
                         maxpages,
                         caching,
                         laparams)

    with open(txt_output_file_name,"w",encoding="utf-8") as txt_output_file_object:
        txt_output_file_object.write(pdf_text)


def main():
    if len(sys.argv) < 2:
        print('Недостаточно аргументов')
        return None

    elif len(sys.argv) == 2:
        outputFileName = None

    elif len(sys.argv) == 3:
        outputFileName = sys.argv[2]

    pdf_2_txt_file(sys.argv[1], outputFileName)


if __name__ == '__main__':
    main()





