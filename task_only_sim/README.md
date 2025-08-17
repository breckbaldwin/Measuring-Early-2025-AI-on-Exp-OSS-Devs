# Simple Task Performance Simulation

## Overview

This simplified simulation abstracts from everything except **task performance** and focuses on `initial_implementation_time` for the two AI treatment conditions with heteroskedastic variance.

## Purpose

The goal is to create a **minimal, focused simulation** that captures the core empirical patterns:
1. **AI treatment effect**: AI slows down developers by ~28.6 minutes
2. **Heteroskedastic variance**: AI enabled group has higher variance than AI disabled group

## Core Model

The simulation uses a simple linear model:

```
initial_implementation_time = baseline + treatment_effect + error
```

Where:
- **`baseline`**: 90 minutes (AI disabled condition)
- **`treatment_effect`**: +28.6 minutes if AI enabled
- **`error`**: Random noise with different variance by treatment group

## Key Features

### 1. **Simplified Structure**
- No developer heterogeneity
- No task complexity effects
- No learning curves or temporal effects
- Pure focus on treatment effect and variance structure

### 2. **Heteroskedastic Error**
- **AI Disabled (0)**: Base error variance
- **AI Enabled (1)**: Base error variance × 1.3 (heteroskedastic factor)

### 3. **Treatment Assignment**
- Matches observed data distribution: 110 AI disabled, 136 AI enabled
- Random assignment within the total sample

## Files

- **`simple_task_simulation.py`**: Main simulation script
- **`simple_simulation_data.csv`**: Generated simulation data
- **`simple_simulation_results.png`**: Visualization plots
- **`README.md`**: This documentation file

## Usage

```bash
cd task_only_sim
python3 simple_task_simulation.py
```

## Expected Output

The simulation should reproduce:
- **Treatment effect**: ~28.6 minutes (AI enabled slower)
- **Variance ratio**: ~1.75 (AI enabled has higher variance)
- **Sample sizes**: 110 AI disabled, 136 AI enabled

## Advantages of Simplified Approach

1. **Clear causal structure**: Easy to understand the treatment effect
2. **Focused analysis**: Isolates the key patterns of interest
3. **Reproducible results**: Simple model, stable outcomes
4. **Easy modification**: Can easily adjust parameters
5. **Fast execution**: No complex calculations or data processing

## Comparison with Full DGP

| Aspect | Full DGP | Simple Simulation |
|--------|----------|-------------------|
| **Developer effects** | ✅ Random effects model | ❌ No individual differences |
| **Task complexity** | ✅ Multi-factor model | ❌ No complexity effects |
| **Treatment effect** | ✅ Reproduces observed | ✅ Reproduces observed |
| **Variance structure** | ✅ Heteroskedastic | ✅ Heteroskedastic |
| **Complexity** | 🔴 High | 🟢 Low |
| **Interpretability** | 🔴 Complex | 🟢 Simple |
| **Modification ease** | 🔴 Difficult | 🟢 Easy |

## Use Cases

This simplified simulation is ideal for:
- **Understanding the core treatment effect**
- **Teaching basic simulation concepts**
- **Quick parameter sensitivity analysis**
- **Baseline comparison for more complex models**
- **Demonstrating heteroskedastic error structures**

## Future Enhancements

While keeping it simple, potential additions could include:
- **Parameter sensitivity analysis**
- **Different error distributions**
- **Alternative treatment effect specifications**
- **Bootstrap confidence intervals**
- **Power analysis for different sample sizes**
