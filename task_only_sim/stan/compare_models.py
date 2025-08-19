#!/usr/bin/env python3
"""
Compare heteroskedastic normal vs lognormal Stan models
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
    
    # Log-scale statistics for lognormal comparison
    print(f"\nLog-scale Statistics:")
    log_disabled = np.log(ai_disabled_times)
    log_enabled = np.log(ai_enabled_times)
    print(f"AI Disabled - Log Mean: {log_disabled.mean():.3f}, Log SD: {log_disabled.std():.3f}")
    print(f"AI Enabled - Log Mean: {log_enabled.mean():.3f}, Log SD: {log_enabled.std():.3f}")
    
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
            'variance_ratio': variance_ratio,
            'log_disabled_mean': log_disabled.mean(),
            'log_disabled_std': log_disabled.std(),
            'log_enabled_mean': log_enabled.mean(),
            'log_enabled_std': log_enabled.std()
        }
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

def build_stan_models():
    """
    Build both Stan models.
    """
    print("\nBuilding Stan models...")
    
    # Get the current directory
    current_dir = Path.cwd()
    cmdstan_dir = Path("/Users/bb/git/others/cmdstan")
    
    # Build heteroskedastic model
    print("Building heteroskedastic model...")
    hetero_cmd = [
        "make", 
        str(current_dir / "simple_heteroskedastic")
    ]
    
    try:
        subprocess.run(hetero_cmd, cwd=cmdstan_dir, check=True, capture_output=True)
        print("✅ Heteroskedastic model built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build heteroskedastic model: {e}")
        return False
    
    # Build lognormal model
    print("Building lognormal model...")
    lognormal_cmd = [
        "make", 
        str(current_dir / "simple_lognormal")
    ]
    
    try:
        subprocess.run(lognormal_cmd, cwd=cmdstan_dir, check=True, capture_output=True)
        print("✅ Lognormal model built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build lognormal model: {e}")
        return False
    
    return True

def run_stan_model(model_name, data_file='experimental_data.json'):
    """
    Run a Stan model on the experimental data.
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
        print(f"Output saved to: output_{model_name}.csv")
        
        # Rename output file to avoid overwriting
        if os.path.exists('output.csv'):
            os.rename('output.csv', f'output_{model_name}.csv')
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {model_name} model failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def analyze_stan_results(model_name):
    """
    Analyze the Stan results using stansummary.
    """
    print(f"\nAnalyzing {model_name} results...")
    
    # Check if output file exists
    output_file = f'output_{model_name}.csv'
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

def compare_model_results():
    """
    Compare results from both models.
    """
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    
    # Load experimental data summary
    data = load_experimental_data()
    
    print(f"\nExperimental Data Summary:")
    print(f"Total tasks: {data['N']}")
    print(f"AI treatment effect: {data['summary_stats']['treatment_effect']:.1f} minutes")
    print(f"Variance ratio: {data['summary_stats']['variance_ratio']:.2f}")
    
    print(f"\nFiles generated:")
    print(f"- experimental_data.json: Data for Stan models")
    print(f"- output_simple_heteroskedastic.csv: Heteroskedastic normal results")
    print(f"- output_simple_lognormal.csv: Lognormal results")
    
    print(f"\nNext steps:")
    print(f"1. Review Stan outputs in output_*.csv files")
    print(f"2. Run stansummary for detailed analysis")
    print(f"3. Compare model fit and parameter estimates")
    print(f"4. Assess which model better captures the data")

def main():
    """Main function to run and compare both Stan models."""
    print("=" * 60)
    print("Stan Model Comparison: Heteroskedastic vs Lognormal")
    print("=" * 60)
    
    try:
        # Load experimental data
        data = load_experimental_data()
        
        # Write Stan data file
        write_stan_data(data)
        
        # Build Stan models
        if not build_stan_models():
            print("❌ Failed to build Stan models. Exiting.")
            return 1
        
        # Run heteroskedastic model
        if run_stan_model('simple_heteroskedastic'):
            analyze_stan_results('simple_heteroskedastic')
        
        # Run lognormal model
        if run_stan_model('simple_lognormal'):
            analyze_stan_results('simple_lognormal')
        
        # Compare results
        compare_model_results()
        
        print("\n" + "=" * 60)
        print("Model Comparison Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
