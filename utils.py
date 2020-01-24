#coding=utf-8

import unidecode
import re

from typing import *

def get_float_from_money(money_str:str,process_no_sign_as_negative=False)->float:
    """
    Converts string, representing money to a float.
    If process_no_sign_as_negative is set to True, then a number will be negative in case no leading sign is available
    """
    
    money_str=unidecode.unidecode(money_str)
    money_str=money_str.replace(' ','')
    money_str=money_str.replace(',','.')

    leading_plus=False
    if money_str[0]=='+':
        leading_plus=True

    money_float=float(money_str)

    if (process_no_sign_as_negative and not leading_plus):
        money_float=-1*money_float

    return money_float

def split_Sberbank_line(line:str)->List[str]:
    """
    Разделяем Сбербанковсую строчку на кусочки данных. Разделяем используя два и более пробела в качестве разделителя
    """
    line_parts=re.split(r'\s\s\s+',line)
    line_parts=list(filter(None,line_parts))
    return line_parts


def main():
    # Testing
    print('*** testing function get_float_from_money()')
    print(get_float_from_money('2\xa0365,01')==-2365.01)
    print(get_float_from_money('+2\xa0365,01')==2365.01)
    print(get_float_from_money('2\xa0365,01',False)==2365.01)
    print(get_float_from_money('+10\xa0425\xa0000,00')==10425000.00)


if __name__=='__main__':
    main()
    
        
    
    
    


