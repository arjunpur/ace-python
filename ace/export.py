"""
Export functions for ACE analysis.
"""
import os
import pandas as pd
import json
import numpy as np
from typing import Dict, List, Optional, Union, Any

from ace.analysis import ModuleSummary


# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles NumPy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)


def export_summary_to_csv(summary_df: pd.DataFrame, output_path: str) -> str:
    """
    Export summary DataFrame to CSV file.
    
    Args:
        summary_df: DataFrame containing summary statistics
        output_path: Path to output CSV file
        
    Returns:
        Path to the saved file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save to CSV
    summary_df.to_csv(output_path, index=False)
    
    return output_path


def export_summary_to_excel(summary_df: pd.DataFrame, output_path: str) -> str:
    """
    Export summary DataFrame to Excel file.
    
    Args:
        summary_df: DataFrame containing summary statistics
        output_path: Path to output Excel file
        
    Returns:
        Path to the saved file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    try:
        # Save to Excel
        summary_df.to_excel(output_path, index=False)
        return output_path
    except ImportError:
        # If openpyxl is not installed, fall back to CSV
        csv_path = output_path.replace('.xlsx', '.csv')
        print(f"Warning: openpyxl not installed. Exporting to CSV instead: {csv_path}")
        return export_summary_to_csv(summary_df, csv_path)


def export_module_summary_to_json(module_summary: ModuleSummary, output_path: str) -> str:
    """
    Export ModuleSummary to JSON file.
    
    Args:
        module_summary: ModuleSummary object
        output_path: Path to output JSON file
        
    Returns:
        Path to the saved file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Convert to dictionary
    summary_dict = {
        'module_name': module_summary.module_name,
        'conditions': module_summary.conditions,
        'metrics': module_summary.metrics
    }
    
    # Save to JSON using custom encoder
    with open(output_path, 'w') as f:
        json.dump(summary_dict, f, indent=2, cls=NumpyEncoder)
    
    return output_path


def export_all_summaries(module_summaries: Dict[str, ModuleSummary], 
                         summary_df: pd.DataFrame,
                         output_dir: str) -> Dict[str, str]:
    """
    Export all summaries to various formats.
    
    Args:
        module_summaries: Dictionary of ModuleSummary objects
        summary_df: Participant summary DataFrame
        output_dir: Output directory
        
    Returns:
        Dictionary mapping export type to output path
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize result dictionary
    result = {}
    
    # Export summary DataFrame to CSV
    csv_path = os.path.join(output_dir, 'participant_summary.csv')
    result['summary_csv'] = export_summary_to_csv(summary_df, csv_path)
    
    # Export summary DataFrame to Excel (with fallback)
    excel_path = os.path.join(output_dir, 'participant_summary.xlsx')
    try:
        result['summary_excel'] = export_summary_to_excel(summary_df, excel_path)
    except Exception as e:
        print(f"Warning: Excel export failed ({e}). Using CSV only.")
    
    # Create module summaries directory
    module_dir = os.path.join(output_dir, 'module_summaries')
    os.makedirs(module_dir, exist_ok=True)
    
    # Export individual module summaries
    for module_name, summary in module_summaries.items():
        json_path = os.path.join(module_dir, f'{module_name}_summary.json')
        try:
            result[f'{module_name}_json'] = export_module_summary_to_json(summary, json_path)
        except Exception as e:
            print(f"Warning: JSON export failed for {module_name}: {e}")
    
    return result


def prepare_rds_export(summary_df: pd.DataFrame) -> str:
    """
    Prepare R data frame export (R code to recreate the dataframe).
    
    Args:
        summary_df: DataFrame to export
        
    Returns:
        R code string to recreate the dataframe
    """
    # Convert column names to valid R names
    r_cols = [col.replace('.', '_') for col in summary_df.columns]
    
    # Start building R code
    r_code = "# Generated R code to recreate summary dataframe\n"
    r_code += "library(dplyr)\n\n"
    r_code += "# Create empty dataframe with correct column names\n"
    r_code += "df <- data.frame(matrix(ncol={}, nrow=0))\n".format(len(r_cols))
    r_code += "colnames(df) <- c({})\n\n".format(
        ', '.join(['"{}"'.format(col) for col in r_cols])
    )
    
    # Add each row
    r_code += "# Add rows\n"
    for _, row in summary_df.iterrows():
        row_values = []
        for val in row:
            if pd.isna(val):
                row_values.append("NA")
            elif isinstance(val, str):
                row_values.append('"{}"'.format(val))
            else:
                row_values.append(str(val))
        
        r_code += "df <- rbind(df, c({}))\n".format(', '.join(row_values))
    
    return r_code


def export_for_r(summary_df: pd.DataFrame, output_path: str) -> str:
    """
    Export summary DataFrame for use in R.
    
    Args:
        summary_df: DataFrame containing summary statistics
        output_path: Path to output R script file
        
    Returns:
        Path to the saved file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Generate R code
    r_code = prepare_rds_export(summary_df)
    
    # Save R script
    with open(output_path, 'w') as f:
        f.write(r_code)
    
    return output_path