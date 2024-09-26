import unittest
import tempfile
import shutil
import os
import pandas as pd
from ace.loader import ACEBulkLoader

class TestACEBulkLoader(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create some CSV files
        self.file1 = os.path.join(self.test_dir, 'file1.csv')
        self.file2 = os.path.join(self.test_dir, 'file2.csv')
        self.exclude_file = os.path.join(self.test_dir, 'exclude_me.csv')
        self.pattern_file = os.path.join(self.test_dir, 'pattern_match.csv')
        self.module1_file = os.path.join(self.test_dir, 'module1_file.csv')
        self.module2_file = os.path.join(self.test_dir, 'module2_file.csv')

        # Write data to the CSV files
        pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}).to_csv(self.file1, index=False)
        pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]}).to_csv(self.file2, index=False)
        pd.DataFrame({'col1': [9, 10], 'col2': [11, 12]}).to_csv(self.exclude_file, index=False)
        pd.DataFrame({'col1': [13, 14], 'col2': [15, 16]}).to_csv(self.pattern_file, index=False)
        pd.DataFrame({'col1': [17, 18], 'col2': [19, 20]}).to_csv(self.module1_file, index=False)
        pd.DataFrame({'col1': [21, 22], 'col2': [23, 24]}).to_csv(self.module2_file, index=False)

    def tearDown(self):
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)

    def test_load_files_on_init(self):
        loader = ACEBulkLoader(path=self.test_dir, verbose=False)
        
        # Check if the files are loaded correctly
        self.assertIn('file1.csv', loader.data_by_filename)
        self.assertIn('file2.csv', loader.data_by_filename)
        self.assertEqual(len(loader.data_by_filename), 4)  # 4 files should be loaded
        
        # Check the content of the loaded DataFrames
        pd.testing.assert_frame_equal(
            loader.data_by_filename['file1.csv'],
            pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        )
        pd.testing.assert_frame_equal(
            loader.data_by_filename['file2.csv'],
            pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
        )

    def test_exclude_files(self):
        loader = ACEBulkLoader(path=self.test_dir, exclude=['exclude_me.csv'], verbose=False)
        
        self.assertIn('file1.csv', loader.data_by_filename)
        self.assertIn('file2.csv', loader.data_by_filename)
        self.assertNotIn('exclude_me.csv', loader.data_by_filename)

    def test_pattern_matching(self):
        loader = ACEBulkLoader(path=self.test_dir, pattern='pattern', verbose=False)
        
        self.assertNotIn('file1.csv', loader.data_by_filename)
        self.assertNotIn('file2.csv', loader.data_by_filename)
        self.assertIn('pattern_match.csv', loader.data_by_filename)

    def test_which_modules(self):
        loader = ACEBulkLoader(path=self.test_dir, which_modules=['module1', 'module2'], verbose=False)
        
        self.assertIn('module1_file.csv', loader.data_by_filename)
        self.assertIn('module2_file.csv', loader.data_by_filename)
        self.assertNotIn('file1.csv', loader.data_by_filename)
        self.assertNotIn('file2.csv', loader.data_by_filename)

if __name__ == '__main__':
    unittest.main()
