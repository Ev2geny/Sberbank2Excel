"""
Abstract Extractor class
All real extractors need to inherit from it and overwrite overwrite all @abstractmethod
"""

from abc import ABC, abstractmethod

import exceptions

class Extractor(ABC):
    def __init__(self, pdf_text: str):
        self.pdf_text = pdf_text + '\n___EOF'

    @abstractmethod
    def check_specific_signatures(self):
        pass

    @abstractmethod
    def get_period_balance(self) -> str:
        pass

    @abstractmethod
    def split_text_on_entries(self)->list[dict]:
        pass

    @abstractmethod
    def decompose_entry_to_dict(self, entry:str)->dict:
        pass

    @abstractmethod
    def get_column_name_for_balance_calculation(self) -> str:
        pass

    def check_support(self)->bool:
        """
        Function checks whether this extractor support the  text format from self.pdf_text
        """
        try:
            result = True
            result = result and isinstance(self.get_period_balance(),float)
            result = result and len(self.split_text_on_entries()) > 0

            self.check_specific_signatures()

            return result

        except exceptions.InputFileStructureError:
            return False

    def get_entries(self)->list[dict]:
        entries_list_of_dicts = [self.decompose_entry_to_dict(entry) for entry in self.split_text_on_entries()]
        return entries_list_of_dicts
