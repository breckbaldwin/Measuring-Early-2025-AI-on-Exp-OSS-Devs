#!/usr/bin/env python3
"""
Run Stan model on experimental data from data_complete.csv
"""

import pandas as pd
import numpy as np
import json
import subprocess
import os
import sys

def load_experimental_data(filepath='../../data_complete.csv'):
    """
    Load and prepare experimental data for Stan analysis.
    
    Args:
        filepath: Path to the experimental data CSV
        
    Returns:
        Dictionary with data for Stan model
    """
    print(f"Loading experimental data from: {filepath}")
    
    # Load the data
    df = pd.read_csv(filepath)
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check for required columns
    required_cols = ['ai_treatment', 'initial_implementation_time']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Extract the data we need
    N = len(df)
    ai_treatment = df['ai_treatment'].values.astype(int)
    initial_time = df['initial_implementation_time'].values
    
    # Basic statistics
    print(f"\nData Summary:")
    print(f"N = {N}")
    print(f"AI treatment distribution: {np.bincount(ai_treatment)}")
    
    # Treatment group statistics
    ai_disabled_times = initial_time[ai_treatment == 0]
    ai_enabled_times = initial_time[ai_treatment == 1]
    
    print(f"\nAI Disabled (0):")
    print(f"  Count: {len(ai_disabled_times)}")
    print(f"  Mean: {ai_disabled_times.mean():.1f}")
    print(f"  SD: {ai_disabled_times.std():.1f}")
    print(f"  Min: {ai_disabled_times.min():.1f}")
    print(f"  Max: {ai_disabled_times.max():.1f}")
    
    print(f"\nAI Enabled (1):")
    print(f"  Count: {len(ai_enabled_times)}")
    print(f"  Mean: {ai_enabled_times.mean():.1f}")
    print(f"  SD: {ai_enabled_times.std():.1f}")
    print(f"  Min: {ai_enabled_times.min():.1f}")
    print(f"  Max: {ai_enabled_times.max():.1f}")
    
    # Treatment effect
    treatment_effect = ai_enabled_times.mean() - ai_disabled_times.mean()
    print(f"\nTreatment Effect: {treatment_effect:.1f} minutes")
    
    # Variance ratio
    variance_ratio = ai_enabled_times.var() / ai_disabled_times.var()
    print(f"Variance Ratio: {variance_ratio:.2f}")
    
    return {
        'N': N,
        'ai_treatment': ai_treatment,
        'initial_time': initial_time,
        'summary_stats': {
            'ai_disabled_mean': ai_disabled_times.mean(),
            'ai_disabled_std': ai_disabled_times.std(),
            'ai_enabled_mean': ai_enabled_times.mean(),
            'ai_enabled_std': ai_enabled_times.std(),
            'treatment_effect': treatment_effect,
            'variance_ratio': variance_ratio
        }
    }

def write_stan_data(data, filename='experimental_data.json'):
    """
    Write experimental data to JSON format for Stan.
    
    Args:
        data: Dictionary with experimental data
        filename: Output filename
    """
    # Prepare data for Stan (only the variables needed by the model)
    stan_data = {
        'N': data['N'],
        'ai_treatment': data['ai_treatment'].tolist(),
        'initial_time': data['initial_time'].tolist()
    }
    
    with open(filename, 'w') as f:
        json.dump(stan_data, f, indent=2)
    
    print(f"\nStan data file written to: {filename}")

def run_stan_model(data_file='experimental_data.json'):
    """
    Run the Stan model on the experimental data.
    
    Args:
        data_file: JSON data file for Stan
    """
    print(f"\nRunning Stan model on experimental data...")
    
    # Check if Stan executable exists
    stan_executable = './simple_ai_treatment'
    if not os.path.exists(stan_executable):
        print(f"Stan executable not found: {stan_executable}")
        print("Please build the Stan model first using:")
        print("cd /Users/bb/git/others/cmdstan")
        print("make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_ai_treatment")
        return False
    
    # Run Stan model
    cmd = [stan_executable, 'sample', 'data', f'file={data_file}']
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Stan model completed successfully!")
        print(f"Output saved to: output.csv")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Stan model failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def analyze_stan_results():
    """
    Analyze the Stan results using stansummary.
    """
    print(f"\nAnalyzing Stan results...")
    
    # Check if output file exists
    if not os.path.exists('output.csv'):
        print("Stan output file not found. Please run the Stan model first.")
        return False
    
    # Try to run stansummary
    try:
        cmd = ['/Users/bb/git/others/cmdstan/bin/stansummary', 'output.csv']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Stan summary results:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"stansummary failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("stansummary not found. Please ensure CmdStan is properly installed.")
        return False

def main():
    """Main function to run Stan analysis on experimental data."""
    print("=" * 60)
    print("Stan Model Analysis on Experimental Data")
    print("=" * 60)
    
    try:
        # Load experimental data
        data = load_experimental_data()
        
        # Write Stan data file
        write_stan_data(data)
        
        # Run Stan model
        if run_stan_model():
            # Analyze results
            analyze_stan_results()
        
        print("\n" + "=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
        
        # Print summary of what was found
        print(f"\nExperimental Data Summary:")
        print(f"Total tasks: {data['N']}")
        print(f"AI treatment effect: {data['summary_stats']['treatment_effect']:.1f} minutes")
        print(f"Variance ratio: {data['summary_stats']['variance_ratio']:.2f}")
        
        print(f"\nFiles generated:")
        print(f"- experimental_data.json: Data for Stan model")
        print(f"- output.csv: Stan sampling results")
        
        print(f"\nNext steps:")
        print(f"1. Review Stan output in output.csv")
        print(f"2. Run stansummary for detailed analysis")
        print(f"3. Compare with simulation results")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
