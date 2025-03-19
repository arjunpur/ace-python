"""
ADP (Face Switch) module analyzer.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from ace.analysis import ModuleAnalyzer
from ace.utils import calculate_rcs, group_trials_by_condition


class ADPAnalyzer(ModuleAnalyzer):
    """Analyzer for ADP (Face Switch) module."""
    
    def validate_data(self) -> bool:
        """Check if data has required columns for ADP analysis."""
        required_cols = ['participant_id', 'trial_number', 'response_time', 'result', 'Condition']
        return all(col in self.data.columns for col in required_cols)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform ADP-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format for ADP analysis'}
        
        results = self.get_basic_stats()
        
        # Add ADP-specific analyses
        df = self.data.copy()
        
        # Calculate accuracy
        df['accuracy'] = (df['result'] == 'successful').astype(int)
        
        # Group by condition (Happy, Negative)
        condition_groups = group_trials_by_condition(df)
        
        # Verify that we have both conditions
        if not all(cond in condition_groups for cond in ['Happy', 'Negative']):
            results['warning'] = 'Missing either Happy or Negative condition'
            return results
        
        # Analyze each condition
        for condition, condition_df in condition_groups.items():
            # Skip if no data
            if condition_df.empty:
                continue
            
            # Calculate overall accuracy
            accuracy = condition_df['accuracy'].mean()
            results[f'accuracy_{condition.lower()}'] = accuracy
            
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
            condition_key = condition.lower()
            results[f'rt_mean_{condition_key}'] = rt_mean
            results[f'rt_median_{condition_key}'] = rt_median
            results[f'rt_stdv_{condition_key}'] = rt_stdv
            
            # Calculate RCS
            correct_count = len(correct_df)
            rcs = calculate_rcs(correct_count, rt_mean)
            results[f'rcs_{condition_key}'] = rcs
        
        # Calculate emotional bias effects if we have both conditions
        happy_df = condition_groups['Happy']
        negative_df = condition_groups['Negative']
        
        if not happy_df.empty and not negative_df.empty:
            # RT Emotional Bias
            happy_correct = happy_df[happy_df['accuracy'] == 1]
            negative_correct = negative_df[negative_df['accuracy'] == 1]
            
            if not happy_correct.empty and not negative_correct.empty:
                # Mean RTs
                happy_rt = happy_correct['response_time'].mean()
                negative_rt = negative_correct['response_time'].mean()
                
                # Emotional bias effect (Negative - Happy)
                rt_bias = negative_rt - happy_rt
                results['rt_emotional_bias'] = rt_bias
                
                # Relative emotional bias
                avg_rt = (happy_rt + negative_rt) / 2
                results['relative_rt_emotional_bias'] = rt_bias / avg_rt if avg_rt > 0 else 0
            
            # Accuracy Emotional Bias
            happy_acc = happy_df['accuracy'].mean()
            negative_acc = negative_df['accuracy'].mean()
            
            # Accuracy emotional bias (Happy - Negative)
            acc_bias = happy_acc - negative_acc
            results['accuracy_emotional_bias'] = acc_bias
        
        # Calculate task switching effects
        if 'trial_number' in df.columns:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Add previous trial condition
            df['prev_condition'] = df['Condition'].shift(1)
            
            # Filter out first trial (no previous)
            df_with_prev = df.dropna(subset=['prev_condition'])
            
            # Create stay and switch groups
            stay_trials = df_with_prev[df_with_prev['Condition'] == df_with_prev['prev_condition']]
            switch_trials = df_with_prev[df_with_prev['Condition'] != df_with_prev['prev_condition']]
            
            if not stay_trials.empty and not switch_trials.empty:
                # Overall switch costs
                stay_acc = stay_trials['accuracy'].mean()
                switch_acc = switch_trials['accuracy'].mean()
                results['stay_accuracy'] = stay_acc
                results['switch_accuracy'] = switch_acc
                results['switch_cost_accuracy'] = stay_acc - switch_acc
                
                # RT switch costs (correct trials only)
                stay_correct = stay_trials[stay_trials['accuracy'] == 1]
                switch_correct = switch_trials[switch_trials['accuracy'] == 1]
                
                if not stay_correct.empty and not switch_correct.empty:
                    stay_rt = stay_correct['response_time'].mean()
                    switch_rt = switch_correct['response_time'].mean()
                    results['stay_rt'] = stay_rt
                    results['switch_rt'] = switch_rt
                    results['switch_cost_rt'] = switch_rt - stay_rt
                    
                    # Relative switch cost
                    avg_rt = (stay_rt + switch_rt) / 2
                    results['relative_switch_cost'] = (switch_rt - stay_rt) / avg_rt if avg_rt > 0 else 0
                
                # Specific emotion transitions
                for prev_cond in ['Happy', 'Negative']:
                    for curr_cond in ['Happy', 'Negative']:
                        transition_df = df_with_prev[
                            (df_with_prev['prev_condition'] == prev_cond) & 
                            (df_with_prev['Condition'] == curr_cond)
                        ]
                        
                        if not transition_df.empty:
                            transition_key = f"{prev_cond.lower()}_to_{curr_cond.lower()}"
                            results[f'accuracy_{transition_key}'] = transition_df['accuracy'].mean()
                            
                            correct_transition = transition_df[transition_df['accuracy'] == 1]
                            if not correct_transition.empty:
                                results[f'rt_{transition_key}'] = correct_transition['response_time'].mean()
        
        # Analyze position effects (first vs. last quarter)
        if len(df) > 20:  # Only if we have enough trials
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Split into quarters
            quarter_size = len(df) // 4
            first_quarter = df.iloc[:quarter_size]
            last_quarter = df.iloc[-quarter_size:]
            
            # Calculate metrics for each quarter
            for quarter_name, quarter_df in [('first_quarter', first_quarter), ('last_quarter', last_quarter)]:
                if not quarter_df.empty:
                    # Accuracy
                    results[f'accuracy_{quarter_name}'] = quarter_df['accuracy'].mean()
                    
                    # RT (correct trials only)
                    correct_quarter = quarter_df[quarter_df['accuracy'] == 1]
                    if not correct_quarter.empty:
                        results[f'rt_{quarter_name}'] = correct_quarter['response_time'].mean()
            
            # Calculate fatigue/practice effects
            if all(k in results for k in ['accuracy_first_quarter', 'accuracy_last_quarter']):
                results['accuracy_change'] = results['accuracy_last_quarter'] - results['accuracy_first_quarter']
            
            if all(k in results for k in ['rt_first_quarter', 'rt_last_quarter']):
                results['rt_change'] = results['rt_first_quarter'] - results['rt_last_quarter']
        
        return results