"""
Flanker module analyzer.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from ace.analysis import ModuleAnalyzer
from ace.utils import calculate_rcs, group_trials_by_condition


class FlankerAnalyzer(ModuleAnalyzer):
    """Analyzer for Flanker module."""
    
    def validate_data(self) -> bool:
        """Check if data has required columns for Flanker analysis."""
        required_cols = ['participant_id', 'trial_number', 'response_time', 'result', 'Condition']
        return all(col in self.data.columns for col in required_cols)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform Flanker-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format for Flanker analysis'}
        
        results = self.get_basic_stats()
        
        # Add Flanker-specific analyses
        df = self.data.copy()
        
        # Calculate accuracy
        df['accuracy'] = (df['result'] == 'successful').astype(int)
        
        # Group by condition (Congruent vs Incongruent)
        condition_groups = group_trials_by_condition(df)
        
        # Verify that we have both conditions
        if not all(cond in condition_groups for cond in ['Congruent', 'Incongruent']):
            results['warning'] = 'Missing either Congruent or Incongruent condition'
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
        
        # Calculate interference effects if we have both conditions
        congruent_df = condition_groups['Congruent']
        incongruent_df = condition_groups['Incongruent']
        
        if not congruent_df.empty and not incongruent_df.empty:
            # RT Interference Effect
            congruent_correct = congruent_df[congruent_df['accuracy'] == 1]
            incongruent_correct = incongruent_df[incongruent_df['accuracy'] == 1]
            
            if not congruent_correct.empty and not incongruent_correct.empty:
                # Mean RTs
                congruent_rt = congruent_correct['response_time'].mean()
                incongruent_rt = incongruent_correct['response_time'].mean()
                
                # Interference effect (Incongruent - Congruent)
                rt_interference = incongruent_rt - congruent_rt
                results['rt_interference_effect'] = rt_interference
                
                # Relative interference effect
                avg_rt = (congruent_rt + incongruent_rt) / 2
                results['relative_rt_interference'] = rt_interference / avg_rt if avg_rt > 0 else 0
            
            # Accuracy Interference Effect
            congruent_acc = congruent_df['accuracy'].mean()
            incongruent_acc = incongruent_df['accuracy'].mean()
            
            # Accuracy interference (Congruent - Incongruent)
            acc_interference = congruent_acc - incongruent_acc
            results['accuracy_interference_effect'] = acc_interference
            
            # Inverse efficiency score (combines RT and accuracy)
            if congruent_acc > 0 and incongruent_acc > 0:
                congruent_ies = congruent_rt / congruent_acc
                incongruent_ies = incongruent_rt / incongruent_acc
                results['congruent_ies'] = congruent_ies
                results['incongruent_ies'] = incongruent_ies
                results['ies_interference'] = incongruent_ies - congruent_ies
        
        # Analyze post-error slowing
        if 'trial_number' in df.columns:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Add previous trial accuracy
            df['prev_accuracy'] = df['accuracy'].shift(1)
            
            # Filter out first trial (no previous)
            df_with_prev = df.dropna(subset=['prev_accuracy'])
            
            # Split by previous trial result
            post_correct_df = df_with_prev[df_with_prev['prev_accuracy'] == 1]
            post_error_df = df_with_prev[df_with_prev['prev_accuracy'] == 0]
            
            if not post_correct_df.empty and not post_error_df.empty:
                # Calculate mean RTs
                post_correct_rt = post_correct_df['response_time'].mean()
                post_error_rt = post_error_df['response_time'].mean()
                
                # Post-error slowing (positive = slowing after errors)
                post_error_slowing = post_error_rt - post_correct_rt
                results['post_error_slowing'] = post_error_slowing
                
                # Relative post-error slowing
                avg_rt = (post_correct_rt + post_error_rt) / 2
                relative_slowing = post_error_slowing / avg_rt if avg_rt > 0 else 0
                results['relative_post_error_slowing'] = relative_slowing
                
                # Post-error accuracy
                post_correct_acc = post_correct_df['accuracy'].mean()
                post_error_acc = post_error_df['accuracy'].mean()
                results['post_correct_accuracy'] = post_correct_acc
                results['post_error_accuracy'] = post_error_acc
                results['post_error_accuracy_change'] = post_error_acc - post_correct_acc
        
        # Calculate conflict adaptation effect (Gratton effect)
        if 'trial_number' in df.columns and 'Condition' in df.columns:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Add previous trial condition
            df['prev_condition'] = df['Condition'].shift(1)
            
            # Filter out first trial (no previous)
            df_with_prev = df.dropna(subset=['prev_condition'])
            
            # Create trial sequence groups
            cc_trials = df_with_prev[(df_with_prev['prev_condition'] == 'Congruent') & 
                                     (df_with_prev['Condition'] == 'Congruent')]
            ci_trials = df_with_prev[(df_with_prev['prev_condition'] == 'Congruent') & 
                                     (df_with_prev['Condition'] == 'Incongruent')]
            ic_trials = df_with_prev[(df_with_prev['prev_condition'] == 'Incongruent') & 
                                     (df_with_prev['Condition'] == 'Congruent')]
            ii_trials = df_with_prev[(df_with_prev['prev_condition'] == 'Incongruent') & 
                                     (df_with_prev['Condition'] == 'Incongruent')]
            
            # Calculate mean RTs for correct trials in each sequence
            for seq_name, seq_df in [('cc', cc_trials), ('ci', ci_trials), 
                                      ('ic', ic_trials), ('ii', ii_trials)]:
                correct_seq = seq_df[seq_df['accuracy'] == 1]
                if not correct_seq.empty:
                    results[f'rt_{seq_name}'] = correct_seq['response_time'].mean()
                    results[f'accuracy_{seq_name}'] = seq_df['accuracy'].mean()
            
            # Calculate conflict adaptation effect if we have all sequences
            if all(f'rt_{seq}' in results for seq in ['cc', 'ci', 'ic', 'ii']):
                # RT conflict adaptation effect
                # (RT_ci - RT_cc) - (RT_ii - RT_ic)
                rt_ce1 = results['rt_ci'] - results['rt_cc']
                rt_ce2 = results['rt_ii'] - results['rt_ic']
                rt_adaptation = rt_ce1 - rt_ce2
                results['rt_conflict_adaptation'] = rt_adaptation
                
                # Accuracy conflict adaptation effect
                if all(f'accuracy_{seq}' in results for seq in ['cc', 'ci', 'ic', 'ii']):
                    # (ACC_cc - ACC_ci) - (ACC_ic - ACC_ii)
                    acc_ce1 = results['accuracy_cc'] - results['accuracy_ci']
                    acc_ce2 = results['accuracy_ic'] - results['accuracy_ii']
                    acc_adaptation = acc_ce1 - acc_ce2
                    results['accuracy_conflict_adaptation'] = acc_adaptation
        
        return results