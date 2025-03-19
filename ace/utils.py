"""
Utility functions for ACE analysis.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any


def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> float:
    """
    Safely divide two numbers, returning 0 if denominator is 0.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        
    Returns:
        Result of division or 0 if denominator is 0
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator


def calculate_rcs(correct_count: int, mean_rt: float) -> float:
    """
    Calculate Rate Correct Score (RCS).
    
    Args:
        correct_count: Number of correct responses
        mean_rt: Mean response time in ms
        
    Returns:
        RCS value
    """
    return safe_divide(correct_count, mean_rt)


def flatten_nested_dict(d: Dict, prefix: str = '', separator: str = '.') -> Dict:
    """
    Flatten a nested dictionary into a single-level dictionary.
    
    Args:
        d: Nested dictionary
        prefix: Prefix for flattened keys
        separator: Separator character for key levels
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{prefix}{separator}{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)


def find_csv_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    Find CSV files in a directory, optionally matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: Optional filename pattern to match
        
    Returns:
        List of CSV file paths
    """
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                if pattern is None or pattern in file:
                    csv_files.append(os.path.join(root, file))
    return csv_files


def group_trials_by_condition(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Group trials by condition.
    
    Args:
        df: DataFrame with 'Condition' column
        
    Returns:
        Dictionary mapping condition names to DataFrames
    """
    if 'Condition' not in df.columns:
        return {'overall': df}
    
    result = {}
    for condition in df['Condition'].unique():
        result[condition] = df[df['Condition'] == condition]
    
    # Also include overall
    result['overall'] = df
    
    return result


def calculate_trial_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trial accuracy based on result column.
    
    Args:
        df: DataFrame with 'result' column
        
    Returns:
        DataFrame with added 'accuracy' column
    """
    if 'result' not in df.columns:
        return df
    
    df = df.copy()
    df['accuracy'] = (df['result'] == 'successful').astype(int)
    return df


def identify_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Identify outliers in a series of values.
    
    Args:
        series: Series of numeric values
        method: Method to use ('iqr' or 'zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean series with True for outliers
    """
    if method == 'iqr':
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == 'zscore':
        z_scores = (series - series.mean()) / series.std()
        return abs(z_scores) > threshold
    
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")


def calculate_split_half_reliability(df: pd.DataFrame, metric_col: str) -> float:
    """
    Calculate split-half reliability for a metric.
    
    Args:
        df: DataFrame with trial data
        metric_col: Column containing the metric to calculate reliability for
        
    Returns:
        Split-half reliability coefficient
    """
    if metric_col not in df.columns or len(df) < 2:
        return np.nan
    
    # Sort by trial number if available
    if 'trial_number' in df.columns:
        df = df.sort_values('trial_number')
    
    # Split into even and odd trials
    even_trials = df.iloc[::2][metric_col]
    odd_trials = df.iloc[1::2][metric_col]
    
    # Calculate correlation
    if len(even_trials) > 1 and len(odd_trials) > 1:
        correlation = even_trials.corr(odd_trials)
        
        # Apply Spearman-Brown correction
        reliability = (2 * correlation) / (1 + correlation)
        return reliability
    
    return np.nan


def create_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a data quality report for a DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with data quality metrics
    """
    report = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'missing_values': {}
    }
    
    # Missing values by column
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing > 0:
            report['missing_values'][col] = {
                'count': missing,
                'percentage': (missing / len(df)) * 100
            }
    
    # Numeric column statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    report['numeric_columns'] = {}
    for col in numeric_cols:
        # Skip if all values are missing
        if df[col].isna().all():
            continue
            
        col_stats = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max()
        }
        
        # Detect outliers
        outliers = identify_outliers(df[col])
        col_stats['outlier_count'] = outliers.sum()
        col_stats['outlier_percentage'] = (outliers.sum() / len(df)) * 100
        
        report['numeric_columns'][col] = col_stats
    
    # Categorical column statistics
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    report['categorical_columns'] = {}
    for col in categorical_cols:
        # Skip if all values are missing
        if df[col].isna().all():
            continue
            
        value_counts = df[col].value_counts()
        col_stats = {
            'unique_values': len(value_counts),
            'most_common': value_counts.index[0] if not value_counts.empty else None,
            'most_common_count': value_counts.iloc[0] if not value_counts.empty else 0,
        }
        
        report['categorical_columns'][col] = col_stats
    
    return report