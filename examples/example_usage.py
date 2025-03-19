#!/usr/bin/env python3
"""
Example usage of the ACE Analysis Package.

This script demonstrates how to use the ACE package to load, analyze,
and visualize ACE data.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from ace.loader import ACELoader, ACEBulkLoader
from ace.analysis import ACEAnalyzer, create_module_analyzer
from ace.visualization import (
    plot_reaction_times_by_condition,
    plot_accuracy_by_condition,
    plot_learning_curve,
    plot_module_comparison,
    create_module_report
)
from ace.export import export_all_summaries


def example_single_dataset():
    """Example analysis on a single dataset."""
    print("\n=== Single Dataset Analysis ===")
    
    # Load data from sample directory
    data_dir = "data/sample_run/sample"
    print(f"Loading data from {data_dir}...")
    
    loader = ACELoader(data_dir)
    ace_data = loader.load_all()
    
    # Print loading summary
    print(f"Loaded {len(ace_data.modules)} modules:")
    for module_name, df in ace_data.modules.items():
        participant_count = df['participant_id'].nunique() if 'participant_id' in df.columns else 0
        trial_count = len(df)
        print(f"  - {module_name}: {participant_count} participants, {trial_count} trials")
    
    # Get participant IDs
    participant_ids = ace_data.participant_ids()
    print(f"Found {len(participant_ids)} participants: {participant_ids}")
    
    # Run analysis
    print("\nRunning analysis...")
    analyzer = ACEAnalyzer(ace_data)
    module_summaries = analyzer.analyze_all_modules()
    
    # Create summary DataFrame
    summary_df = analyzer.create_summary_dataframe(module_summaries)
    print("\nSummary DataFrame:")
    print(summary_df.head())
    
    # Focus on a specific module
    module_name = "BRT"
    if module_name in ace_data.modules:
        print(f"\nDetailed analysis of {module_name} module:")
        module_df = ace_data.modules[module_name]
        
        # Use module-specific analyzer
        specific_analyzer = create_module_analyzer(module_name, module_df)
        module_results = specific_analyzer.analyze()
        
        print("Module-specific metrics:")
        for key, value in module_results.items():
            if isinstance(value, (int, float, str)):
                print(f"  - {key}: {value}")
        
        # Generate and display visualizations
        print("\nGenerating visualizations...")
        
        # Create output directory for visualizations
        viz_dir = "output/example_visualizations"
        os.makedirs(viz_dir, exist_ok=True)
        
        # Create comprehensive module report
        figures = create_module_report(module_df, viz_dir)
        print(f"Saved {len(figures)} visualizations to {viz_dir}")
    
    # Export results
    output_dir = "output/example_single"
    os.makedirs(output_dir, exist_ok=True)
    
    export_paths = export_all_summaries(module_summaries, summary_df, output_dir)
    print(f"\nExported summary data to {output_dir}")
    
    return summary_df, module_summaries


def example_bulk_analysis():
    """Example bulk analysis on multiple datasets."""
    print("\n=== Bulk Dataset Analysis ===")
    
    # Define base directory containing multiple datasets
    base_dir = "data"
    print(f"Searching for datasets in {base_dir}...")
    
    # Load multiple datasets
    bulk_loader = ACEBulkLoader(base_dir)
    data_directories = bulk_loader.find_data_directories()
    
    print(f"Found {len(data_directories)} data directories")
    
    # Process first dataset as an example
    if data_directories:
        data_dir = data_directories[0]
        dir_name = os.path.basename(data_dir)
        print(f"\nProcessing dataset: {dir_name}")
        
        # Load single dataset
        loader = ACELoader(data_dir)
        ace_data = loader.load_all()
        
        # Run analysis
        analyzer = ACEAnalyzer(ace_data)
        module_summaries = analyzer.analyze_all_modules()
        
        # Create summary DataFrame
        summary_df = analyzer.create_summary_dataframe(module_summaries)
        print("\nSummary DataFrame:")
        print(summary_df.head())
        
        # Export results
        output_dir = f"output/example_bulk/{dir_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        export_paths = export_all_summaries(module_summaries, summary_df, output_dir)
        print(f"\nExported summary data to {output_dir}")
        
        return summary_df, module_summaries
    
    print("No data directories found")
    return None, None


def example_participant_analysis():
    """Example analysis focusing on a specific participant."""
    print("\n=== Participant-Specific Analysis ===")
    
    # Load data from sample directory
    data_dir = "data/sample_run/sample"
    print(f"Loading data from {data_dir}...")
    
    loader = ACELoader(data_dir)
    ace_data = loader.load_all()
    
    # Get participant IDs
    participant_ids = ace_data.participant_ids()
    print(f"Found {len(participant_ids)} participants: {participant_ids}")
    
    # Select first participant as an example
    if participant_ids:
        participant_id = participant_ids[0]
        print(f"\nAnalyzing participant: {participant_id}")
        
        # Filter data to include only this participant
        participant_data = ace_data.filter_by_participant(participant_id)
        
        # Run analysis
        analyzer = ACEAnalyzer(participant_data)
        module_summaries = analyzer.analyze_all_modules()
        
        # Create summary DataFrame
        summary_df = analyzer.create_summary_dataframe(module_summaries)
        print("\nParticipant Summary:")
        print(summary_df)
        
        # Export results
        output_dir = f"output/example_participant/{participant_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        export_paths = export_all_summaries(module_summaries, summary_df, output_dir)
        print(f"\nExported participant data to {output_dir}")
        
        return summary_df, module_summaries
    
    print("No participants found")
    return None, None


def main():
    """Run all example analyses."""
    # Create base output directory
    os.makedirs("output", exist_ok=True)
    
    # Run examples
    single_results = example_single_dataset()
    bulk_results = example_bulk_analysis()
    participant_results = example_participant_analysis()
    
    print("\n=== Examples Complete ===")
    print("Results are saved in the 'output' directory")


if __name__ == "__main__":
    main()