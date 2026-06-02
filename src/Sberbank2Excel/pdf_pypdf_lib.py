# Created-By: FazziCLAY (fazziclay@gmail.com)
# This converted preferer to use for VTB-Bank pdf's

import os
from typing import Union

PAGE_DEVIDER_CRIB = "--------- PAGE DEVIDER -----------"

# as in pdf2txtev.py
def pdf_2_txt_file(pdf_file_name: str,
                   txt_output_file_name: Union[None, str] = None
                   ):
    """
    Такая же функция как и в pdf2txtev.py только использующая pypdf
    """
    if not txt_output_file_name:
        txt_output_file_name = os.path.splitext(pdf_file_name)[0]+".txt"

    pdf_text= convert_pdf_to_txt(pdf_file_name)

    with open(txt_output_file_name,"w",encoding="utf-8") as txt_output_file_object:
        txt_output_file_object.write(pdf_text)

def convert_pdf_to_txt(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError("pypdf required", e)
    
    try:
        reader = PdfReader(pdf_path)
        extracted_text = []

        # Loop through each page and extract text
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        # Join the text pages together
        full_text = f"\n{PAGE_DEVIDER_CRIB}\n".join(extracted_text)
        return full_text

    except Exception as e:
        raise Exception("Ошибка во время конвертации PDF -> TXT (используя ВТБ-preferer библиотеку pypdf)", e)


if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Define your source file path and target save folder here
    pdf_path = PDF_SOURCE = "Выписка по счету •  3915.pdf"
    output_directory = SAVE_LOCATION = "SAVE"

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_filename = f"{file_name}.txt"
    txt_path = os.path.join(output_directory, txt_filename)

    full_text = convert_pdf_to_txt(pdf_path)

    # Save the content to the designated location
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(full_text)

    print(f"Success! Text saved to: {txt_path}")

    # Run the function
    convert_pdf_to_txt(PDF_SOURCE, SAVE_LOCATION)
