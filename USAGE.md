# Nassau Candy Distributor - Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Workflow](#detailed-workflow)
3. [Dashboard Guide](#dashboard-guide)
4. [Interpreting Results](#interpreting-results)
5. [Advanced Usage](#advanced-usage)

---

## Quick Start

### For First-Time Users

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your CSV in data/raw/ directory
# File: C:\Users\abina\Downloads\Nassau Candy Distributor.csv

# 3. Run the complete pipeline
python run_pipeline.py --csv "C:\Users\abina\Downloads\Nassau Candy Distributor.csv"

# 4. Launch dashboard
streamlit run dashboard/app.py

# 5. Open http://localhost:8501 in browser
```

---

## Detailed Workflow

### Phase 1: Data Processing

```python
from src.data_processing import DataProcessor

# Initialize processor
processor = DataProcessor(r"C:\Users\abina\Downloads\Nassau Candy Distributor.csv")

# Load and process data
processor.load_data()
processor.display_data_info()  # View initial data
processor.validate_and_clean()  # Clean and standardize
processor.feature_engineering()  # Add calculated features
processor.generate_summary_report()  # View statistics
processor.save_processed_data()  # Save to processed_orders.csv
```

**Output**: `data/processed/processed_orders.csv`

### Phase 2: Feature Engineering

```python
from src.feature_engineering import FeatureEngineer

# Initialize engineer
engineer = FeatureEngineer()

# Generate all metrics
results = engineer.run_full_feature_engineering()

# Access specific metrics
route_metrics = results['route_metrics']
top_routes = results['top_routes']
bottlenecks = results['bottlenecks']
```

**Outputs**:
- `route_metrics.csv` - All routes with KPIs
- `top_10_routes.csv` - Best performers
- `bottom_10_routes.csv` - Underperformers
- `bottleneck_analysis.csv` - Geographic bottlenecks
- `regional_metrics.csv` - Region-level analysis
- `shipmode_metrics.csv` - Shipping mode comparison
- `factory_route_matrix.csv` - Factory performance
- `state_performance.csv` - State-level metrics

### Phase 3: Advanced Analysis

```python
from src.analysis import AdvancedAnalysis

# Initialize analyzer
analyzer = AdvancedAnalysis()

# Run complete analysis
results = analyzer.run_full_analysis()

# Access results
anomalies = results['anomalies']  # Unusual shipments
bottlenecks = results['bottlenecks']  # Critical issues
delays = results['delay_patterns']  # Delay analysis
recommendations = results['recommendations']  # Actionable insights
```

**Outputs**:
- `anomalies_detected.csv` - Unusual patterns
- `critical_bottlenecks.csv` - High-priority issues
- `factory_performance.csv` - Factory comparison
- `executive_summary.txt` - Report with recommendations

---

## Dashboard Guide

### Overview Page

**Purpose**: High-level performance metrics

**Key Visualizations**:
- KPI cards (Avg Lead Time, Total Routes, Excellent %)
- Efficiency score distribution histogram
- Route classification pie chart
- Lead time vs volume scatter plot

**How to Use**:
1. Filter by efficiency class (Excellent/Good/Poor)
2. Filter by volume class (Low/Medium/High)
3. View top 20 routes in leaderboard
4. Identify performance trends

### Geographic Analysis Page

**Purpose**: Regional and state performance

**Key Visualizations**:
- Regional lead time bar chart
- Regional delay rate comparison
- US state heatmap (efficiency by state)
- Geographic bottleneck list

**How to Use**:
1. Hover over states on heatmap for details
2. Review regional performance metrics
3. Identify high-delay regions
4. Investigate bottleneck locations

**Insights**:
- Red states = high delays
- Green states = efficient
- Larger shipment volumes appear in legend

### Ship Mode Comparison Page

**Purpose**: Compare shipping methods

**Key Visualizations**:
- Metrics table (all shipping modes)
- Average lead time comparison
- Delay rate by mode
- Cost-speed tradeoff scatter

**How to Use**:
1. Compare lead times across modes
2. Analyze cost vs speed tradeoff
3. Identify best mode for efficiency
4. Review delay patterns

**Interpretation**:
- Standard typically slower but cheaper
- Expedited typically faster but variable
- Look for consistent vs variable performance

### Drill-Down Analysis Page

**Purpose**: Detailed investigation

**Key Views**:
- Top 10 most efficient routes
- Bottom 10 least efficient routes
- Factory performance comparison
- Critical bottlenecks list

**How to Use**:
1. Review top performers for best practices
2. Investigate bottom performers for issues
3. Compare factory efficiency
4. Prioritize critical bottlenecks

**Actions**:
- Click route names to investigate
- Export data for further analysis
- Share findings with operations team

### Insights Page

**Purpose**: Executive summary and recommendations

**Contents**:
- Overall delay rate
- Critical bottleneck details
- Ship mode recommendations
- Regional improvement opportunities
- Seasonal patterns
- Anomaly warnings

**How to Use**:
1. Read key findings
2. Review top recommendations
3. Prioritize action items
4. Share with stakeholders

---

## Interpreting Results

### Route Efficiency Metrics

```
Route_ID: Lot's O' Nuts → CA
Total_Shipments: 250
Avg_Lead_Time: 4.5 days
Median_Lead_Time: 4.0 days
Std_Lead_Time: 1.2 days
On_Time_Rate: 94% ✓
Delay_Rate: 6%
Efficiency_Score: 92/100
Efficiency_Class: Excellent
Risk_Level: Low
```

**What It Means**:
- 250 shipments on this route
- Average delivery in 4.5 days (Good)
- 94% on-time delivery (Excellent)
- Very consistent performance (low std dev)
- Low risk - maintain current operations

### Bottleneck Identification

```
State: TX
Shipment_Volume: 500
Avg_Lead_Time: 8.2 days ⚠️
Std_Lead_Time: 2.8 days (High variability)
Delay_Rate: 22% 🚨
Bottleneck_Score: 68/100
Bottleneck_Level: High
```

**What It Means**:
- Texas is a high-volume region (500 shipments)
- Significantly longer lead times (8.2 vs avg 5 days)
- High variability - unpredictable delivery
- 22% of shipments delayed
- **Action**: Increase capacity, improve routing, or add hub

### Delay Pattern Analysis

```
Overall Delay Rate: 12%
By Ship Mode:
  - Standard: 15% ⚠️
  - Expedited: 8% ✓

By Region:
  - South: 18% (Worst)
  - Northeast: 8% (Best)

By Month:
  - July: 22% (Peak)
  - January: 8% (Off-season)
```

**Insights**:
1. Expedited shipping more reliable than standard
2. Southern region has service issues
3. Summer months have peak delays
4. **Recommendations**: Use expedited for South in summer, negotiate with carriers

---

## Advanced Usage

### Custom Analysis

```python
from src.feature_engineering import FeatureEngineer
import pandas as pd

# Load processed data
engineer = FeatureEngineer()
route_metrics = engineer.calculate_route_metrics()

# Filter specific region
california_routes = route_metrics[route_metrics['Route_ID'].str.contains('CA')]

# Find worst 5 routes
worst_5 = california_routes.nsmallest(5, 'Efficiency_Score')

# Export for investigation
worst_5.to_csv('california_worst_routes.csv')
```

### Batch Processing

```bash
# Process multiple files
for file in data/raw/*.csv; do
    echo "Processing: $file"
    python run_pipeline.py --csv "$file"
done
```

### Schedule Regular Updates

**Windows Task Scheduler**:
```batch
@echo off
cd C:\path\to\Nassau-candy-distributor-s-Route-analysis
python run_pipeline.py
streamlit run dashboard/app.py
```

**Linux Cron**:
```bash
0 6 * * * cd /path/to/project && python run_pipeline.py
```

---

## Performance Tips

1. **Large Datasets (>100K rows)**:
   - Use `--skip-processing` for reruns
   - Increase memory allocation
   - Consider sampling for initial analysis

2. **Dashboard Performance**:
   - Clear browser cache
   - Restart streamlit if slow
   - Use filters to limit data shown

3. **Analysis Accuracy**:
   - Ensure clean, consistent data format
   - Validate date formats match
   - Check for missing critical fields

---

## Exporting Results

### Export from Dashboard
1. Right-click chart → Save as PNG
2. Click table → Download CSV
3. Screenshot metrics cards

### Export Programmatically
```python
route_metrics.to_excel('route_analysis.xlsx')
route_metrics.to_json('route_analysis.json')
route_metrics.to_html('route_analysis.html')
```

### Generate Reports
```python
from src.analysis import AdvancedAnalysis

analyzer = AdvancedAnalysis()
results = analyzer.run_full_analysis()

# Get executive summary
summary = results['executive_summary']
with open('report.txt', 'w') as f:
    f.write(summary)
```

---

**For more help, check README.md or open an issue on GitHub!** 🚀
