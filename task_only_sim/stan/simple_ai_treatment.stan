// Simple AI Treatment Model with Heteroskedastic Variance
// Models initial_implementation_time as a function of AI treatment
// with different error variances for AI enabled vs disabled groups

data {
  int<lower=0> N;                    // Number of tasks
  array[N] int<lower=0, upper=1> ai_treatment;  // AI treatment (0=disabled, 1=enabled)
  array[N] real<lower=0> initial_time;     // Implementation time in minutes
}

parameters {
  real<lower=0> baseline_time;       // Baseline time when AI is disabled
  real ai_treatment_effect;          // Treatment effect (can be positive or negative)
  real<lower=0> base_error_std;      // Base error standard deviation
  real<lower=1> heteroskedastic_factor;  // Multiplier for AI group variance
}

model {
  // Priors - weakly informative
  baseline_time ~ normal(90, 30);    // Prior centered around observed mean
  ai_treatment_effect ~ normal(0, 20);  // Prior for treatment effect
  base_error_std ~ normal(60, 20);   // Prior for base error std
  heteroskedastic_factor ~ normal(1.3, 0.3);  // Prior for variance multiplier
  
  // Likelihood - heteroskedastic normal model
  for (n in 1:N) {
    real mu = baseline_time + ai_treatment[n] * ai_treatment_effect;
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
  
  // Treatment effect in minutes
  real treatment_effect_minutes = ai_treatment_effect;
  
  // Variance ratio (AI enabled / AI disabled)
  real variance_ratio = heteroskedastic_factor^2;
  
  // Generate predictions
  for (n in 1:N) {
    real mu = baseline_time + ai_treatment[n] * ai_treatment_effect;
    real sigma = base_error_std;
    
    if (ai_treatment[n] == 1) {
      sigma *= heteroskedastic_factor;
    }
    
    y_pred[n] = normal_rng(mu, sigma);
    // Ensure positive times
    if (y_pred[n] < 0) y_pred[n] = 0;
  }
  
  // Generate predictions for each treatment group
  baseline_pred = normal_rng(baseline_time, base_error_std);
  if (baseline_pred < 0) baseline_pred = 0;
  
  ai_enabled_pred = normal_rng(baseline_time + ai_treatment_effect, 
                               base_error_std * heteroskedastic_factor);
  if (ai_enabled_pred < 0) ai_enabled_pred = 0;
}
