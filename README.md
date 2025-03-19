# ACE Python: Adaptive Cognitive Evaluation Analysis Toolkit

The ACE Python package provides tools for processing, analyzing, and visualizing data from UCSF's Adaptive Cognitive Evaluation (ACE) platform - a suite of cognitive assessment games that measure various aspects of executive function.

## Overview

ACE Explorer consists of 15 validated cognitive assessment games that measure different aspects of Cognitive Control:
- Attention and focus
- Working memory
- Distractor filtering
- Goal management and cognitive flexibility

This Python package provides a comprehensive toolkit for:
1. Loading and preprocessing ACE data files
2. Analyzing game (module) data with specialized analyzers
3. Calculating standard cognitive metrics for each game
4. Generating publication-quality visualizations
5. Exporting results to various formats (CSV, Excel, JSON)

## Installation

### Prerequisites
- Python 3.7+
- Required Python packages: pandas, numpy, matplotlib, seaborn, openpyxl (for Excel export)

### Install from source
```bash
# Clone the repository
git clone https://github.com/arjunpur/ace-python.git
cd ace-python

# Install the package in development mode
pip install -e .
```

## Usage

### Command-Line Interface

The package provides a command-line script called `ace_analysis.py` for quick analysis:

```bash
# Basic usage
python ace_analysis.py --data-dir /path/to/ace/data --output-dir /path/to/output --visualize

# Process only specific modules
python ace_analysis.py --data-dir /path/to/ace/data --modules BRT FLANKER --visualize

# Process only specific participants
python ace_analysis.py --data-dir /path/to/ace/data --participants participant1 participant2 --visualize

# Generate a comprehensive report
python ace_analysis.py --data-dir /path/to/ace/data --report --visualize

# Process multiple datasets at once (bulk mode)
python ace_analysis.py --data-dir /path/to/multiple/datasets --bulk --visualize
```

### Python API

You can also use the Python API directly in your scripts:

```python
from ace.loader import ACELoader
from ace.analysis import ACEAnalyzer
from ace.visualization import create_module_report, plot_module_comparison

# Load data
loader = ACELoader("path/to/data")
ace_data = loader.load_all()

# Run analysis
analyzer = ACEAnalyzer(ace_data)
module_summaries = analyzer.analyze_all_modules()

# Generate summary DataFrame
summary_df = analyzer.create_summary_dataframe(module_summaries)

# Create visualizations
for module_name, df in ace_data.modules.items():
    figures = create_module_report(df, output_dir=f"output/{module_name}")
```

See the `examples/example_usage.py` file for more detailed usage examples.

## Project Structure

```
ace-python/
├── ace/                       # Main package directory
│   ├── __init__.py            # Package initialization
│   ├── analysis.py            # Core analysis functionality
│   ├── constants.py           # Constants and configuration
│   ├── export.py              # Export functionality
│   ├── loader.py              # Data loading utilities
│   ├── modules/               # Module-specific analyzers
│   │   ├── adp.py             # ADP (Face Switch) analyzer
│   │   ├── flanker.py         # Flanker analyzer
│   │   └── ...                # Additional module analyzers
│   ├── utils.py               # Utility functions
│   └── visualization.py       # Visualization functionality
├── data/                      # Sample data directory
├── examples/                  # Example scripts
│   ├── example_usage.py       # Example API usage
│   └── exploration.ipynb      # Jupyter notebook exploration
├── scripts/                   # Helper scripts
│   └── generate_sample_data.py # Generate sample data
├── tests/                     # Test directory
│   ├── test_loader.py         # Tests for the loader module
│   └── ...                    # Additional tests
├── ace_analysis.py            # Command-line interface script
├── README.md                  # Project documentation
└── setup.py                   # Package setup script
```

## Modules and Features

### Supported Modules (Games)

