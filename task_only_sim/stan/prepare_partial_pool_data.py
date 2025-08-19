#!/usr/bin/env python3
"""
Prepare data for partially pooled Stan models
Includes developer-level random effects
"""

import pandas as pd
import numpy as np
import json
import sys

def load_and_prepare_data(filepath='../../data_complete.csv'):
    """
    Load experimental data and prepare for partially pooled models.
    """
    print(f"Loading experimental data from: {filepath}")
    
    df = pd.read_csv(filepath)
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Extract the data we need
    N = len(df)
    ai_treatment = df['ai_treatment'].values.astype(int)
    initial_time = df['initial_implementation_time'].values
    dev_id_raw = df['dev_id'].values
    
    # Create unique developer IDs (1-indexed)
    unique_devs = np.unique(dev_id_raw)
    N_dev = len(unique_devs)
    
    # Create mapping from original dev_id to sequential 1-indexed IDs
    dev_id_mapping = {dev: i+1 for i, dev in enumerate(unique_devs)}
    dev_id = np.array([dev_id_mapping[dev] for dev in dev_id_raw])
    
    print(f"\nDeveloper Information:")
    print(f"Number of unique developers: {N_dev}")
    print(f"Developer ID range: {dev_id.min()} to {dev_id.max()}")
    
    # Check developer distribution
    dev_counts = np.bincount(dev_id)[1:]  # Skip index 0
    print(f"Tasks per developer: min={dev_counts.min()}, max={dev_counts.max()}, mean={dev_counts.mean():.1f}")
    
    # Basic statistics
    print(f"\nData Summary:")
    print(f"N = {N}")
    print(f"N_dev = {N_dev}")
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
    
    # Developer-level analysis
    print(f"\nDeveloper-Level Analysis:")
    dev_treatment_effects = []
    dev_baseline_means = []
    
    for dev_idx in range(1, N_dev + 1):
        dev_mask = dev_id == dev_idx
        if dev_mask.sum() > 0:
            dev_times = initial_time[dev_mask]
            dev_treatments = ai_treatment[dev_mask]
            
            # Developer baseline (AI disabled)
            dev_baseline = dev_times[dev_treatments == 0]
            if len(dev_baseline) > 0:
                dev_baseline_means.append(dev_baseline.mean())
            
            # Developer treatment effect
            dev_ai_enabled = dev_times[dev_treatments == 1]
            if len(dev_baseline) > 0 and len(dev_ai_enabled) > 0:
                dev_effect = dev_ai_enabled.mean() - dev_baseline.mean()
                dev_treatment_effects.append(dev_effect)
    
    if dev_baseline_means:
        print(f"  Developer baseline variation: mean={np.mean(dev_baseline_means):.1f}, std={np.std(dev_baseline_means):.1f}")
    
    if dev_treatment_effects:
        print(f"  Developer treatment effect variation: mean={np.mean(dev_treatment_effects):.1f}, std={np.std(dev_treatment_effects):.1f}")
    
    return {
        'N': N,
        'N_dev': N_dev,
        'ai_treatment': ai_treatment,
        'initial_time': initial_time,
        'dev_id': dev_id,
        'dev_id_mapping': dev_id_mapping,
        'summary_stats': {
            'ai_disabled_mean': ai_disabled_times.mean(),
            'ai_disabled_std': ai_disabled_times.std(),
            'ai_enabled_mean': ai_enabled_times.mean(),
            'ai_enabled_std': ai_enabled_times.std(),
            'treatment_effect': treatment_effect,
            'variance_ratio': variance_ratio,
            'dev_baseline_std': np.std(dev_baseline_means) if dev_baseline_means else 0,
            'dev_treatment_std': np.std(dev_treatment_effects) if dev_treatment_effects else 0
        }
    }

def write_stan_data(data, filename='partial_pool_data.json'):
    """
    Write data for partially pooled Stan models to JSON format.
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
    
    print(f"\nStan data file written to: {filename}")
    print(f"Data structure:")
    print(f"  - N: {data['N']} tasks")
    print(f"  - N_dev: {data['N_dev']} developers")
    print(f"  - ai_treatment: {len(data['ai_treatment'])} binary values")
    print(f"  - initial_time: {len(data['initial_time'])} time values")
    print(f"  - dev_id: {len(data['dev_id'])} developer IDs (1-indexed)")

def write_developer_summary(data, filename='developer_summary.csv'):
    """
    Write developer-level summary statistics to CSV.
    """
    dev_summary = []
    
    for dev_idx in range(1, data['N_dev'] + 1):
        dev_mask = data['dev_id'] == dev_idx
        if dev_mask.sum() > 0:
            dev_times = data['initial_time'][dev_mask]
            dev_treatments = data['ai_treatment'][dev_mask]
            
            # Find original dev_id
            original_dev_id = None
            for orig_id, mapped_id in data['dev_id_mapping'].items():
                if mapped_id == dev_idx:
                    original_dev_id = orig_id
                    break
            
            # Developer baseline (AI disabled)
            dev_baseline = dev_times[dev_treatments == 0]
            dev_baseline_mean = dev_baseline.mean() if len(dev_baseline) > 0 else np.nan
            dev_baseline_std = dev_baseline.std() if len(dev_baseline) > 0 else np.nan
            dev_baseline_count = len(dev_baseline)
            
            # Developer AI enabled
            dev_ai_enabled = dev_times[dev_treatments == 1]
            dev_ai_mean = dev_ai_enabled.mean() if len(dev_ai_enabled) > 0 else np.nan
            dev_ai_std = dev_ai_enabled.std() if len(dev_ai_enabled) > 0 else np.nan
            dev_ai_count = len(dev_ai_enabled)
            
            # Treatment effect
            dev_effect = dev_ai_mean - dev_baseline_mean if not (np.isnan(dev_ai_mean) or np.isnan(dev_baseline_mean)) else np.nan
            
            dev_summary.append({
                'dev_id': dev_idx,
                'original_dev_id': original_dev_id,
                'total_tasks': dev_mask.sum(),
                'ai_disabled_count': dev_baseline_count,
                'ai_enabled_count': dev_ai_count,
                'ai_disabled_mean': dev_baseline_mean,
                'ai_disabled_std': dev_baseline_std,
                'ai_enabled_mean': dev_ai_mean,
                'ai_enabled_std': dev_ai_std,
                'treatment_effect': dev_effect
            })
    
    dev_df = pd.DataFrame(dev_summary)
    dev_df.to_csv(filename, index=False)
    print(f"Developer summary written to: {filename}")

def main():
    """Main function to prepare data for partially pooled models."""
    print("=" * 60)
    print("Data Preparation for Partially Pooled Stan Models")
    print("=" * 60)
    
    try:
        # Load and prepare data
        data = load_and_prepare_data()
        
        # Write Stan data file
        write_stan_data(data)
        
        # Write developer summary
        write_developer_summary(data)
        
        print("\n" + "=" * 60)
        print("Data Preparation Complete!")
        print("=" * 60)
        print(f"\nFiles generated:")
        print(f"- partial_pool_data.json: Data for partially pooled Stan models")
        print(f"- developer_summary.csv: Developer-level statistics")
        print(f"\nNext steps:")
        print(f"1. Build partially pooled Stan models")
        print(f"2. Run models with partial_pool_data.json")
        print(f"3. Compare with non-pooled models")
        print(f"4. Analyze developer-level random effects")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
