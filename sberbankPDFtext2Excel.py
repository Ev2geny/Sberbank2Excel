"""
Программа для конфертации выписки по карте Сбербанка из формата Adobe PDF в формат Excel.

Программа не читает PDF файл непосредственно. Сначала надо скофертировать выписку Сбербанка в текстовый формат используя Foxit PDF reader

Как пользоваться

1) Установить Foxit PDF reader https://www.foxitsoftware.com/pdf-reader/

2) 


"""

import re
import pandas as pd
import sys
import os

# importing own modules out of project
import utils
import exceptions

def sberbankPDFtext2Excel(input_txt_file_name:str,output_excel_file_name:str=None)->None:
    """
    Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF помощью конвертации Foxit PDF reader в Excel формат
    Если output_excel_file_name не задан, то он создаётся из input_txt_file_name путём замены расширения файла на xlsx
    """

    # creating output file name for Excel file, if not provided
    if not output_excel_file_name:
        pre, ext = os.path.splitext(input_txt_file_name)
        output_excel_file_name=pre+'.xlsx'

    file=open(input_txt_file_name, encoding="utf8")

    file_text=file.read()

    # extracting entries (operations) from text file on
    all_entries=re.findall(r"""
    \s{40}                                        # 44 white speces 
    \d\d\.\d\d\.\d\d\d\d                          # Date like 25.04.1991
    \s{15,18}                                     # 15-18 white speces (the amount of white speces in different places of the document is different
    [\s\S]*?                                      # any character, including new line. !!None-greedy!! See URL why [\s\S] is used https://stackoverflow.com/a/33312193
    \s{40}\d\d\.\d\d\.\d\d\d\d\s/                 # Again 44 white spaces, followed by like '25.12.2019 /' 
    .*?\n                                         # everything till end of the line
    """,
    file_text, re.VERBOSE)

    # Creating pandas dataframe for output
    df=pd.DataFrame(columns=['operation_date',
                             'processing_date',
                             'authorisation_code',
                             'description',
                             'category',
                             'value_account_currency',
                             'value_operational_currency',
                             'operational_currency',
                             'remainder_account_currency'])

    # Defining header in Russian.  Will be used later, when saving to Excel. Defining it hear, so that it is close to Dataframe definition
    myheader=['Дата операции',
              'дата обработки',
              'код авторизации',
              'Описание операции',
              'категория',
              'Сумма в валюте счёта',
              'cумма в валюте операции',
              'валюта операции',
              'Остаток по счёту в валюте счёта']

    for entry in all_entries:
        """
        print('================================================================================================================================')
        print(entry)
        print('--------------------------------------------------------------------------------------------------------------------------------')
        """
        lines=entry.split('\n')
        lines=list(filter(None,lines))

        result={}
        #************** looking at the 1st line
        line_parts=utils.split_Sberbank_line(lines[0])
        result['operation_date']=line_parts[0]
        result['description']=line_parts[1]
        result['value_account_currency']=utils.get_float_from_money(line_parts[2],True)
        result['remainder_account_currency']=utils.get_float_from_money(line_parts[3])

        #************* looking at lines between 1st and the last
        sublines=lines[1:-1]
        for line in sublines:
            line_parts=utils.split_Sberbank_line(line)
            if len(line_parts)!=1:
                raise exceptions.SberbankPDFtext2ExcelError("Line is expected to have only one part :"+line)
            result['description']=result['description']+' '+line_parts[0]

        #************* looking at the last line
        line_parts=utils.split_Sberbank_line(lines[-1])

        if len(line_parts) <2 or len(line_parts)>3:
            raise exceptions.SberbankPDFtext2ExcelError("Line is expected to 2 or parts :"+line)

        result['processing_date']=line_parts[0][0:11]
        result['authorisation_code']=line_parts[0][13:]
        result['category']=line_parts[1]

        if len(line_parts)==3:
            found=re.search(r'[(](.*?)(\w\w\w)[)]',line_parts[2])  #processing string like (33,31 EUR)
            if found:
                result['value_operational_currency']=utils.get_float_from_money(found.group(1),True)
                result['operational_currency']=found.group(2)
            else:
                raise exceptions.SberbankPDFtext2ExcelError("Could not process string. Expected something like (33,31 EUR):"+line)

        # print(result)
        df=df.append(result,ignore_index=True)

    # convert to date https://stackoverflow.com/questions/41514173/change-multiple-columns-in-pandas-dataframe-to-datetime
    df['operation_date']=pd.to_datetime(df['operation_date'])
    df['processing_date']=pd.to_datetime(df['processing_date'])

    # Saving pandas dataframe to Excel
    writer = pd.ExcelWriter(output_excel_file_name,
                            engine='xlsxwriter',
                            datetime_format='dd.mm.yyyy')

    df.to_excel(writer,header=myheader,sheet_name='Sheet1',index=False)
    
    writer.close()

    return output_excel_file_name

def main():
    if len(sys.argv)<2:
        print('Недостаточно аргументов')
        print(__doc__)
        return None
    
    elif len(sys.argv)==2:
        outputFileName=None

    elif len(sys.argv)==3:
        outputFileName=sys.argv[2]

    sberbankPDFtext2Excel(sys.argv[1],outputFileName)



if __name__=='__main__':
    main()