#!/usr/bin/env python3
"""
Comprehensive Data Analysis for Measuring Early-2025 AI on Experienced OSS Devs

This script provides detailed analysis of the data_complete.csv dataset,
including exploratory data analysis, summary statistics, and additional insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data(filepath):
    """Load and prepare the data for analysis."""
    print("Loading data...")
    df = pd.read_csv(filepath)
    
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Number of unique developers: {df['dev_id'].nunique()}")
    print(f"Number of unique issues: {df['issue_id'].nunique()}")
    
    return df

def basic_statistics(df):
    """Generate basic statistics for the dataset."""
    print("\n" + "="*60)
    print("BASIC STATISTICS")
    print("="*60)
    
    # Time-related statistics
    print("\nTime Statistics (in minutes):")
    print(f"Initial implementation time:")
    print(f"  Mean: {df['initial_implementation_time'].mean():.2f}")
    print(f"  Median: {df['initial_implementation_time'].median():.2f}")
    print(f"  Std: {df['initial_implementation_time'].std():.2f}")
    print(f"  Min: {df['initial_implementation_time'].min():.2f}")
    print(f"  Max: {df['initial_implementation_time'].max():.2f}")
    
    print(f"\nPost-review implementation time:")
    print(f"  Mean: {df['post_review_implementation_time'].mean():.2f}")
    print(f"  Median: {df['post_review_implementation_time'].median():.2f}")
    print(f"  Std: {df['post_review_implementation_time'].std():.2f}")
    print(f"  Min: {df['post_review_implementation_time'].min():.2f}")
    print(f"  Max: {df['post_review_implementation_time'].max():.2f}")
    
    # Prediction statistics
    print(f"\nPrediction Statistics:")
    print(f"Predicted time without AI:")
    print(f"  Mean: {df['predicted_time_no_ai'].mean():.2f}")
    print(f"  Median: {df['predicted_time_no_ai'].median():.2f}")
    
    print(f"Predicted time with AI:")
    print(f"  Mean: {df['predicted_time_ai_allowed'].mean():.2f}")
    print(f"  Median: {df['predicted_time_ai_allowed'].median():.2f}")
    
    # Treatment group statistics
    print(f"\nTreatment Group Statistics:")
    ai_allowed = df[df['ai_treatment'] == 1]  # AI was used
    ai_disallowed = df[df['ai_treatment'] == 0]  # AI was not allowed
    
    print(f"AI Used (n={len(ai_allowed)}):")
    print(f"  Initial time mean: {ai_allowed['initial_implementation_time'].mean():.2f}")
    print(f"  Post-review time mean: {ai_allowed['post_review_implementation_time'].mean():.2f}")
    
    print(f"AI Not Allowed (n={len(ai_disallowed)}):")
    print(f"  Initial time mean: {ai_disallowed['initial_implementation_time'].mean():.2f}")
    print(f"  Post-review time mean: {ai_disallowed['post_review_implementation_time'].mean():.2f}")

def missing_data_analysis(df):
    """Analyze missing data patterns."""
    print("\n" + "="*60)
    print("MISSING DATA ANALYSIS")
    print("="*60)
    
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing_counts.index,
        'Missing_Count': missing_counts.values,
        'Missing_Percentage': missing_percentages.values
    }).sort_values('Missing_Percentage', ascending=False)
    
    print("\nMissing data summary:")
    print(missing_df.to_string(index=False))
    
    # Analyze missing data by treatment group
    print(f"\nMissing post-review time by treatment group:")
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        missing_count = df[df['ai_treatment'] == treatment]['post_review_implementation_time'].isnull().sum()
        total_count = len(df[df['ai_treatment'] == treatment])
        print(f"  {treatment_name}: {missing_count}/{total_count} ({missing_count/total_count*100:.1f}%)")

def treatment_effect_analysis(df):
    """Analyze treatment effects in detail."""
    print("\n" + "="*60)
    print("TREATMENT EFFECT ANALYSIS")
    print("="*60)
    
    # Create total time column
    df['total_time'] = df['initial_implementation_time'] + df['post_review_implementation_time'].fillna(0)
    
    # Group by treatment
    ai_allowed = df[df['ai_treatment'] == 1]  # AI was used
    ai_disallowed = df[df['ai_treatment'] == 0]  # AI was not allowed
    
    print(f"Total implementation time comparison:")
    print(f"AI Used (n={len(ai_allowed)}):")
    print(f"  Mean: {ai_allowed['total_time'].mean():.2f} minutes")
    print(f"  Median: {ai_allowed['total_time'].median():.2f} minutes")
    print(f"  Std: {ai_allowed['total_time'].std():.2f} minutes")
    
    print(f"AI Not Allowed (n={len(ai_disallowed)}):")
    print(f"  Mean: {ai_disallowed['total_time'].mean():.2f} minutes")
    print(f"  Median: {ai_disallowed['total_time'].median():.2f} minutes")
    print(f"  Std: {ai_disallowed['total_time'].std():.2f} minutes")
    
    # Calculate effect size
    mean_diff = ai_allowed['total_time'].mean() - ai_disallowed['total_time'].mean()
    pooled_std = np.sqrt(((len(ai_allowed)-1)*ai_allowed['total_time'].var() + 
                          (len(ai_disallowed)-1)*ai_disallowed['total_time'].var()) / 
                         (len(ai_allowed) + len(ai_disallowed) - 2))
    cohens_d = mean_diff / pooled_std
    
    print(f"\nEffect size (Cohen's d): {cohens_d:.3f}")
    
    # T-test
    t_stat, p_value = stats.ttest_ind(ai_allowed['total_time'], ai_disallowed['total_time'])
    print(f"Independent t-test: t={t_stat:.3f}, p={p_value:.6f}")
    
    # Mann-Whitney U test (non-parametric)
    u_stat, u_p_value = stats.mannwhitneyu(ai_allowed['total_time'], ai_disallowed['total_time'], 
                                          alternative='two-sided')
    print(f"Mann-Whitney U test: U={u_stat:.1f}, p={u_p_value:.6f}")

def developer_analysis(df):
    """Analyze patterns by individual developers."""
    print("\n" + "="*60)
    print("DEVELOPER-LEVEL ANALYSIS")
    print("="*60)
    
    # Group by developer
    dev_stats = df.groupby('dev_id').agg({
        'ai_treatment': ['count', 'sum', 'mean'],
        'initial_implementation_time': ['mean', 'std'],
        'post_review_implementation_time': ['mean', 'std'],
        'predicted_time_no_ai': ['mean', 'std'],
        'predicted_time_ai_allowed': ['mean', 'std']
    }).round(2)
    
    dev_stats.columns = ['_'.join(col).strip() for col in dev_stats.columns]
    dev_stats = dev_stats.reset_index()
    
    print("Developer statistics summary:")
    print(dev_stats.to_string(index=False))
    
    # Developer efficiency analysis
    df['total_time'] = df['initial_implementation_time'] + df['post_review_implementation_time'].fillna(0)
    df['efficiency_ratio'] = df['total_time'] / df['predicted_time_no_ai']
    
    dev_efficiency = df.groupby('dev_id').agg({
        'efficiency_ratio': ['mean', 'std'],
        'ai_treatment': 'count'
    }).round(3)
    
    dev_efficiency.columns = ['_'.join(col).strip() for col in dev_efficiency.columns]
    dev_efficiency = dev_efficiency.reset_index()
    
    print(f"\nDeveloper efficiency (actual/predicted time ratio):")
    print(dev_efficiency.to_string(index=False))

def prediction_accuracy_analysis(df):
    """Analyze prediction accuracy."""
    print("\n" + "="*60)
    print("PREDICTION ACCURACY ANALYSIS")
    print("="*60)
    
    # Calculate total time
    df['total_time'] = df['initial_implementation_time'] + df['post_review_implementation_time'].fillna(0)
    
    # Prediction accuracy metrics
    df['prediction_error_no_ai'] = df['total_time'] - df['predicted_time_no_ai']
    df['prediction_error_ai'] = df['total_time'] - df['predicted_time_ai_allowed']
    df['prediction_accuracy_no_ai'] = np.abs(df['prediction_error_no_ai']) / df['predicted_time_no_ai']
    df['prediction_accuracy_ai'] = np.abs(df['prediction_error_ai']) / df['predicted_time_ai_allowed']
    
    print("Prediction accuracy summary:")
    print(f"Mean absolute prediction error (no AI): {df['prediction_error_no_ai'].abs().mean():.2f} minutes")
    print(f"Mean absolute prediction error (with AI): {df['prediction_error_ai'].abs().mean():.2f} minutes")
    print(f"Mean prediction accuracy (no AI): {df['prediction_accuracy_no_ai'].mean():.3f}")
    print(f"Mean prediction accuracy (with AI): {df['prediction_accuracy_ai'].mean():.3f}")
    
    # By treatment group
    print(f"\nPrediction accuracy by treatment group:")
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        treatment_data = df[df['ai_treatment'] == treatment]
        
        print(f"\n{treatment_name}:")
        print(f"  Mean prediction error: {treatment_data['prediction_error_no_ai'].mean():.2f} minutes")
        print(f"  Mean prediction accuracy: {treatment_data['prediction_accuracy_no_ai'].mean():.3f}")

def create_summary_report(df):
    """Create a comprehensive summary report."""
    print("\n" + "="*60)
    print("COMPREHENSIVE SUMMARY REPORT")
    print("="*60)
    
    # Key findings
    ai_allowed = df[df['ai_treatment'] == 1]  # AI was used
    ai_disallowed = df[df['ai_treatment'] == 0]  # AI was not allowed
    
    # Calculate total times
    df['total_time'] = df['initial_implementation_time'] + df['post_review_implementation_time'].fillna(0)
    
    print("\nKEY FINDINGS:")
    print(f"• Dataset contains {len(df)} issues from {df['dev_id'].nunique()} developers")
    print(f"• AI was used on {len(ai_allowed)} issues and not allowed on {len(ai_disallowed)} issues")
    print(f"• Missing data: {df['post_review_implementation_time'].isnull().sum()} post-review times ({df['post_review_implementation_time'].isnull().sum()/len(df)*100:.1f}%)")
    
    # Treatment effect summary
    ai_allowed_mean = ai_allowed['total_time'].mean()
    ai_disallowed_mean = ai_disallowed['total_time'].mean()
    effect_size = (ai_allowed_mean / ai_disallowed_mean - 1) * 100
    
    print(f"\nTREATMENT EFFECT:")
    print(f"• AI Used: {ai_allowed_mean:.1f} minutes (mean total time)")
    print(f"• AI Not Allowed: {ai_disallowed_mean:.1f} minutes (mean total time)")
    print(f"• Effect: {effect_size:+.1f}% (positive = slower with AI)")
    
    # Statistical significance
    t_stat, p_value = stats.ttest_ind(ai_allowed['total_time'], ai_disallowed['total_time'])
    print(f"• Statistical significance: p = {p_value:.6f} {'(significant)' if p_value < 0.05 else '(not significant)'}")
    
    print(f"\nCONCLUSION:")
    if effect_size > 0:
        print(f"• Developers appear to be {effect_size:.1f}% slower when using AI")
        print(f"• This suggests AI may be hindering productivity in this context")
    else:
        print(f"• Developers appear to be {abs(effect_size):.1f}% faster when using AI")
        print(f"• This suggests AI may be improving productivity in this context")

def main():
    """Main analysis function."""
    print("Measuring Early-2025 AI on Experienced OSS Devs - Data Analysis")
    print("="*80)
    
    # Load data
    df = load_and_prepare_data('data_complete.csv')
    
    # Run analyses
    basic_statistics(df)
    missing_data_analysis(df)
    treatment_effect_analysis(df)
    developer_analysis(df)
    prediction_accuracy_analysis(df)
    create_summary_report(df)
    
    print("\n" + "="*80)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
