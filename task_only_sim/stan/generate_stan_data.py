#!/usr/bin/env python3
"""
Generate Stan data from the simple task simulation.
Converts Python simulation output to R data format for Stan.
"""

import numpy as np
import pandas as pd
import json

def generate_stan_data(n_tasks=246, seed=42):
    """
    Generate data matching our simulation for Stan model.
    
    Args:
        n_tasks: Number of tasks to simulate
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with data for Stan model
    """
    np.random.seed(seed)
    
    # Observed parameters from the real data
    observed_params = {
        'ai_disabled_mean': 90.9,
        'ai_disabled_std': 89.4,
        'ai_enabled_mean': 119.5,
        'ai_enabled_std': 118.1,
        'treatment_effect': 119.5 - 90.9,  # 28.6 minutes
        'n_ai_disabled': 110,
        'n_ai_enabled': 136
    }
    
    # Simulation parameters
    sim_params = {
        'baseline_time': 90.0,  # Baseline time (AI disabled)
        'ai_treatment_effect': 28.6,  # AI slows down by this amount
        'base_error_std': 60.0,  # Base error standard deviation
        'heteroskedastic_factor': 1.3  # AI group gets higher variance
    }
    
    # Generate treatments to match observed counts
    treatments = np.concatenate([
        np.zeros(observed_params['n_ai_disabled']),  # AI disabled
        np.ones(observed_params['n_ai_enabled'])     # AI enabled
    ])
    np.random.shuffle(treatments)
    
    # Generate implementation times
    times = np.zeros(n_tasks)
    for i in range(n_tasks):
        ai_treatment = treatments[i]
        base_time = sim_params['baseline_time']
        ai_effect = ai_treatment * sim_params['ai_treatment_effect']
        error_std = sim_params['base_error_std']
        if ai_treatment == 1:  # AI enabled gets higher variance
            error_std *= sim_params['heteroskedastic_factor']
        error = np.random.normal(0, error_std)
        time = base_time + ai_effect + error
        times[i] = max(5, time)
    
    return {
        'N': n_tasks,
        'ai_treatment': treatments.astype(int),
        'initial_time': times,
        'observed_params': observed_params,
        'sim_params': sim_params
    }

def write_json_data_file(data, filename='simple_ai_treatment.json'):
    """
    Write data to JSON format file for Stan.
    
    Args:
        data: Dictionary with simulation data
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
    
    print(f"JSON data file written to: {filename}")

def write_r_data_file(data, filename='simple_ai_treatment.data.R'):
    """
    Write data to R format file for Stan.
    
    Args:
        data: Dictionary with simulation data
        filename: Output filename
    """
    with open(filename, 'w') as f:
        f.write("# Data file for simple AI treatment Stan model\n")
        f.write("# Generated from simulation data\n\n")
        
        # Write N
        f.write(f"# Number of tasks\n")
        f.write(f"N <- {data['N']}\n\n")
        
        # Write AI treatment vector
        f.write("# AI treatment assignments (0 = disabled, 1 = enabled)\n")
        f.write("ai_treatment <- c(\n")
        f.write("  # AI Disabled ({} tasks)\n".format(sum(data['ai_treatment'] == 0)))
        f.write("  rep(0, {}),\n".format(sum(data['ai_treatment'] == 0)))
        f.write("  # AI Enabled ({} tasks)\n".format(sum(data['ai_treatment'] == 1)))
        f.write("  rep(1, {})\n".format(sum(data['ai_treatment'] == 1)))
        f.write(")\n\n")
        
        # Write initial time vector
        f.write("# Initial implementation times (in minutes)\n")
        f.write("initial_time <- c(\n")
        for i, time in enumerate(data['initial_time']):
            if i == len(data['initial_time']) - 1:
                f.write(f"  {time:.2f}\n")
            else:
                f.write(f"  {time:.2f},\n")
        f.write(")\n\n")
        
        # Write data summary
        f.write("# Data summary for verification\n")
        f.write("cat(\"Data summary:\\n\")\n")
        f.write("cat(\"N =\", N, \"\\n\")\n")
        f.write("cat(\"AI treatment distribution:\\n\")\n")
        f.write("cat(\"  Disabled (0):\", sum(ai_treatment == 0), \"\\n\")\n")
        f.write("cat(\"  Enabled (1):\", sum(ai_treatment == 1), \"\\n\")\n")
        f.write("cat(\"Time statistics by treatment:\\n\")\n")
        f.write("cat(\"  AI Disabled - Mean:\", round(mean(initial_time[ai_treatment == 0]), 1), \n")
        f.write("    \"SD:\", round(sd(initial_time[ai_treatment == 0]), 1), \"\\n\")\n")
        f.write("cat(\"  AI Enabled - Mean:\", round(mean(initial_time[ai_treatment == 1]), 1), \n")
        f.write("    \"SD:\", round(sd(initial_time[ai_treatment == 1]), 1), \"\\n\")\n")
        f.write("cat(\"Treatment effect:\", round(mean(initial_time[ai_treatment == 1]) - mean(initial_time[ai_treatment == 0]), 1), \"minutes\\n\")\n")
        f.write("cat(\"Variance ratio:\", round(var(initial_time[ai_treatment == 1]) / var(initial_time[ai_treatment == 0]), 2), \"\\n\")\n")
    
    print(f"R data file written to: {filename}")

def write_csv_data(data, filename='simple_ai_treatment_data.csv'):
    """
    Write data to CSV format for easy inspection.
    
    Args:
        data: Dictionary with simulation data
        filename: Output filename
    """
    df = pd.DataFrame({
        'task_id': range(1, data['N'] + 1),
        'ai_treatment': data['ai_treatment'],
        'initial_time': data['initial_time']
    })
    df.to_csv(filename, index=False)
    print(f"CSV data file written to: {filename}")

def main():
    """Main function to generate and save Stan data."""
    print("Generating Stan data from simple task simulation...")
    
    # Generate data
    data = generate_stan_data()
    
    # Print summary
    print(f"\nGenerated {data['N']} tasks")
    print(f"AI treatment distribution: {np.bincount(data['ai_treatment'])}")
    
    ai_disabled_times = data['initial_time'][data['ai_treatment'] == 0]
    ai_enabled_times = data['initial_time'][data['ai_treatment'] == 1]
    
    print(f"AI Disabled - Mean: {ai_disabled_times.mean():.1f}, SD: {ai_disabled_times.std():.1f}")
    print(f"AI Enabled - Mean: {ai_enabled_times.mean():.1f}, SD: {ai_enabled_times.std():.1f}")
    print(f"Treatment effect: {ai_enabled_times.mean() - ai_disabled_times.mean():.1f} minutes")
    print(f"Variance ratio: {ai_enabled_times.var() / ai_disabled_times.var():.2f}")
    
    # Write files
    write_json_data_file(data)  # Modern JSON format
    write_r_data_file(data)     # Legacy R format
    write_csv_data(data)        # CSV for inspection
    
    print("\nStan data generation complete!")
    print("\nNext steps:")
    print("1. Build the Stan model: make simple_ai_treatment")
    print("2. Run the model: ./simple_ai_treatment sample data file=simple_ai_treatment.json")
    print("3. Analyze results: bin/stansummary output.csv")

if __name__ == "__main__":
    main()
