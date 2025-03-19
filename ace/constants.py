"""
Constants used throughout the ACE analysis package.
"""

# List of all ACE module names
MODULE_NAMES = [
    "ADP",
    "BRT",
    "BOXED",
    "COLOR_PICKING",
    "COMPASS",
    "FILTER",
    "FLANKER",
    "ISHIHARA",
    "SAAT_SUSTAINED",
    "SAAT_IMPULSIVE",
    "SPATIAL_SPAN_FORWARD",
    "SPATIAL_SPAN_BACKWARD",
    "STROOP",
    "TASKSWITCH",
    "TNT",
]

# Mapping of module names to descriptive names
MODULE_DESCRIPTIONS = {
    "ADP": "Face Switch",
    "BRT": "Basic Response Time",
    "BOXED": "Boxed",
    "COLOR_PICKING": "Color Swatch",
    "COMPASS": "Compass",
    "FILTER": "Filter",
    "FLANKER": "Flanker Arrow",
    "ISHIHARA": "What's This Number",
    "SAAT_SUSTAINED": "Mars UFO (Sustained)",
    "SAAT_IMPULSIVE": "Venus UFO (Impulsive)",
    "SPATIAL_SPAN_FORWARD": "Gem Chaser",
    "SPATIAL_SPAN_BACKWARD": "Gem Chaser (Backwards)",
    "STROOP": "Color Tricker",
    "TASKSWITCH": "Sun and Moon",
    "TNT": "Triangle Trace",
}

# Module conditions
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

# Trial result categories
TRIAL_RESULTS = [
    "successful",
    "wrong",
    "late",
    "unanswered",
    "invalid",
]

# Outcome metrics
OUTCOMES = [
    "accuracy",
    "response_window",
    "reaction_time",
]

# Summary statistics
SUMMARY_METRICS = [
    "total_trials",
    "total_trials_responded",
    "mean",
    "median",
    "stdv",
    "rcs",
]

# Data subsets for analysis
SUBSETS = [
    "correct",
    "incorrect",
    "overall",
    "first_half",
    "second_half",
    "early",
    "late_incorrect",
    "prev_incorrect",
    "prev_correct",
]

# Column name mappings for standardization
COLUMN_MAPPINGS = {
    "participantId": "participant_id",
    "participantTaskId": "participant_task_id",
    "timeGameplayedUtc": "time_gameplayed_utc",
    "finishStatus": "finish_status",
    "trialNumber": "trial_number",
    "sessionType": "session_type",
    "responseWindow": "response_window",
    "responseTime": "response_time",
    "feedbackResult": "result",
    "GameType": "module",
}

# Required columns for analysis
REQUIRED_COLUMNS = [
    "module",
    "participant_id",
    "trial_number",
    "response_time",
    "response_window",
    "result",
    "Condition",
]