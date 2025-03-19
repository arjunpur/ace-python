"""
Visualization utilities for ACE analysis.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Union, Tuple, Any
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

from ace.analysis import ACEAnalyzer, ModuleSummary
from ace.loader import ACEData

# Set global matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
mpl.rcParams['axes.labelsize'] = 12
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['figure.titlesize'] = 16

# Custom color palettes
MAIN_COLORS = ["#2C7FB8", "#7FCDBB", "#253494", "#2C7FB8", "#41B6C4"]
PAIRED_COLORS = ["#1f77b4", "#ff7f0e"]
SEQUENTIAL_COLORS = ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c"]

# Create custom colormaps
ACE_CMAP = LinearSegmentedColormap.from_list("ace_colors", MAIN_COLORS)
ACE_DIVERGING = LinearSegmentedColormap.from_list("ace_diverging", ["#d73027", "#f46d43", "#fdae61", "#fee090", "#ffffbf", "#e0f3f8", "#abd9e9", "#74add1", "#4575b4"])


def plot_reaction_times_by_condition(module_df: pd.DataFrame, 
                                     title: Optional[str] = None,
                                     figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot reaction times by condition.
    
    Args:
        module_df: DataFrame containing module data
        title: Optional title for the plot
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    if 'Condition' not in module_df.columns or 'response_time' not in module_df.columns:
        raise ValueError("DataFrame must have 'Condition' and 'response_time' columns")
    
    # Create figure with adjusted bottom margin for annotations
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate summary statistics for annotation
    condition_stats = module_df.groupby('Condition')['response_time'].agg(['mean', 'median', 'std']).reset_index()
    
    # Set color palette - fix seaborn warning by creating a proper mapping
    df_plot = module_df.copy()
    df_plot['hue_column'] = df_plot['Condition']
    conditions = module_df['Condition'].unique()
    color_list = MAIN_COLORS[:len(conditions)]
    color_dict = {condition: color for condition, color in zip(conditions, color_list)}
    
    # Plot
    sns.boxplot(x='Condition', y='response_time', hue='hue_column', data=df_plot, ax=ax, 
                palette=color_dict, linewidth=1.5, showfliers=False, legend=False)
    
    # Add individual data points as stripplot with transparency
    sns.stripplot(x='Condition', y='response_time', data=module_df, ax=ax,
                 size=4, alpha=0.3, color='gray', jitter=0.25)
    
    # Add title
    if title:
        ax.set_title(title, fontweight='bold', pad=15)
    else:
        if 'module' in module_df.columns and len(module_df) > 0:
            module_name = module_df['module'].iloc[0]
        else:
            module_name = "Module"
        ax.set_title(f"Reaction Times by Condition - {module_name}", fontweight='bold', pad=15)
    
    # Format axes
    ax.set_xlabel("Condition", fontweight='bold')
    ax.set_ylabel("Response Time (ms)", fontweight='bold')
    
    # Add annotations for mean and median below the plot
    for i, condition in enumerate(condition_stats['Condition']):
        stats = condition_stats[condition_stats['Condition'] == condition].iloc[0]
        median_val = stats['median']
        mean_val = stats['mean']
        
        # Add text label below x-axis
        ax.text(i, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.08,
               f"Mean: {mean_val:.1f}ms\nMedian: {median_val:.1f}ms",
               ha='center', va='top', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.9, ec='gray', linewidth=1))
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Improve layout
    plt.tight_layout()
    
    return fig


def plot_accuracy_by_condition(module_df: pd.DataFrame, 
                               title: Optional[str] = None,
                               figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot accuracy rates by condition.
    
    Args:
        module_df: DataFrame containing module data
        title: Optional title for the plot
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    if 'Condition' not in module_df.columns:
        raise ValueError("DataFrame must have 'Condition' column")
    
    # Calculate accuracy if not already present
    if 'accuracy' not in module_df.columns:
        if 'result' not in module_df.columns:
            raise ValueError("DataFrame must have either 'accuracy' or 'result' column")
        module_df = module_df.copy()
        module_df['accuracy'] = module_df['result'].map(lambda x: 1 if x == 'successful' else 0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate accuracy rates by condition
    accuracy_by_condition = module_df.groupby('Condition')['accuracy'].mean().reset_index()
    
    # Set color palette - using different colors for accuracy with proper hue mapping
    conditions = module_df['Condition'].unique()
    color_list = MAIN_COLORS[:len(conditions)]
    color_dict = {condition: color for condition, color in zip(conditions, color_list)}
    
    # Add hue column that matches the x column to enable proper color mapping
    accuracy_plot = accuracy_by_condition.copy()
    accuracy_plot['hue_column'] = accuracy_plot['Condition']
    
    # Plot - update to avoid seaborn deprecation warning
    bars = sns.barplot(x='Condition', y='accuracy', hue='hue_column', data=accuracy_plot, ax=ax,
                palette=color_dict, errorbar=('ci', 95), errwidth=1.5, legend=False)
    
    # Add title
    if title:
        ax.set_title(title, fontweight='bold', pad=15)
    else:
        if 'module' in module_df.columns and len(module_df) > 0:
            module_name = module_df['module'].iloc[0]
        else:
            module_name = "Module"
        ax.set_title(f"Accuracy by Condition - {module_name}", fontweight='bold', pad=15)
    
    # Format axes
    ax.set_xlabel("Condition", fontweight='bold')
    ax.set_ylabel("Accuracy Rate", fontweight='bold')
    
    # Set y-axis limits with a bit of headroom
    ax.set_ylim(0, min(1.05, accuracy_by_condition['accuracy'].max() * 1.2))
    
    # Add reference line at chance level (0.5) if data's min accuracy is < 0.6
    if accuracy_by_condition['accuracy'].min() < 0.6:
        ax.axhline(0.5, color='red', linestyle='--', alpha=0.6, label='Chance Level')
        ax.legend(loc='lower right')
    
    # Add value labels on bars with better formatting
    for i, p in enumerate(ax.patches):
        percentage = p.get_height() * 100
        ax.annotate(f"{percentage:.1f}%", 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha='center', va='bottom', fontweight='bold',
                   color='black', fontsize=11, xytext=(0, 5),
                   textcoords='offset points')
    
    # Add individual participant data points
    participant_accuracy = module_df.groupby(['participant_id', 'Condition'])['accuracy'].mean().reset_index()
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Add stripplot for individual participant data
    sns.stripplot(x='Condition', y='accuracy', data=participant_accuracy, ax=ax,
                 size=6, jitter=0.2, alpha=0.7, palette='viridis', linewidth=1, edgecolor='w')
    
    plt.tight_layout()
    return fig


def plot_learning_curve(module_df: pd.DataFrame, 
                        metric: str = 'response_time',
                        window_size: int = 5,
                        title: Optional[str] = None,
                        figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Plot learning curve with rolling average.
    
    Args:
        module_df: DataFrame containing module data
        metric: Metric to plot ('response_time' or 'accuracy')
        window_size: Size of the rolling window
        title: Optional title for the plot
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    # Make a copy to avoid modifying the original
    df = module_df.copy()
    
    # Check required columns
    if 'trial_number' not in df.columns:
        raise ValueError("DataFrame must have 'trial_number' column")
    
    # Handle accuracy metric
    if metric == 'accuracy' and metric not in df.columns:
        if 'result' in df.columns:
            # Create accuracy column
            df['accuracy'] = df['result'].map(lambda x: 1 if x == 'successful' else 0)
            metric = 'accuracy'  # Make sure we use the newly created column
        else:
            raise ValueError("DataFrame must have either 'accuracy' or 'result' column")
    
    # Make sure we have the required metric column
    if metric not in df.columns:
        raise ValueError(f"DataFrame must have '{metric}' column")
    
    # Sort by trial number
    df = df.sort_values('trial_number')
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Filter for correct trials if plotting response time
    if metric == 'response_time' and 'accuracy' in df.columns:
        df = df[df['accuracy'] == 1]
    
    # Check if we have data after filtering
    if len(df) == 0:
        raise ValueError(f"No data available for plotting after filtering. Check your DataFrame.")
    
    # Create grouped data by trial_number for aggregation
    grouped_data = df.groupby('trial_number')[metric].agg(['mean', 'std', 'count']).reset_index()
    grouped_data['sem'] = grouped_data['std'] / np.sqrt(grouped_data['count'])
    
    # Calculate rolling average
    rolling_avg = grouped_data['mean'].rolling(window=window_size, min_periods=1).mean()
    
    # Calculate confidence intervals for the rolling average
    rolling_sem = grouped_data['sem'].rolling(window=window_size, min_periods=1).mean()
    
    # Plot individual data points with transparency
    ax.scatter(df['trial_number'], df[metric], alpha=0.2, s=30, label='Individual Trials', 
               color='#a6cee3', edgecolor='none')
    
    # Plot mean for each trial with error bars
    ax.errorbar(grouped_data['trial_number'], grouped_data['mean'], yerr=grouped_data['sem'],
               fmt='o', color='#1f78b4', label='Trial Mean', alpha=0.6, markersize=4)
    
    # Plot rolling average with confidence interval
    ax.plot(grouped_data['trial_number'], rolling_avg, color='#e31a1c', linewidth=2.5, 
            label=f'{window_size}-Trial Rolling Average')
    
    # Add confidence interval around rolling average
    ax.fill_between(grouped_data['trial_number'], 
                   rolling_avg - rolling_sem * 1.96, 
                   rolling_avg + rolling_sem * 1.96,
                   color='#e31a1c', alpha=0.2)
    
    # Add title
    if title:
        ax.set_title(title, fontweight='bold', pad=15)
    else:
        if 'module' in df.columns and len(df) > 0:
            module_name = df['module'].iloc[0]
        else:
            module_name = "Module"
        metric_label = "Response Time" if metric == 'response_time' else "Accuracy"
        ax.set_title(f"{metric_label} Learning Curve - {module_name}", fontweight='bold', pad=15)
    
    # Format axes
    ax.set_xlabel("Trial Number", fontweight='bold')
    ylabel = "Response Time (ms)" if metric == 'response_time' else "Accuracy"
    ax.set_ylabel(ylabel, fontweight='bold')
    
    # Customize y-axis limits for better visualization
    if metric == 'accuracy':
        ax.set_ylim(-0.05, 1.05)
        # Add chance level line for accuracy
        ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='Chance Level (0.5)')
    else:
        # For response time, set a reasonable lower bound
        y_min = max(0, grouped_data['mean'].min() * 0.8)
        y_max = grouped_data['mean'].max() * 1.2
        ax.set_ylim(y_min, y_max)
    
    # Add linear trend line
    x = grouped_data['trial_number']
    y = grouped_data['mean']
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    # Add trend line with equation
    trend_line = ax.plot(x, p(x), "--", color='#33a02c', linewidth=2)
    
    # Format equation for display
    slope, intercept = z
    if metric == 'response_time':
        equation = f"Trend: {slope:.2f} ms/trial"
        if slope < 0:
            trend_label = f"Improvement Rate: {-slope:.2f} ms/trial"
        else:
            trend_label = f"Trend: {slope:.2f} ms/trial"
    else:
        if slope > 0:
            trend_label = f"Learning Rate: +{slope*100:.2f}%/trial"
        else:
            trend_label = f"Trend: {slope*100:.2f}%/trial"
    
    # Add trend line to legend
    trend_line[0].set_label(trend_label)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend with better positioning and formatting
    ax.legend(loc='best', frameon=True, fancybox=True, framealpha=0.9,
             shadow=True, borderpad=1, fontsize=10)
    
    # Add text box with summary statistics
    if metric == 'response_time':
        first_half = df[df['trial_number'] <= df['trial_number'].max() / 2][metric].mean()
        second_half = df[df['trial_number'] > df['trial_number'].max() / 2][metric].mean()
        improvement = first_half - second_half
        
        stats_text = (
            f"First Half Mean: {first_half:.1f} ms\n"
            f"Second Half Mean: {second_half:.1f} ms\n"
            f"Improvement: {improvement:.1f} ms ({improvement/first_half*100:.1f}%)"
        )
    else:
        first_half = df[df['trial_number'] <= df['trial_number'].max() / 2][metric].mean()
        second_half = df[df['trial_number'] > df['trial_number'].max() / 2][metric].mean()
        improvement = second_half - first_half
        
        stats_text = (
            f"First Half Mean: {first_half:.3f}\n"
            f"Second Half Mean: {second_half:.3f}\n"
            f"Improvement: {improvement:.3f} ({improvement/first_half*100:.1f}%)"
        )
    
    # Add stats text box to top right
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, 
           fontsize=9, va='bottom', ha='right',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='#999999'))
    
    plt.tight_layout()
    return fig


def plot_module_comparison(summary_df: pd.DataFrame, 
                           metric: str = 'rt.mean.overall',
                           figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot module comparison based on a specific metric.
    
    Args:
        summary_df: Summary DataFrame from ACEAnalyzer
        metric: Metric to compare (e.g., 'rt.mean.overall', 'accuracy.mean.overall')
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    # Find columns matching the metric pattern
    metric_cols = [col for col in summary_df.columns if col.endswith(f".{metric}")]
    
    if not metric_cols:
        raise ValueError(f"No columns found matching pattern '*.{metric}'")
    
    # Extract module names and metric values
    module_metrics = []
    for col in metric_cols:
        module_name = col.split('.')[0]
        module_metrics.append({
            'module': module_name,
            'metric': summary_df[col].mean(),
            'std': summary_df[col].std()
        })
    
    # Convert to DataFrame
    comparison_df = pd.DataFrame(module_metrics)
    
    # Sort by metric value for better visualization
    comparison_df = comparison_df.sort_values('metric', ascending=False)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create custom color map for the bars
    num_modules = len(comparison_df)
    colors = plt.cm.viridis(np.linspace(0, 0.8, num_modules))
    
    # Plot with custom colors using matplotlib directly 
    # Matplotlib's bar() doesn't have the seaborn deprecation issues
    bars = ax.bar(comparison_df['module'], comparison_df['metric'], 
             yerr=comparison_df['std'], capsize=8, 
             color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Format axes
    metric_parts = metric.split('.')
    metric_name = metric_parts[0]
    metric_type = metric_parts[1] if len(metric_parts) > 1 else ""
    
    # Convert metric name to readable format
    metric_labels = {
        'rt': 'Response Time (ms)',
        'accuracy': 'Accuracy Rate',
        'rcs': 'Rate Correct Score'
    }
    
    ylabel = metric_labels.get(metric_name, metric_name)
    ax.set_title(f"Module Comparison - {ylabel}", fontweight='bold', fontsize=16, pad=20)
    ax.set_xlabel("Module", fontweight='bold', fontsize=14, labelpad=15)
    ax.set_ylabel(ylabel, fontweight='bold', fontsize=14, labelpad=15)
    
    # Customize y-axis
    if 'accuracy' in metric:
        ax.set_ylim(0, 1.05)
        # Add chance level for accuracy
        ax.axhline(y=0.5, linestyle='--', color='red', alpha=0.7, label='Chance Level')
        ax.legend()
    else:
        # For RT, make sure y-axis starts at zero
        ax.set_ylim(0, ax.get_ylim()[1])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        if 'accuracy' in metric:
            label = f"{height:.2f}"
        else:
            label = f"{height:.1f}"
        
        ax.text(bar.get_x() + bar.get_width()/2, height + (comparison_df['std'].max() * 0.2),
               label, ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Rotate x-axis labels for better readability and adjust
    plt.xticks(rotation=45, ha='right', fontsize=12, fontweight='bold')
    
    # Add a horizontal line for the mean across all modules
    mean_value = comparison_df['metric'].mean()
    ax.axhline(y=mean_value, linestyle='-', color='black', alpha=0.5)
    ax.text(0.02, mean_value, f"Mean: {mean_value:.2f}", 
           transform=ax.get_yaxis_transform(), ha='left', va='bottom',
           fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    
    # Add overall stats in a text box
    stats_text = (
        f"Max: {comparison_df['metric'].max():.2f} ({comparison_df.loc[comparison_df['metric'].idxmax(), 'module']})\n"
        f"Min: {comparison_df['metric'].min():.2f} ({comparison_df.loc[comparison_df['metric'].idxmin(), 'module']})\n"
        f"Average: {comparison_df['metric'].mean():.2f}\n"
        f"Std Dev: {comparison_df['metric'].std():.2f}"
    )
    
    # Place the text box in the upper right corner
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, 
           fontsize=11, va='top', ha='right',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='#999999'))
    
    plt.tight_layout()
    return fig


def plot_participant_comparison(module_df: pd.DataFrame, 
                                metric: str = 'response_time',
                                condition: Optional[str] = None,
                                figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot comparison between participants for a specific module and metric.
    
    Args:
        module_df: DataFrame containing module data
        metric: Metric to compare ('response_time' or 'accuracy')
        condition: Optional condition to filter by
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    if 'participant_id' not in module_df.columns:
        raise ValueError("DataFrame must have 'participant_id' column")
    
    # Filter by condition if specified
    df = module_df.copy()
    if condition is not None and 'Condition' in df.columns:
        df = df[df['Condition'] == condition]
    
    # Calculate accuracy if needed
    if metric == 'accuracy' and 'accuracy' not in df.columns:
        if 'result' not in df.columns:
            raise ValueError("DataFrame must have either 'accuracy' or 'result' column")
        df['accuracy'] = df['result'].map(lambda x: 1 if x == 'successful' else 0)
    
    # Filter for correct trials if comparing response time
    if metric == 'response_time' and 'accuracy' in df.columns:
        correct_only = df[df['accuracy'] == 1].copy()
        # Only filter if we have enough data
        if len(correct_only) > len(df) * 0.2:
            df = correct_only
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate statistics by participant
    if metric == 'response_time':
        participant_stats = df.groupby('participant_id')[metric].agg(['mean', 'median', 'std']).reset_index()
        
        # Sort by median for better visualization
        participant_stats = participant_stats.sort_values('median')
        ordered_participants = participant_stats['participant_id'].tolist()
        
        # Create a categorical type with specific order
        df['participant_id'] = pd.Categorical(df['participant_id'], categories=ordered_participants, ordered=True)
    else:
        # For accuracy, calculate the mean accuracy by participant
        participant_stats = df.groupby('participant_id')[metric].mean().reset_index()
        
        # Sort by mean accuracy
        participant_stats = participant_stats.sort_values(metric, ascending=False)
        ordered_participants = participant_stats['participant_id'].tolist()
        
        # Create a categorical type with specific order
        df['participant_id'] = pd.Categorical(df['participant_id'], categories=ordered_participants, ordered=True)
    
    # Plot
    if metric == 'response_time':
        # Use violin plot for response time with proper hue mapping
        df_plot = df.copy()
        df_plot['hue_column'] = df_plot['participant_id']
        
        # Create custom palette for participants
        participants = ordered_participants
        participant_colors = plt.cm.viridis(np.linspace(0, 0.8, len(participants)))
        participant_color_dict = {p: color for p, color in zip(participants, participant_colors)}
        
        # Updated violin plot with hue parameter to avoid deprecation warning
        sns.violinplot(x='participant_id', y=metric, hue='hue_column', data=df_plot, ax=ax,
                      palette=participant_color_dict, inner='quartile', linewidth=1, alpha=0.7, legend=False)
        
        # Add strip plot on top for individual data points
        sns.stripplot(x='participant_id', y=metric, data=df, ax=ax,
                     size=4, alpha=0.4, color='black', jitter=0.3, dodge=True)
    else:
        # For accuracy, use a different approach - bar plot with individual trial points
        # Create a hue column that matches the x column to enable proper color mapping
        bar_plot_df = participant_stats.copy()
        bar_plot_df['hue_column'] = bar_plot_df['participant_id']
        
        # Create custom palette for participants
        participants = ordered_participants
        participant_colors = plt.cm.viridis(np.linspace(0, 0.8, len(participants)))
        participant_color_dict = {p: color for p, color in zip(participants, participant_colors)}
        
        # Updated barplot with hue parameter to avoid deprecation warning
        sns.barplot(x='participant_id', y=metric, hue='hue_column', data=bar_plot_df, ax=ax,
                   palette=participant_color_dict, alpha=0.7, errorbar=None, legend=False)
        
        # Add horizontal line for chance level
        ax.axhline(y=0.5, linestyle='--', color='red', alpha=0.7, label='Chance Level')
        
        # Add points for individual trials
        if 'Condition' in df.columns:
            # If we have conditions, use them for color
            sns.stripplot(x='participant_id', y=metric, hue='Condition', data=df, ax=ax,
                         size=3, alpha=0.5, jitter=0.3, dodge=True)
            ax.legend(title='Condition', loc='lower right')
        else:
            sns.stripplot(x='participant_id', y=metric, data=df, ax=ax,
                         size=3, alpha=0.5, jitter=0.3, color='black')
    
    # Add title
    if 'module' in df.columns and len(df) > 0:
        module_name = df['module'].iloc[0]
    else:
        module_name = "Module"
    
    title_text = f"Participant Comparison - {module_name}"
    if condition is not None:
        title_text += f" ({condition} Condition)"
    ax.set_title(title_text, fontweight='bold', fontsize=14, pad=15)
    
    # Format axes
    ax.set_xlabel("Participant ID", fontweight='bold', fontsize=12, labelpad=10)
    
    if metric == 'response_time':
        ylabel = "Response Time (ms)"
        # Add a reasonable buffer above the max value
        ax.set_ylim(0, df[metric].max() * 1.1)
    else:
        ylabel = "Accuracy Rate"
        ax.set_ylim(0, 1.05)
        
    ax.set_ylabel(ylabel, fontweight='bold', fontsize=12, labelpad=10)
    
    # Add annotations for median or mean value
    if metric == 'response_time':
        # For RT, add the median values above each violin
        for i, p_id in enumerate(ordered_participants):
            median_val = participant_stats[participant_stats['participant_id'] == p_id]['median'].values[0]
            mean_val = participant_stats[participant_stats['participant_id'] == p_id]['mean'].values[0]
            
            ax.text(i, median_val, f"{median_val:.0f}", ha='center', va='bottom', 
                   fontweight='bold', color='white', fontsize=9)
    else:
        # For accuracy, add percentage text at the top of each bar
        for i, p_id in enumerate(ordered_participants):
            accuracy_val = participant_stats[participant_stats['participant_id'] == p_id][metric].values[0]
            ax.text(i, accuracy_val + 0.02, f"{accuracy_val:.0%}", ha='center', va='bottom', 
                   fontweight='bold', color='black', fontsize=10)
            
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right', fontsize=10)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Add overall statistics text
    if metric == 'response_time':
        stats_text = (
            f"Overall Mean: {df[metric].mean():.1f} ms\n"
            f"Overall Median: {df[metric].median():.1f} ms\n"
            f"Min: {df[metric].min():.1f} ms\n"
            f"Max: {df[metric].max():.1f} ms"
        )
    else:
        stats_text = (
            f"Overall Mean: {df[metric].mean():.1%}\n"
            f"Best: {participant_stats[metric].max():.1%}\n"
            f"Worst: {participant_stats[metric].min():.1%}\n"
            f"Range: {(participant_stats[metric].max() - participant_stats[metric].min()):.1%}"
        )
    
    # Place the text box in the upper right corner
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, 
           fontsize=10, va='bottom', ha='right',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='#999999'))
    
    plt.tight_layout()
    return fig


def plot_switch_costs(module_df: pd.DataFrame, 
                      figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Plot switch costs for task switching modules (ADP, TASKSWITCH).
    
    Args:
        module_df: DataFrame containing module data
        figsize: Figure size as (width, height)
        
    Returns:
        Matplotlib figure
    """
    if 'trial_number' not in module_df.columns or 'Condition' not in module_df.columns:
        raise ValueError("DataFrame must have 'trial_number' and 'Condition' columns")
    
    if 'response_time' not in module_df.columns:
        raise ValueError("DataFrame must have 'response_time' column")
    
    # Calculate accuracy if needed
    df = module_df.copy()
    if 'accuracy' not in df.columns:
        if 'result' in df.columns:
            df['accuracy'] = df['result'].map(lambda x: 1 if x == 'successful' else 0)
        else:
            raise ValueError("DataFrame must have either 'accuracy' or 'result' column")
    
    # Sort by trial number
    df = df.sort_values('trial_number')
    
    # Add previous trial condition
    df.loc[:, 'prev_condition'] = df['Condition'].shift(1)
    
    # Filter out first trial (no previous)
    df = df.dropna(subset=['prev_condition'])
    
    # Determine if switch or stay
    df.loc[:, 'trial_type'] = 'stay'
    mask = df['Condition'] != df['prev_condition']
    df.loc[mask, 'trial_type'] = 'switch'
    
    # Check if we have enough data
    if len(df) == 0:
        raise ValueError("No data available after filtering")
    
    if 'switch' not in df['trial_type'].values or 'stay' not in df['trial_type'].values:
        raise ValueError("Data does not contain both 'switch' and 'stay' trials")
    
    # Calculate summary statistics
    switch_stats = df.groupby('trial_type').agg({
        'response_time': ['mean', 'median', 'std', 'count'],
        'accuracy': ['mean', 'std']
    }).reset_index()
    
    # Rearrange multi-index columns to flat
    switch_stats.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in switch_stats.columns.values]
    
    # Calculate switch cost
    stay_rt = switch_stats[switch_stats['trial_type'] == 'stay']['response_time_mean'].values[0]
    switch_rt = switch_stats[switch_stats['trial_type'] == 'switch']['response_time_mean'].values[0]
    rt_switch_cost = switch_rt - stay_rt
    
    stay_acc = switch_stats[switch_stats['trial_type'] == 'stay']['accuracy_mean'].values[0]
    switch_acc = switch_stats[switch_stats['trial_type'] == 'switch']['accuracy_mean'].values[0]
    acc_switch_cost = stay_acc - switch_acc
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Use nicer colors that indicate switch (red) vs stay (blue)
    colors = ["#4575b4", "#d73027"]  # Blue for stay, red for switch
    
    # Create and store summary for plotting
    rt_summary = df.groupby(['participant_id', 'trial_type'])['response_time'].median().reset_index()
    
    # Plot 1: Reaction Time by Trial Type (violin plot with individual data points)
    # Create a copy with hue column for violinplot
    violin_df = df[df['accuracy'] == 1].copy()
    violin_df['hue_column'] = violin_df['trial_type']
    
    # Create color dict for proper hue mapping
    trial_type_color_dict = {trial_type: color for trial_type, color in zip(['stay', 'switch'], colors)}
    
    # Use violinplot with hue parameter to avoid deprecation warning
    sns.violinplot(x='trial_type', y='response_time', hue='hue_column', data=violin_df, 
                  ax=ax1, palette=trial_type_color_dict, inner='quartile', 
                  order=['stay', 'switch'], legend=False)
    
    # Add individual participant medians
    sns.stripplot(x='trial_type', y='response_time', data=rt_summary, ax=ax1,
                 size=7, jitter=0.2, alpha=0.7, color='#333333', order=['stay', 'switch'])
    
    # Annotate with switch cost
    if rt_switch_cost > 0:
        cost_label = f"Switch Cost: +{rt_switch_cost:.1f} ms"
    else:
        cost_label = f"Switch Benefit: {-rt_switch_cost:.1f} ms"
    
    ax1.annotate(cost_label, xy=(0.5, 0.95), xycoords='axes fraction',
               ha='center', va='top', fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='black'))
    
    # Add mean values as text on violin plot
    for i, trial_type in enumerate(['stay', 'switch']):
        stats = switch_stats[switch_stats['trial_type'] == trial_type]
        mean_val = stats['response_time_mean'].values[0]
        median_val = stats['response_time_median'].values[0]
        
        ax1.text(i, df['response_time'].min(), 
                f"Mean: {mean_val:.1f} ms\nMedian: {median_val:.1f} ms", 
                ha='center', va='bottom', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    ax1.set_title("Response Time by Trial Type\n(Correct Trials Only)", fontweight='bold')
    ax1.set_xlabel("Trial Type", fontweight='bold')
    ax1.set_ylabel("Response Time (ms)", fontweight='bold')
    
    # Customize y-axis to start at 0
    y_max = df['response_time'].max() * 1.1
    ax1.set_ylim(0, y_max)
    
    # Plot 2: Accuracy by Trial Type (bar plot with individual data points)
    accuracy_by_type = df.groupby(['participant_id', 'trial_type'])['accuracy'].mean().reset_index()
    
    # Get means for each trial type across participants
    acc_means = accuracy_by_type.groupby('trial_type')['accuracy'].mean().reset_index()
    
    # Create bar plot with proper hue mapping to avoid deprecation warnings
    # Create a copy with hue column for proper color mapping
    bar_df = acc_means.copy()
    bar_df['hue_column'] = bar_df['trial_type']
    
    # Create barplot with hue parameter
    sns.barplot(x='trial_type', y='accuracy', hue='hue_column', data=bar_df, ax=ax2,
                palette=trial_type_color_dict, order=['stay', 'switch'], legend=False)
    
    # Add individual participant data
    sns.stripplot(x='trial_type', y='accuracy', data=accuracy_by_type, ax=ax2,
                 size=7, jitter=0.2, alpha=0.7, color='black', order=['stay', 'switch'])
    
    # Add value labels on bars
    for i, trial_type in enumerate(['stay', 'switch']):
        acc = acc_means[acc_means['trial_type'] == trial_type]['accuracy'].values[0]
        count = switch_stats[switch_stats['trial_type'] == trial_type]['response_time_count'].values[0]
        
        ax2.text(i, acc + 0.02, f"{acc:.2f}", ha='center', va='bottom', fontweight='bold', fontsize=11)
        ax2.text(i, 0.05, f"n={int(count)}", ha='center', va='bottom', fontsize=9)
    
    # Annotate with switch cost for accuracy
    if acc_switch_cost > 0:
        acc_cost_label = f"Accuracy Cost: {acc_switch_cost:.2f}"
    else:
        acc_cost_label = f"Accuracy Benefit: {-acc_switch_cost:.2f}"
    
    ax2.annotate(acc_cost_label, xy=(0.5, 0.95), xycoords='axes fraction',
               ha='center', va='top', fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='black'))
    
    ax2.set_title("Accuracy by Trial Type", fontweight='bold')
    ax2.set_xlabel("Trial Type", fontweight='bold')
    ax2.set_ylabel("Accuracy Rate", fontweight='bold')
    ax2.set_ylim(0, 1.05)
    
    # Add chance level for accuracy
    ax2.axhline(y=0.5, linestyle='--', color='red', alpha=0.5, label='Chance Level')
    ax2.legend(loc='lower right')
    
    # Add overall title
    if 'module' in df.columns and len(df) > 0:
        module_name = df['module'].iloc[0]
    else:
        module_name = "Module"
    
    # Add summary statistics in a text box
    stats_text = (
        f"RT Switch Cost: {rt_switch_cost:.1f} ms ({rt_switch_cost/stay_rt*100:.1f}%)\n"
        f"Accuracy Cost: {acc_switch_cost:.3f} ({acc_switch_cost/stay_acc*100:.1f}%)\n"
        f"Switch Trials: {sum(df['trial_type'] == 'switch')}\n"
        f"Stay Trials: {sum(df['trial_type'] == 'stay')}"
    )
    
    # Add a figure-level title that's more descriptive
    fig.suptitle(f"Task Switching Analysis - {module_name}", fontsize=16, fontweight='bold', y=0.98)
    
    # Add the stats text to the figure
    fig.text(0.98, 0.01, stats_text, ha='right', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='#999999'))
    
    # Improve layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    
    return fig


