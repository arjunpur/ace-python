"""
Stroop module analyzer.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from ace.analysis import ModuleAnalyzer
from ace.utils import calculate_rcs, group_trials_by_condition


class StroopAnalyzer(ModuleAnalyzer):
    """Analyzer for Stroop module."""
    
    def validate_data(self) -> bool:
        """Check if data has required columns for Stroop analysis."""
        required_cols = ['participant_id', 'trial_number', 'response_time', 'result', 'Condition']
        return all(col in self.data.columns for col in required_cols)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform Stroop-specific analysis.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.validate_data():
            return {'error': 'Invalid data format for Stroop analysis'}
        
        results = self.get_basic_stats()
        
        # Add Stroop-specific analyses
        df = self.data.copy()
        
        # Calculate accuracy
        df['accuracy'] = (df['result'] == 'successful').astype(int)
        
        # Group by condition (Color only, Congruent, Incongruent)
        condition_groups = group_trials_by_condition(df)
        
        # Analyze each condition
        for condition, condition_df in condition_groups.items():
            # Skip if no data
            if condition_df.empty:
                continue
            
            # Calculate overall accuracy
            accuracy = condition_df['accuracy'].mean()
            condition_key = condition.lower().replace(' ', '_')
            results[f'accuracy_{condition_key}'] = accuracy
            
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
            results[f'rt_mean_{condition_key}'] = rt_mean
            results[f'rt_median_{condition_key}'] = rt_median
            results[f'rt_stdv_{condition_key}'] = rt_stdv
            
            # Calculate RCS
            correct_count = len(correct_df)
            rcs = calculate_rcs(correct_count, rt_mean)
            results[f'rcs_{condition_key}'] = rcs
        
        # Calculate Stroop effects if we have the necessary conditions
        has_congruent = 'Congruent' in condition_groups and not condition_groups['Congruent'].empty
        has_incongruent = 'Incongruent' in condition_groups and not condition_groups['Incongruent'].empty
        has_neutral = 'Color only' in condition_groups and not condition_groups['Color only'].empty
        
        # Classic Stroop effect (Incongruent - Congruent)
        if has_congruent and has_incongruent:
            congruent_df = condition_groups['Congruent']
            incongruent_df = condition_groups['Incongruent']
            
            # RT Stroop Effect
            congruent_correct = congruent_df[congruent_df['accuracy'] == 1]
            incongruent_correct = incongruent_df[incongruent_df['accuracy'] == 1]
            
            if not congruent_correct.empty and not incongruent_correct.empty:
                # Mean RTs
                congruent_rt = congruent_correct['response_time'].mean()
                incongruent_rt = incongruent_correct['response_time'].mean()
                
                # Stroop effect (Incongruent - Congruent)
                rt_stroop_effect = incongruent_rt - congruent_rt
                results['rt_stroop_effect'] = rt_stroop_effect
                
                # Relative Stroop effect
                avg_rt = (congruent_rt + incongruent_rt) / 2
                results['relative_rt_stroop_effect'] = rt_stroop_effect / avg_rt if avg_rt > 0 else 0
            
            # Accuracy Stroop Effect
            congruent_acc = congruent_df['accuracy'].mean()
            incongruent_acc = incongruent_df['accuracy'].mean()
            
            # Accuracy Stroop effect (Congruent - Incongruent)
            acc_stroop_effect = congruent_acc - incongruent_acc
            results['accuracy_stroop_effect'] = acc_stroop_effect
        
        # Facilitation effect (Neutral - Congruent)
        if has_neutral and has_congruent:
            neutral_df = condition_groups['Color only']
            congruent_df = condition_groups['Congruent']
            
            # RT Facilitation Effect
            neutral_correct = neutral_df[neutral_df['accuracy'] == 1]
            congruent_correct = congruent_df[congruent_df['accuracy'] == 1]
            
            if not neutral_correct.empty and not congruent_correct.empty:
                # Mean RTs
                neutral_rt = neutral_correct['response_time'].mean()
                congruent_rt = congruent_correct['response_time'].mean()
                
                # Facilitation effect (Neutral - Congruent)
                rt_facilitation = neutral_rt - congruent_rt
                results['rt_facilitation_effect'] = rt_facilitation
                
                # Relative facilitation effect
                avg_rt = (neutral_rt + congruent_rt) / 2
                results['relative_rt_facilitation'] = rt_facilitation / avg_rt if avg_rt > 0 else 0
            
            # Accuracy Facilitation Effect
            neutral_acc = neutral_df['accuracy'].mean()
            congruent_acc = congruent_df['accuracy'].mean()
            
            # Accuracy facilitation effect (Congruent - Neutral)
            acc_facilitation = congruent_acc - neutral_acc
            results['accuracy_facilitation_effect'] = acc_facilitation
        
        # Interference effect (Incongruent - Neutral)
        if has_neutral and has_incongruent:
            neutral_df = condition_groups['Color only']
            incongruent_df = condition_groups['Incongruent']
            
            # RT Interference Effect
            neutral_correct = neutral_df[neutral_df['accuracy'] == 1]
            incongruent_correct = incongruent_df[incongruent_df['accuracy'] == 1]
            
            if not neutral_correct.empty and not incongruent_correct.empty:
                # Mean RTs
                neutral_rt = neutral_correct['response_time'].mean()
                incongruent_rt = incongruent_correct['response_time'].mean()
                
                # Interference effect (Incongruent - Neutral)
                rt_interference = incongruent_rt - neutral_rt
                results['rt_interference_effect'] = rt_interference
                
                # Relative interference effect
                avg_rt = (neutral_rt + incongruent_rt) / 2
                results['relative_rt_interference'] = rt_interference / avg_rt if avg_rt > 0 else 0
            
            # Accuracy Interference Effect
            neutral_acc = neutral_df['accuracy'].mean()
            incongruent_acc = incongruent_df['accuracy'].mean()
            
            # Accuracy interference effect (Neutral - Incongruent)
            acc_interference = neutral_acc - incongruent_acc
            results['accuracy_interference_effect'] = acc_interference
        
        # Analyze practice effects
        if len(df) > 10:  # Only if we have enough trials
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Split into first and last third
            first_third = df.iloc[:len(df)//3]
            last_third = df.iloc[-(len(df)//3):]
            
            # Calculate mean RTs for correct trials in each third
            first_third_correct = first_third[first_third['accuracy'] == 1]
            last_third_correct = last_third[last_third['accuracy'] == 1]
            
            if not first_third_correct.empty and not last_third_correct.empty:
                first_third_rt = first_third_correct['response_time'].mean()
                last_third_rt = last_third_correct['response_time'].mean()
                
                # Practice effect (first - last)
                practice_effect = first_third_rt - last_third_rt
                results['practice_effect'] = practice_effect
                
                # Relative practice effect
                avg_rt = (first_third_rt + last_third_rt) / 2
                results['relative_practice_effect'] = practice_effect / avg_rt if avg_rt > 0 else 0
            
            # Calculate accuracy in each third
            first_third_acc = first_third['accuracy'].mean()
            last_third_acc = last_third['accuracy'].mean()
            results['first_third_accuracy'] = first_third_acc
            results['last_third_accuracy'] = last_third_acc
            results['accuracy_improvement'] = last_third_acc - first_third_acc
        
        # Calculate conflict adaptation effect if we have trial sequence
        if has_congruent and has_incongruent and 'trial_number' in df.columns:
            # Sort by trial number
            df = df.sort_values('trial_number')
            
            # Filter to just congruent and incongruent trials
            stroop_df = df[df['Condition'].isin(['Congruent', 'Incongruent'])].copy()
            
            # Add previous trial condition
            stroop_df.loc[:, 'prev_condition'] = stroop_df['Condition'].shift(1)
            
            # Filter out first trial (no previous)
            stroop_with_prev = stroop_df.dropna(subset=['prev_condition'])
            
            # Create trial sequence groups
            cc_trials = stroop_with_prev[(stroop_with_prev['prev_condition'] == 'Congruent') & 
                                         (stroop_with_prev['Condition'] == 'Congruent')]
            ci_trials = stroop_with_prev[(stroop_with_prev['prev_condition'] == 'Congruent') & 
                                         (stroop_with_prev['Condition'] == 'Incongruent')]
            ic_trials = stroop_with_prev[(stroop_with_prev['prev_condition'] == 'Incongruent') & 
                                         (stroop_with_prev['Condition'] == 'Congruent')]
            ii_trials = stroop_with_prev[(stroop_with_prev['prev_condition'] == 'Incongruent') & 
                                         (stroop_with_prev['Condition'] == 'Incongruent')]
            
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
        
        return results