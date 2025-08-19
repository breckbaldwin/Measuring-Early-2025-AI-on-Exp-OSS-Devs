# Stan Model Directory

This directory contains Stan models for analyzing AI treatment effects on task performance.

## Contents

### **Model Files**
- **`simple_heteroskedastic.stan`** - Heteroskedastic normal model for AI treatment effects
- **`simple_lognormal.stan`** - Lognormal model for AI treatment effects
- **`simple_ai_treatment.json`** - Data file in modern JSON format for Stan

### **Scripts**
- **`generate_stan_data.py`** - Python script to generate simulation data for Stan analysis
- **`run_stan_on_experimental_data.py`** - Run Stan models on experimental data
- **`compare_models.py`** - Compare heteroskedastic normal vs lognormal models

### **Documentation**
- **`STAN_MODEL_SUMMARY.md`** - Comprehensive summary of Stan implementation and results
- **`EXPERIMENTAL_DATA_ANALYSIS.md`** - Analysis of experimental data results
- **`README.md`** - This file

## Model Comparison

### **Heteroskedastic Normal Model (`simple_heteroskedastic.stan`)**
- **Distribution**: Normal with different variances by treatment group
- **Parameters**: baseline_time, ai_treatment_effect, base_error_std, heteroskedastic_factor
- **Variance Structure**: AI enabled group gets higher error variance
- **Use Case**: When you expect additive treatment effects with heteroskedastic errors

### **Lognormal Model (`simple_lognormal.stan`)**
- **Distribution**: Lognormal with different log-scale variances by treatment group
- **Parameters**: Same as heteroskedastic model but on log scale
- **Variance Structure**: Multiplicative treatment effects with log-scale heteroskedasticity
- **Use Case**: When you expect multiplicative treatment effects or right-skewed data

## Quick Start

### **1. Generate Data**
```bash
cd stan
python3 generate_stan_data.py
```

### **2. Build Stan Models**
```bash
cd /Users/bb/git/others/cmdstan
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_heteroskedastic
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_lognormal
```

### **3. Run on Experimental Data**
```bash
cd /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan
python3 run_stan_on_experimental_data.py
```

### **4. Compare Both Models**
```bash
python3 compare_models.py
```

### **5. Analyze Results**
```bash
cd /Users/bb/git/others/cmdstan
bin/stansummary /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/output_simple_heteroskedastic.csv
bin/stansummary /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/output_simple_lognormal.csv
```

## Model Overview

Both models implement AI treatment analysis but with different distributional assumptions:

### **Heteroskedastic Normal**
- **Likelihood**: `initial_time ~ normal(mu, sigma)`
- **Mean**: `mu = baseline_time + ai_treatment * ai_treatment_effect`
- **Variance**: `sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`

### **Lognormal**
- **Likelihood**: `initial_time ~ lognormal(log_mu, log_sigma)`
- **Log Mean**: `log_mu = log(baseline_time + ai_treatment * ai_treatment_effect)`
- **Log Variance**: `log_sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`

## Data Structure

- **N**: Number of tasks (246 for experimental data)
- **ai_treatment**: Binary treatment assignment (0=disabled, 1=enabled)
- **initial_time**: Implementation time in minutes

## Results

### **Experimental Data Results**
- **Treatment Effect**: ~20-30 minutes (AI increases implementation time)
- **Variance Ratio**: ~1.9 (AI enabled has higher variance)
- **Model Fit**: Both models show excellent convergence (R_hat = 1.00)

### **Simulation Results**
- **Parameter Recovery**: Excellent recovery of true simulation parameters
- **Treatment Effect**: ~27 minutes (close to true value of 28.6)
- **Variance Structure**: Good recovery of heteroskedastic patterns

## Dependencies

- **CmdStan**: Stan command-line interface
- **Python**: For data generation and analysis
- **NumPy/Pandas**: For data manipulation
- **CmdStanPy**: For Stan model execution (optional)

## Use Cases

1. **Model Comparison**: Compare normal vs lognormal assumptions
2. **Treatment Effect Analysis**: Quantify AI treatment effects with uncertainty
3. **Variance Structure**: Understand heteroskedastic patterns
4. **Simulation Validation**: Test model assumptions with simulated data
5. **Experimental Analysis**: Analyze real field experiment data

## Future Enhancements

- **Hierarchical Structure**: Add developer-level random effects
- **Covariates**: Include task complexity, developer experience
- **Temporal Effects**: Model learning curves over time
- **Multiple Outcomes**: Extend to other performance metrics
- **Model Selection**: Implement formal model comparison criteria
