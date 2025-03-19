#!/usr/bin/env python3
"""
ACE Analysis Pipeline

This script loads ACE data, performs comprehensive analysis, and generates
summary statistics for all game modules.
"""
import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

from ace.loader import ACELoader, ACEBulkLoader
from ace.analysis import ACEAnalyzer, create_module_analyzer
from ace.utils import create_data_quality_report
from ace.visualization import create_module_report, plot_module_comparison
from ace.export import export_all_summaries, export_summary_to_csv


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='ACE Analysis Pipeline')
    parser.add_argument('--data-dir', '-d', type=str, required=True,
                        help='Directory containing ACE data files')
    parser.add_argument('--output-dir', '-o', type=str, default='output',
                        help='Directory to save analysis results')
    parser.add_argument('--modules', '-m', type=str, nargs='+',
                        help='Specific modules to analyze (default: all)')
    parser.add_argument('--participants', '-p', type=str, nargs='+',
                        help='Specific participants to analyze (default: all)')
    parser.add_argument('--visualize', '-v', action='store_true',
                        help='Generate visualizations')
    parser.add_argument('--report', '-r', action='store_true',
                        help='Generate comprehensive report')
    parser.add_argument('--bulk', '-b', action='store_true',
                        help='Process directory as containing multiple datasets')
    
    return parser.parse_args()


def run_analysis(data_dir, output_dir, modules=None, participants=None, 
                visualize=False, report=False):
    """
    Run ACE analysis on a single data directory.
    
    Args:
        data_dir: Path to data directory
        output_dir: Path to output directory
        modules: Optional list of modules to analyze
        participants: Optional list of participants to analyze
        visualize: Whether to generate visualizations
        report: Whether to generate a comprehensive report
        
    Returns:
        Summary DataFrame
    """
    print(f"Loading data from {data_dir}...")
    loader = ACELoader(data_dir)
    ace_data = loader.load_all()
    
    # Filter by modules if specified
    if modules:
        ace_data.modules = {k: v for k, v in ace_data.modules.items() if k in modules}
    
    # Filter by participants if specified
    if participants:
        filtered_modules = {}
        for name, df in ace_data.modules.items():
            filtered_df = df[df['participant_id'].isin(participants)]
            if not filtered_df.empty:
                filtered_modules[name] = filtered_df
        
        ace_data.modules = filtered_modules
        
        if ace_data.demographics is not None:
            ace_data.demographics = ace_data.demographics[
                ace_data.demographics['participant_id'].isin(participants)
            ]
    
    # Print loading summary
    print(f"Loaded {len(ace_data.modules)} modules:")
    for module_name, df in ace_data.modules.items():
        participant_count = df['participant_id'].nunique() if 'participant_id' in df.columns else 0
        trial_count = len(df)
        print(f"  - {module_name}: {participant_count} participants, {trial_count} trials")
    
    # Run analysis
    print("Running analysis...")
    analyzer = ACEAnalyzer(ace_data)
    module_summaries = analyzer.analyze_all_modules()
    
    # Create summary DataFrame
    summary_df = analyzer.create_summary_dataframe(module_summaries)
    
    # Use module-specific analyzers for deeper analysis
    module_specific_results = {}
    for module_name, df in ace_data.modules.items():
        specific_analyzer = create_module_analyzer(module_name, df)
        module_specific_results[module_name] = specific_analyzer.analyze()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Export summary data - first ensure at least CSV export works
    csv_path = os.path.join(output_dir, 'participant_summary.csv')
    export_summary_to_csv(summary_df, csv_path)
    print(f"Exported summary data to CSV: {csv_path}")
    
    # Now try the full export with potential Excel export
    try:
        export_paths = export_all_summaries(module_summaries, summary_df, output_dir)
        print(f"Exported summary data to {output_dir}")
    except Exception as e:
        print(f"Warning: Full export failed: {e}. CSV export was successful.")
    
    # Generate visualizations if requested
    if visualize:
        try:
            viz_dir = os.path.join(output_dir, 'visualizations')
            os.makedirs(viz_dir, exist_ok=True)
            
            # Create visualizations for each module
            for module_name, df in ace_data.modules.items():
                module_viz_dir = os.path.join(viz_dir, module_name)
                os.makedirs(module_viz_dir, exist_ok=True)
                
                print(f"Generating visualizations for {module_name}...")
                try:
                    # Add debug information for troubleshooting
                    required_columns = ['Condition', 'response_time', 'participant_id', 'trial_number', 'accuracy', 'result']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        print(f"  - Warning: Missing columns in {module_name}: {', '.join(missing_columns)}")
                    
                    # Add accuracy column if needed
                    if 'accuracy' not in df.columns and 'result' in df.columns:
                        df = df.copy()
                        df['accuracy'] = (df['result'] == 'successful').astype(int)
                        print(f"  - Added accuracy column based on result")
                    
                    # Create visualizations - pass module_name explicitly to avoid Series issues
                    figures = create_module_report(df, module_viz_dir, module_name=module_name)
                    print(f"  - Created {len(figures)} visualizations")
                except Exception as e:
                    print(f"  - Error creating visualizations for {module_name}: {e}")
                    # Print more details about the error
                    import traceback
                    print(f"  - Traceback: {traceback.format_exc()}")
                
            # Save comparison plot
            if len(ace_data.modules) > 1:
                try:
                    comparison_fig = plot_module_comparison(summary_df)
                    comparison_fig.savefig(os.path.join(viz_dir, 'module_comparison.png'), dpi=300)
                    print("Created module comparison visualization")
                except Exception as e:
                    print(f"Error creating module comparison: {e}")
            
            print(f"Visualizations saved to {viz_dir}")
        except Exception as e:
            print(f"Error generating visualizations: {e}")
    
    # Generate comprehensive report if requested
    if report:
        try:
            report_dir = os.path.join(output_dir, 'report')
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate data quality report
            quality_reports = {}
            for module_name, df in ace_data.modules.items():
                quality_reports[module_name] = create_data_quality_report(df)
            
            # Save quality reports
            with open(os.path.join(report_dir, 'data_quality.json'), 'w') as f:
                import json
                # Convert any non-serializable values to strings
                serializable_reports = {}
                for module, report in quality_reports.items():
                    serializable_reports[module] = {}
                    for key, value in report.items():
                        if isinstance(value, dict):
                            serializable_reports[module][key] = {
                                k: str(v) if not isinstance(v, (int, float, str, list, dict, bool, type(None))) else v
                                for k, v in value.items()
                            }
                        else:
                            serializable_reports[module][key] = str(value) if not isinstance(value, (int, float, str, list, dict, bool, type(None))) else value
                json.dump(serializable_reports, f, indent=2)
            
            # Save module-specific analysis results
            with open(os.path.join(report_dir, 'module_analysis.json'), 'w') as f:
                # Convert any non-serializable values to strings
                serializable_results = {}
                for module, results in module_specific_results.items():
                    serializable_results[module] = {
                        k: str(v) if not isinstance(v, (int, float, str, list, dict, bool, type(None))) else v
                        for k, v in results.items()
                    }
                json.dump(serializable_results, f, indent=2)
            
            print(f"Comprehensive report saved to {report_dir}")
        except Exception as e:
            print(f"Error generating report: {e}")
    
    return summary_df


