import os
import pandas as pd
import re
from typing import List, Optional, Union
from dataclasses import dataclass
import glob
import logging

import ace.constants as constants

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
        self._standardize_data(self._data_by_filename)
 
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
                data = pd.read_csv(file)
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
    
    def _standardize_data(self, data_by_file: dict[str, pd.DataFrame]):
        for file, df in data_by_file.items():
            df = standardize_ace_column_names(df)
            df = add_module_name(df, file)


def standardize_ace_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes the column names of the DataFrame to be consistent with the ACE format.

    - Convert all column names to lowercase.
    - Replace special characters with underscores.
    - Replace spaces with underscores.

    Args:
        df (pd.DataFrame): The DataFrame to standardize.
    """
    new_names = [replace_special_characters(col, replacement='_') for col in df.columns]
    new_names = [replace_spaces(name, replacement='_') for name in new_names]
    df.columns = new_names
    return df

def replace_special_characters(name: str, replacement: str = '') -> str:
    return re.sub(r'[^a-zA-Z0-9_]', replacement, name)

def replace_spaces(name: str, replacement: str = '_') -> str:
    return re.sub(r' ', replacement, name)

def add_module_name(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    if constants.COL_MODULE_NAME in df.columns:
        df = df.rename(columns={constants.COL_MODULE_NAME: constants.COL_MODULE})
        module_str_series = df[constants.COL_MODULE].astype(str)
    else:
        base_filename = os.path.basename(filename)
        name_without_ext = os.path.splitext(base_filename)[0]
        module_str_series = pd.Series([name_without_ext] * len(df))

    # Standardize the module strings: uppercase and remove spaces
    df[constants.COL_MODULE] = module_str_series.str.upper().str.replace(' ', '', regex=False)
    return df

def standardize_ace_ids(df: pd.DataFrame) -> pd.DataFrame:
    return df

def standardize_ace_column_types(df: pd.DataFrame) -> pd.DataFrame:
    return df

def standardize_ace_values(df: pd.DataFrame) -> pd.DataFrame:
    return df



