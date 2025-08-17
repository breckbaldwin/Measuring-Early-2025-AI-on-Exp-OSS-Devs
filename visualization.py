#!/usr/bin/env python3
"""
Visualization script for Measuring Early-2025 AI on Experienced OSS Devs

This script creates various charts and graphs to visualize the data patterns
and treatment effects from the study.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_prepare_data(filepath):
    """Load and prepare the data for visualization."""
    df = pd.read_csv(filepath)
    
    # Add total time column
    df['total_time'] = df['initial_implementation_time'] + df['post_review_implementation_time'].fillna(0)
    
    # Add treatment labels
    df['treatment_label'] = df['ai_treatment'].map({0: 'AI Not Allowed', 1: 'AI Used'})
    
    return df

def plot_treatment_comparison(df):
    """Create comparison plots for AI treatment groups."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('AI Treatment Effect Analysis', fontsize=16, fontweight='bold')
    
    # 1. Total time distribution
    ax1 = axes[0, 0]
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        treatment_data = df[df['ai_treatment'] == treatment]['total_time']
        ax1.hist(treatment_data, alpha=0.7, label=treatment_name, bins=20)
    
    ax1.set_xlabel('Total Implementation Time (minutes)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Total Implementation Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Box plot comparison
    ax2 = axes[0, 1]
    treatment_data = [df[df['ai_treatment'] == 0]['total_time'], 
                     df[df['ai_treatment'] == 1]['total_time']]
    ax2.boxplot(treatment_data, labels=['AI Not Allowed', 'AI Used'])
    ax2.set_ylabel('Total Implementation Time (minutes)')
    ax2.set_title('Box Plot Comparison')
    ax2.grid(True, alpha=0.3)
    
    # 3. Initial vs Post-review time scatter
    ax3 = axes[1, 0]
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        treatment_data = df[df['ai_treatment'] == treatment]
        ax3.scatter(treatment_data['initial_implementation_time'], 
                   treatment_data['post_review_implementation_time'],
                   alpha=0.6, label=treatment_name)
    
    ax3.set_xlabel('Initial Implementation Time (minutes)')
    ax3.set_ylabel('Post-Review Implementation Time (minutes)')
    ax3.set_title('Initial vs Post-Review Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Time comparison bar chart
    ax4 = axes[1, 1]
    ai_allowed = df[df['ai_treatment'] == 1]  # AI was used
    ai_disallowed = df[df['ai_treatment'] == 0]  # AI was not allowed
    
    categories = ['Initial Time', 'Post-Review Time', 'Total Time']
    ai_allowed_means = [
        ai_allowed['initial_implementation_time'].mean(),
        ai_allowed['post_review_implementation_time'].mean(),
        ai_allowed['total_time'].mean()
    ]
    ai_disallowed_means = [
        ai_disallowed['initial_implementation_time'].mean(),
        ai_disallowed['post_review_implementation_time'].mean(),
        ai_disallowed['total_time'].mean()
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax4.bar(x - width/2, ai_allowed_means, width, label='AI Used', alpha=0.8)
    ax4.bar(x + width/2, ai_disallowed_means, width, label='AI Not Allowed', alpha=0.8)
    
    ax4.set_xlabel('Time Category')
    ax4.set_ylabel('Time (minutes)')
    ax4.set_title('Mean Time by Category and Treatment')
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('treatment_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_developer_analysis(df):
    """Create developer-level analysis plots."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Developer-Level Analysis', fontsize=16, fontweight='bold')
    
    # 1. Developer efficiency by treatment
    ax1 = axes[0, 0]
    df['efficiency_ratio'] = df['total_time'] / df['predicted_time_no_ai']
    
    dev_efficiency = df.groupby(['dev_id', 'treatment_label'])['efficiency_ratio'].mean().unstack()
    dev_efficiency.plot(kind='bar', ax=ax1, alpha=0.8)
    ax1.set_xlabel('Developer ID')
    ax1.set_ylabel('Efficiency Ratio (Actual/Predicted)')
    ax1.set_title('Developer Efficiency by Treatment')
    ax1.legend(title='Treatment')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # 2. Developer workload distribution
    ax2 = axes[0, 1]
    dev_workload = df['dev_id'].value_counts().sort_index()
    ax2.bar(dev_workload.index, dev_workload.values, alpha=0.8, color='skyblue')
    ax2.set_xlabel('Developer ID')
    ax2.set_ylabel('Number of Issues')
    ax2.set_title('Workload Distribution Across Developers')
    ax2.grid(True, alpha=0.3)
    
    # 3. Treatment assignment by developer
    ax3 = axes[1, 0]
    treatment_by_dev = df.groupby(['dev_id', 'treatment_label']).size().unstack(fill_value=0)
    treatment_by_dev.plot(kind='bar', stacked=True, ax=ax3, alpha=0.8)
    ax3.set_xlabel('Developer ID')
    ax3.set_ylabel('Number of Issues')
    ax3.set_title('Treatment Assignment by Developer')
    ax3.legend(title='Treatment')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Developer performance scatter
    ax4 = axes[1, 1]
    dev_performance = df.groupby('dev_id').agg({
        'total_time': 'mean',
        'efficiency_ratio': 'mean',
        'ai_treatment': 'mean'
    }).reset_index()
    
    scatter = ax4.scatter(dev_performance['total_time'], 
                          dev_performance['efficiency_ratio'],
                          c=dev_performance['ai_treatment'], 
                          s=100, alpha=0.7, cmap='viridis')
    ax4.set_xlabel('Mean Total Time (minutes)')
    ax4.set_ylabel('Mean Efficiency Ratio')
    ax4.set_title('Developer Performance: Time vs Efficiency')
    
    # Add developer ID labels
    for _, row in dev_performance.iterrows():
        ax4.annotate(int(row['dev_id']), 
                    (row['total_time'], row['efficiency_ratio']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.colorbar(scatter, ax=ax4, label='AI Treatment Rate')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('developer_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_prediction_analysis(df):
    """Create prediction accuracy analysis plots."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Prediction Accuracy Analysis', fontsize=16, fontweight='bold')
    
    # 1. Prediction vs Actual time scatter
    ax1 = axes[0, 0]
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        treatment_data = df[df['ai_treatment'] == treatment]
        ax1.scatter(treatment_data['predicted_time_no_ai'], 
                   treatment_data['total_time'],
                   alpha=0.6, label=treatment_name)
    
    # Add perfect prediction line
    max_val = max(df['predicted_time_no_ai'].max(), df['total_time'].max())
    ax1.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Perfect Prediction')
    
    ax1.set_xlabel('Predicted Time (minutes)')
    ax1.set_ylabel('Actual Total Time (minutes)')
    ax1.set_title('Predicted vs Actual Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Prediction error distribution
    ax2 = axes[0, 1]
    df['prediction_error'] = df['total_time'] - df['predicted_time_no_ai']
    
    for treatment in [0, 1]:
        treatment_name = "AI Not Allowed" if treatment == 0 else "AI Used"
        treatment_data = df[df['ai_treatment'] == treatment]['prediction_error']
        ax2.hist(treatment_data, alpha=0.7, label=treatment_name, bins=20)
    
    ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Perfect Prediction')
    ax2.set_xlabel('Prediction Error (minutes)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Prediction Errors')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Prediction accuracy by time range
    ax3 = axes[1, 0]
    df['time_range'] = pd.cut(df['predicted_time_no_ai'], 
                              bins=[0, 60, 120, 180, 300, 600], 
                              labels=['0-60', '60-120', '120-180', '180-300', '300+'])
    
    # Calculate absolute prediction error first
    df['abs_prediction_error'] = df['prediction_error'].abs()
    accuracy_by_range = df.groupby(['time_range', 'treatment_label'])['abs_prediction_error'].mean().unstack()
    accuracy_by_range.plot(kind='bar', ax=ax3, alpha=0.8)
    ax3.set_xlabel('Predicted Time Range (minutes)')
    ax3.set_ylabel('Mean Absolute Prediction Error (minutes)')
    ax3.set_title('Prediction Accuracy by Time Range')
    ax3.legend(title='Treatment')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Prediction bias analysis
    ax4 = axes[1, 1]
    bias_by_treatment = df.groupby('treatment_label')['prediction_error'].agg(['mean', 'std']).reset_index()
    
    x_pos = np.arange(len(bias_by_treatment))
    ax4.bar(x_pos, bias_by_treatment['mean'], 
            yerr=bias_by_treatment['std'], 
            alpha=0.8, capsize=5)
    ax4.set_xlabel('Treatment Group')
    ax4.set_ylabel('Mean Prediction Error (minutes)')
    ax4.set_title('Prediction Bias by Treatment Group')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(bias_by_treatment['treatment_label'])
    ax4.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Perfect Prediction')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('prediction_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_summary_statistics(df):
    """Create summary statistics visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Summary Statistics and Key Metrics', fontsize=16, fontweight='bold')
    
    # 1. Treatment effect summary
    ax1 = axes[0, 0]
    ai_allowed = df[df['ai_treatment'] == 1]  # AI was used
    ai_disallowed = df[df['ai_treatment'] == 0]  # AI was not allowed
    
    metrics = ['Initial Time', 'Post-Review Time', 'Total Time']
    ai_allowed_means = [
        ai_allowed['initial_implementation_time'].mean(),
        ai_allowed['post_review_implementation_time'].mean(),
        ai_allowed['total_time'].mean()
    ]
    ai_disallowed_means = [
        ai_disallowed['initial_implementation_time'].mean(),
        ai_disallowed['post_review_implementation_time'].mean(),
        ai_disallowed['total_time'].mean()
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, ai_allowed_means, width, label='AI Used', alpha=0.8)
    bars2 = ax1.bar(x + width/2, ai_disallowed_means, width, label='AI Not Allowed', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10)
    
    ax1.set_xlabel('Time Metric')
    ax1.set_ylabel('Time (minutes)')
    ax1.set_title('Treatment Effect Summary')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Missing data visualization
    ax2 = axes[0, 1]
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0]  # Only show columns with missing data
    
    if len(missing_data) > 0:
        ax2.bar(missing_data.index, missing_data.values, alpha=0.8, color='orange')
        ax2.set_xlabel('Column')
        ax2.set_ylabel('Missing Count')
        ax2.set_title('Missing Data Summary')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No Missing Data', ha='center', va='center', 
                transform=ax2.transAxes, fontsize=14)
        ax2.set_title('Missing Data Summary')
    
    # 3. Effect size visualization
    ax3 = axes[1, 0]
    effect_size = (ai_allowed['total_time'].mean() / ai_disallowed['total_time'].mean() - 1) * 100
    
    colors = ['green' if effect_size < 0 else 'red']
    ax3.bar(['AI Effect'], [abs(effect_size)], color=colors, alpha=0.8)
    ax3.set_ylabel('Effect Size (%)')
    ax3.set_title(f'AI Treatment Effect: {effect_size:+.1f}%')
    ax3.grid(True, alpha=0.3)
    
    # Add effect direction label
    direction = "faster" if effect_size < 0 else "slower"
    ax3.text(0, abs(effect_size)/2, f'Developers are\n{direction} with AI', 
             ha='center', va='center', fontweight='bold', fontsize=12)
    
    # 4. Statistical significance visualization
    ax4 = axes[1, 1]
    t_stat, p_value = stats.ttest_ind(ai_allowed['total_time'], ai_disallowed['total_time'])
    
    # Create a simple significance indicator
    significance = "Significant" if p_value < 0.05 else "Not Significant"
    color = 'green' if p_value < 0.05 else 'red'
    
    ax4.text(0.5, 0.6, f'p-value: {p_value:.6f}', ha='center', va='center', 
             transform=ax4.transAxes, fontsize=14)
    ax4.text(0.5, 0.4, f'Result: {significance}', ha='center', va='center', 
             transform=ax4.transAxes, fontsize=16, fontweight='bold', color=color)
    ax4.text(0.5, 0.2, f't-statistic: {t_stat:.3f}', ha='center', va='center', 
             transform=ax4.transAxes, fontsize=12)
    ax4.set_title('Statistical Significance')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('summary_statistics.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main visualization function."""
    print("Creating visualizations for Measuring Early-2025 AI on Experienced OSS Devs...")
    
    # Load data
    df = load_and_prepare_data('data_complete.csv')
    
    # Create visualizations
    print("1. Creating treatment comparison plots...")
    plot_treatment_comparison(df)
    
    print("2. Creating developer analysis plots...")
    plot_developer_analysis(df)
    
    print("3. Creating prediction analysis plots...")
    plot_prediction_analysis(df)
    
    print("4. Creating summary statistics plots...")
    plot_summary_statistics(df)
    
    print("\nAll visualizations completed and saved!")
    print("Generated files:")
    print("- treatment_comparison.png")
    print("- developer_analysis.png")
    print("- prediction_analysis.png")
    print("- summary_statistics.png")

if __name__ == "__main__":
    main()