def create_module_report(module_df: pd.DataFrame, 
                         output_dir: Optional[str] = None,
                         module_name: str = None) -> Dict[str, plt.Figure]:
    """
    Create a comprehensive visual report for a module.
    
    Args:
        module_df: DataFrame containing module data
        output_dir: Optional directory to save figures
        module_name: Optional module name to use (if not in DataFrame)
        
    Returns:
        Dictionary of figures
    """
    figures = {}
    
    # Get module name
    if module_name is None:
        if 'module' in module_df.columns and len(module_df) > 0:
            module_name = module_df['module'].iloc[0]
        else:
            module_name = "Module"
    
    # Ensure necessary columns exist
    if 'result' in module_df.columns and 'accuracy' not in module_df.columns:
        module_df = module_df.copy()
        module_df['accuracy'] = module_df['result'].map(lambda x: 1 if x == 'successful' else 0)
    
    # 1. Reaction time by condition (if applicable)
    if 'Condition' in module_df.columns and 'response_time' in module_df.columns:
        try:
            figures['rt_by_condition'] = plot_reaction_times_by_condition(
                module_df, 
                title=f"Reaction Times by Condition - {module_name}"
            )
        except Exception as e:
            print(f"Error creating RT by condition plot: {e}")
    
    # 2. Accuracy by condition (if applicable)
    if 'Condition' in module_df.columns:
        try:
            figures['accuracy_by_condition'] = plot_accuracy_by_condition(
                module_df,
                title=f"Accuracy by Condition - {module_name}"
            )
        except Exception as e:
            print(f"Error creating accuracy by condition plot: {e}")
    
    # 3. Learning curve for response time
    if 'response_time' in module_df.columns and 'trial_number' in module_df.columns:
        try:
            figures['rt_learning_curve'] = plot_learning_curve(
                module_df,
                metric='response_time',
                title=f"Response Time Learning Curve - {module_name}"
            )
        except Exception as e:
            print(f"Error creating RT learning curve: {e}")
    
    # 4. Learning curve for accuracy
    if 'trial_number' in module_df.columns:
        try:
            figures['accuracy_learning_curve'] = plot_learning_curve(
                module_df,
                metric='accuracy',
                title=f"Accuracy Learning Curve - {module_name}"
            )
        except Exception as e:
            print(f"Error creating accuracy learning curve: {e}")
    
    # 5. Participant comparison (if multiple participants)
    if 'participant_id' in module_df.columns and module_df['participant_id'].nunique() > 1:
        if 'response_time' in module_df.columns:
            try:
                figures['participant_rt_comparison'] = plot_participant_comparison(
                    module_df,
                    metric='response_time'
                )
            except Exception as e:
                print(f"Error creating participant RT comparison: {e}")
        
        try:
            figures['participant_accuracy_comparison'] = plot_participant_comparison(
                module_df,
                metric='accuracy'
            )
        except Exception as e:
            print(f"Error creating participant accuracy comparison: {e}")
    
    # 6. Switch costs (if applicable)
    if module_name in ['ADP', 'TASKSWITCH'] and 'Condition' in module_df.columns:
        try:
            figures['switch_costs'] = plot_switch_costs(module_df)
        except Exception as e:
            print(f"Error creating switch costs plot: {e}")
    
    # Save figures if output directory is specified
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, fig in figures.items():
            try:
                file_path = os.path.join(output_dir, f"{module_name}_{name}.png")
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                plt.close(fig)  # Close figure to avoid memory issues
            except Exception as e:
                print(f"Error saving figure {name}: {e}")
    else:
        # Even if we're not saving, close all figures to avoid memory issues
        for name, fig in figures.items():
            plt.close(fig)
    
    return figures