def run_bulk_analysis(base_dir, output_dir, modules=None, participants=None, 
                     visualize=False, report=False):
    """
    Run ACE analysis on multiple data directories.
    
    Args:
        base_dir: Path to base directory containing multiple datasets
        output_dir: Path to output directory
        modules: Optional list of modules to analyze
        participants: Optional list of participants to analyze
        visualize: Whether to generate visualizations
        report: Whether to generate a comprehensive report
        
    Returns:
        Dictionary mapping dataset names to summary DataFrames
    """
    print(f"Loading bulk data from {base_dir}...")
    bulk_loader = ACEBulkLoader(base_dir)
    data_directories = bulk_loader.find_data_directories()
    
    print(f"Found {len(data_directories)} data directories")
    
    # Create bulk output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each dataset
    results = {}
    for i, data_dir in enumerate(data_directories):
        dir_name = os.path.basename(data_dir)
        print(f"\nProcessing dataset {i+1}/{len(data_directories)}: {dir_name}")
        
        dataset_output_dir = os.path.join(output_dir, dir_name)
        
        try:
            summary_df = run_analysis(
                data_dir=data_dir,
                output_dir=dataset_output_dir,
                modules=modules,
                participants=participants,
                visualize=visualize,
                report=report
            )
            results[dir_name] = summary_df
        except Exception as e:
            print(f"Error processing {dir_name}: {e}")
    
    # Create a combined summary if we have multiple results
    if len(results) > 1:
        try:
            # Add dataset column to each DataFrame
            combined_dfs = []
            for dataset_name, df in results.items():
                if not df.empty:
                    df = df.copy()
                    df['dataset'] = dataset_name
                    combined_dfs.append(df)
            
            if combined_dfs:
                combined_df = pd.concat(combined_dfs, ignore_index=True)
                combined_path = os.path.join(output_dir, 'combined_summary.csv')
                combined_df.to_csv(combined_path, index=False)
                print(f"Combined summary saved to {combined_path}")
        except Exception as e:
            print(f"Error creating combined summary: {e}")
    
    return results


def main():
    """Main function."""
    args = parse_args()
    
    # Validate arguments
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory {args.data_dir} does not exist")
        return 1
    
    # Create timestamp for output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(args.output_dir, f"ace_analysis_{timestamp}")
    
    print("ACE Analysis Pipeline")
    print("=" * 80)
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {output_dir}")
    if args.modules:
        print(f"Modules to analyze: {', '.join(args.modules)}")
    if args.participants:
        print(f"Participants to analyze: {', '.join(args.participants)}")
    print(f"Generate visualizations: {args.visualize}")
    print(f"Generate comprehensive report: {args.report}")
    print(f"Bulk processing: {args.bulk}")
    print("=" * 80)
    
    # Run analysis
    try:
        if args.bulk:
            run_bulk_analysis(
                base_dir=args.data_dir,
                output_dir=output_dir,
                modules=args.modules,
                participants=args.participants,
                visualize=args.visualize,
                report=args.report
            )
        else:
            run_analysis(
                data_dir=args.data_dir,
                output_dir=output_dir,
                modules=args.modules,
                participants=args.participants,
                visualize=args.visualize,
                report=args.report
            )
        
        print(f"\nAnalysis complete. Results saved to {output_dir}")
        return 0
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())