# Simple Task Simulation with PlotNine

## Overview

This is the **PlotNine version** of the simple task performance simulation. It provides the same functionality as `simple_task_simulation.py` but uses PlotNine (ggplot2-style) for all visualizations instead of matplotlib.

## Key Differences from Matplotlib Version

### **Visualization Engine**
- **Original**: Uses matplotlib/seaborn for plotting
- **PlotNine Version**: Uses PlotNine (ggplot2-style) for all visualizations

### **Plot Output**
- **Original**: Single combined plot saved as `simple_simulation_results.png`
- **PlotNine Version**: 4 individual plots saved separately:
  - `simple_simulation_results_plotnine_1_treatment_effect.png`
  - `simple_simulation_results_plotnine_2_distribution.png`
  - `simple_simulation_results_plotnine_3_boxplot.png`
  - `simple_simulation_results_plotnine_4_variance.png`

### **Code Structure**
- **Class Name**: `SimpleTaskSimulationPlotNine` (vs `SimpleTaskSimulation`)
- **Plotting Method**: `plot_results()` uses PlotNine syntax
- **Theme**: Uses `theme_minimal()` for clean, professional appearance

## PlotNine Advantages

### **1. Cleaner Syntax**
```python
# PlotNine (declarative)
p1 = (ggplot(data, aes(x='Treatment', y='Mean_Time', fill='Source')) +
      geom_col(position='dodge', alpha=0.8) +
      labs(title='Treatment Effect Comparison') +
      theme(legend_position='top'))

# Matplotlib (imperative)
fig, ax = plt.subplots()
ax.bar(x - width/2, synthetic_means, width, label='Simulated')
ax.set_title('Treatment Effect Comparison')
ax.legend()
```

### **2. Better Defaults**
- **Professional appearance** out of the box
- **Consistent styling** across all plots
- **Better color schemes** and typography
- **Automatic legend positioning** and formatting

### **3. Modular Design**
- **Each plot is a separate object** that can be easily modified
- **Easy to combine plots** using PlotNine's composition features
- **Simple to save individual plots** or create multi-panel layouts

## Files Generated

### **Data Files**
- `simple_simulation_data_plotnine.csv` - Generated simulation data (246 tasks)

### **Visualization Files**
- `simple_simulation_results_plotnine_1_treatment_effect.png` - Treatment effect comparison
- `simple_simulation_results_plotnine_2_distribution.png` - Time distribution by treatment
- `simple_simulation_results_plotnine_3_boxplot.png` - Box plot comparison
- `simple_simulation_results_plotnine_4_variance.png` - Variance comparison

## Usage

### **Prerequisites**
```bash
pip3 install plotnine
```

### **Run Simulation**
```bash
python3 simple_task_simulation_plotnine.py
```

### **Expected Output**
The simulation will:
1. Generate 246 tasks with AI treatment assignments
2. Create implementation times using the DGP
3. Analyze results and compare with observed data
4. Generate 4 PlotNine plots and save them individually
5. Run 100 simulations for stability analysis
6. Save the generated data to CSV

## Plot Descriptions

### **1. Treatment Effect Comparison**
- **Purpose**: Compare simulated vs observed treatment effects
- **Type**: Grouped bar chart
- **X-axis**: AI Treatment (Disabled/Enabled)
- **Y-axis**: Mean Implementation Time (minutes)
- **Groups**: Simulated vs Observed data

### **2. Time Distribution by Treatment**
- **Purpose**: Show distribution of implementation times by treatment
- **Type**: Histogram with overlay
- **X-axis**: Implementation Time (minutes)
- **Y-axis**: Frequency
- **Fill**: Treatment group (AI Disabled/Enabled)

### **3. Box Plot Comparison**
- **Purpose**: Compare central tendency and spread by treatment
- **Type**: Box plot
- **X-axis**: Treatment Group
- **Y-axis**: Implementation Time (minutes)
- **Shows**: Median, quartiles, outliers

### **4. Variance Comparison**
- **Purpose**: Compare variance between treatment groups
- **Type**: Grouped bar chart
- **X-axis**: AI Treatment (Disabled/Enabled)
- **Y-axis**: Variance (minutes²)
- **Groups**: Simulated vs Observed data

## Technical Details

### **Dependencies**
- **plotnine**: Main plotting library (ggplot2-style)
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scipy**: Statistical functions

### **PlotNine Theme**
```python
theme_set(theme_minimal())  # Clean, professional appearance
```

### **Plot Saving**
```python
# Individual plot saving with high quality
p1.save('plot_1.png', dpi=300, width=8, height=6)
```

## Comparison with Original Version

| Feature | Original (Matplotlib) | PlotNine Version |
|---------|----------------------|------------------|
| **Plotting Engine** | matplotlib/seaborn | PlotNine |
| **Output Format** | Single combined plot | 4 individual plots |
| **Code Style** | Imperative | Declarative |
| **Default Appearance** | Basic | Professional |
| **Modification Ease** | Moderate | High |
| **Theme Consistency** | Manual | Automatic |
| **File Size** | ~332 KB | ~762 KB total |

## Benefits of PlotNine Version

1. **Professional Appearance**: Better-looking plots out of the box
2. **Easier Modification**: Simple to change colors, themes, layouts
3. **Individual Plots**: Can use plots separately in presentations/papers
4. **Consistent Styling**: Unified theme across all visualizations
5. **Modern Syntax**: ggplot2-style syntax familiar to R users
6. **Better Defaults**: Automatic legend positioning, color schemes

## Future Enhancements

### **Potential PlotNine Features**
- **Facet plots**: Split visualizations by additional variables
- **Custom themes**: Create project-specific styling
- **Interactive plots**: Integration with plotly for web display
- **Publication-ready plots**: High-quality output for papers
- **Color palettes**: Custom color schemes for different audiences

## Conclusion

The PlotNine version provides the same simulation functionality with significantly improved visualizations. The declarative plotting syntax makes it easier to modify and customize plots, while the professional default appearance ensures publication-ready quality.

This version is ideal for:
- **Research presentations** requiring high-quality plots
- **Publications** needing professional visualizations
- **Teaching** where plot aesthetics matter
- **Collaboration** with R users familiar with ggplot2
