"""
Utility functions and constants for Nassau Candy Distributor Route Analysis
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "outputs"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Path = CONFIG_FILE) -> Dict:
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise


# Load configuration
CONFIG = load_config()

# Factory Information
FACTORIES = {factory['name']: factory for factory in CONFIG.get('factories', [])}
FACTORY_COORDS = {
    factory['name']: (factory['latitude'], factory['longitude'])
    for factory in CONFIG.get('factories', [])
}
FACTORY_REGIONS = {
    factory['name']: factory['region']
    for factory in CONFIG.get('factories', [])
}

# Product-Factory Mapping
PRODUCT_FACTORY_MAP = {}
for division, products in CONFIG.get('products', {}).items():
    for product in products:
        PRODUCT_FACTORY_MAP[product['name']] = product['factory']

# Ship Modes
SHIP_MODES = CONFIG.get('ship_modes', [])

# Performance Thresholds
THRESHOLDS = CONFIG.get('thresholds', {})
DELAY_DAYS = THRESHOLDS.get('delay_days', 7)
ACCEPTABLE_LEAD_TIME = THRESHOLDS.get('acceptable_lead_time', 5)
HIGH_VOLUME_THRESHOLD = THRESHOLDS.get('high_volume_threshold', 100)
EFFICIENCY_SCORE_GOOD = THRESHOLDS.get('efficiency_score_good', 85)
EFFICIENCY_SCORE_ACCEPTABLE = THRESHOLDS.get('efficiency_score_acceptable', 70)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in miles
    """
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    miles = 3959 * c  # Radius of earth in miles
    return miles


def calculate_lead_time(order_date: pd.Timestamp, ship_date: pd.Timestamp) -> int:
    """Calculate shipping lead time in days"""
    return (ship_date - order_date).days


def map_product_to_factory(product_name: str) -> str:
    """Map product name to factory"""
    return PRODUCT_FACTORY_MAP.get(product_name, "Unknown")


def calculate_efficiency_score(avg_lead_time: float, acceptable_lead_time: float = None) -> float:
    """
    Calculate efficiency score (0-100)
    Higher is better
    """
    if acceptable_lead_time is None:
        acceptable_lead_time = ACCEPTABLE_LEAD_TIME

    if avg_lead_time <= acceptable_lead_time:
        score = 100.0
    elif avg_lead_time <= acceptable_lead_time * 1.5:
        score = 100 - (avg_lead_time - acceptable_lead_time) / acceptable_lead_time * 50
    else:
        score = max(0, 50 - (avg_lead_time - acceptable_lead_time * 1.5) / acceptable_lead_time * 25)

    return round(score, 2)


def classify_efficiency(score: float) -> str:
    """Classify efficiency based on score"""
    if score >= EFFICIENCY_SCORE_GOOD:
        return "Excellent"
    elif score >= EFFICIENCY_SCORE_ACCEPTABLE:
        return "Good"
    else:
        return "Poor"


def classify_delay_status(lead_time: int, threshold: int = None) -> str:
    """Classify delay status based on lead time"""
    if threshold is None:
        threshold = DELAY_DAYS

    if lead_time <= threshold:
        return "On-Time"
    else:
        return "Delayed"


def get_delay_severity(lead_time: int, threshold: int = None) -> str:
    """Classify delay severity"""
    if threshold is None:
        threshold = DELAY_DAYS

    excess_days = lead_time - threshold
    if excess_days <= 0:
        return "None"
    elif excess_days <= 2:
        return "Minor"
    elif excess_days <= 5:
        return "Moderate"
    else:
        return "Severe"


def standardize_state_code(state_str: str) -> str:
    """Standardize state names to 2-letter codes"""
    state_mapping = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
    }

    state_str = str(state_str).strip().lower()
    return state_mapping.get(state_str, state_str.upper())


def validate_dates(df: pd.DataFrame, order_date_col: str, ship_date_col: str) -> pd.DataFrame:
    """Validate and clean date columns"""
    # Convert to datetime
    df[order_date_col] = pd.to_datetime(df[order_date_col], errors='coerce')
    df[ship_date_col] = pd.to_datetime(df[ship_date_col], errors='coerce')

    # Remove rows with invalid dates
    initial_rows = len(df)
    df = df.dropna(subset=[order_date_col, ship_date_col])
    removed_rows = initial_rows - len(df)

    if removed_rows > 0:
        logger.warning(f"Removed {removed_rows} rows with invalid dates")

    # Ensure order_date < ship_date
    df = df[df[order_date_col] <= df[ship_date_col]].copy()

    logger.info(f"Date validation complete. Remaining rows: {len(df)}")
    return df


def remove_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Remove outliers from a series
    method: 'iqr' or 'zscore'
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return series[(series >= lower_bound) & (series <= upper_bound)]

    elif method == 'zscore':
        from scipy import stats
        z_scores = np.abs(stats.zscore(series.dropna()))
        return series[z_scores < threshold]

    return series


def get_region_from_state(state_code: str) -> str:
    """Map state code to US region"""
    regions = {
        'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
        'Midwest': ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
        'South': ['DE', 'MD', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL', 'KY', 'TN', 'AL', 'MS', 'LA', 'AR', 'OK', 'TX'],
        'West': ['MT', 'WY', 'CO', 'NM', 'ID', 'UT', 'NV', 'AZ', 'WA', 'OR', 'CA', 'AK', 'HI']
    }

    state_code = state_code.upper()
    for region, states in regions.items():
        if state_code in states:
            return region
    return "Unknown"


def get_geojson_url() -> str:
    """Return URL for US states GeoJSON"""
    return "https://raw.githubusercontent.com/plotly/datasets/master/geojson-states-fips.json"


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"


def save_dataframe(df: pd.DataFrame, filename: str, data_type: str = 'processed') -> Path:
    """Save dataframe to CSV or Parquet"""
    if data_type == 'processed':
        output_dir = PROCESSED_DATA_DIR
    elif data_type == 'output':
        output_dir = OUTPUT_DIR
    else:
        output_dir = RAW_DATA_DIR

    output_path = output_dir / filename
    if filename.endswith('.parquet'):
        df.to_parquet(output_path, index=False)
    else:
        df.to_csv(output_path, index=False)

    logger.info(f"Saved {len(df)} rows to {output_path}")
    return output_path


def load_dataframe(filename: str, data_type: str = 'processed') -> pd.DataFrame:
    """Load dataframe from CSV or Parquet"""
    if data_type == 'processed':
        input_dir = PROCESSED_DATA_DIR
    elif data_type == 'output':
        input_dir = OUTPUT_DIR
    else:
        input_dir = RAW_DATA_DIR

    input_path = input_dir / filename
    if filename.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    logger.info(f"Loaded {len(df)} rows from {input_path}")
    return df


def get_summary_statistics(df: pd.DataFrame, column: str) -> Dict:
    """Get summary statistics for a column"""
    return {
        'count': df[column].count(),
        'mean': df[column].mean(),
        'median': df[column].median(),
        'std': df[column].std(),
        'min': df[column].min(),
        'max': df[column].max(),
        'q25': df[column].quantile(0.25),
        'q75': df[column].quantile(0.75),
    }


if __name__ == "__main__":
    logger.info("Utility module loaded successfully")
    logger.info(f"Number of factories: {len(FACTORIES)}")
    logger.info(f"Number of products: {len(PRODUCT_FACTORY_MAP)}")
    logger.info(f"Ship modes: {SHIP_MODES}")
