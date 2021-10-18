"""
Abstract Extractor class
All real extractors need to inherit from it and overwrite overwrite all @abstractmethod
"""

from abc import ABC, abstractmethod

import attr

import exceptions

class Extractor(ABC):
    def __init__(self, pdf_text: str):
        self.pdf_text = pdf_text

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
    def decompose_entry(self, entry:str):
        """
        Returns a class object, defined by attrs
        """
        pass

    @abstractmethod
    def get_column_name_for_balance_calculation(self) -> str:
        pass

    @abstractmethod
    def _get_transaction_data_class():
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
        entries_list_of_dicts = [attr.asdict(self.decompose_entry(entry)) for entry in self.split_text_on_entries()]
        return entries_list_of_dicts

    def get_columns_info(self)->dict:
        # print(self)
        result = dict()

        data_class_attibutes = self._get_transaction_data_class().__dict__['__attrs_attrs__']

        print("data_class_attibutes")
        print('*'*20)
        print(data_class_attibutes)

        for attribute in data_class_attibutes:
            print(attribute)
            result[attribute.name] = attribute.metadata['long_name']

        return result