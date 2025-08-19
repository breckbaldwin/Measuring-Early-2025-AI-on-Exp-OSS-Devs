// Partially Pooled Heteroskedastic Normal Model for AI Treatment Effects
// Models initial_implementation_time with developer-level random effects
// and heteroskedastic variance by treatment group

data {
  int<lower=0> N;                    // Number of tasks
  int<lower=0> N_dev;                // Number of developers
  array[N] int<lower=0, upper=1> ai_treatment;  // AI treatment (0=disabled, 1=enabled)
  array[N] real<lower=0> initial_time;     // Implementation time in minutes
  array[N] int<lower=1, upper=N_dev> dev_id;  // Developer ID for each task
}

parameters {
  real<lower=0> baseline_time;       // Baseline time when AI is disabled
  real ai_treatment_effect;          // Treatment effect (can be positive or negative)
  real<lower=0> base_error_std;      // Base error standard deviation
  
  // Developer-level random effects
  array[N_dev] real dev_baseline_offset;  // Developer-specific baseline offsets
  array[N_dev] real dev_treatment_offset; // Developer-specific treatment effect offsets
  
  // Hyperparameters for random effects
  real<lower=0> dev_baseline_std;    // Standard deviation of developer baseline offsets
  real<lower=0> dev_treatment_std;   // Standard deviation of developer treatment offsets
  
  // Heteroskedastic variance structure
  real<lower=1> heteroskedastic_factor;  // Multiplier for AI group variance
}

model {
  // Priors - weakly informative
  baseline_time ~ normal(90, 30);    // Prior centered around observed mean
  ai_treatment_effect ~ normal(0, 20);  // Prior for treatment effect
  base_error_std ~ normal(60, 20);   // Prior for base error std
  
  // Developer random effect priors
  dev_baseline_std ~ normal(20, 10);     // Prior for developer baseline variation
  dev_treatment_std ~ normal(10, 5);     // Prior for developer treatment variation
  
  // Heteroskedastic factor prior
  heteroskedastic_factor ~ normal(1.3, 0.2);  // Prior for variance multiplier
  
  // Developer-level random effects
  for (d in 1:N_dev) {
    dev_baseline_offset[d] ~ normal(0, dev_baseline_std);
    dev_treatment_offset[d] ~ normal(0, dev_treatment_std);
  }
  
  // Likelihood - heteroskedastic normal with developer effects
  for (n in 1:N) {
    int dev = dev_id[n];
    real mu = baseline_time + 
              dev_baseline_offset[dev] + 
              ai_treatment[n] * (ai_treatment_effect + dev_treatment_offset[dev]);
    
    real sigma = base_error_std;
    if (ai_treatment[n] == 1) {
      sigma *= heteroskedastic_factor;  // AI enabled gets higher variance
    }
    
    initial_time[n] ~ normal(mu, sigma);
  }
}

generated quantities {
  // Posterior predictive samples
  array[N] real<lower=0> y_pred;
  real<lower=0> baseline_pred;
  real<lower=0> ai_enabled_pred;
  
  // Treatment effect in minutes (including developer variation)
  real treatment_effect_minutes = ai_treatment_effect;
  
  // Developer-level treatment effects
  array[N_dev] real dev_treatment_effects;
  for (d in 1:N_dev) {
    dev_treatment_effects[d] = ai_treatment_effect + dev_treatment_offset[d];
  }
  
  // Variance ratio (AI enabled / AI disabled)
  real variance_ratio = heteroskedastic_factor^2;
  
  // Overall variance components
  real total_baseline_variance = base_error_std^2 + dev_baseline_std^2;
  real total_treatment_variance = base_error_std^2 * heteroskedastic_factor^2 + 
                                 dev_treatment_std^2;
  
  // Generate predictions
  for (n in 1:N) {
    int dev = dev_id[n];
    real mu = baseline_time + 
              dev_baseline_offset[dev] + 
              ai_treatment[n] * (ai_treatment_effect + dev_treatment_offset[dev]);
    
    real sigma = base_error_std;
    if (ai_treatment[n] == 1) {
      sigma *= heteroskedastic_factor;
    }
    
    y_pred[n] = normal_rng(mu, sigma);
  }
  
  // Generate predictions for each treatment group (averaging over developers)
  baseline_pred = normal_rng(baseline_time, sqrt(base_error_std^2 + dev_baseline_std^2));
  ai_enabled_pred = normal_rng(baseline_time + ai_treatment_effect, 
                               sqrt((base_error_std * heteroskedastic_factor)^2 + 
                                    dev_baseline_std^2 + dev_treatment_std^2));
}
