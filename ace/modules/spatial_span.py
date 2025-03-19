"""
Spatial Span module analyzers (forward and backward).
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from ace.analysis import ModuleAnalyzer


class SpatialSpanAnalyzer(ModuleAnalyzer):
    """Analyzer for Spatial Span modules (forward and backward)."""
    
    def validate_data(self) -> bool:
        """Check if data has required columns for Spatial Span analysis."""
        required_cols = ['participant_id', 'trial_number', 'result']
        return all(col in self.data.columns for col in required_cols)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform Spatial Span-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format for Spatial Span analysis'}
        
        results = self.get_basic_stats()
        
        # Add Spatial Span-specific analyses
        df = self.data.copy()
        
        # Calculate basic accuracy
        df['accuracy'] = (df['result'] == 'successful').astype(int)
        results['overall_accuracy'] = df['accuracy'].mean()
        
        # Check if we have level information (essential for spatial span)
        if 'level' not in df.columns:
            # Try to derive level information if possible
            if 'detail' in df.columns and df['detail'].str.contains('level').any():
                # Extract level from detail column
                df['level'] = df['detail'].str.extract(r'level\s*(\d+)', flags=re.IGNORECASE).astype(float)
            else:
                results['warning'] = 'No level information available'
                return results
        
        # Calculate maximum span reached
        max_level = df['level'].max()
        results['max_level_reached'] = max_level
        
        # Calculate span (highest level with at least one correct trial)
        for level in sorted(df['level'].unique(), reverse=True):
            level_df = df[df['level'] == level]
            if level_df['accuracy'].sum() > 0:
                results['object_count_span'] = level
                break
        
        # Calculate span with stricter criteria (2 consecutive correct trials)
        prev_correct_level = None
        for level in sorted(df['level'].unique()):
            level_df = df[df['level'] == level]
            if level_df['accuracy'].mean() >= 0.5:  # At least half correct
                if prev_correct_level == level - 1:  # Previous level was also correct
                    results['strict_span'] = level
                prev_correct_level = level
            else:
                prev_correct_level = None
        
        # Analyze level-specific performance
        level_stats = {}
        for level in sorted(df['level'].unique()):
            level_df = df[df['level'] == level]
            level_stats[level] = {
                'trials': len(level_df),
                'accuracy': level_df['accuracy'].mean(),
            }
            
            # RT analysis if available
            if 'response_time' in level_df.columns:
                correct_level = level_df[level_df['accuracy'] == 1]
                if not correct_level.empty:
                    level_stats[level]['rt_mean'] = correct_level['response_time'].mean()
                    level_stats[level]['rt_stdv'] = correct_level['response_time'].std()
        
        results['level_stats'] = level_stats
        
        # Calculate level transition metrics (difficulty adaptation)
        if 'trial_number' in df.columns:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Track level transitions
            transitions = []
            prev_level = None
            
            for _, row in df.iterrows():
                level = row['level']
                if prev_level is not None and level != prev_level:
                    transition = 1 if level > prev_level else -1
                    transitions.append(transition)
                prev_level = level
            
            if transitions:
                results['level_increases'] = transitions.count(1)
                results['level_decreases'] = transitions.count(-1)
                results['net_progression'] = sum(transitions)
        
        # Calculate first-trial success rate by level
        first_trial_success = {}
        for level in sorted(df['level'].unique()):
            level_trials = df[df['level'] == level].sort_values('trial_number')
            if not level_trials.empty:
                first_trial = level_trials.iloc[0]
                first_trial_success[level] = int(first_trial['accuracy'])
        
        results['first_trial_success'] = first_trial_success
        
        # Calculate trial-by-trial error patterns
        if 'detail' in df.columns:
            # Look for sequence information
            sequence_cols = [col for col in df.columns if 'sequence' in col.lower()]
            response_cols = [col for col in df.columns if 'response' in col.lower()]
            
            if sequence_cols and response_cols:
                seq_col = sequence_cols[0]
                resp_col = response_cols[0]
                
                # Calculate error types
                error_types = self._analyze_sequence_errors(df, seq_col, resp_col)
                results.update(error_types)
        
        # Direction-specific analysis for backward span
        is_backward = 'BACKWARD' in self.data['module'].iloc[0] if 'module' in self.data.columns else False
        if is_backward:
            results['is_backward'] = True
            
            # Add any backward-specific analyses here
            # Comparison to forward span would require external data
        
        return results
    
    def _analyze_sequence_errors(self, df: pd.DataFrame, 
                                sequence_col: str, 
                                response_col: str) -> Dict[str, Any]:
        """
        Analyze sequence errors in spatial span task.
        
        Args:
            df: DataFrame with sequence and response data
            sequence_col: Column name for correct sequence
            response_col: Column name for participant response
            
        Returns:
            Dictionary of error analysis results
        """
        results = {}
        
        # Initialize counters
        omission_errors = 0  # Missing items
        commission_errors = 0  # Extra items
        order_errors = 0  # Items in wrong order
        
        # Analyze each trial
        for _, row in df.iterrows():
            if row['accuracy'] == 0:  # Incorrect trial
                # Parse sequences
                correct_seq = self._parse_sequence(row[sequence_col])
                response_seq = self._parse_sequence(row[response_col])
                
                if not correct_seq or not response_seq:
                    continue
                
                # Check for different error types
                if len(response_seq) < len(correct_seq):
                    omission_errors += 1
                elif len(response_seq) > len(correct_seq):
                    commission_errors += 1
                else:
                    # Check if all items are present but in wrong order
                    if sorted(response_seq) == sorted(correct_seq):
                        order_errors += 1
        
        # Calculate error proportions
        total_errors = df['accuracy'].value_counts().get(0, 0)
        if total_errors > 0:
            results['omission_error_rate'] = omission_errors / total_errors
            results['commission_error_rate'] = commission_errors / total_errors
            results['order_error_rate'] = order_errors / total_errors
        
        return results
    
    def _parse_sequence(self, seq_str: str) -> List[str]:
        """
        Parse sequence string into list of items.
        
        Args:
            seq_str: String representation of sequence
            
        Returns:
            List of sequence items
        """
        if not seq_str or not isinstance(seq_str, str):
            return []
        
        # Handle different sequence formats
        if ',' in seq_str:
            return seq_str.split(',')
        elif ' ' in seq_str:
            return seq_str.split()
        else:
            return list(seq_str)  # Split into characters