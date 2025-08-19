# Task-Only AI Treatment Simulation

This folder contains a simplified simulation focusing only on task performance and heteroskedastic variance for `initial_implementation_time` across AI treatment conditions.

## Overview

The simulation abstracts from everything except:
1. **Initial implementation time** across AI treatment conditions
2. **Heteroskedastic variance** structure
3. **Core treatment effects** without complex developer heterogeneity

## File Structure

### **Core Simulation Files**
- **`simple_task_simulation.py`** - Main simulation script (matplotlib version)
- **`simple_task_simulation_plotnine.py`** - PlotNine visualization version
- **`simple_simulation_data.csv`** - Generated simulation data
- **`simple_simulation_results.png`** - Combined visualization plots

### **PlotNine Version**
- **`simple_simulation_data_plotnine.csv`** - PlotNine simulation data
- **`simple_simulation_results_plotnine_*.png`** - Individual PlotNine plots
- **`README_PLOTNINE.md`** - Documentation for PlotNine version

### **Stan Model Implementation**
- **`stan/`** - Directory containing all Stan-related files
  - Stan model specification and data files
  - Data generation scripts
  - Comprehensive documentation
  - See `stan/README.md` for details

### **Documentation**
- **`SIMULATION_SUMMARY.md`** - Complete memorialization of simulation creation
- **`README_PLOTNINE.md`** - PlotNine version documentation
- **`stan/README.md`** - Stan model documentation

## Quick Start

### **1. Run Basic Simulation**
```bash
python3 simple_task_simulation.py
```

### **2. Run PlotNine Version**
```bash
python3 simple_task_simulation_plotnine.py
```

### **3. Run Stan Model**
```bash
cd stan
python3 generate_stan_data.py
# Then follow stan/README.md for Stan execution
```

## Model Structure

### **Core DGP**
```
initial_implementation_time = baseline + treatment_effect + error
```

Where:
- **baseline**: Base time when AI is disabled (~90 minutes)
- **treatment_effect**: AI treatment effect (~28.6 minutes, positive = slower)
- **error**: Random error with heteroskedastic variance
  - AI disabled: ~60 minutes std
  - AI enabled: ~78 minutes std (1.3x higher variance)

### **Parameters**
- **Sample size**: 246 tasks
- **Treatment distribution**: 110 AI disabled, 136 AI enabled
- **Heteroskedastic factor**: 1.3 (AI group gets higher variance)

## Key Results

### **Treatment Effects**
- **AI Disabled**: Mean = 90.1, SD = 58.6 minutes
- **AI Enabled**: Mean = 121.9, SD = 72.4 minutes
- **Treatment Effect**: 31.8 minutes (AI slows down implementation)
- **Variance Ratio**: 1.53 (AI group has higher variance)

### **Validation**
- **Parameter Recovery**: Successfully recovers true simulation parameters
- **Variance Structure**: Captures observed heteroskedastic patterns
- **Treatment Effects**: Matches empirical observations from real data

## Visualization

### **Matplotlib Version**
- Single combined plot with 4 subplots
- Treatment comparison, distribution, box plots, variance analysis

### **PlotNine Version**
- 4 individual high-quality plots
- Professional appearance with `theme_minimal()`
- Publication-ready visualizations

### **Stan Analysis**
- Bayesian parameter estimation
- Posterior predictive samples
- Uncertainty quantification

## Dependencies

- **Python 3**: Core simulation and data generation
- **NumPy**: Numerical operations and random sampling
- **Pandas**: Data manipulation and CSV output
- **Matplotlib**: Basic plotting (matplotlib version)
- **PlotNine**: Advanced plotting (PlotNine version)
- **CmdStan**: Stan model execution (Stan version)

## Use Cases

1. **Research**: Validate treatment effect hypotheses
2. **Teaching**: Demonstrate heteroskedastic variance concepts
3. **Methodology**: Compare frequentist vs Bayesian approaches
4. **Extension**: Foundation for more complex models

## Future Enhancements

- **Hierarchical Structure**: Add developer-level random effects
- **Covariates**: Include task complexity, developer experience
- **Temporal Effects**: Model learning curves over time
- **Multiple Outcomes**: Extend to other performance metrics
