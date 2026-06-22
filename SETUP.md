# Nassau Candy Distributor - Quick Start Guide

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/Abinash-002/Nassau-candy-distributor-s-Route-analysis.git
cd Nassau-candy-distributor-s-Route-analysis
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Prepare Your Data
1. Place your CSV file in the `data/raw/` directory
2. Or specify the path when running the pipeline

Expected columns in your CSV:
- Order ID, Row ID
- Order Date, Ship Date
- Ship Mode (Standard, Expedited, etc.)
- Customer Location (Country, Region, State/Province, City)
- Sales, Units, Cost, Gross Profit
- Product Name, Division

---

## 📊 Running the Pipeline

### Option 1: Full Pipeline (Recommended)
```bash
# Auto-detect CSV from data/raw/
python run_pipeline.py

# Or specify CSV path
python run_pipeline.py --csv "C:\Users\abina\Downloads\Nassau Candy Distributor.csv"
```

### Option 2: Skip Already Processed Data
```bash
# Use existing processed data
python run_pipeline.py --skip-processing
```

### Option 3: Analysis Only
```bash
# Run only analysis (skip data processing & feature engineering)
python run_pipeline.py --analysis-only
```

---

## 🎨 Launch Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Dashboard Pages:
1. **Overview** - Route efficiency metrics and performance
2. **Geographic Analysis** - Regional and state-level performance with US heatmap
3. **Ship Mode Comparison** - Shipping method performance analysis
4. **Drill-Down** - Top/bottom routes and factory performance
5. **Insights** - Executive summary and recommendations

---

## 📁 Output Files

After running the pipeline, check `data/outputs/` for:

### Metrics Files
- `route_metrics.csv` - Comprehensive route performance data
- `regional_metrics.csv` - Regional performance analysis
- `shipmode_metrics.csv` - Ship mode comparison
- `state_performance.csv` - State-level KPIs
- `factory_performance.csv` - Factory-level analysis
- `factory_route_matrix.csv` - Factory-region performance matrix

### Analysis Files
- `top_10_routes.csv` - Best performing routes
- `bottom_10_routes.csv` - Routes needing improvement
- `critical_bottlenecks.csv` - Identified operational bottlenecks
- `anomalies_detected.csv` - Unusual shipment patterns
- `bottleneck_analysis.csv` - Detailed bottleneck metrics

### Reports
- `executive_summary.txt` - Key findings and recommendations

---

## 📊 Data Processing Pipeline

### Stage 1: Data Cleaning
- ✓ Validate date formats (Order Date < Ship Date)
- ✓ Remove duplicates and invalid records
- ✓ Handle missing values in critical fields
- ✓ Standardize state codes and text fields
- ✓ Convert numeric fields and validate ranges

### Stage 2: Feature Engineering
- ✓ Calculate shipping lead times
- ✓ Map products to origin factories
- ✓ Create route identifiers (Factory → State)
- ✓ Categorize lead times (Fast/Normal/Slow/Very Slow)
- ✓ Extract temporal features (month, quarter, day of week)
- ✓ Mark delayed shipments
- ✓ Calculate profit margins

### Stage 3: Analysis
- ✓ Route efficiency scoring (0-100)
- ✓ Regional performance analysis
- ✓ Ship mode comparison
- ✓ Delay pattern detection
- ✓ Bottleneck identification
- ✓ Anomaly detection (Isolation Forest)
- ✓ Factory performance comparison
- ✓ Temporal pattern analysis

---

## 🔍 Key Metrics Explained

### Efficiency Score (0-100)
- **90-100**: Excellent - Fast delivery, high consistency
- **70-89**: Good - Acceptable performance
- **Below 70**: Poor - Needs improvement

### Lead Time Categories
- **Fast**: ≤ 3 days
- **Normal**: 4-7 days
- **Slow**: 8-14 days
- **Very Slow**: > 14 days

### Bottleneck Levels
- **Critical**: High volume + high delays + high variability
- **High**: Medium-High volume with performance issues
- **Medium**: Performance concerns in specific dimensions
- **Low**: Acceptable performance

### On-Time Delivery
- **On-Time**: Delivered within 7 days (configurable)
- **Delayed**: Delivered after 7 days

---

## 🛠️ Customization

### Edit Configuration (config.yaml)

Modify thresholds and settings:
```yaml
thresholds:
  delay_days: 7                    # Days for on-time delivery
  acceptable_lead_time: 5          # Target lead time
  high_volume_threshold: 100       # Volume for bottleneck identification
  efficiency_score_good: 85        # Good efficiency score threshold
  efficiency_score_acceptable: 70  # Acceptable efficiency threshold
```

### Adjust Anomaly Detection
Edit in `src/analysis.py`:
```python
anomalies = analyzer.detect_anomalies(contamination=0.05)  # 5% contamination
```

---

## 📈 Example Workflow

```bash
# 1. Place CSV in data/raw/ or use full path

# 2. Run full pipeline
python run_pipeline.py --csv "C:\Users\abina\Downloads\Nassau Candy Distributor.csv"

# 3. Review executive summary in terminal output

# 4. Launch dashboard
streamlit run dashboard/app.py

# 5. Explore interactive visualizations
# 6. Export insights for stakeholders
```

---

## ❓ Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### CSV file not found
Specify full path:
```bash
python run_pipeline.py --csv "C:\full\path\to\file.csv"
```

### Dashboard won't load
```bash
# Reinstall streamlit
pip install --upgrade streamlit
streamlit run dashboard/app.py
```

### Memory issues with large datasets
Process in chunks or use skip options:
```bash
python run_pipeline.py --skip-processing --analysis-only
```

---

## 📞 Support

For issues or questions:
1. Check the README.md for project overview
2. Review generated reports in `data/outputs/`
3. Check logs in terminal output
4. Open a GitHub issue

---

## 📚 Documentation Files

- **README.md** - Project overview and architecture
- **SETUP.md** - Installation and configuration guide (this file)
- **src/utils.py** - Utility functions reference
- **notebooks/01_eda.ipynb** - Exploratory data analysis
- **reports/executive_summary.md** - Key findings template

---

**Happy Analyzing! 🚀📊**
