#!/usr/bin/env python3
"""
Simple Task Performance Simulation

This simulation abstracts from everything except task performance and focuses on
initial_implementation_time for the two AI treatment conditions with heteroskedastic variance.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class SimpleTaskSimulation:
    """
    Simplified simulation focusing only on task performance and heteroskedastic variance.
    
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
        Create plots to visualize simulation results.
        
        Args:
            df: Simulation results DataFrame
            save_path: Optional path to save plots
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Simple Task Performance Simulation Results', fontsize=16)
        
        # 1. Treatment effect comparison
        ax1 = axes[0, 0]
        synthetic_means = df.groupby('ai_treatment')['initial_implementation_time'].mean()
        observed_means = [self.observed_params['ai_disabled_mean'], 
                         self.observed_params['ai_enabled_mean']]
        
        x = np.arange(2)
        width = 0.35
        
        ax1.bar(x - width/2, synthetic_means.values, width, label='Simulated', alpha=0.8)
        ax1.bar(x + width/2, observed_means, width, label='Observed', alpha=0.8)
        ax1.set_xlabel('AI Treatment')
        ax1.set_ylabel('Mean Implementation Time (minutes)')
        ax1.set_title('Treatment Effect Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(['AI Disabled', 'AI Enabled'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Time distribution by treatment
        ax2 = axes[0, 1]
        for treatment in [0, 1]:
            treatment_name = "AI Disabled" if treatment == 0 else "AI Enabled"
            treatment_data = df[df['ai_treatment'] == treatment]['initial_implementation_time']
            ax2.hist(treatment_data, alpha=0.7, label=f'{treatment_name}', bins=20)
        
        ax2.set_xlabel('Implementation Time (minutes)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Time Distribution by Treatment')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Box plot comparison
        ax3 = axes[1, 0]
        treatment_data = [df[df['ai_treatment'] == 0]['initial_implementation_time'], 
                         df[df['ai_treatment'] == 1]['initial_implementation_time']]
        ax3.boxplot(treatment_data, labels=['AI Disabled', 'AI Enabled'])
        ax3.set_ylabel('Implementation Time (minutes)')
        ax3.set_title('Box Plot Comparison')
        ax3.grid(True, alpha=0.3)
        
        # 4. Variance comparison
        ax4 = axes[1, 1]
        variances = [df[df['ai_treatment'] == 0]['initial_implementation_time'].var(),
                    df[df['ai_treatment'] == 1]['initial_implementation_time'].var()]
        observed_variances = [self.observed_params['ai_disabled_std']**2,
                             self.observed_params['ai_enabled_std']**2]
        
        x = np.arange(2)
        width = 0.35
        
        ax4.bar(x - width/2, variances, width, label='Simulated', alpha=0.8)
        ax4.bar(x + width/2, observed_variances, width, label='Observed', alpha=0.8)
        ax4.set_xlabel('AI Treatment')
        ax4.set_ylabel('Variance (minutes²)')
        ax4.set_title('Variance Comparison')
        ax4.set_xticks(x)
        ax4.set_xticklabels(['AI Disabled', 'AI Enabled'])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
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
    """Main function to run the simple simulation."""
    print("Simple Task Performance Simulation")
    print("=" * 50)
    
    # Initialize simulation
    sim = SimpleTaskSimulation(n_tasks=246, seed=42)
    
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
    print("\nCreating plots...")
    sim.plot_results(df, 'simple_simulation_results.png')
    
    # Run multiple simulations
    print("\nRunning multiple simulations...")
    sim_results = sim.run_multiple_simulations(n_simulations=100)
    
    print(f"Mean treatment effect: {sim_results['mean_treatment_effect']:.2f} ± {sim_results['std_treatment_effect']:.2f}")
    print(f"Mean variance ratio: {sim_results['mean_variance_ratio']:.2f} ± {sim_results['std_variance_ratio']:.2f}")
    print(f"Mean effect error: {sim_results['mean_effect_error']:.2f} ± {sim_results['std_effect_error']:.2f}")
    print(f"Mean variance error: {sim_results['mean_variance_error']:.2f} ± {sim_results['std_variance_error']:.2f}")
    
    # Save results
    output_file = 'simple_simulation_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSimulation data saved to: {output_file}")
    
    print("\nSimple simulation complete!")

if __name__ == "__main__":
    main()
