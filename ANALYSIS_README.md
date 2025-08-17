# Measuring Early-2025 AI on Experienced OSS Devs - Analysis Guide

This document provides a comprehensive guide to analyzing the data from the study "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity."

## Project Overview

The study examines whether AI tools improve or hinder developer productivity by randomly assigning AI access to experienced open-source developers working on real issues. The dataset contains 246 issues from 16 developers, with detailed timing information and developer predictions.

## Data Structure

The `data_complete.csv` file contains the following columns:

- **`dev_id`**: Unique developer identifier (16 unique developers)
- **`issue_id`**: Unique issue identifier (246 issues)
- **`predicted_time_no_ai`**: Developer's estimate of time without AI (minutes)
- **`predicted_time_ai_allowed`**: Developer's estimate of time with AI (minutes)
- **`prior_task_exposure_1_to_5`**: Developer familiarity with task type (1-5 scale)
- **`external_resource_needs_1_to_3`**: Expected external resource needs (1-3 scale)
- **`ai_treatment`**: Treatment assignment (0 = AI allowed, 1 = AI disallowed)
- **`initial_implementation_time`**: Time to create pull request (minutes)
- **`post_review_implementation_time`**: Time to address review comments (minutes)

## Key Findings

### Main Result
- **AI Treatment Effect**: Developers are **25.1% faster** when using AI
- **Statistical Significance**: p = 0.026 (significant at α = 0.05)
- **Effect Size**: Cohen's d = -0.287 (moderate effect)

### Treatment Group Comparison
- **AI Allowed (n=110)**: Mean total time = 100.0 minutes
- **AI Disallowed (n=136)**: Mean total time = 133.5 minutes
- **Difference**: 33.5 minutes (25.1% improvement)

### Missing Data
- **Post-review time**: 16 missing values (6.5%)
- **Task exposure & resource needs**: 87 missing values (35.4%) - collected halfway through study

## Analysis Scripts

### 1. `regression.py` - Core Regression Analysis
The original regression script that replicates the paper's main results:
```bash
python3 regression.py --input-data data_complete.csv
```

**Output**: Treatment effect estimate and confidence intervals with different standard error specifications.

### 2. `data_analysis.py` - Comprehensive Data Analysis
Provides detailed exploratory data analysis:
```bash
python3 data_analysis.py
```

**Features**:
- Basic statistics and summary metrics
- Missing data analysis
- Treatment effect analysis with effect sizes
- Developer-level analysis
- Prediction accuracy analysis
- Comprehensive summary report

### 3. `visualization.py` - Data Visualizations
Creates four comprehensive visualization sets:
```bash
python3 visualization.py
```

**Generated Charts**:
- `treatment_comparison.png`: Treatment effect visualizations
- `developer_analysis.png`: Developer-level patterns
- `prediction_analysis.png`: Prediction accuracy analysis
- `summary_statistics.png`: Key metrics and significance

## Analysis Results

### Treatment Effect Analysis
- **T-test**: t = -2.236, p = 0.026 (significant)
- **Mann-Whitney U**: U = 6546.5, p = 0.093 (not significant)
- **Effect Size**: Cohen's d = -0.287 (moderate effect)

### Developer Efficiency
- **Efficiency Ratio**: Actual time / Predicted time
- **Range**: 0.679 to 1.760 across developers
- **Pattern**: Most developers show improved efficiency with AI

### Prediction Accuracy
- **Mean Prediction Error**: -6.19 minutes (AI allowed) vs 17.44 minutes (AI disallowed)
- **Prediction Accuracy**: 0.463 (AI allowed) vs 0.585 (AI disallowed)
- **Insight**: Developers are more accurate in predicting AI-assisted completion times

## Statistical Notes

### Multiple Testing
The study uses multiple statistical tests. While the parametric t-test shows significance (p = 0.026), the non-parametric Mann-Whitney U test does not (p = 0.093). This suggests the effect may be sensitive to distributional assumptions.

### Effect Size Interpretation
Cohen's d = -0.287 indicates a moderate effect size, suggesting the AI treatment has a meaningful impact on developer productivity.

### Missing Data Handling
The analysis imputes missing post-review times using treatment group means, which is the approach used in the original paper.

## Recommendations for Further Analysis

### 1. Subgroup Analysis
- Analyze effects by developer experience level
- Examine effects by task complexity (predicted time ranges)
- Investigate effects by prior task exposure

### 2. Robustness Checks
- Test different imputation methods for missing data
- Analyze effects excluding outliers
- Examine treatment effect heterogeneity across developers

### 3. Additional Metrics
- Analyze code quality measures if available
- Examine review comment patterns
- Investigate developer satisfaction or perceived productivity

## Dependencies

Required Python packages:
```bash
pip install pandas numpy statsmodels scipy matplotlib seaborn
```

## File Structure

```
Measuring-Early-2025-AI-on-Exp-OSS-Devs/
├── data_complete.csv          # Main dataset
├── regression.py              # Original regression analysis
├── data_analysis.py           # Comprehensive data analysis
├── visualization.py            # Data visualization script
├── ANALYSIS_README.md         # This analysis guide
├── README.md                  # Original project README
└── Generated visualizations:
    ├── treatment_comparison.png
    ├── developer_analysis.png
    ├── prediction_analysis.png
    └── summary_statistics.png
```

## Conclusion

The analysis confirms the paper's main finding: AI tools appear to significantly improve developer productivity in this context, with developers completing tasks approximately 25% faster when AI access is allowed. The effect is statistically significant and represents a meaningful improvement in development efficiency.

However, the sensitivity of results to statistical test choice suggests the need for careful interpretation and potential follow-up studies to confirm these findings in different contexts.

## References

- Original Paper: [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://arxiv.org/abs/2507.09089)
- Study Announcement: [METR Blog Post](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- Dataset: `data_complete.csv` (246 issues, 16 developers)