| Module ID | Game Name | Description |
|-----------|-----------|-------------|
| ADP | Face Switch | Emotional task switching |
| BRT | Basic Response Time | Simple reaction time |
| BOXED | Boxed | Visual search task |
| COLOR_PICKING | Color Swatch | Color working memory |
| COMPASS | Compass | Spatial attention task |
| FILTER | Filter | Visual distractor filtering |
| FLANKER | Flanker Arrow | Inhibitory control |
| ISHIHARA | What's This Number | Color vision test |
| SAAT_SUSTAINED | Mars UFO | Sustained attention |
| SAAT_IMPULSIVE | Venus UFO | Impulsive attention |
| SPATIAL_SPAN_FORWARD | Gem Chaser | Visual working memory |
| SPATIAL_SPAN_BACKWARD | Gem Chaser (Backwards) | Backward working memory |
| STROOP | Color Tricker | Inhibitory control |
| TASKSWITCH | Sun and Moon | Task switching |
| TNT | Triangle Trace | Motor control |

### Key Features

1. **Data Loading**
   - Load individual ACE module data files
   - Bulk load multiple datasets for cross-study analysis
   - Filter data by participant, module, or condition

2. **Data Analysis**
   - Module-specific analyzers for specialized metrics
   - Common analyses across modules (accuracy, reaction time, etc.)
   - Learning curves and performance over time
   - Condition-specific effects (switch costs, interference effects, etc.)

3. **Visualization**
   - Publication-quality figures using matplotlib and seaborn
   - Response time distributions by condition
   - Accuracy rates with confidence intervals
   - Learning curves with trend analysis
   - Module and participant comparisons
   - Switch costs for task switching paradigms

4. **Export**
   - CSV export for summary statistics
   - Excel export with formatted worksheets
   - JSON export for further processing
   - R-compatible data export

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

