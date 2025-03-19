import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import json

"""
Sample data generator for ACE (Adaptive Cognitive Evaluation) data.
Creates realistic sample data for all modules following the same format as real data.
"""

# Create output directory if it doesn't exist
OUTPUT_DIR = "data/sample"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "ucsf_ace"), exist_ok=True)

# Common parameters for all games
NUM_PARTICIPANTS = 5
NUM_TRIALS_PER_MODULE = 30
HANDEDNESS = ["RIGHT", "LEFT"]
AGES = list(range(18, 65))
SESSION_TYPES = ["Real", "Initial", "StartingWindow"]
GENDERS = ["MALE", "FEMALE", "UNDEFINED"]

# Module names - match those in the real dataset
MODULES = [
    "BRT",                # Basic Response Time
    "BOXED",              # Boxed
    "COLOR_PICKING",      # Color Swatch
    "STROOP",             # Color Tricker
    "SPATIAL_CUEING",     # Compass
    "ADP",                # Face Switch
    "FILTER",             # Filter
    "FLANKER",            # Flanker Arrow
    "ISHIHARA",           # What's This Number
    "SAAT_SUSTAINED",     # Mars UFO (Impulsive)
    "SAAT_IMPULSIVE",     # Venus UFO (Sustained)
    "SPATIAL_SPAN",       # Gem Chaser
    "REVERSE_SPATIAL_SPAN", # Gem Chaser (Backwards)
    "TASK_SWITCH_V2",     # Sun and Moon
    "TNT"                 # Triangle Trace
]

# Module-specific conditions - exact values from the real dataset
MODULE_CONDITIONS = {
    "BRT": ["RIGHTINDEX", "LEFTINDEX"],
    "BOXED": ["FEATURE4", "FEATURE12", "CONJUNCTION4", "CONJUNCTION12"],
    "COLOR_PICKING": ["DEFAULT"],  # Always DEFAULT in real data
    "STROOP": ["ONLYCOLOR", "CONGRUENT", "INCONGRUENT"],
    "SPATIAL_CUEING": ["VALID", "INVALID", "NEUTRAL"],
    "ADP": ["HAPPY", "SAD", "NEUTRAL"],
    "FILTER": ["R2B0", "R2B2", "R2B4"],
    "FLANKER": ["CONGRUENT", "INCONGRUENT"],
    "ISHIHARA": [""],
    "SAAT_SUSTAINED": [""],
    "SAAT_IMPULSIVE": [""],
    "SPATIAL_SPAN": [""],
    "REVERSE_SPATIAL_SPAN": [""],
    "TASK_SWITCH_V2": ["STAY_CONGRUENT", "STAY_INCONGRUENT", "SWITCH_CONGRUENT", "SWITCH_INCONGRUENT"],
    "TNT": ["Trace Only", "Tap Only"]
}

# Stroop trial types - mapping from condition to trialType
STROOP_TRIAL_TYPES = {
    "ONLYCOLOR": "OnlyColor",
    "CONGRUENT": "Congruent",
    "INCONGRUENT": "Incongruent"
}

# TNT cue types
TNT_CUE_TYPES = ["TARGET", "LCL"]

# Trial results - match real data feedback values
TRIAL_RESULTS = ["green", "red", "yellow"]
RESULT_PROBABILITIES = [0.7, 0.2, 0.1]  # Higher chance of successful trials

# Response window values by module
MODULE_RESPONSE_WINDOWS = {
    "SPATIAL_CUEING": [525, 535, 545],
    "FLANKER": [550, 560, 570, 580],
    "TNT": [1500.0, 2500.0],
    # Most modules use either these values or -1
    "DEFAULT": [-1, 500, 600, 700, 800]
}

def generate_uuid():
    """Generate a random UUID string."""
    return str(uuid.uuid4())

