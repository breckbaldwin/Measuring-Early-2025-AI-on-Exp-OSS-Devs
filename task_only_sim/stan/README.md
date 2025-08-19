# Stan Model Directory

This directory contains all Stan-related files for the simple AI treatment analysis.

## Contents

### **Model Files**
- **`simple_ai_treatment.stan`** - Stan model specification for heteroskedastic AI treatment effects
- **`simple_ai_treatment.json`** - Data file in modern JSON format for Stan

### **Scripts**
- **`generate_stan_data.py`** - Python script to generate simulation data for Stan analysis

### **Documentation**
- **`STAN_MODEL_SUMMARY.md`** - Comprehensive summary of Stan implementation and results
- **`README.md`** - This file

## Quick Start

### **1. Generate Data**
```bash
cd stan
python3 generate_stan_data.py
```

### **2. Build Stan Model**
```bash
cd /Users/bb/git/others/cmdstan
make /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_ai_treatment
```

### **3. Run Stan Model**
```bash
cd /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan
/Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/simple_ai_treatment sample data file=simple_ai_treatment.json
```

### **4. Analyze Results**
```bash
cd /Users/bb/git/others/cmdstan
bin/stansummary /Users/bb/git/others/Measuring-Early-2025-AI-on-Exp-OSS-Devs/task_only_sim/stan/output.csv
```

## Model Overview

The Stan model implements a **heteroskedastic normal model** for AI treatment effects:

- **Baseline time**: Implementation time when AI is disabled
- **Treatment effect**: Additional time when AI is enabled
- **Heteroskedastic variance**: Different error variances for AI enabled vs disabled groups

## Data Structure

- **N**: 246 tasks
- **ai_treatment**: Binary treatment assignment (0=disabled, 1=enabled)
- **initial_time**: Implementation time in minutes

## Results

The model successfully recovers simulation parameters:
- **Baseline time**: 92.0 ± 5.6 minutes
- **Treatment effect**: 27.0 ± 8.2 minutes
- **Heteroskedastic factor**: 1.3 ± 0.11
- **Variance ratio**: 1.6 (AI enabled has higher variance)

## Dependencies

- **CmdStan**: Stan command-line interface
- **Python**: For data generation
- **NumPy/Pandas**: For data manipulation
