#!/usr/bin/env python3
"""
Generate sample ACE data for testing and development.

This script creates synthetic ACE data files that mimic the structure and
content of real ACE data, but with randomly generated values.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from pathlib import Path

# Define constants
MODULE_NAMES = [
    "ADP", "BRT", "BOXED", "COLOR_PICKING", "COMPASS", "FILTER", "FLANKER",
    "ISHIHARA", "SAAT_SUSTAINED", "SAAT_IMPULSIVE", "SPATIAL_SPAN_FORWARD",
    "SPATIAL_SPAN_BACKWARD", "STROOP", "TASKSWITCH", "TNT"
]

MODULE_CONDITIONS = {
    "BRT": ["Right Index", "Left Index", "Right Thumb", "Left Thumb"],
    "BOXED": ["Feature 4", "Feature 12", "Congruent 4", "Congruent 12"],
    "COLOR_PICKING": [],
    "STROOP": ["Color only", "Congruent", "Incongruent"],
    "COMPASS": ["Valid", "Invalid", "Neutral"],
    "ADP": ["Happy", "Negative"],
    "FILTER": ["2T 0D", "4T 0D", "2T 2D", "2T 4D", "4T 2D"],
    "FLANKER": ["Congruent", "Incongruent"],
    "SPATIAL_SPAN_FORWARD": [],
    "SPATIAL_SPAN_BACKWARD": [],
    "TASKSWITCH": ["Stay Incongruent", "Switch Incongruent", "Stay Congruent", "Switch Congruent"],
    "TNT": ["Go/no-go Tap", "Trace", "Go/no-go & Trace"],
    "SAAT_IMPULSIVE": [],
    "SAAT_SUSTAINED": [],
    "ISHIHARA": [],
}

RESULTS = ["successful", "wrong", "late", "unanswered", "invalid"]

RESULT_PROBABILITIES = {
    "successful": 0.75,
    "wrong": 0.15,
    "late": 0.05,
    "unanswered": 0.03,
    "invalid": 0.02
}

# Helper functions
def generate_participant_id(prefix="testpfx_p", length=3):
    """Generate a random participant ID."""
    return f"{prefix}{str(random.randint(0, 999)).zfill(length)}"

def generate_unique_participant_ids(n=10, prefix="testpfx_p", length=3):
    """Generate n unique participant IDs."""
    ids = set()
    while len(ids) < n:
        ids.add(generate_participant_id(prefix, length))
    return list(ids)

def generate_random_date(start_date=datetime(2025, 1, 1), end_date=datetime(2025, 3, 31)):
    """Generate a random date between start_date and end_date."""
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    random_seconds = random.randrange(86400)  # seconds in a day
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def generate_random_result(probabilities=RESULT_PROBABILITIES):
    """Generate a random result based on probabilities."""
    results = list(probabilities.keys())
    probs = list(probabilities.values())
    return np.random.choice(results, p=probs)

def generate_module_data(module_name, participant_ids, num_trials_per_participant=50):
    """Generate synthetic data for a specific module."""
    data = []
    
    conditions = MODULE_CONDITIONS.get(module_name, [])
    has_conditions = len(conditions) > 0
    
    for pid in participant_ids:
        age = random.randint(18, 80)
        handedness = np.random.choice(["RIGHT", "LEFT"], p=[0.9, 0.1])
        
        for trial in range(num_trials_per_participant):
            # Generate participant task ID
            participant_task_id = "-".join([
                str(random.randint(10000, 99999)),
                str(random.randint(1000, 9999)),
                str(random.randint(1000, 9999))
            ])
            
            # Generate base trial data
            trial_data = {
                "GameType": module_name,
                "pid": pid,
                "participantId": pid,
                "participantTaskId": participant_task_id,
                "sessionNumber": random.randint(1, 3),
                "age": age,
                "handedness": handedness,
                "timeGameplayedUtc": generate_random_date().isoformat() + "Z",
                "finishStatus": "Complete",
                "trialNumber": trial,
                "sessionType": np.random.choice(["Practice", "Real"], p=[0.2, 0.8]),
                "module": module_name,
            }
            
            # Add condition if applicable
            if has_conditions:
                trial_data["Condition"] = np.random.choice(conditions)
            
            # Generate response data
            response_window = random.randint(300, 600)
            trial_data["responseWindow"] = response_window
            
            # Generate result
            result = generate_random_result()
            trial_data["feedbackResult"] = result
            
            # Generate response time based on result
            if result == "successful":
                # Successful response within window
                trial_data["responseTime"] = random.randint(200, response_window)
            elif result == "wrong":
                # Wrong response within window
                trial_data["responseTime"] = random.randint(200, response_window)
            elif result == "late":
                # Late response (after window)
                trial_data["responseTime"] = random.randint(response_window + 1, response_window + 500)
            elif result == "unanswered":
                # No response
                trial_data["responseTime"] = np.nan
            elif result == "invalid":
                # Invalid response (too early)
                trial_data["responseTime"] = random.randint(1, 199)
            
            # Add module-specific data
            if module_name == "BRT":
                trial_data["result_details_FPSMean"] = random.uniform(60, 120)
                trial_data["result_details_FPSVariance"] = random.uniform(20, 100)
            elif module_name in ["SPATIAL_SPAN_FORWARD", "SPATIAL_SPAN_BACKWARD"]:
                trial_data["level"] = random.randint(1, 8)
            
            data.append(trial_data)
    
    return pd.DataFrame(data)

def generate_demographics_data(participant_ids):
    """Generate demographics data for participants."""
    data = []
    
    for pid in participant_ids:
        age = random.randint(18, 80)
        gender = np.random.choice(["Male", "Female", "Non-binary"], p=[0.48, 0.48, 0.04])
        handedness = np.random.choice(["RIGHT", "LEFT"], p=[0.9, 0.1])
        
        data.append({
            "participantId": pid,
            "pid": pid,
            "age": age,
            "gender": gender,
            "handedness": handedness,
            "education": np.random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
            "date_registered": generate_random_date().date().isoformat()
        })
    
    return pd.DataFrame(data)

def main():
    """Generate sample ACE data and save to CSV files."""
    # Create output directory structure
    output_dir = Path("data/sample_run/sample")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate participant IDs
    num_participants = 5
    participant_ids = generate_unique_participant_ids(num_participants)
    print(f"Generated {num_participants} participant IDs: {participant_ids}")
    
    # Generate demographics data
    demographics_df = generate_demographics_data(participant_ids)
    demographics_path = output_dir / "demographics.csv"
    demographics_df.to_csv(demographics_path, index=False)
    print(f"Generated demographics data: {demographics_path}")
    
    # Generate module data
    for module_name in MODULE_NAMES:
        trials_per_participant = random.randint(30, 100)
        module_df = generate_module_data(module_name, participant_ids, trials_per_participant)
        
        module_path = output_dir / f"{module_name}.csv"
        module_df.to_csv(module_path, index=False)
        
        total_trials = len(module_df)
        print(f"Generated {module_name} data: {total_trials} trials across {num_participants} participants")
    
    print(f"\nSample data generation complete. Files saved to {output_dir}")


if __name__ == "__main__":
    main()