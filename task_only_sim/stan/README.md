# Stan Model Directory

This directory contains Stan models for analyzing AI treatment effects on task performance, including both non-pooled and partially pooled approaches.

## Contents

### **Model Files**
- **`simple_heteroskedastic.stan`** - Non-pooled heteroskedastic normal model
- **`simple_lognormal.stan`** - Non-pooled lognormal model
- **`simple_heteroskedastic_partial_pool.stan`** - Partially pooled heteroskedastic normal model
- **`simple_lognormal_partial_pool.stan`** - Partially pooled lognormal model

### **Data Files**
- **`simple_ai_treatment.json`** - Data file for non-pooled models
- **`partial_pool_data.json`** - Data file for partially pooled models (includes developer IDs)

### **Scripts**
- **`generate_stan_data.py`** - Generate simulation data for Stan analysis
- **`run_stan_on_experimental_data.py`** - Run non-pooled models on experimental data
- **`compare_models.py`** - Compare non-pooled heteroskedastic normal vs lognormal models
- **`prepare_partial_pool_data.py`** - Prepare data for partially pooled models
- **`compare_all_models.py`** - Comprehensive comparison of all four models

### **Documentation**
- **`STAN_MODEL_SUMMARY.md`** - Summary of non-pooled Stan implementation and results
- **`EXPERIMENTAL_DATA_ANALYSIS.md`** - Analysis of experimental data results
- **`README.md`** - This file

## Model Architecture Comparison

### **Non-Pooled Models**
- **Distribution**: Normal or lognormal with heteroskedastic variance
- **Structure**: Single baseline + treatment effect for all observations
- **Use Case**: When developer heterogeneity is not a primary concern

### **Partially Pooled Models**
- **Distribution**: Same as non-pooled but with developer-level random effects
- **Structure**: 
  - Global baseline + treatment effect
  - Developer-specific baseline offsets
  - Developer-specific treatment effect offsets
- **Use Case**: When developer heterogeneity is important and should be modeled

## Model Comparison

### **Heteroskedastic Normal Models**
- **Distribution**: Normal with different variances by treatment group
- **Parameters**: baseline_time, ai_treatment_effect, base_error_std, heteroskedastic_factor
- **Variance Structure**: AI enabled group gets higher error variance
- **Use Case**: Additive treatment effects with heteroskedastic errors

### **Lognormal Models**
- **Distribution**: Lognormal with different log-scale variances by treatment group
- **Parameters**: Same as heteroskedastic model but on log scale
- **Variance Structure**: Multiplicative treatment effects with log-scale heteroskedasticity
- **Use Case**: Multiplicative treatment effects or right-skewed data

## Quick Start

### **1. Prepare Data**
```bash
cd stan
python3 prepare_partial_pool_data.py
```

### **2. Build All Stan Models**
```bash
cd /Users/bb/git/others/cmdstan
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_heteroskedastic
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_lognormal
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_heteroskedastic_partial_pool
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_lognormal_partial_pool
```

### **3. Run Comprehensive Comparison**
```bash
cd /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan
python3 compare_all_models.py
```

### **4. Individual Model Analysis**
```bash
# Non-pooled models
python3 compare_models.py

# Partially pooled models only
python3 prepare_partial_pool_data.py
# Then run individual models manually
```

### **5. Analyze Results**
```bash
cd /Users/bb/git/others/cmdstan
bin/stansummary output_simple_heteroskedastic.csv
bin/stansummary output_simple_lognormal.csv
bin/stansummary output_simple_heteroskedastic_partial_pool.csv
bin/stansummary output_simple_lognormal_partial_pool.csv
```

## Model Overview

### **Non-Pooled Models**
Both implement AI treatment analysis with different distributional assumptions:

#### **Heteroskedastic Normal**
- **Likelihood**: `initial_time ~ normal(mu, sigma)`
- **Mean**: `mu = baseline_time + ai_treatment * ai_treatment_effect`
- **Variance**: `sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`

