// Simple AI Treatment Model with Lognormal Distribution
// Models initial_implementation_time as a function of AI treatment
// using lognormal distribution instead of heteroskedastic normal

data {
  int<lower=0> N;                    // Number of tasks
  array[N] int<lower=0, upper=1> ai_treatment;  // AI treatment (0=disabled, 1=enabled)
  array[N] real<lower=0> initial_time;     // Implementation time in minutes
}

parameters {
  real<lower=0> baseline_time;       // Baseline time when AI is disabled
  real ai_treatment_effect;          // Treatment effect (can be positive or negative)
  real<lower=0> base_error_std;      // Base error standard deviation (on log scale)
  real<lower=1> heteroskedastic_factor;  // Multiplier for AI group variance (on log scale)
}

model {
  // Priors - weakly informative
  baseline_time ~ normal(90, 30);    // Prior centered around observed mean
  ai_treatment_effect ~ normal(0, 20);  // Prior for treatment effect
  base_error_std ~ normal(0.5, 0.2);   // Prior for log-scale error std
  heteroskedastic_factor ~ normal(1.2, 0.2);  // Prior for variance multiplier
  
  // Likelihood - lognormal model
  for (n in 1:N) {
    real mu = log(baseline_time + ai_treatment[n] * ai_treatment_effect);
    real sigma = base_error_std;
    
    if (ai_treatment[n] == 1) {
      sigma *= heteroskedastic_factor;  // AI enabled gets higher variance on log scale
    }
    
    initial_time[n] ~ lognormal(mu, sigma);
  }
}

generated quantities {
  // Posterior predictive samples
  array[N] real<lower=0> y_pred;
  real<lower=0> baseline_pred;
  real<lower=0> ai_enabled_pred;
  
  // Treatment effect in minutes
  real treatment_effect_minutes = ai_treatment_effect;
  
  // Variance ratio (AI enabled / AI disabled) on original scale
  // For lognormal, variance = exp(2*mu + sigma^2) * (exp(sigma^2) - 1)
  real variance_ratio = (exp(2 * log(baseline_time + ai_treatment_effect) + 
                           (base_error_std * heteroskedastic_factor)^2) * 
                          (exp((base_error_std * heteroskedastic_factor)^2) - 1)) /
                        (exp(2 * log(baseline_time)) * (exp(base_error_std^2) - 1));
  
  // Generate predictions
  for (n in 1:N) {
    real mu = log(baseline_time + ai_treatment[n] * ai_treatment_effect);
    real sigma = base_error_std;
    
    if (ai_treatment[n] == 1) {
      sigma *= heteroskedastic_factor;
    }
    
    y_pred[n] = lognormal_rng(mu, sigma);
  }
  
  // Generate predictions for each treatment group
  baseline_pred = lognormal_rng(log(baseline_time), base_error_std);
  ai_enabled_pred = lognormal_rng(log(baseline_time + ai_treatment_effect), 
                                 base_error_std * heteroskedastic_factor);
}
