import os
import pandas as pd
import re
from typing import List, Optional, Union
from dataclasses import dataclass
import glob
import logging

from ace.constants import COL_AGE, COL_CONDITION, COL_GENDER, COL_GRADE, COL_HANDEDNESS, COL_MODULE, COL_NAME, COL_PID, COL_RT, COL_RW, COL_SUB_ID, COL_TIME

@dataclass
class ACEBulkLoader:
    path: str = "."
    verbose: bool = True
    recursive: bool = False 
    exclude: Optional[List[str]] = None
    pattern: str = ""
    which_modules: Union[str, List[str]] = ""

    def __post_init__(self):
        self.logger = self._setup_logger()
        self._data_by_filename = self._load_files_on_init()
 
    @property
    def data_by_filename(self) -> dict:
        return self._data_by_filename

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def _load_files_on_init(self) -> dict:
        files = self._load_csv_files()
        data_by_filename = {}
        for file in files:
            if self.verbose:
                self.logger.info(f"Processing {file}")
            try:
                data = self._load_ace_file(file)
                if data is not None and not data.empty:
                    data_by_filename[file] = data
            except Exception as e:
                self.logger.error(f"Error processing {file}: {str(e)}")
        return data_by_filename

    def _load_csv_files(self) -> List[str]:
        files = glob.glob(os.path.join(self.path, "**/*.csv"), recursive=True)

        if self.exclude:
            files = [f for f in files if not any(ex in f for ex in self.exclude)]
        
        if self.pattern:
            files = [f for f in files if re.search(self.pattern, f)]
        
        if self.which_modules:
            files = [f for f in files if any(module in f for module in self.which_modules)]
        
        if not files:
            raise ValueError("No matching CSV files found")

        return files
    
    def _load_ace_file(self, file: str) -> pd.DataFrame:
        df = pd.read_csv(file)

        # Standardize column names
        df = standardize_ace_column_names(df)
        df = add_module_name(df, file)


def standardize_ace_column_names(df: pd.DataFrame) -> pd.DataFrame:

    # Convert all column names to lowercase
    new_names = [col.lower() for col in df.columns]
    new_names = [replace_special_characters(name, replacement='_') for name in new_names]
    new_names = [replace_spaces(name, replacement='_') for name in new_names]
    df.columns = new_names
    return df

def replace_special_characters(name: str, replacement: str = '') -> str:
    return re.sub(r'[^a-zA-Z0-9_]', replacement, name)

def replace_spaces(name: str, replacement: str = '_') -> str:
    return re.sub(r' ', replacement, name)


def add_module_name(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Adds a 'module' column to the DataFrame based on the 'moduleName' column or the filename.

    - If 'moduleName' exists in the DataFrame:
        - Rename it to 'module'.
        - Convert its values to uppercase and remove all spaces.
    - If 'moduleName' does not exist:
        - Extract the module from the filename.
        - Convert it to uppercase and remove all spaces.
        - Verify against the list of expected modules. If not matched, set to 'unknown'.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        filename (str): The filename from which to extract module information if 'moduleName' is absent.

    Returns:
        pd.DataFrame: The DataFrame with an added 'module' column.
    """
    if 'moduleName' in df.columns:
        # Rename 'moduleName' to 'module'
        df = df.rename(columns={'moduleName': COL_MODULE})
        module_str_series = df[COL_MODULE].astype(str)
    else:
        # Extract module from filename
        base_filename = os.path.basename(filename)
        name_without_ext = os.path.splitext(base_filename)[0]
        module_str_series = pd.Series([name_without_ext] * len(df))

    # Standardize the module strings: uppercase and remove spaces
    module_str_series = module_str_series.str.upper().str.replace(' ', '', regex=False)

    # Verify against ALL_MODULES, set to 'unknown' if not matched
    df[COL_MODULE] = module_str_series.where(module_str_series.isin(ALL_MODULES), 'unknown')

    return df

def standardize_ace_ids(df: pd.DataFrame) -> pd.DataFrame:
    return df

def standardize_ace_column_types(df: pd.DataFrame) -> pd.DataFrame:
    return df

def standardize_ace_values(df: pd.DataFrame) -> pd.DataFrame:
    return df



