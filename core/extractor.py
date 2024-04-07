"""
Abstract Extractor class
All real extractors need to inherit from it and overwrite  all @abstractmethod
"""

from abc import ABC, abstractmethod

import exceptions

class Extractor(ABC):
    def __init__(self, bank_text: str):
        self.bank_text = bank_text 

    @abstractmethod
    def check_specific_signatures(self):
        """Function is not expected to return any result, but is expected to raise 
        exceptions.InputFileStructureError() if the text is not supported
        """
        pass

    @abstractmethod
    def get_period_balance(self) -> float:
        """Function gets information about transaction balance from the header of the banlk extract

        Returns:
            float: balance of the period
        """
        pass

    @abstractmethod
    def split_text_on_entries(self)->list[str]:
        """Function splits the text on entries (on individual transactions)

        Returns:
            list[str]: list of entries
        """
        pass

    @abstractmethod
    def decompose_entry_to_dict(self, entry:str)->dict:
        """Function decomposes entry into a dictionary

        Args:
            entry (str): _description_

        Returns:
            dict: _description_
        """
        pass

    @abstractmethod
    def get_column_name_for_balance_calculation(self) -> str:
        """Function returns the name of the column that is used for calculation of the balance of the period

        Returns:
            str: _description_
        """
        pass

    @abstractmethod
    def get_columns_info(self)->dict:
        """Returns full column names in the order and in the form they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """

    def check_support(self)->bool:
        """Function checks if the text is supported by the extractor
        
        Returns:
            bool: True if the text is supported, False otherwise
        """
        try:
            # this would raise an exception if the text is not supported
            self.check_specific_signatures()
            
            result = isinstance(self.get_period_balance(),float) and len(self.split_text_on_entries()) > 0

            return result

        except exceptions.InputFileStructureError:
            return False

    def get_entries(self)->list[dict]:
        """Function returns list of dictionaries, where each dictionary corresponds to one entry

        Raises:
            e: if there was an error while processing one of the entries, the function with print the entry and raise the exception

        Returns:
            list[dict]: list of dictionaries, where each dictionary corresponds to one entry
        """
        # entries_list_of_dicts = [self.decompose_entry_to_dict(entry) for entry in self.split_text_on_entries()]
        entries_list_of_dicts = []
        
        for entry in self.split_text_on_entries():
            try:
                entries_list_of_dicts.append(self.decompose_entry_to_dict(entry))
            except Exception as e:
                print("Ошибка при обработке трансакции\n"+
                      "-"*20 +
                      "\n"+ 
                      entry +
                      "\n"+ 
                      "-"*20)
                raise e
        
        return entries_list_of_dicts