def generate_common_columns(module_name, participant_id, session_number, trial_number):
    """
    Generate common columns that appear in all module data files.
    
    Args:
        module_name: The name of the module
        participant_id: Unique ID for the participant
        session_number: Session number (0-2)
        trial_number: Trial index within the session
        
    Returns:
        Dictionary with common column values
    """
    # Basic participant info
    age = random.choice(AGES)
    handedness = random.choice(HANDEDNESS)
    
    # Generate realistic timestamps
    base_time = datetime.now()
    game_time = (base_time - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    session_time = (base_time - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    # Generate IDs
    task_id = generate_uuid()
    session_id = generate_uuid()
    session_key = random.choice(SESSION_TYPES)
    
    # Generate device info
    os_version = random.choice(["Mac OS X 10_15_7", "Windows 10", "Android 13"])
    screen_height = random.randint(800, 1500)
    screen_width = random.randint(1000, 2500)
    
    # Return dictionary with all common columns
    return {
        "index": trial_number,
        "is_partial": True,
        "GameType": module_name,
        "create_at": (base_time - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S.%f+00:00"),
        "is_active": True,
        "after_closed": False,
        "pid": random.randint(20000, 30000),
        "participantTaskId": task_id,
        "appId": "ucsf_ace",
        "sessionNumber": session_number,
        "sessionId": session_id,
        "finishStatus": "Complete",
        "practiceApproved": True,
        "section": None,
        "sessionCompletedUtc": session_time,
        "timeGameplayedUtc": game_time,
        "timesFinishedGame": 0,
        "age": age,
        "handedness": handedness,
        "customData": "{}",
        "participantId": participant_id,
        "studyId": "04e33ff6-dd98-401c-8a33-e3d02d146b02",
        "key": session_key,
        "OSVersion": os_version,
        "screenHeight": screen_height,
        "screenWidth": screen_width,
        "clientTimeZone": "Pacific Standard Time",
        "clientTimeZoneOffset": -7,
        "graphicsDeviceName": "ANGLE (Intel Inc., Intel(R) UHD Graphics 617, OpenGL 4.1)",
        "processorFrequency": 0,
        "runtimePlatform": "WebGLPlayer",
        "touchScreenEnabled": False,
        "i18n": "English",
        "processorCount": 1,
        "systemMemorySize": 128,
        "installMode": 0,
        "build": "1.22.33",
        "versionId": "NEXUS",
        "FPSMean": random.uniform(55, 80),
        "FPSVariance": random.uniform(100, 300),
        "deviceDPI": 0,
        "deviceModel": f"Chrome {random.randint(120, 128)}",
        "deviceType": "Desktop",
        "session": "default",
    }

def generate_module_specific_columns(module_name, trial_number, is_practice=True):
    """
    Generate module-specific columns based on the module type.
    
    Args:
        module_name: The name of the module
        trial_number: Trial index within the session
        is_practice: Whether this is a practice session
        
    Returns:
        Dictionary with module-specific column values
    """
    columns = {}
    
    # Add condition based on module
    if module_name in MODULE_CONDITIONS:
        columns["result_details:Condition"] = random.choice(MODULE_CONDITIONS[module_name])
    
    # Set responseWindow based on module
    if module_name in MODULE_RESPONSE_WINDOWS:
        # If practice, usually -1
        if is_practice:
            columns["result_details:responseWindow"] = -1
        else:
            # Choose from the appropriate values for this module
            columns["result_details:responseWindow"] = random.choice(MODULE_RESPONSE_WINDOWS[module_name])
    else:
        # Default value for modules not specifically mapped
        columns["result_details:responseWindow"] = random.choice(MODULE_RESPONSE_WINDOWS["DEFAULT"])
    
    # Add maxResponseTime
    columns["result_details:maxResponseTime"] = 999
    
    # Generate timestamps
    now = datetime.now()
    columns["result_details:trialStartDateTime"] = now.strftime("%-m/%-d/%Y %-I:%M:%S %p")
    columns["result_details:responseWindowStartDateTime"] = "1/1/0001 12:00:00 AM"
    columns["result_details:interTrialResponseDateTime"] = "0001/01/01/00:00:00:000000"
    
    # Add trial interval
    columns["result_details:interTrialInterval"] = random.choice([800, 900, 1000, 1100, 1200])
    
    # Generate NGUI and time fields
    columns["result_details:NGUI"] = -1 if random.random() > 0.5 else random.uniform(100, 600)
    columns["result_details:time"] = random.randint(5000, 50000)
    
    # Generate response time and result
    success_result = random.choices(TRIAL_RESULTS, RESULT_PROBABILITIES)[0]
    columns["result_details:feedbackResult"] = success_result
    
    # Set response time based on result
    if success_result == "green" or success_result == "red":
        # Correct or incorrect response
        columns["result_details:responseTime"] = random.randint(200, 800)
        columns["result_details:wasResponseRecorded"] = True
    elif success_result == "yellow":
        # Late response
        columns["result_details:responseTime"] = random.randint(800, 1500)
        columns["result_details:wasResponseRecorded"] = True
    
    # Add response date/time
    if columns.get("result_details:wasResponseRecorded", False):
        response_time = now + timedelta(milliseconds=columns["result_details:responseTime"])
        columns["result_details:responseDateTime"] = response_time.strftime("%-m/%-d/%Y %-I:%M:%S %p")
    else:
        columns["result_details:responseDateTime"] = "0001/01/01/00:00:00:000000"
    
    # Add module-specific fields
    add_module_specific_fields(columns, module_name, trial_number)
    
    # Add FPS data common to all modules
    columns["result_details:fpsMean"] = random.uniform(50, 80)
    columns["result_details:fpsVariance"] = random.uniform(150, 250)
    
    # Add trialNumber and DifferenceNGUI-NT
    columns["result_details:trialNumber"] = trial_number
    columns["result_details:DifferenceNGUI-NT"] = -1
    
    return columns

def add_module_specific_fields(columns, module_name, trial_number):
    """
    Add fields that are specific to certain modules.
    
    Args:
        columns: Dictionary of columns to modify
        module_name: The name of the module
        trial_number: Trial index within the session
    """
    # STROOP-specific fields
    if module_name == "STROOP":
        columns["result_details:colorInkIndex"] = random.randint(0, 3)
        
        # Color word index depends on condition
        if columns.get("result_details:Condition") == "CONGRUENT":
            columns["result_details:colorWordIndex"] = columns["result_details:colorInkIndex"]
        else:
            columns["result_details:colorWordIndex"] = random.choice([i for i in range(4) if i != columns["result_details:colorInkIndex"]])
        
        # Set the trialType based on the condition
        if columns.get("result_details:Condition") in STROOP_TRIAL_TYPES:
            columns["result_details:trialType"] = STROOP_TRIAL_TYPES[columns["result_details:Condition"]]
    
    # TNT-specific fields
    elif module_name == "TNT":
        if columns.get("result_details:Condition") == "Tap Only":
            columns["result_details:cueType"] = random.choice(TNT_CUE_TYPES)
            if columns["result_details:cueType"] == "TARGET" and columns["result_details:feedbackResult"] == "green":
                columns["result_details:wasResponseRecorded"] = 1
    
    # SAAT modules - specific fields
    elif module_name in ["SAAT_SUSTAINED", "SAAT_IMPULSIVE"]:
        columns["result_details:isTarget"] = random.choice([0, 1])
        
        # Whether response was recorded depends on target and result
        if columns["result_details:isTarget"] == 1 and columns["result_details:feedbackResult"] == "green":
            columns["result_details:wasResponseRecorded"] = 1
        elif columns["result_details:isTarget"] == 0 and columns["result_details:feedbackResult"] == "green":
            columns["result_details:wasResponseRecorded"] = 0

def generate_demographics_data(participant_ids):
    """
    Generate demographics data for all participants.
    
    Args:
        participant_ids: List of participant IDs
        
    Returns:
        DataFrame with demographics data
    """
    demographics_rows = []
    study_id = "04e33ff6-dd98-401c-8a33-e3d02d146b02"
    
    for participant_id in participant_ids:
        # Construct game list config
        games_list = {}
        for i, module in enumerate(MODULES):
            games_list[module] = {"name": module, "order": str(i+1), "enabled": "True"}
        
        config_dict = {
            "playBrt": "True",
            "studyId": "mec2024",
            "gamesList": games_list,
            "playingInOrder": "1",
            "daysBeforeClossingSession": "10"
        }
        
        demographics_rows.append({
            "age": random.choice(AGES),
            "i18n": "English",
            "appId": "ACE Explorer",
            "build": "1.22.33",
            "config": json.dumps(config_dict),
            "gender": random.choice(GENDERS),
            "section": None,
            "studyId": study_id,
            "study_id": study_id,
            "taskList": [generate_uuid()],
            "username": participant_id,
            "OSVersion": random.choice(["Mac OS X 10_15_7", "Windows 10", "Android 13"]),
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp()),
            "deviceType": random.choice(["Desktop", "Mobile", "Tablet"]),
            "handedness": random.choice(HANDEDNESS),
            "deviceModel": f"Chrome {random.randint(120, 128)}",
            "gamesScores": [],
            "installMode": 0,
            "participantId": participant_id,
            "clientTimeZone": "Pacific Standard Time",
            "gamesPlayCount": [],
            "participant_id": participant_id,
            "processorCount": 1,
            "runtimePlatform": random.choice(["17", "WebGLPlayer"]),
            "systemMemorySize": 128,
            "timesFinishedGame": 0,
            "graphicsDeviceName": "ANGLE (Intel Inc., Intel(R) UHD Graphics 617, OpenGL 4.1)",
            "processorFrequency": 0,
            "gamesMapDialogStage": 0,
            "participant_task_id": generate_uuid(),
            "timesSessionExpired": 0,
            "clientTimeZoneOffset": -7,
            "races": "",
            "hasHispanicOrigin": random.choice(["", "True", "False"])
        })
    
    return pd.DataFrame(demographics_rows)

def main():
    """Main function to generate all sample data."""
    
    # Generate participant IDs
    participant_ids = [f"testpfx_p{i:03d}" for i in range(NUM_PARTICIPANTS)]
    
    # Generate data for each module
    for module_name in MODULES:
        all_rows = []
        
        for participant_id in participant_ids:
            session_number = random.randint(0, 2)
            
            # Determine if this is a practice or real test session
            is_practice = random.random() < 0.3  # 30% chance of being practice
            
            for trial in range(NUM_TRIALS_PER_MODULE):
                # Create a row with common columns
                row = generate_common_columns(module_name, participant_id, session_number, trial)
                
                # Set is_partial based on practice/real
                row["is_partial"] = is_practice
                
                # Add module-specific columns
                module_columns = generate_module_specific_columns(module_name, trial, is_practice)
                row.update(module_columns)
                
                all_rows.append(row)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(all_rows)
        output_file = os.path.join(OUTPUT_DIR, "ucsf_ace", f"{module_name}.csv")
        df.to_csv(output_file, index=True)
        print(f"Generated {len(df)} rows for {module_name}, saved to {output_file}")
    
    # Generate and save demographics data
    demographics_df = generate_demographics_data(participant_ids)
    demographics_file = os.path.join(OUTPUT_DIR, "ucsf_ace", "demographics.csv")
    demographics_df.to_csv(demographics_file, index=True)
    print(f"Generated demographics data for {len(demographics_df)} participants, saved to {demographics_file}")
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()