#### **Lognormal**
- **Likelihood**: `initial_time ~ lognormal(log_mu, log_sigma)`
- **Log Mean**: `log_mu = log(baseline_time + ai_treatment * ai_treatment_effect)`
- **Log Variance**: `log_sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`

### **Partially Pooled Models**
Extend non-pooled models with developer-level random effects:

#### **Partially Pooled Heteroskedastic Normal**
- **Likelihood**: `initial_time ~ normal(mu, sigma)`
- **Mean**: `mu = baseline_time + dev_baseline_offset[dev] + ai_treatment * (ai_treatment_effect + dev_treatment_offset[dev])`
- **Variance**: `sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`
- **Random Effects**: `dev_baseline_offset[dev] ~ normal(0, dev_baseline_std)`, `dev_treatment_offset[dev] ~ normal(0, dev_treatment_std)`

#### **Partially Pooled Lognormal**
- **Likelihood**: `initial_time ~ lognormal(log_mu, log_sigma)`
- **Log Mean**: `log_mu = log(baseline_time + dev_baseline_offset[dev] + ai_treatment * (ai_treatment_effect + dev_treatment_offset[dev]))`
- **Log Variance**: `log_sigma = base_error_std * heteroskedastic_factor^(ai_treatment)`
- **Random Effects**: Same structure as normal model

## Data Structure

### **Non-Pooled Models**
- **N**: Number of tasks (246 for experimental data)
- **ai_treatment**: Binary treatment assignment (0=disabled, 1=enabled)
- **initial_time**: Implementation time in minutes

### **Partially Pooled Models**
- **N**: Number of tasks (246 for experimental data)
- **N_dev**: Number of unique developers
- **ai_treatment**: Binary treatment assignment (0=disabled, 1=enabled)
- **initial_time**: Implementation time in minutes
- **dev_id**: Developer ID for each task (1-indexed)

## Results

### **Experimental Data Results**
- **Treatment Effect**: ~20-30 minutes (AI increases implementation time)
- **Variance Ratio**: ~1.9 (AI enabled has higher variance)
- **Model Fit**: All models show excellent convergence (R_hat = 1.00)

### **Model Comparison Results**
- **Non-pooled**: Heteroskedastic normal better matches observed data patterns
- **Partially pooled**: Capture developer heterogeneity and individual treatment effects
- **Trade-offs**: Partially pooled models more complex but richer inference

## Dependencies

- **CmdStan**: Stan command-line interface
- **Python**: For data generation and analysis
- **NumPy/Pandas**: For data manipulation
- **CmdStanPy**: For Stan model execution (optional)

## Use Cases

1. **Model Comparison**: Compare normal vs lognormal assumptions
2. **Treatment Effect Analysis**: Quantify AI treatment effects with uncertainty
3. **Variance Structure**: Understand heteroskedastic patterns
4. **Developer Heterogeneity**: Model individual developer differences
5. **Simulation Validation**: Test model assumptions with simulated data
6. **Experimental Analysis**: Analyze real field experiment data

## Model Selection Guide

### **Choose Non-Pooled When:**
- Developer heterogeneity is minimal
- Focus is on overall treatment effects
- Computational efficiency is important
- Simpler interpretation is preferred

### **Choose Partially Pooled When:**
- Developer heterogeneity is substantial
- Individual developer effects are of interest
- More nuanced treatment effect analysis is needed
- Hierarchical structure is theoretically justified

### **Choose Normal When:**
- Additive treatment effects are expected
- Data is approximately symmetric
- Variance structure is additive

### **Choose Lognormal When:**
- Multiplicative treatment effects are expected
- Data is right-skewed
- Log-scale variance structure is preferred

## Future Enhancements

- **Full Hierarchical Structure**: Add task-level random effects
- **Covariates**: Include task complexity, developer experience
- **Temporal Effects**: Model learning curves over time
- **Multiple Outcomes**: Extend to other performance metrics
- **Model Selection**: Implement formal model comparison criteria (WAIC, LOO-CV)
- **Cross-validation**: Implement k-fold cross-validation for model comparison

