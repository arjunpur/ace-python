import unittest
import tempfile
import shutil
import os
import pandas as pd
import pytest
from ace.loader import ACEBulkLoader, add_module_name

@pytest.fixture
def test_dir():
    # Setup: Create a temporary directory and CSV files
    test_dir = tempfile.mkdtemp()

    file1 = os.path.join(test_dir, 'file1.csv')
    file2 = os.path.join(test_dir, 'file2.csv')
    exclude_file = os.path.join(test_dir, 'exclude_me.csv')
    pattern_file = os.path.join(test_dir, 'pattern_match.csv')
    module1_file = os.path.join(test_dir, 'module1_file.csv')
    module2_file = os.path.join(test_dir, 'module2_file.csv')

    # Write data to the CSV files
    pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}).to_csv(file1, index=False)
    pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]}).to_csv(file2, index=False)
    pd.DataFrame({'col1': [9, 10], 'col2': [11, 12]}).to_csv(exclude_file, index=False)
    pd.DataFrame({'col1': [13, 14], 'col2': [15, 16]}).to_csv(pattern_file, index=False)
    pd.DataFrame({'col1': [17, 18], 'col2': [19, 20]}).to_csv(module1_file, index=False)
    pd.DataFrame({'col1': [21, 22], 'col2': [23, 24]}).to_csv(module2_file, index=False)

    yield test_dir

    # Teardown: Remove the temporary directory and all its contents
    shutil.rmtree(test_dir)

def test_load_files_on_init(test_dir):
    loader = ACEBulkLoader(path=test_dir, verbose=False)
    
    # Check if the files are loaded correctly
    assert 'file1.csv' in loader.data_by_filename
    assert 'file2.csv' in loader.data_by_filename
    assert len(loader.data_by_filename) == 4  # 4 files should be loaded
    
    # Check the content of the loaded DataFrames
    pd.testing.assert_frame_equal(
        loader.data_by_filename['file1.csv'],
        pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    )
    pd.testing.assert_frame_equal(
        loader.data_by_filename['file2.csv'],
        pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    )

def test_exclude_files(test_dir):
    loader = ACEBulkLoader(path=test_dir, exclude=['exclude_me.csv'], verbose=False)
    
    assert 'file1.csv' in loader.data_by_filename
    assert 'file2.csv' in loader.data_by_filename
    assert 'exclude_me.csv' not in loader.data_by_filename

def test_pattern_matching(test_dir):
    loader = ACEBulkLoader(path=test_dir, pattern='pattern', verbose=False)
    
    assert 'file1.csv' not in loader.data_by_filename
    assert 'file2.csv' not in loader.data_by_filename
    assert 'pattern_match.csv' in loader.data_by_filename

def test_which_modules(test_dir):
    loader = ACEBulkLoader(path=test_dir, which_modules=['module1', 'module2'], verbose=False)
    
    assert 'module1_file.csv' in loader.data_by_filename
    assert 'module2_file.csv' in loader.data_by_filename
    assert 'file1.csv' not in loader.data_by_filename
    assert 'file2.csv' not in loader.data_by_filename

def test_add_module_name(subtests):
    # Subtest 1: Has the moduleName field
    with subtests.test(msg="Has moduleName field"):
        df = pd.DataFrame({
            'data': [1, 2, 3],
            'moduleName': [' Module 1 ', 'module2', 'MoDuLe 3']
        })
        filename = 'test_file.csv'
        result_df = add_module_name(df, filename)
        expected_modules = ['MODULE1', 'MODULE2', 'MODULE3']
        assert result_df['module'].tolist() == expected_modules

    # Subtest 2: Does not have the moduleName field
    with subtests.test(msg="Does not have moduleName field"):
        df = pd.DataFrame({
            'data': [1, 2, 3],
        })
        filename = 'test_file.csv'
        result_df = add_module_name(df, filename)
        expected_modules = ['TEST_FILE', 'TEST_FILE', 'TEST_FILE']
        assert result_df['module'].tolist() == expected_modules

if __name__ == '__main__':
    unittest.main()
