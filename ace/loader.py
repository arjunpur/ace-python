"""
Data loading utilities for ACE analysis.
"""
import os
import glob
import pandas as pd
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from ace.constants import MODULE_NAMES, COLUMN_MAPPINGS, REQUIRED_COLUMNS


@dataclass
class ACEData:
    """Container for ACE data from multiple modules and demographics."""
    modules: Dict[str, pd.DataFrame]
    demographics: Optional[pd.DataFrame] = None

    def get_module(self, module_name: str) -> Optional[pd.DataFrame]:
        """Get data for a specific module if it exists."""
        return self.modules.get(module_name)

    def participant_ids(self) -> List[str]:
        """Get list of unique participant IDs across all modules."""
        all_ids = set()
        for df in self.modules.values():
            if 'participant_id' in df.columns:
                all_ids.update(df['participant_id'].unique())
        return list(all_ids)

    def filter_by_participant(self, participant_id: str) -> 'ACEData':
        """Filter data to include only a specific participant."""
        filtered_modules = {}
        for name, df in self.modules.items():
            if 'participant_id' in df.columns:
                filtered_df = df[df['participant_id'] == participant_id]
                if not filtered_df.empty:
                    filtered_modules[name] = filtered_df
        
        filtered_demographics = None
        if self.demographics is not None and 'participant_id' in self.demographics.columns:
            filtered_demographics = self.demographics[
                self.demographics['participant_id'] == participant_id
            ]
        
        return ACEData(modules=filtered_modules, demographics=filtered_demographics)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names using the mapping from constants."""
    df = df.copy()
    for old_name, new_name in COLUMN_MAPPINGS.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)
    return df


def preprocess_module_data(df: pd.DataFrame, module_name: str) -> pd.DataFrame:
    """Apply module-specific preprocessing to the data."""
    df = df.copy()
    
    # Convert timestamps to datetime
    if 'time_gameplayed_utc' in df.columns:
        df['time_gameplayed_utc'] = pd.to_datetime(df['time_gameplayed_utc'])
    
    # Convert numeric columns
    numeric_cols = ['response_time', 'response_window', 'trial_number', 'age']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure module name is consistent
    if 'module' in df.columns:
        df['module'] = module_name
    
    # Drop rows with missing critical values
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            df = df.dropna(subset=[col])
    
    # Add calculated fields
    if all(col in df.columns for col in ['response_time', 'result']):
        # Binary accuracy (1 for successful, 0 for others)
        df['accuracy'] = df['result'].apply(lambda x: 1 if x == 'successful' else 0)
        
        # Mark late responses
        if 'response_window' in df.columns:
            df['is_late'] = (df['response_time'] > df['response_window']).astype(int)
    
    return df


class ACELoader:
    """Loads and processes ACE data from files."""
    
    def __init__(self, data_dir: str):
        """
        Initialize with path to data directory.
        
        Args:
            data_dir: Path to directory containing ACE CSV files
        """
        self.data_dir = data_dir
        
    def load_module_file(self, file_path: str) -> pd.DataFrame:
        """
        Load and preprocess a single module file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Preprocessed DataFrame for the module
        """
        try:
            # Extract module name from file path
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Standardize column names
            df = standardize_columns(df)
            
            # Apply module-specific preprocessing
            df = preprocess_module_data(df, module_name)
            
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def load_demographics(self) -> Optional[pd.DataFrame]:
        """
        Load demographics data if available.
        
        Returns:
            Demographics DataFrame or None if not found
        """
        demo_path = os.path.join(self.data_dir, "demographics.csv")
        
        # Try both current directory and subdirectories
        if not os.path.exists(demo_path):
            demo_files = glob.glob(os.path.join(self.data_dir, "**", "demographics.csv"), recursive=True)
            if demo_files:
                demo_path = demo_files[0]
            else:
                return None
        
        try:
            df = pd.read_csv(demo_path)
            return standardize_columns(df)
        except Exception as e:
            print(f"Error loading demographics: {e}")
            return None
    
    def load_all(self) -> ACEData:
        """
        Load all module data files from the specified directory.
        
        Returns:
            ACEData object containing all module data and demographics
        """
        modules = {}
        
        # Find module files in the data directory and subdirectories
        for module_name in MODULE_NAMES:
            # Search in both the main directory and subdirectories
            module_files = glob.glob(os.path.join(self.data_dir, f"{module_name}.csv"))
            if not module_files:
                module_files = glob.glob(os.path.join(self.data_dir, "**", f"{module_name}.csv"), recursive=True)
            
            if module_files:
                df = self.load_module_file(module_files[0])
                if not df.empty:
                    modules[module_name] = df
        
        # Load demographics if available
        demographics = self.load_demographics()
        
        return ACEData(modules=modules, demographics=demographics)


class ACEBulkLoader:
    """Loads multiple ACE datasets from different directories."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize with optional base directory.
        
        Args:
            base_dir: Base directory containing multiple ACE data directories
        """
        self.base_dir = base_dir
    
    def find_data_directories(self) -> List[str]:
        """
        Find directories that might contain ACE data.
        
        Returns:
            List of directory paths
        """
        if not self.base_dir:
            return []
        
        # Look for directories containing CSV files
        potential_dirs = []
        for root, dirs, files in os.walk(self.base_dir):
            csv_files = [f for f in files if f.endswith('.csv')]
            if csv_files:
                potential_dirs.append(root)
        
        return potential_dirs
    
    def load_from_directories(self, directories: List[str]) -> Dict[str, ACEData]:
        """
        Load ACE data from multiple directories.
        
        Args:
            directories: List of directory paths to load from
            
        Returns:
            Dictionary mapping directory names to ACEData objects
        """
        result = {}
        for directory in directories:
            dir_name = os.path.basename(directory)
            loader = ACELoader(directory)
            result[dir_name] = loader.load_all()
        
        return result
    
    def load_all(self) -> Dict[str, ACEData]:
        """
        Find and load all ACE data from subdirectories.
        
        Returns:
            Dictionary mapping directory names to ACEData objects
        """
        directories = self.find_data_directories()
        return self.load_from_directories(directories)