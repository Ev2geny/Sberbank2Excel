import pytest
from pathlib import Path
import exceptions
import tempfile

from utils import get_output_extentionless_file_name

class Test_get_output_extentionless_file_name:

    def test_output_file_name_standard_the_same_dir(self):
        """
        Test creation of the output file name from the input file name, when no output directory is specified
        Should be the same as the input file name, but without the extension
        """
        # getting directorry of this file
        test_file = Path(__file__).parent/"test_data"/"input_file.txt"
        
        expected_output_file = Path(__file__).parent/"test_data"/"input_file"
        
        output_file = get_output_extentionless_file_name(test_file)
        
        assert output_file == expected_output_file
        
        
    def test___output__is_present(self):
        """
        Test creation of the output file name from the input file name, when there is a directory named "_output_" 
        in the same directory.
        """
        test_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"input_file.txt"
        expected_output_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"_output_"/"input_file"
        
        output_file = get_output_extentionless_file_name(test_file)
        
        # print(f"output_file: {output_file}")
        
        assert output_file == expected_output_file
        
    def test_when_new_existing_dir_provided(self):
        """
        Test creation of the output file name from the input file name, when name of single output directory is 
        provided and it is present
        """
        test_file = Path(__file__).parent/"test_data"/"input_file.txt"
        expected_output_file = Path(__file__).parent/"test_data"/"output_dir"/"input_file"
        
        # with pytest.raises(exceptions.UserInputError):
        output_file = get_output_extentionless_file_name(test_file, output_dir="output_dir")
        
        assert output_file == expected_output_file
        
    def test_when_new_not_existing_dir_provided(self):
        """
        Test creation of the output file name from the input file name, when name of single output directory is 
        provided but it is not present and not required to be created
        """
        test_file = Path(__file__).parent/"test_data"/"input_file.txt"
        # expected_output_file = Path(__file__).parent/"test_data"/"output_dir"/"input_file"
        
        with pytest.raises(exceptions.UserInputError) as exc_info:
            output_file = get_output_extentionless_file_name(test_file, output_dir="output_dir_new")
        
        assert "does not exist and it is not requested to create it" in str(exc_info.value)
            
    def test_when_new_not_existing_dir_provided_but_can_create(self, tmpdir):
        """
        Test creation of the output file name from the input file name, when name of single output directory is 
        provided but it is not present and it is required to be created
        """
        # test_file = Path(__file__).parent/"test_data"/"input_file.txt"
        # # expected_output_file = Path(__file__).parent/"test_data"/"output_dir"/"input_file"
        
    
        # output_file = get_output_extentionless_file_name(test_file, output_dir="output_dir_new", create_output_dir=True)
        

        # Creating file 'input_file.txt' in the temporary directory
        test_file = Path(tmpdir)/"input_file.txt"
        
        # creating test file
        with open(test_file, "w") as file:
            file.write("test")
            
        output_file = get_output_extentionless_file_name(test_file, output_dir="output_dir_new", create_output_dir=True)
        expected_output_file = Path(tmpdir)/"output_dir_new"/"input_file"
        
        assert output_file == expected_output_file
        
        # testing that the directory was created
        expected_created_dir = Path(tmpdir)/"output_dir_new"
        assert expected_created_dir.exists()
        
        # testing that this directory is a directory
        assert expected_created_dir.is_dir()
                    
    def test_exiting_output_folder_absolute_path_provided(self):
        """
        Test the situation, when the existing directory is provided as an absolute path
        """
        test_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"input_file.txt"
        
        exiting_output_folder_absolute_path = Path(__file__).parent/"test_data"/"dir2"
        
        expected_output_file = Path(__file__).parent/"test_data"/"dir2"/"input_file"
        
        output_file = get_output_extentionless_file_name(test_file, output_dir=exiting_output_folder_absolute_path)
        
        # print(f"output_file: {output_file}")
        
        assert output_file == expected_output_file
        
    def test_not_exiting_output_folder_absolute_path_provided(self):
        """
        Test the situation, when the existing directory is provided as an absolute path
        """
        test_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"input_file.txt"
        
        not_exiting_output_folder_absolute_path = Path(__file__).parent/"test_data"/"dir3"
        
        with pytest.raises(exceptions.UserInputError) as exc_info:
             get_output_extentionless_file_name(test_file, output_dir=not_exiting_output_folder_absolute_path)
        
        assert "is not an existing directory" in str(exc_info.value)

    def test_output_file_is_provided_as_single_file(self):
        """
        Test the situation, when the output file is provided as a single file, not absolute path
        """
        test_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"input_file.txt"
        
        output_file = "output_file.txt"
        
        expected_output_file = Path(__file__).parent/"test_data"/"dir1_with_output_folder"/"_output_"/"output_file"
        
        output_file = get_output_extentionless_file_name(test_file, output_file_name=output_file)
        
        assert output_file == expected_output_file

    
if __name__ == "__main__":
    # test_output_file_name_when_new_existing_dir_provided()
    pass