#!/usr/bin/env python3
"""
Compare all four Stan models:
1. Non-pooled heteroskedastic normal
2. Non-pooled lognormal
3. Partially pooled heteroskedastic normal
4. Partially pooled lognormal
"""

import pandas as pd
import numpy as np
import json
import subprocess
import os
import sys
from pathlib import Path

def load_experimental_data(filepath='../../data_complete.csv'):
    """
    Load and prepare experimental data for Stan analysis.
    """
    print(f"Loading experimental data from: {filepath}")
    
    df = pd.read_csv(filepath)
    
    print(f"Data shape: {df.shape}")
    
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
    
    print(f"\nAI Enabled (1):")
    print(f"  Count: {len(ai_enabled_times)}")
    print(f"  Mean: {ai_enabled_times.mean():.1f}")
    print(f"  SD: {ai_enabled_times.std():.1f}")
    
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

def prepare_partial_pool_data(data):
    """
    Prepare data for partially pooled models.
    """
    print(f"\nPreparing data for partially pooled models...")
    
    # Create unique developer IDs (1-indexed)
    unique_devs = np.unique(data['dev_id_raw'])
    N_dev = len(unique_devs)
    
    # Create mapping from original dev_id to sequential 1-indexed IDs
    dev_id_mapping = {dev: i+1 for i, dev in enumerate(unique_devs)}
    dev_id = np.array([dev_id_mapping[dev] for dev in data['dev_id_raw']])
    
    print(f"Number of unique developers: {N_dev}")
    
    return {
        'N': data['N'],
        'N_dev': N_dev,
        'ai_treatment': data['ai_treatment'],
        'initial_time': data['initial_time'],
        'dev_id': dev_id
    }

def write_stan_data(data, filename='experimental_data.json'):
    """
    Write experimental data to JSON format for Stan.
    """
    stan_data = {
        'N': data['N'],
        'ai_treatment': data['ai_treatment'].tolist(),
        'initial_time': data['initial_time'].tolist()
    }
    
    with open(filename, 'w') as f:
        json.dump(stan_data, f, indent=2)
    
    print(f"Stan data file written to: {filename}")

def write_partial_pool_data(data, filename='partial_pool_data.json'):
    """
    Write partially pooled data to JSON format for Stan.
    """
    stan_data = {
        'N': data['N'],
        'N_dev': data['N_dev'],
        'ai_treatment': data['ai_treatment'].tolist(),
        'initial_time': data['initial_time'].tolist(),
        'dev_id': data['dev_id'].tolist()
    }
    
    with open(filename, 'w') as f:
        json.dump(stan_data, f, indent=2)
    
    print(f"Partially pooled data file written to: {filename}")

def build_stan_models():
    """
    Build all four Stan models.
    """
    print("\nBuilding Stan models...")
    
    # Get the current directory
    current_dir = Path.cwd()
    cmdstan_dir = Path("/Users/bb/git/others/cmdstan")
    
    models = [
        "simple_heteroskedastic",
        "simple_lognormal", 
        "simple_heteroskedastic_partial_pool",
        "simple_lognormal_partial_pool"
    ]
    
    for model in models:
        print(f"Building {model}...")
        cmd = ["make", str(current_dir / model)]
        
        try:
            subprocess.run(cmd, cwd=cmdstan_dir, check=True, capture_output=True)
            print(f"✅ {model} built successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build {model}: {e}")
            return False
    
    return True

