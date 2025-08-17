#!/usr/bin/env python3
"""
Simple Task Performance Simulation using PlotNine

This simulation abstracts from everything except task performance and focuses on
initial_implementation_time for the two AI treatment conditions with heteroskedastic variance.
Uses PlotNine (ggplot2-style) for all visualizations.
"""

import numpy as np
import pandas as pd
from plotnine import *
from plotnine.data import *
import warnings
warnings.filterwarnings('ignore')

# Set PlotNine theme
theme_set(theme_minimal())

class SimpleTaskSimulationPlotNine:
    """
    Simplified simulation focusing only on task performance and heteroskedastic variance.
    Uses PlotNine for all visualizations.
    
    Core model: initial_implementation_time = baseline + treatment_effect + error
    Where error has different variance for AI enabled vs disabled groups.
    """
    
    def __init__(self, n_tasks: int = 246, seed: int = 42):
        """
        Initialize the simple simulation.
        
        Args:
            n_tasks: Number of tasks to simulate
            seed: Random seed for reproducibility
        """
        self.n_tasks = n_tasks
        self.seed = seed
        np.random.seed(seed)
        
        # Observed parameters from the real data
        self.observed_params = {
            'ai_disabled_mean': 90.9,
            'ai_disabled_std': 89.4,
            'ai_enabled_mean': 119.5,
            'ai_enabled_std': 118.1,
            'treatment_effect': 119.5 - 90.9,  # 28.6 minutes
            'n_ai_disabled': 110,
            'n_ai_enabled': 136
        }
        
        # Simulation parameters
        self.sim_params = {
            'baseline_time': 90.0,  # Baseline time (AI disabled)
            'ai_treatment_effect': 28.6,  # AI slows down by this amount
            'base_error_std': 60.0,  # Base error standard deviation
            'heteroskedastic_factor': 1.3  # AI group gets higher variance
        }
    
    def generate_treatments(self) -> np.ndarray:
        """
        Generate AI treatment assignments matching the observed distribution.
        
        Returns:
            Array of AI treatment assignments (0 = disabled, 1 = enabled)
        """
        # Generate treatments to match observed counts
        treatments = np.concatenate([
            np.zeros(self.observed_params['n_ai_disabled']),  # AI disabled
            np.ones(self.observed_params['n_ai_enabled'])     # AI enabled
        ])
        
        # Shuffle to randomize order
        np.random.shuffle(treatments)
        return treatments
    
    def generate_implementation_times(self, treatments: np.ndarray) -> np.ndarray:
        """
        Generate initial implementation times using the simple model.
        
        Args:
            treatments: Array of AI treatment assignments
            
        Returns:
            Array of generated implementation times
        """
        times = np.zeros(self.n_tasks)
        
        for i in range(self.n_tasks):
            ai_treatment = treatments[i]
            
            # Base time
            base_time = self.sim_params['baseline_time']
            
            # AI treatment effect (positive = slower with AI)
            ai_effect = ai_treatment * self.sim_params['ai_treatment_effect']
            
            # Random error (heteroskedastic by treatment)
            error_std = self.sim_params['base_error_std']
            if ai_treatment == 1:  # AI enabled gets higher variance
                error_std *= self.sim_params['heteroskedastic_factor']
            
            error = np.random.normal(0, error_std)
            
            # Combine effects
            time = base_time + ai_effect + error
            
            # Ensure non-negative times
            times[i] = max(5, time)
        
        return times
    
    def run_simulation(self) -> pd.DataFrame:
        """
        Run the complete simulation.
        
        Returns:
            DataFrame with simulation results
        """
        # Generate treatments
        treatments = self.generate_treatments()
        
        # Generate implementation times
        times = self.generate_implementation_times(treatments)
        
        # Create DataFrame
        df = pd.DataFrame({
            'task_id': range(1, self.n_tasks + 1),
            'ai_treatment': treatments,
            'initial_implementation_time': times
        })
        
        # Add treatment labels for plotting
        df['treatment_label'] = df['ai_treatment'].map({0: 'AI Disabled', 1: 'AI Enabled'})
        
        return df
    
    def analyze_results(self, df: pd.DataFrame) -> dict:
        """
        Analyze simulation results and compare with observed data.
        
        Args:
            df: Simulation results DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        results = {}
        
        # Treatment group sizes
        treatment_counts = df['ai_treatment'].value_counts().sort_index()
        results['treatment_counts'] = treatment_counts.to_dict()
        
        # Implementation time statistics by treatment
        time_stats = df.groupby('ai_treatment')['initial_implementation_time'].describe()
        results['time_statistics'] = time_stats.to_dict()
        
        # Treatment effect
        ai_disabled_mean = df[df['ai_treatment'] == 0]['initial_implementation_time'].mean()
        ai_enabled_mean = df[df['ai_treatment'] == 1]['initial_implementation_time'].mean()
        treatment_effect = ai_enabled_mean - ai_disabled_mean
        results['treatment_effect'] = treatment_effect
        
        # Variance analysis
        ai_disabled_var = df[df['ai_treatment'] == 0]['initial_implementation_time'].var()
        ai_enabled_var = df[df['ai_treatment'] == 1]['initial_implementation_time'].var()
        variance_ratio = ai_enabled_var / ai_disabled_var
        results['variance_ratio'] = variance_ratio
        
        # Compare with observed data
        observed_effect = self.observed_params['treatment_effect']
        effect_error = abs(treatment_effect - observed_effect)
        results['effect_error'] = effect_error
        results['effect_accuracy'] = 1 - (effect_error / observed_effect)
        
        # Observed variance ratio for comparison
        observed_var_ratio = (self.observed_params['ai_enabled_std'] ** 2) / (self.observed_params['ai_disabled_std'] ** 2)
        results['observed_variance_ratio'] = observed_var_ratio
        results['variance_accuracy'] = 1 - abs(variance_ratio - observed_var_ratio) / observed_var_ratio
        
        return results
    
    def plot_results(self, df: pd.DataFrame, save_path: str = None):
        """
        Create plots to visualize simulation results using PlotNine.
        
        Args:
            df: Simulation results DataFrame
            save_path: Optional path to save plots
        """
        # 1. Treatment effect comparison
        synthetic_means = df.groupby('treatment_label')['initial_implementation_time'].mean()
        comparison_data = pd.DataFrame({
            'Treatment': ['AI Disabled', 'AI Enabled'],
            'Mean_Time': [synthetic_means['AI Disabled'], synthetic_means['AI Enabled']],
            'Source': ['Simulated', 'Simulated']
        })
        
        # Add observed data for comparison
        observed_data = pd.DataFrame({
            'Treatment': ['AI Disabled', 'AI Enabled'],
            'Mean_Time': [self.observed_params['ai_disabled_mean'], 
                         self.observed_params['ai_enabled_mean']],
            'Source': ['Observed', 'Observed']
        })
        
        # Combine data
        plot_data = pd.concat([comparison_data, observed_data], ignore_index=True)
        
        p1 = (ggplot(plot_data, aes(x='Treatment', y='Mean_Time', fill='Source')) +
              geom_col(position='dodge', alpha=0.8) +
              labs(title='Treatment Effect Comparison',
                   x='AI Treatment',
                   y='Mean Implementation Time (minutes)',
                   fill='Data Source') +
              theme(legend_position='top'))
        
        # 2. Time distribution by treatment
        p2 = (ggplot(df, aes(x='initial_implementation_time', fill='treatment_label')) +
              geom_histogram(alpha=0.7, bins=20, position='identity') +
              labs(title='Time Distribution by Treatment',
                   x='Implementation Time (minutes)',
                   y='Frequency',
                   fill='Treatment') +
              theme(legend_position='top'))
        
        # 3. Box plot comparison
        p3 = (ggplot(df, aes(x='treatment_label', y='initial_implementation_time', fill='treatment_label')) +
              geom_boxplot(alpha=0.8) +
              labs(title='Box Plot Comparison',
                   x='Treatment Group',
                   y='Implementation Time (minutes)',
                   fill='Treatment') +
              theme(legend_position='none'))
        
        # 4. Variance comparison
        variances = [df[df['ai_treatment'] == 0]['initial_implementation_time'].var(),
                    df[df['ai_treatment'] == 1]['initial_implementation_time'].var()]
        observed_variances = [self.observed_params['ai_disabled_std']**2,
                             self.observed_params['ai_enabled_std']**2]
        
        variance_data = pd.DataFrame({
            'Treatment': ['AI Disabled', 'AI Enabled', 'AI Disabled', 'AI Enabled'],
            'Variance': variances + observed_variances,
            'Source': ['Simulated', 'Simulated', 'Observed', 'Observed']
        })
        
        p4 = (ggplot(variance_data, aes(x='Treatment', y='Variance', fill='Source')) +
              geom_col(position='dodge', alpha=0.8) +
              labs(title='Variance Comparison',
                   x='AI Treatment',
                   y='Variance (minutes²)',
                   fill='Data Source') +
              theme(legend_position='top'))
        
        # Save plots individually
        if save_path:
            base_path = save_path.replace('.png', '')
            p1.save(f'{base_path}_1_treatment_effect.png', dpi=300, width=8, height=6)
            p2.save(f'{base_path}_2_distribution.png', dpi=300, width=8, height=6)
            p3.save(f'{base_path}_3_boxplot.png', dpi=300, width=8, height=6)
            p4.save(f'{base_path}_4_variance.png', dpi=300, width=8, height=6)
            print(f"Plots saved as: {base_path}_1_treatment_effect.png, {base_path}_2_distribution.png, {base_path}_3_boxplot.png, {base_path}_4_variance.png")
        
        # Display plots
        print("Displaying plots...")
        print("\n1. Treatment Effect Comparison:")
        print(p1)
        print("\n2. Time Distribution by Treatment:")
        print(p2)
        print("\n3. Box Plot Comparison:")
        print(p3)
        print("\n4. Variance Comparison:")
        print(p4)
    
    def run_multiple_simulations(self, n_simulations: int = 100) -> dict:
        """
        Run multiple simulations to assess stability.
        
        Args:
            n_simulations: Number of simulations to run
            
        Returns:
            Dictionary with simulation results
        """
        treatment_effects = []
        variance_ratios = []
        effect_errors = []
        variance_errors = []
        
        for i in range(n_simulations):
            # Set seed for reproducibility but vary it
            np.random.seed(self.seed + i)
            
            # Run simulation
            df = self.run_simulation()
            
            # Analyze results
            results = self.analyze_results(df)
            
            treatment_effects.append(results['treatment_effect'])
            variance_ratios.append(results['variance_ratio'])
            effect_errors.append(results['effect_error'])
            variance_errors.append(abs(results['variance_ratio'] - results['observed_variance_ratio']))
        
        sim_results = {
            'mean_treatment_effect': np.mean(treatment_effects),
            'std_treatment_effect': np.std(treatment_effects),
            'mean_variance_ratio': np.mean(variance_ratios),
            'std_variance_ratio': np.std(variance_ratios),
            'mean_effect_error': np.mean(effect_errors),
            'std_effect_error': np.std(effect_errors),
            'mean_variance_error': np.mean(variance_errors),
            'std_variance_error': np.std(variance_errors),
            'treatment_effects': treatment_effects,
            'variance_ratios': variance_ratios
        }
        
        return sim_results

def main():
    """Main function to run the simple simulation with PlotNine."""
    print("Simple Task Performance Simulation using PlotNine")
    print("=" * 60)
    
    # Initialize simulation
    sim = SimpleTaskSimulationPlotNine(n_tasks=246, seed=42)
    
    # Run single simulation
    print("Running simulation...")
    df = sim.run_simulation()
    
    print(f"Generated {len(df)} tasks")
    print(f"AI treatment distribution: {df['ai_treatment'].value_counts().sort_index().to_dict()}")
    
    # Analyze results
    print("\nAnalyzing results...")
    results = sim.analyze_results(df)
    
    print(f"Treatment effect: {results['treatment_effect']:.2f} minutes")
    print(f"Observed effect: {sim.observed_params['treatment_effect']:.2f} minutes")
    print(f"Effect accuracy: {results['effect_accuracy']:.1%}")
    print(f"Variance ratio: {results['variance_ratio']:.2f}")
    print(f"Observed variance ratio: {results['observed_variance_ratio']:.2f}")
    print(f"Variance accuracy: {results['variance_accuracy']:.1%}")
    
    # Create plots
    print("\nCreating plots using PlotNine...")
    sim.plot_results(df, 'simple_simulation_results_plotnine.png')
    
    # Run multiple simulations
    print("\nRunning multiple simulations...")
    sim_results = sim.run_multiple_simulations(n_simulations=100)
    
    print(f"Mean treatment effect: {sim_results['mean_treatment_effect']:.2f} ± {sim_results['std_treatment_effect']:.2f}")
    print(f"Mean variance ratio: {sim_results['mean_variance_ratio']:.2f} ± {sim_results['std_variance_ratio']:.2f}")
    print(f"Mean effect error: {sim_results['mean_effect_error']:.2f} ± {sim_results['std_effect_error']:.2f}")
    print(f"Mean variance error: {sim_results['mean_variance_error']:.2f} ± {sim_results['std_variance_error']:.2f}")
    
    # Save results
    output_file = 'simple_simulation_data_plotnine.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSimulation data saved to: {output_file}")
    
    print("\nSimple simulation with PlotNine complete!")

if __name__ == "__main__":
    main()