For more information on the ACE platform:
- [UCSF Neuroscape ACE Explorer](https://neuroscape.ucsf.edu/technology/ace-explorer/)

# Background Context

UCSF has a Adaptive Cognitive Evaluation (ACE) platform, a series of 15 games to measure executive function. This platform returns data per-participant for a single study. The games in ACE Explorer replicate validated gold-standard tasks that assess different aspects of Cognitive Control (attention/focus, working memory, distractor filtering, and goal management/cognitive flexibility). Each modular game incorporates adaptive algorithms

A **module**, for our purposes, is a game that a participant played. For each trial, we have a wide range of data about how the participant performed (such as response time, and correct / incorrect). I will be giving you the exact input format, and values that fields in the input can take.

The modules, along with their descriptive names are:
- ADP: Face Switch
- BRT: Basic Response Time
- BOXED: Boxed
- COLOR_PICKING: Color Swatch
- COMPASS: Compass
- FILTER: Filter
- FLANKER: Flanker Arrow
- ISHIHARA: What's This Number
- SAAT_SUSTAINED: Mars UFO (Impulsive)
- SAAT_IMPULSIVE: Venus UFO (Sustained)
- SPATIAL_SPAN_FORWARD: Gem Chaser
- SPATIAL_SPAN_BACKWARD: Gem Chaser (Backwards) 
- STROOP: Color Tricker
- TASKSWITCH: Sun and Moon
- TNT: Triangle Trace

# Modules

Each game (module) consists of a tutorial, practice, and the test. The tutorial is interactive and includes written and verbal instructions. The practice is used to determine the starting level of the game. The game then adapts based on the participant's performance.

## Module Types

* Forced choice
  - The participant has multiple responses to select from.
  - The number is parentheses indicates how many options the participant has to select from.
* Go/ No-go
  - The participant can respond or withhold.
* Memory span
  - The participant makes multiple selections in a sequence.
* Trace
  - The participant traces a shape.
* Digit entry
  - The participant types a number.

## Module Timing

Modules typically follow 1 of 3 timing patterns:
- `stim-only`: A stimulus is displayed and the participant must respond
- `cue-stim`: A cues is displayed to orient the participant to a stimulus. The cue disappers and a stimulus is shown. The participant then responds
- `stim-probe`: A stimulus or stimulus array is displayed that the participant must remember or make a judgement on. The stimulus disappears for set amount of time then a test probe or test array is displayed and the participant must respond.


| Timing Scheme   | Cue Time (0)  | Delay (0) | Response Window (5000) | Buffer Response Window (1000) | Result Time (200) | Inter-trial Time (800-1200¹) |
|-----------------|---------------|-----------|-------------------------|-------------------------------|-------------------|-----------------------------|
| **Stim-Only**   | -             | -         | Stimulus               | -                             | Feedback          | -                           |
| **Cue-Stim**    | Cue           | -         | Stimulus and Cue²      | -                             | Feedback          | -                           |
| **Stim-Probe**  | Stimulus      | Mask      | Test probe             | -                             | Feedback          | -                           |


| Module                               | Pattern      | Cue Time       | Delay      | Response Window     |
|--------------------------------------|--------------|----------------|------------|---------------------|
| **BRT**                              | Stim-Only    | -              | -          | adapts              |
| **BOXED**                            | Stim-Only    | -              | -          | adapts              |
| **STROOP**                           | Stim-Only    | -              | -          | adapts              |
| **COLOR_PICKING**                    | Stim-Probe   | 1500           | 300        | 5000                |
| **COMPASS**                          | Cue-Stim     | 500            | -          | adapts              |
| **ADP**                      	       | Cue-Stim     | 1000           | -          | adapts              |
| **FILTER**                           | Stim-Probe   | 200            | 900        | adapts              |
| **FLANKER**                          | Stim-Only    | -              | -          | adapts              |
| **SPATIAL_SPAN_FORWARD**             | Stim-Probe   | 1000 x level   | -          | 1000 x level + 5000 |
| **SPATIAL_SPAN_BACKWARD**            | Stim-Probe   | 1000 x level   | -          | 1000 x level + 5000 |
| **TASKSWITCH**                       | Cue-Stim     | 500            | -          | adapts              |
| **TNT**                              | Stim-Only    | -              | -          | adapts              |
| **SAAT_SUSTAINED                     | Stim-Only    | -              | -          | 2100                |
| **SAAT_IMPULSIVE                     | Stim-Only    | -              | -          | 2100                |
| **ISHIHARA**                         | Stim-Only    | -              | -          | 5000                |

## Module Trial Results

A trial, in a module can have one of five results:
- `successful`: For forced choice, participant correctly responds in the response window. For go/no-go, participant does not respond within the maximum trial time, for invalid trails OR the participant does respond within the response window for valid trials.j 
- `wrong`: 
- `late`: Participant responds within the buffer response window
- `unanswered`: Participant does not respond within the buffer response window.
- `invalid`: The response is <150ms within the response window OR the participant taps the screen 2x during cue+delay time.

## Module Timing


# Output Aggregated Statistics

Our primary goal is to calculate aggregrated statistics in the following manner:

- For each **module**, a number of **outcomes** (e.g., 'accuracy') are reported, and **summary stats** (e.g., 'mean') are calculated for each of these outcomes. 
- Then, the metrics these stats are calculated on **subsets** of the outcomes (e.g., 'first half' vs 'second half'). 
- All of these **subsets** are calculated for each **condition** of each module in addition to some cost variables to comapre performance between conditions.

Outcomes:
- `accuracy`
- `response_window`
- `reaction_time`

Metrics:
- `total_trials`: Total # of trials presented to the participant
- `total_trials_responded`: Total # of trials a participant responded to
- `mean`
- `median`
- `stdv`: standard deviation
- `rcs`: The Rate Correct Score: Number of correct responses / mean overall response time

Subsets:
- `correct`: only correct trials
- `incorrect`: only incorrect trials
- `overall`: all trials from all conditions
- `first_half`: only trials from the first half of the module
- `second_half`: only trials from the second half of the module 
- `early`: trials that were 'late' are excluded
- `late_incorrect`: for accuracy only, when all late trials are considered incorrect
- `prev_incorrect`: only trials where the previous trial response was incorrect
- `prev_correct`: only trials where the previous trial response was correct

Conditions:

Here are the types of conditions that each module can take.

| Module Name                 | Conditions                     |
|-----------------------------|--------------------------------|
| **BRT**                     | Right Index, Left Index, Right Thumb, Left Thumb |
| **BOXED**                   | Feature 4, Feature 12, Congruent 4, Congruent 12 |
| **COLOR_PICKING**           | -                              |
| **STROOP**                  | Color only, Congruent, Incongruent |
| **COMPASS**                 | Valid (68%), Invalid (17%), Neutral (17%) |
| **ADP**                     | Happy, Negative               |
| **FILTER**                  | 2T 0D, 4T 0D, 2T 2D, 2T 4D, 4T 2D |
| **FLANKER**                 | Congruent, Incongruent        |
| **SPATIAL_SPAN_FORWARD**    | -                              |
| **SPATIAL_SPAN_BACKWARD**   | -                              |
| **TASK_SWITCH**             | Stay Incongruent, Switch Incongruent, Stay Congruent, Switch Congruent |
| **TNT**                     | Go/no-go Tap, Trace, Go/no-go & Trace |
| **SAAT_IMPULSIVE**          | -                              |
| **SAAT_SUSTAINED**          | -                              |
| **ISHIHARA**                | -                              |

# Input Data Format

Here is a sample input from the BRT module:

```
,Time Gameplayed Utc,participantTaskId,Participant Id,Finish Status,Times Finished Game,Session Type,OS Version,Screen Height,Screen Width,Client Time Zone,Graphics Device Name,Processor Frequency,Runtime Platform,I18n,Processor Count,System Memory Size,Build,Device DPI,Device Model,Device Type,Response Window,Response Time,Inter Time Interval,Trial Number,FPS Mean,FPS Variance,Condition,Correct Button,Late Response,Time Sent Utc,Detail,Finger Used
0,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,550,484,1000,0,120.148491,53.8195648,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
1,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,540,317,1100,1,120.523514,28.9355812,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
2,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,520,467,1200,2,120.060272,36.0820961,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
3,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,490,367,900,3,121.054596,46.3254051,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
4,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,450,367,800,4,120.881752,28.2051754,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
5,2024-09-27T18:24:29.3090000Z,c14e3ed0-728a-425c-b95f-4fcc339fd274,testpfx_arjun092724,Successful,0,Real,Mac OS X 10_15_7,1598,2396,Pacific Standard Time,"ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",0,17,10,1,128,1.23.1,0,Chrome 126,3,400,300,1100,5,119.88884,49.48621,LEFT,1,0,2024-09-27T18:24:29.3090000Z,N/A,N/A
```


# Desired Output

Here is an example of valid output for the aggregated statistics:

```
pid,age,handedness,bid,ADP.rcs.overall,SAATSUSTAINED.rt_mean.correct,STROOP.rcs.overall,TASKSWITCH.rcs.overall,BRT.rt_mean.correct,BRT.rt_mean.correct.dominant,BRT.rt_mean.correct.dominant.thumb,BRT.rt_mean.correct.nondominant,BRT.rt_mean.correct.nondominant.thumb,SPATIALSPAN.object_count_span.overall,SPATIALCUEING.rcs.overall
testpfxtestapple11062021,42,RIGHT,testpfxtestapple11062021.session0,1.152173286862344,535.5333333333333,1.2901473484076866,NA,304.2542372881356,306.73333333333335,312.3333333333333,264.4,335.64285714285717,NA,NA
testpfxjctest05142024,29,RIGHT,testpfxjctest05142024.session0,NA,NA,NA,1.85417788145224,230.1,221.2,NA,239,NA,7,3.9086607693890145
testpfxaptest051624,29,RIGHT,testpfxaptest051624.session0,NA,NA,NA,1.8869750338687827,282.76666666666665,277.8666666666667,NA,287.6666666666667,NA,NA,NA
```

In here, you see that:
- For each module executed on (ADP, SAATSUSTAINED, STROOP, TASKSWITCH, BRT, SPATIALSPAN) we calculated metrics such as `rcs`, rt_mean,

