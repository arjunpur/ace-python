import os
import pandas as pd
import re
from typing import List, Optional, Union
from dataclasses import dataclass

@dataclass
class ACEBulkLoader:
    path: str = "."
    verbose: bool = True
    recursive: bool = False 
    exclude: Optional[List[str]] = None
    pattern: str = ""
    which_modules: Union[str, List[str]] = ""
    data_type: str = "explorer"

    def __post_init__(self):
        self.logger = self._setup_logger()

    def _setup_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def load(self) -> pd.DataFrame:
        """
        Load and process all ACE CSV files in the specified directory.

        Returns:
            pd.DataFrame: Combined data from all processed CSV files.
        """
        files = self._get_csv_files()
        data_list = self._process_files(files)
        
        if not data_list:
            raise ValueError("No data could be loaded from the CSV files")
        
        return pd.concat(data_list, ignore_index=True)

    def _get_csv_files(self) -> List[str]:
        files = []
        for root, _, filenames in os.walk(self.path):
            for filename in filenames:
                if filename.endswith('.csv'):
                    files.append(os.path.join(root, filename))
            if not self.recursive:
                break
        
        files.sort()
        files = self._apply_filters(files)
        
        if not files:
            raise ValueError("No matching CSV files found")
        
        return files

    def _apply_filters(self, files: List[str]) -> List[str]:
        if self.exclude:
            files = [f for f in files if not any(ex in f for ex in self.exclude)]
        
        if self.pattern:
            files = [f for f in files if re.search(self.pattern, f)]
        
        if self.which_modules:
            files = [f for f in files if any(module in f for module in self.which_modules)]
        
        return files

    def _process_files(self, files: List[str]) -> List[pd.DataFrame]:
        data_list = []
        for file in files:
            if self.verbose:
                self.logger.info(f"Processing {file}")
            try:
                data = pd.read_csv(file)
                data_list.append(data)
            except Exception as e:
                self.logger.error(f"Error processing {file}: {str(e)}")
        return data_list




