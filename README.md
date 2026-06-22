# Nassau Candy Distributor - Route Analysis & Optimization

An ML-driven logistics analytics platform analyzing shipping route efficiency, identifying bottlenecks, and optimizing nationwide delivery performance for Nassau Candy Distributor.

## 📊 Project Goals

- **Route Efficiency Analysis**: Identify fastest and slowest factory-to-customer routes
- **Delay Pattern Detection**: Find routes with consistent delays and predict delays
- **Regional Performance Mapping**: Analyze shipping performance by region, state, and ship mode
- **Bottleneck Identification**: Detect geographic and operational bottlenecks
- **Data-Driven Optimization**: Transform reactive logistics into proactive route optimization

## 📦 Data Overview

### Datasets
- **Orders Data**: 10,000+ orders with dates, shipping modes, customer locations, sales metrics
- **Factory Coordinates**: 5 distribution centers (Lot's O' Nuts, Wicked Choccy's, Sugar Shack, Secret Factory, The Other Factory)
- **Product-Factory Mapping**: 15 products across 3 divisions (Chocolate, Sugar, Other)

### Key Fields
| Field | Description |
|-------|-------------|
| Order ID | Unique order identifier |
| Order Date | Date of order placement |
| Ship Date | Date of shipment |
| Ship Mode | Shipping method (Standard, Expedited) |
| Customer Location | Country, Region, State, City, Postal Code |
| Sales Metrics | Sales, Units, Cost, Gross Profit |

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| Data Processing | Pandas, NumPy, GeoPandas |
| Analysis | Scikit-learn, SciPy, Statsmodels |
| ML Models | XGBoost, LightGBM, Isolation Forest |
| Visualization | Plotly, Folium, Matplotlib, Seaborn |
| Web Dashboard | Streamlit |
| Database | SQLite |

## 📁 Project Structure

```
Nassau-candy-distributor-s-Route-analysis/
├── data/
│   ├── raw/                      # Raw CSV files
│   ├── processed/                # Cleaned and engineered data
│   └── outputs/                  # Analysis results
├── src/
│   ├── __init__.py
│   ├── data_processing.py        # Data cleaning & validation
│   ├── feature_engineering.py    # Route definitions & KPIs
│   ├── analysis.py               # Bottleneck & efficiency analysis
│   ├── anomaly_detection.py      # Delay detection models
│   └── utils.py                  # Helper functions & constants
├── dashboard/
│   ├── __init__.py
│   ├── app.py                    # Main Streamlit application
│   ├── pages/
│   │   ├── route_efficiency.py
│   │   ├── geographic_analysis.py
│   │   ├── shipmode_comparison.py
│   │   └── drill_down.py
│   └── components.py             # Reusable dashboard components
├── notebooks/
│   ├── 01_eda.ipynb              # Exploratory Data Analysis
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_evaluation.ipynb
├── reports/
│   ├── analysis_report.md        # Key findings & recommendations
│   └── executive_summary.md      # Government stakeholder summary
├── requirements.txt
├── .gitignore
├── config.yaml                   # Configuration file
└── README.md
```

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/Abinash-002/Nassau-candy-distributor-s-Route-analysis.git
cd Nassau-candy-distributor-s-Route-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Step 1: Data Processing & Cleaning
python src/data_processing.py

# Step 2: Feature Engineering
python src/feature_engineering.py

# Step 3: Analysis
python src/analysis.py

# Step 4: Launch Streamlit Dashboard
streamlit run dashboard/app.py
```

## 📊 Key Deliverables

1. ✅ **Processed Dataset** with route definitions and KPIs
2. ✅ **Route Efficiency Rankings** (Top 10 & Bottom 10 routes)
3. ✅ **Geographic Bottleneck Analysis** with heatmaps
4. ✅ **Ship Mode Performance Comparison**
5. ✅ **Interactive Streamlit Dashboard** for stakeholder exploration
6. ✅ **Research Report** with insights and recommendations
7. ✅ **Executive Summary** for government stakeholders

## 📈 Key Metrics & KPIs

| KPI | Definition | Target |
|-----|-----------|--------|
| **Shipping Lead Time** | Ship Date - Order Date (days) | Minimize |
| **Average Lead Time** | Mean duration per route | Baseline |
| **Route Volume** | Number of orders per route | Monitor |
| **Delay Frequency** | % of shipments exceeding threshold | < 5% |
| **Route Efficiency Score** | Normalized lead-time performance (0-100) | > 85 |
| **On-Time Delivery Rate** | % delivered within SLA | > 95% |

## 🔍 Analytical Methodology

### Phase 1: Data Cleaning & Validation
- ✓ Validate date formats (Order Date < Ship Date)
- ✓ Remove invalid/negative lead times
- ✓ Handle missing shipment records
- ✓ Standardize geographic fields
- ✓ Map products to factories

### Phase 2: Feature Engineering
- ✓ Calculate shipping lead times (days)
- ✓ Define routes: Factory → Customer State/Region
- ✓ Group shipments by ship mode
- ✓ Compute variability metrics (std dev, percentiles)
- ✓ Assign efficiency scores

### Phase 3: Route Analysis
- ✓ Aggregate shipments per route
- ✓ Calculate avg/min/max lead times
- ✓ Rank routes by efficiency
- ✓ Identify top 10 & bottom 10 performers
- ✓ Analyze performance by ship mode

### Phase 4: Bottleneck Detection
- ✓ Identify high lead-time regions
- ✓ Detect congestion-prone states
- ✓ Find high-volume + poor-performance hotspots
- ✓ Compare across ship modes
- ✓ Anomaly detection for unusual delays

### Phase 5: Dashboard & Visualization
- ✓ Route efficiency leaderboard
- ✓ US heatmap of shipping efficiency
- ✓ Regional performance drill-down
- ✓ Ship mode comparisons
- ✓ Interactive filters (date, region, state, ship mode)

## 🎯 Dashboard Features

### Module 1: Route Efficiency Overview
- Average lead time by route
- Route performance leaderboard (top/bottom routes)
- Performance trends over time

### Module 2: Geographic Analysis
- US heatmap showing regional efficiency
- State-level performance breakdown
- Regional bottleneck visualization
- Factory-to-region performance matrix

### Module 3: Ship Mode Comparison
- Lead time comparison (Standard vs Expedited)
- Volume by ship mode
- Cost-time tradeoff analysis
- Performance consistency

### Module 4: Drill-Down Analysis
- State-level performance insights
- Order-level shipment timelines
- Individual route performance
- Delay pattern analysis

### Filters & Controls
- 📅 Date range selector
- 🗺️ Region/State multi-select
- 📦 Ship mode filter
- ⏱️ Lead-time threshold slider
- 🏭 Factory selector

## 🔬 ML Models & Techniques

| Task | Approach | Models |
|------|----------|--------|
| Route Efficiency | Regression | Linear Regression, XGBoost, LightGBM |
| Delay Prediction | Classification | Logistic Regression, Random Forest, XGBoost |
| Anomaly Detection | Unsupervised | Isolation Forest, DBSCAN, Autoencoders |
| Bottleneck Identification | Clustering | K-Means, DBSCAN, Hierarchical |
| Time Series Forecasting | Time Series | ARIMA, Prophet, LSTM |
| Route Optimization | Graph Optimization | Dijkstra, A*, Genetic Algorithms |

## 📋 Data Sources & Specifications

### Factory Locations
| Factory | Latitude | Longitude | Region |
|---------|----------|-----------|--------|
| Lot's O' Nuts | 32.881893 | -111.768036 | West |
| Wicked Choccy's | 32.076176 | -81.088371 | South |
| Sugar Shack | 48.11914 | -96.18115 | Midwest |
| Secret Factory | 41.446333 | -90.565487 | Midwest |
| The Other Factory | 35.1175 | -89.971107 | South |

### Product-Factory Mapping
- **Chocolate Division**: Wonka Bars (Lot's O' Nuts, Wicked Choccy's)
- **Sugar Division**: Taffy, SweeTARTS, Nerds, Fun Dip, Gobstoppers (Sugar Shack, Secret Factory)
- **Other Division**: Fizzy Drinks, Lickable Wallpaper, Wonka Gum, Kazookles (Multiple Factories)

## 📚 Next Steps

1. ✅ Upload your CSV data to `data/raw/`
2. ⏳ Run data processing pipeline (`python src/data_processing.py`)
3. ⏳ Explore EDA notebook (`notebooks/01_eda.ipynb`)
4. ⏳ Deploy Streamlit dashboard (`streamlit run dashboard/app.py`)
5. ⏳ Generate insights report (`reports/analysis_report.md`)
6. ⏳ Present executive summary to stakeholders

---

**Project Status**: 
- ✅ Project Setup Complete
- 🔄 Data Processing - In Progress
- 📊 Analysis - In Progress
- 🎨 Dashboard - In Progress
- 📝 Reporting - Pending

**Last Updated**: June 2026
**Author**: Abinash-002