def run_stan_model(model_name, data_file, output_suffix=""):
    """
    Run a Stan model on the specified data file.
    """
    print(f"\nRunning {model_name} model...")
    
    # Check if Stan executable exists
    stan_executable = f'./{model_name}'
    if not os.path.exists(stan_executable):
        print(f"Stan executable not found: {stan_executable}")
        return False
    
    # Run Stan model
    cmd = [stan_executable, 'sample', 'data', f'file={data_file}']
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {model_name} model completed successfully!")
        
        # Rename output file to avoid overwriting
        if os.path.exists('output.csv'):
            output_filename = f'output_{model_name}{output_suffix}.csv'
            os.rename('output.csv', output_filename)
            print(f"Output saved to: {output_filename}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {model_name} model failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def analyze_stan_results(model_name, output_suffix=""):
    """
    Analyze the Stan results using stansummary.
    """
    print(f"\nAnalyzing {model_name} results...")
    
    # Check if output file exists
    output_file = f'output_{model_name}{output_suffix}.csv'
    if not os.path.exists(output_file):
        print(f"Stan output file not found: {output_file}")
        return False
    
    # Try to run stansummary
    try:
        cmd = ['/Users/bb/git/others/cmdstan/bin/stansummary', output_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Stan summary results for {model_name}:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"stansummary failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("stansummary not found. Please ensure CmdStan is properly installed.")
        return False

def compare_all_models():
    """
    Compare results from all four models.
    """
    print("\n" + "="*60)
    print("COMPREHENSIVE MODEL COMPARISON SUMMARY")
    print("="*60)
    
    # Load experimental data summary
    data = load_experimental_data()
    
    print(f"\nExperimental Data Summary:")
    print(f"Total tasks: {data['N']}")
    print(f"AI treatment effect: {data['summary_stats']['treatment_effect']:.1f} minutes")
    print(f"Variance ratio: {data['summary_stats']['variance_ratio']:.2f}")
    
    print(f"\nModels compared:")
    print(f"1. Non-pooled heteroskedastic normal")
    print(f"2. Non-pooled lognormal")
    print(f"3. Partially pooled heteroskedastic normal")
    print(f"4. Partially pooled lognormal")
    
    print(f"\nFiles generated:")
    print(f"- experimental_data.json: Data for non-pooled models")
    print(f"- partial_pool_data.json: Data for partially pooled models")
    print(f"- output_*.csv: Stan sampling results for each model")
    
    print(f"\nNext steps:")
    print(f"1. Review Stan outputs in output_*.csv files")
    print(f"2. Run stansummary for detailed analysis of each model")
    print(f"3. Compare parameter estimates across models")
    print(f"4. Assess model fit and developer-level effects")
    print(f"5. Choose best model for final analysis")

def main():
    """Main function to run and compare all four Stan models."""
    print("=" * 60)
    print("Comprehensive Stan Model Comparison")
    print("=" * 60)
    
    try:
        # Load experimental data
        data = load_experimental_data()
        
        # Add dev_id_raw for partial pooling
        df = pd.read_csv('../../data_complete.csv')
        data['dev_id_raw'] = df['dev_id'].values
        
        # Write data files
        write_stan_data(data)
        partial_pool_data = prepare_partial_pool_data(data)
        write_partial_pool_data(partial_pool_data)
        
        # Build Stan models
        if not build_stan_models():
            print("❌ Failed to build Stan models. Exiting.")
            return 1
        
        # Run non-pooled models
        print(f"\n{'='*40}")
        print("RUNNING NON-POOLED MODELS")
        print(f"{'='*40}")
        
        if run_stan_model('simple_heteroskedastic', 'experimental_data.json'):
            analyze_stan_results('simple_heteroskedastic')
        
        if run_stan_model('simple_lognormal', 'experimental_data.json'):
            analyze_stan_results('simple_lognormal')
        
        # Run partially pooled models
        print(f"\n{'='*40}")
        print("RUNNING PARTIALLY POOLED MODELS")
        print(f"{'='*40}")
        
        if run_stan_model('simple_heteroskedastic_partial_pool', 'partial_pool_data.json'):
            analyze_stan_results('simple_heteroskedastic_partial_pool')
        
        if run_stan_model('simple_lognormal_partial_pool', 'partial_pool_data.json'):
            analyze_stan_results('simple_lognormal_partial_pool')
        
        # Compare all results
        compare_all_models()
        
        print("\n" + "=" * 60)
        print("Comprehensive Model Comparison Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
