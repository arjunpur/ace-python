"""
Basic Response Time (BRT) module analyzer.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from ace.analysis import ModuleAnalyzer
from ace.utils import calculate_rcs, group_trials_by_condition


class BRTAnalyzer(ModuleAnalyzer):
    """Analyzer for Basic Response Time (BRT) module."""
    
    def validate_data(self) -> bool:
        """Check if data has required columns for BRT analysis."""
        required_cols = ['participant_id', 'trial_number', 'response_time', 'result']
        return all(col in self.data.columns for col in required_cols)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform BRT-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format for BRT analysis'}
        
        results = self.get_basic_stats()
        
        # Add BRT-specific analyses
        df = self.data.copy()
        
        # Calculate accuracy
        df['accuracy'] = (df['result'] == 'successful').astype(int)
        
        # Group by condition (hand used)
        condition_groups = group_trials_by_condition(df)
        
        # Analyze each condition
        for condition, condition_df in condition_groups.items():
            # Skip if no data
            if condition_df.empty:
                continue
            
            # Get correct trials only
            correct_df = condition_df[condition_df['accuracy'] == 1]
            
            # Skip if no correct trials
            if correct_df.empty:
                continue
            
            # Calculate reaction time statistics
            rt_mean = correct_df['response_time'].mean()
            rt_median = correct_df['response_time'].median()
            rt_stdv = correct_df['response_time'].std()
            
            # Store results
            condition_key = condition.replace(' ', '_').lower()
            results[f'rt_mean_{condition_key}'] = rt_mean
            results[f'rt_median_{condition_key}'] = rt_median
            results[f'rt_stdv_{condition_key}'] = rt_stdv
            
            # Calculate RCS
            correct_count = len(correct_df)
            rcs = calculate_rcs(correct_count, rt_mean)
            results[f'rcs_{condition_key}'] = rcs
        
        # Calculate dominance effects if possible
        if all(hand in condition_groups for hand in ['Right Index', 'Left Index']):
            right_df = condition_groups['Right Index']
            left_df = condition_groups['Left Index']
            
            if not right_df.empty and not left_df.empty:
                # Get correct trials only
                right_correct = right_df[right_df['accuracy'] == 1]
                left_correct = left_df[left_df['accuracy'] == 1]
                
                if not right_correct.empty and not left_correct.empty:
                    # Calculate mean RTs
                    right_rt = right_correct['response_time'].mean()
                    left_rt = left_correct['response_time'].mean()
                    
                    # Calculate dominance effect (positive = right faster)
                    dominance_effect = left_rt - right_rt
                    results['dominance_effect'] = dominance_effect
                    
                    # Calculate relative dominance effect
                    avg_rt = (right_rt + left_rt) / 2
                    relative_dominance = dominance_effect / avg_rt
                    results['relative_dominance_effect'] = relative_dominance
        
        # Calculate learning effect (early vs late trials)
        if len(df) > 10:  # Only if we have enough trials
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Split into first and last half
            first_half = df.iloc[:len(df)//2]
            second_half = df.iloc[len(df)//2:]
            
            # Calculate mean RTs for correct trials in each half
            first_half_correct = first_half[first_half['accuracy'] == 1]
            second_half_correct = second_half[second_half['accuracy'] == 1]
            
            if not first_half_correct.empty and not second_half_correct.empty:
                first_half_rt = first_half_correct['response_time'].mean()
                second_half_rt = second_half_correct['response_time'].mean()
                
                # Calculate learning effect (positive = getting faster)
                learning_effect = first_half_rt - second_half_rt
                results['learning_effect'] = learning_effect
                
                # Calculate relative learning effect
                avg_rt = (first_half_rt + second_half_rt) / 2
                relative_learning = learning_effect / avg_rt
                results['relative_learning_effect'] = relative_learning
        
        # Analyze response time variability
        if not df.empty:
            correct_df = df[df['accuracy'] == 1]
            if not correct_df.empty:
                # Coefficient of variation (CV)
                mean_rt = correct_df['response_time'].mean()
                stdv_rt = correct_df['response_time'].std()
                cv = stdv_rt / mean_rt
                results['cv'] = cv
                
                # Intra-individual variability (IIV)
                # Group by participant
                for pid, pid_df in correct_df.groupby('participant_id'):
                    if len(pid_df) > 1:
                        pid_mean = pid_df['response_time'].mean()
                        pid_stdv = pid_df['response_time'].std()
                        results[f'iiv_{pid}'] = pid_stdv / pid_mean
        
        return results