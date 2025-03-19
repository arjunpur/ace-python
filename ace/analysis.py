"""
Analysis utilities for ACE data.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass

from ace.constants import (
    MODULE_NAMES,
    MODULE_CONDITIONS,
    OUTCOMES,
    SUMMARY_METRICS,
    SUBSETS
)
from ace.loader import ACEData


@dataclass
class ModuleSummary:
    """Summary statistics for a single module."""
    module_name: str
    metrics: Dict[str, Dict[str, float]]
    conditions: List[str]
    
    def get_metric(self, metric: str, subset: str = "overall", condition: Optional[str] = None) -> Optional[float]:
        """
        Get a specific metric value.
        
        Args:
            metric: Name of the metric (e.g., 'accuracy.mean')
            subset: Data subset (e.g., 'correct', 'overall')
            condition: Specific condition or None for all conditions
            
        Returns:
            Metric value or None if not available
        """
        key = f"{metric}.{subset}"
        if condition:
            key = f"{key}.{condition}"
            
        # Navigate nested dictionary
        parts = key.split('.')
        current = self.metrics
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current if isinstance(current, (int, float)) else None


class ACEAnalyzer:
    """Analysis tools for ACE data."""
    
    def __init__(self, data: ACEData):
        """
        Initialize with ACE data.
        
        Args:
            data: ACEData object containing module data
        """
        self.data = data
    
    def calculate_module_summary(self, module_name: str) -> Optional[ModuleSummary]:
        """
        Calculate comprehensive summary statistics for a module.
        
        Args:
            module_name: Name of the module to analyze
            
        Returns:
            ModuleSummary object or None if module data not available
        """
        df = self.data.get_module(module_name)
        if df is None or df.empty:
            return None
        
        # Get conditions for this module
        conditions = MODULE_CONDITIONS.get(module_name, [])
        actual_conditions = []
        if 'Condition' in df.columns:
            actual_conditions = df['Condition'].unique().tolist()
        
        # Initialize metrics dictionary
        metrics = {}
        
        # Calculate basic trial counts
        metrics['total_trials'] = {'overall': len(df)}
        metrics['total_trials_responded'] = {'overall': df['response_time'].count()}
        
        # Calculate accuracy metrics if available
        if 'accuracy' in df.columns:
            metrics['accuracy'] = {
                'overall': {
                    'mean': df['accuracy'].mean(),
                    'stdv': df['accuracy'].std(),
                }
            }
            
            # Accuracy by condition
            if 'Condition' in df.columns and actual_conditions:
                for condition in actual_conditions:
                    cond_df = df[df['Condition'] == condition]
                    if not cond_df.empty:
                        if 'accuracy' not in metrics:
                            metrics['accuracy'] = {}
                        metrics['accuracy'][condition] = {
                            'mean': cond_df['accuracy'].mean(),
                            'stdv': cond_df['accuracy'].std(),
                        }
        
        # Calculate reaction time metrics
        if 'response_time' in df.columns:
            # Overall
            rt_metrics = {
                'mean': df['response_time'].mean(),
                'median': df['response_time'].median(),
                'stdv': df['response_time'].std(),
                'min': df['response_time'].min(),
                'max': df['response_time'].max(),
                'iqr': df['response_time'].quantile(0.75) - df['response_time'].quantile(0.25),
            }
            metrics['rt'] = {'overall': rt_metrics}
            
            # By condition
            if 'Condition' in df.columns and actual_conditions:
                for condition in actual_conditions:
                    cond_df = df[df['Condition'] == condition]
                    if not cond_df.empty:
                        rt_cond_metrics = {
                            'mean': cond_df['response_time'].mean(),
                            'median': cond_df['response_time'].median(),
                            'stdv': cond_df['response_time'].std(),
                            'min': cond_df['response_time'].min(),
                            'max': cond_df['response_time'].max(),
                            'iqr': cond_df['response_time'].quantile(0.75) - cond_df['response_time'].quantile(0.25),
                        }
                        metrics['rt'][condition] = rt_cond_metrics
        
        # Calculate subsets
        self._calculate_subset_metrics(metrics, df, actual_conditions)
        
        # Calculate RCS (Rate Correct Score)
        self._calculate_rcs(metrics, df, actual_conditions)
        
        # Calculate first half vs second half metrics
        self._calculate_half_metrics(metrics, df, actual_conditions)
        
        # Calculate previous trial effect metrics
        self._calculate_prev_trial_metrics(metrics, df, actual_conditions)
        
        return ModuleSummary(
            module_name=module_name,
            metrics=metrics,
            conditions=actual_conditions
        )
    
    def _calculate_subset_metrics(self, metrics: Dict, df: pd.DataFrame, conditions: List[str]) -> None:
        """Calculate metrics for different data subsets."""
        # Correct trials
        if 'accuracy' in df.columns:
            correct_df = df[df['accuracy'] == 1]
            if not correct_df.empty and 'response_time' in correct_df.columns:
                metrics['rt']['correct'] = {
                    'mean': correct_df['response_time'].mean(),
                    'median': correct_df['response_time'].median(),
                    'stdv': correct_df['response_time'].std(),
                }
                
                # By condition
                if 'Condition' in df.columns and conditions:
                    for condition in conditions:
                        cond_correct_df = correct_df[correct_df['Condition'] == condition]
                        if not cond_correct_df.empty:
                            if condition not in metrics['rt']:
                                metrics['rt'][condition] = {}
                            metrics['rt'][condition]['correct'] = {
                                'mean': cond_correct_df['response_time'].mean(),
                                'median': cond_correct_df['response_time'].median(),
                                'stdv': cond_correct_df['response_time'].std(),
                            }
            
            # Incorrect trials
            incorrect_df = df[df['accuracy'] == 0]
            if not incorrect_df.empty and 'response_time' in incorrect_df.columns:
                metrics['rt']['incorrect'] = {
                    'mean': incorrect_df['response_time'].mean(),
                    'median': incorrect_df['response_time'].median(),
                    'stdv': incorrect_df['response_time'].std(),
                }
                
                # By condition
                if 'Condition' in df.columns and conditions:
                    for condition in conditions:
                        cond_incorrect_df = incorrect_df[incorrect_df['Condition'] == condition]
                        if not cond_incorrect_df.empty:
                            if condition not in metrics['rt']:
                                metrics['rt'][condition] = {}
                            metrics['rt'][condition]['incorrect'] = {
                                'mean': cond_incorrect_df['response_time'].mean(),
                                'median': cond_incorrect_df['response_time'].median(),
                                'stdv': cond_incorrect_df['response_time'].std(),
                            }
        
        # Early (not late) responses
        if 'is_late' in df.columns:
            early_df = df[df['is_late'] == 0]
            if not early_df.empty and 'response_time' in early_df.columns:
                metrics['rt']['early'] = {
                    'mean': early_df['response_time'].mean(),
                    'median': early_df['response_time'].median(),
                    'stdv': early_df['response_time'].std(),
                }
                
                if 'accuracy' in early_df.columns:
                    if 'accuracy' not in metrics:
                        metrics['accuracy'] = {}
                    metrics['accuracy']['early'] = {
                        'mean': early_df['accuracy'].mean(),
                        'stdv': early_df['accuracy'].std(),
                    }
    
    def _calculate_rcs(self, metrics: Dict, df: pd.DataFrame, conditions: List[str]) -> None:
        """Calculate Rate Correct Score (RCS) metrics."""
        # RCS = Number of correct responses / mean overall response time
        if 'accuracy' in df.columns and 'response_time' in df.columns:
            correct_count = df['accuracy'].sum()
            mean_rt = df['response_time'].mean()
            
            if mean_rt > 0:
                rcs = correct_count / mean_rt
                
                if 'rcs' not in metrics:
                    metrics['rcs'] = {}
                metrics['rcs']['overall'] = rcs
                
                # By condition
                if 'Condition' in df.columns and conditions:
                    for condition in conditions:
                        cond_df = df[df['Condition'] == condition]
                        if not cond_df.empty:
                            cond_correct_count = cond_df['accuracy'].sum()
                            cond_mean_rt = cond_df['response_time'].mean()
                            
                            if cond_mean_rt > 0:
                                cond_rcs = cond_correct_count / cond_mean_rt
                                metrics['rcs'][condition] = cond_rcs
    
    def _calculate_half_metrics(self, metrics: Dict, df: pd.DataFrame, conditions: List[str]) -> None:
        """Calculate metrics comparing first half vs second half of trials."""
        if 'trial_number' in df.columns and len(df) > 1:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Split into halves
            mid_point = len(df) // 2
            first_half = df.iloc[:mid_point]
            second_half = df.iloc[mid_point:]
            
            # Calculate metrics for each half
            for half_name, half_df in [('first_half', first_half), ('second_half', second_half)]:
                if not half_df.empty:
                    # Reaction time metrics
                    if 'response_time' in half_df.columns:
                        if 'rt' not in metrics:
                            metrics['rt'] = {}
                        metrics['rt'][half_name] = {
                            'mean': half_df['response_time'].mean(),
                            'median': half_df['response_time'].median(),
                            'stdv': half_df['response_time'].std(),
                        }
                    
                    # Accuracy metrics
                    if 'accuracy' in half_df.columns:
                        if 'accuracy' not in metrics:
                            metrics['accuracy'] = {}
                        metrics['accuracy'][half_name] = {
                            'mean': half_df['accuracy'].mean(),
                            'stdv': half_df['accuracy'].std(),
                        }
                    
                    # RCS metrics
                    if 'accuracy' in half_df.columns and 'response_time' in half_df.columns:
                        correct_count = half_df['accuracy'].sum()
                        mean_rt = half_df['response_time'].mean()
                        
                        if mean_rt > 0:
                            rcs = correct_count / mean_rt
                            if 'rcs' not in metrics:
                                metrics['rcs'] = {}
                            metrics['rcs'][half_name] = rcs
    
    def _calculate_prev_trial_metrics(self, metrics: Dict, df: pd.DataFrame, conditions: List[str]) -> None:
        """Calculate metrics based on previous trial result."""
        if 'trial_number' in df.columns and 'accuracy' in df.columns and len(df) > 1:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Add previous trial accuracy
            df['prev_accuracy'] = df['accuracy'].shift(1)
            
            # Filter out first trial (no previous)
            df_with_prev = df.dropna(subset=['prev_accuracy'])
            
            # Split by previous trial result
            prev_correct_df = df_with_prev[df_with_prev['prev_accuracy'] == 1]
            prev_incorrect_df = df_with_prev[df_with_prev['prev_accuracy'] == 0]
            
            # Calculate metrics for each subset
            for prev_name, prev_df in [('prev_correct', prev_correct_df), ('prev_incorrect', prev_incorrect_df)]:
                if not prev_df.empty:
                    # Reaction time metrics
                    if 'response_time' in prev_df.columns:
                        if 'rt' not in metrics:
                            metrics['rt'] = {}
                        metrics['rt'][prev_name] = {
                            'mean': prev_df['response_time'].mean(),
                            'median': prev_df['response_time'].median(),
                            'stdv': prev_df['response_time'].std(),
                        }
                    
                    # Accuracy metrics
                    if 'accuracy' in prev_df.columns:
                        if 'accuracy' not in metrics:
                            metrics['accuracy'] = {}
                        metrics['accuracy'][prev_name] = {
                            'mean': prev_df['accuracy'].mean(),
                            'stdv': prev_df['accuracy'].std(),
                        }
    
    def analyze_all_modules(self) -> Dict[str, ModuleSummary]:
        """
        Analyze all available modules in the data.
        
        Returns:
            Dictionary mapping module names to ModuleSummary objects
        """
        results = {}
        for module_name in self.data.modules.keys():
            summary = self.calculate_module_summary(module_name)
            if summary:
                results[module_name] = summary
        
        return results
    
    def create_summary_dataframe(self, module_summaries: Dict[str, ModuleSummary]) -> pd.DataFrame:
        """
        Create a flat summary DataFrame from module summaries.
        
        Args:
            module_summaries: Dictionary of ModuleSummary objects
            
        Returns:
            DataFrame with one row per participant and columns for metrics
        """
        # Get unique participant IDs
        participant_ids = self.data.participant_ids()
        
        # Create empty DataFrame
        df_data = {'participant_id': participant_ids}
        
        # Add demographic data if available
        if self.data.demographics is not None:
            demo_df = self.data.demographics
            if 'participant_id' in demo_df.columns:
                # Extract key demographic columns
                for col in ['age', 'handedness', 'gender']:
                    if col in demo_df.columns:
                        demo_subset = demo_df[['participant_id', col]].drop_duplicates()
                        demo_dict = dict(zip(demo_subset['participant_id'], demo_subset[col]))
                        df_data[col] = [demo_dict.get(pid) for pid in participant_ids]
        
        # Prepare data for all metrics
        for module_name, summary in module_summaries.items():
            # Overall accuracy
            if 'accuracy' in summary.metrics and 'overall' in summary.metrics['accuracy']:
                df_data[f"{module_name}.accuracy.mean.overall"] = [summary.metrics['accuracy']['overall'].get('mean')] * len(participant_ids)
            
            # Overall reaction time 
            if 'rt' in summary.metrics and 'overall' in summary.metrics['rt']:
                df_data[f"{module_name}.rt.mean.overall"] = [summary.metrics['rt']['overall'].get('mean')] * len(participant_ids)
                df_data[f"{module_name}.rt.median.overall"] = [summary.metrics['rt']['overall'].get('median')] * len(participant_ids)
                df_data[f"{module_name}.rt.stdv.overall"] = [summary.metrics['rt']['overall'].get('stdv')] * len(participant_ids)
            
            # RCS
            if 'rcs' in summary.metrics and 'overall' in summary.metrics['rcs']:
                df_data[f"{module_name}.rcs.overall"] = [summary.metrics['rcs']['overall']] * len(participant_ids)
            
            # By condition
            for condition in summary.conditions:
                # Clean condition name for column
                clean_cond = condition.replace(' ', '_').lower()
                
                # Condition-specific accuracy
                if 'accuracy' in summary.metrics and condition in summary.metrics['accuracy']:
                    df_data[f"{module_name}.accuracy.mean.{clean_cond}"] = [summary.metrics['accuracy'][condition].get('mean')] * len(participant_ids)
                
                # Condition-specific RT
                if 'rt' in summary.metrics and condition in summary.metrics['rt']:
                    df_data[f"{module_name}.rt.mean.{clean_cond}"] = [summary.metrics['rt'][condition].get('mean')] * len(participant_ids)
                
                # Condition-specific RCS
                if 'rcs' in summary.metrics and condition in summary.metrics['rcs']:
                    df_data[f"{module_name}.rcs.{clean_cond}"] = [summary.metrics['rcs'][condition]] * len(participant_ids)
        
        # Create DataFrame from collected data
        result = pd.DataFrame(df_data)
        
        return result


class ModuleAnalyzer:
    """Base class for module-specific analyzers."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with module data.
        
        Args:
            data: DataFrame containing module data
        """
        self.data = data
    
    def validate_data(self) -> bool:
        """
        Validate that the data contains required columns.
        
        Returns:
            True if data is valid, False otherwise
        """
        required_cols = ['participant_id', 'trial_number', 'response_time', 'result']
        return all(col in self.data.columns for col in required_cols)
    
    def get_basic_stats(self) -> Dict:
        """
        Calculate basic statistics for the module.
        
        Returns:
            Dictionary of basic statistics
        """
        stats = {
            'trial_count': len(self.data),
            'participant_count': self.data['participant_id'].nunique(),
        }
        
        if 'response_time' in self.data.columns:
            stats.update({
                'rt_mean': self.data['response_time'].mean(),
                'rt_median': self.data['response_time'].median(),
                'rt_stdv': self.data['response_time'].std(),
            })
        
        if 'result' in self.data.columns:
            result_counts = self.data['result'].value_counts(normalize=True)
            for result, count in result_counts.items():
                stats[f'result_{result}'] = count
        
        return stats
    
    def analyze(self) -> Dict:
        """
        Perform module-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format'}
        
        return self.get_basic_stats()


# Factory function to create module-specific analyzers
def create_module_analyzer(module_name: str, data: pd.DataFrame) -> ModuleAnalyzer:
    """
    Create an appropriate analyzer for the given module.
    
    Args:
        module_name: Name of the module
        data: DataFrame containing module data
        
    Returns:
        Module-specific analyzer instance
    """
    # Import specific analyzers
    from ace.modules.brt import BRTAnalyzer
    from ace.modules.adp import ADPAnalyzer
    from ace.modules.flanker import FlankerAnalyzer
    from ace.modules.stroop import StroopAnalyzer
    from ace.modules.spatial_span import SpatialSpanAnalyzer
    
    # Map module names to analyzer classes
    analyzer_map = {
        'BRT': BRTAnalyzer,
        'ADP': ADPAnalyzer,
        'FLANKER': FlankerAnalyzer,
        'STROOP': StroopAnalyzer,
        'SPATIAL_SPAN_FORWARD': SpatialSpanAnalyzer,
        'SPATIAL_SPAN_BACKWARD': SpatialSpanAnalyzer,
    }
    
    # Get the appropriate analyzer class or default to base class
    analyzer_class = analyzer_map.get(module_name, ModuleAnalyzer)
    
    return analyzer_class(data)