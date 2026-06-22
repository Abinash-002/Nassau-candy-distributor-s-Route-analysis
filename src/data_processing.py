"""
Data Processing Module - Nassau Candy Distributor Route Analysis
Handles data cleaning, validation, and standardization
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    validate_dates, remove_outliers, standardize_state_code, 
    get_region_from_state, map_product_to_factory, calculate_lead_time,
    RAW_DATA_DIR, PROCESSED_DATA_DIR, save_dataframe, logger
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Main data processing class"""

    def __init__(self, raw_file_path: str = None):
        """Initialize processor"""
        if raw_file_path is None:
            # Look for CSV files in raw data directory
            csv_files = list(RAW_DATA_DIR.glob("*.csv"))
            if csv_files:
                raw_file_path = csv_files[0]
            else:
                raise FileNotFoundError(f"No CSV files found in {RAW_DATA_DIR}")

        self.raw_file_path = Path(raw_file_path)
        self.df = None
        self.df_processed = None
        logger.info(f"Initialized DataProcessor with file: {self.raw_file_path}")

    def load_data(self) -> pd.DataFrame:
        """Load CSV data"""
        try:
            self.df = pd.read_csv(self.raw_file_path)
            logger.info(f"Loaded {len(self.df)} rows from {self.raw_file_path.name}")
            logger.info(f"Columns: {list(self.df.columns)}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def display_data_info(self):
        """Display basic data information"""
        logger.info("\n" + "="*80)
        logger.info("DATA INFORMATION")
        logger.info("="*80)
        logger.info(f"Shape: {self.df.shape}")
        logger.info(f"\nColumn Names and Types:\n{self.df.dtypes}")
        logger.info(f"\nMissing Values:\n{self.df.isnull().sum()}")
        logger.info(f"\nFirst few rows:\n{self.df.head()}")
        logger.info("="*80 + "\n")

    def validate_and_clean(self) -> pd.DataFrame:
        """Validate and clean data"""
        logger.info("Starting data validation and cleaning...")

        self.df_processed = self.df.copy()
        initial_rows = len(self.df_processed)

        # Step 1: Validate dates
        logger.info("Step 1: Validating dates...")
        self.df_processed = validate_dates(
            self.df_processed,
            order_date_col='Order Date',
            ship_date_col='Ship Date'
        )

        # Step 2: Remove duplicates
        logger.info("Step 2: Removing duplicates...")
        duplicate_rows = self.df_processed.duplicated(subset=['Row ID']).sum()
        self.df_processed = self.df_processed.drop_duplicates(subset=['Row ID'])
        if duplicate_rows > 0:
            logger.warning(f"Removed {duplicate_rows} duplicate rows")

        # Step 3: Handle missing values
        logger.info("Step 3: Handling missing values...")
        critical_columns = ['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'State/Province']
        for col in critical_columns:
            if col in self.df_processed.columns:
                missing = self.df_processed[col].isnull().sum()
                if missing > 0:
                    logger.warning(f"Removing {missing} rows with missing {col}")
                    self.df_processed = self.df_processed.dropna(subset=[col])

        # Step 4: Standardize text fields
        logger.info("Step 4: Standardizing text fields...")
        text_columns = ['Ship Mode', 'Country/Region', 'State/Province', 'Division']
        for col in text_columns:
            if col in self.df_processed.columns:
                self.df_processed[col] = self.df_processed[col].str.strip().str.title()

        # Step 5: Standardize State/Province codes
        logger.info("Step 5: Standardizing state codes...")
        if 'State/Province' in self.df_processed.columns:
            self.df_processed['State_Code'] = self.df_processed['State/Province'].apply(
                standardize_state_code
            )

        # Step 6: Validate numeric fields
        logger.info("Step 6: Validating numeric fields...")
        numeric_columns = ['Sales', 'Units', 'Cost', 'Gross Profit']
        for col in numeric_columns:
            if col in self.df_processed.columns:
                # Convert to numeric
                self.df_processed[col] = pd.to_numeric(self.df_processed[col], errors='coerce')
                # Remove negative values (except for negative profits which might be valid)
                if col != 'Gross Profit':
                    invalid_count = (self.df_processed[col] < 0).sum()
                    if invalid_count > 0:
                        logger.warning(f"Removing {invalid_count} rows with negative {col}")
                        self.df_processed = self.df_processed[self.df_processed[col] >= 0]

        # Step 7: Add region from state
        logger.info("Step 7: Adding region information...")
        if 'State_Code' in self.df_processed.columns:
            self.df_processed['Region_Mapped'] = self.df_processed['State_Code'].apply(
                get_region_from_state
            )

        removed_rows = initial_rows - len(self.df_processed)
        logger.info(f"Data cleaning complete. Removed {removed_rows} rows. Remaining: {len(self.df_processed)}")

        return self.df_processed

    def feature_engineering(self) -> pd.DataFrame:
        """Add engineered features"""
        logger.info("Starting feature engineering...")

        if self.df_processed is None:
            raise ValueError("Run validate_and_clean first")

        # Step 1: Calculate lead time
        logger.info("Step 1: Calculating shipping lead time...")
        self.df_processed['Lead_Time_Days'] = self.df_processed.apply(
            lambda row: calculate_lead_time(row['Order Date'], row['Ship Date']),
            axis=1
        )

        # Step 2: Map products to factories
        logger.info("Step 2: Mapping products to factories...")
        if 'Product Name' in self.df_processed.columns:
            self.df_processed['Origin_Factory'] = self.df_processed['Product Name'].apply(
                map_product_to_factory
            )

        # Step 3: Create route identifier
        logger.info("Step 3: Creating route identifiers...")
        if 'Origin_Factory' in self.df_processed.columns and 'State_Code' in self.df_processed.columns:
            self.df_processed['Route_ID'] = (
                self.df_processed['Origin_Factory'] + ' → ' + 
                self.df_processed['State_Code']
            )

        # Step 4: Categorize lead times
        logger.info("Step 4: Categorizing lead times...")
        def categorize_lead_time(days):
            if days <= 3:
                return 'Fast'
            elif days <= 7:
                return 'Normal'
            elif days <= 14:
                return 'Slow'
            else:
                return 'Very Slow'

        self.df_processed['Lead_Time_Category'] = self.df_processed['Lead_Time_Days'].apply(
            categorize_lead_time
        )

        # Step 5: Extract temporal features
        logger.info("Step 5: Extracting temporal features...")
        self.df_processed['Order_Month'] = self.df_processed['Order Date'].dt.month
        self.df_processed['Order_Quarter'] = self.df_processed['Order Date'].dt.quarter
        self.df_processed['Order_Year'] = self.df_processed['Order Date'].dt.year
        self.df_processed['Order_Day_of_Week'] = self.df_processed['Order Date'].dt.dayofweek
        self.df_processed['Order_Is_Weekend'] = self.df_processed['Order_Day_of_Week'].isin([5, 6]).astype(int)

        # Step 6: Mark delayed shipments
        logger.info("Step 6: Marking delayed shipments...")
        from utils import DELAY_DAYS
        self.df_processed['Is_Delayed'] = (self.df_processed['Lead_Time_Days'] > DELAY_DAYS).astype(int)

        # Step 7: Calculate profit margin
        logger.info("Step 7: Calculating profit metrics...")
        if all(col in self.df_processed.columns for col in ['Sales', 'Cost']):
            self.df_processed['Profit_Margin'] = (
                (self.df_processed['Gross Profit'] / self.df_processed['Sales'] * 100).round(2)
            ).fillna(0)

        logger.info(f"Feature engineering complete. New columns added: {len(self.df_processed.columns) - len(self.df.columns)}")

        return self.df_processed

    def generate_summary_report(self):
        """Generate data quality summary report"""
        logger.info("\n" + "="*80)
        logger.info("DATA QUALITY SUMMARY REPORT")
        logger.info("="*80)

        logger.info(f"\nTotal Records: {len(self.df_processed):,}")
        logger.info(f"Total Features: {len(self.df_processed.columns)}")

        # Lead time statistics
        logger.info(f"\n--- LEAD TIME STATISTICS ---")
        logger.info(f"  Average Lead Time: {self.df_processed['Lead_Time_Days'].mean():.2f} days")
        logger.info(f"  Median Lead Time: {self.df_processed['Lead_Time_Days'].median():.2f} days")
        logger.info(f"  Min Lead Time: {self.df_processed['Lead_Time_Days'].min()} days")
        logger.info(f"  Max Lead Time: {self.df_processed['Lead_Time_Days'].max()} days")
        logger.info(f"  Std Dev: {self.df_processed['Lead_Time_Days'].std():.2f} days")

        # Delay analysis
        delayed_count = self.df_processed['Is_Delayed'].sum()
        delay_pct = (delayed_count / len(self.df_processed)) * 100
        logger.info(f"\n--- DELAY ANALYSIS ---")
        logger.info(f"  Total Delayed Shipments: {delayed_count:,} ({delay_pct:.2f}%)")
        logger.info(f"  On-Time Shipments: {len(self.df_processed) - delayed_count:,} ({100-delay_pct:.2f}%)")

        # Ship mode analysis
        if 'Ship Mode' in self.df_processed.columns:
            logger.info(f"\n--- SHIP MODE ANALYSIS ---")
            for mode in self.df_processed['Ship Mode'].unique():
                mode_data = self.df_processed[self.df_processed['Ship Mode'] == mode]
                avg_lead = mode_data['Lead_Time_Days'].mean()
                logger.info(f"  {mode}: {len(mode_data):,} shipments, avg lead time: {avg_lead:.2f} days")

        # Route analysis
        if 'Route_ID' in self.df_processed.columns:
            logger.info(f"\n--- ROUTE ANALYSIS ---")
            logger.info(f"  Total Unique Routes: {self.df_processed['Route_ID'].nunique()}")
            logger.info(f"  Average Shipments per Route: {len(self.df_processed) / self.df_processed['Route_ID'].nunique():.0f}")

        # Regional analysis
        if 'Region_Mapped' in self.df_processed.columns:
            logger.info(f"\n--- REGIONAL ANALYSIS ---")
            for region in self.df_processed['Region_Mapped'].unique():
                if region != 'Unknown':
                    region_data = self.df_processed[self.df_processed['Region_Mapped'] == region]
                    avg_lead = region_data['Lead_Time_Days'].mean()
                    logger.info(f"  {region}: {len(region_data):,} shipments, avg lead time: {avg_lead:.2f} days")

        logger.info("="*80 + "\n")

    def save_processed_data(self, filename: str = "processed_orders.csv") -> Path:
        """Save processed data to file"""
        if self.df_processed is None:
            raise ValueError("Process data first before saving")

        output_path = save_dataframe(
            self.df_processed,
            filename,
            data_type='processed'
        )
        return output_path

    def run_full_pipeline(self) -> pd.DataFrame:
        """Run complete data processing pipeline"""
        logger.info("\n" + "🚀"*40)
        logger.info("STARTING FULL DATA PROCESSING PIPELINE")
        logger.info("🚀"*40 + "\n")

        # Load data
        self.load_data()
        self.display_data_info()

        # Clean and validate
        self.validate_and_clean()

        # Feature engineering
        self.feature_engineering()

        # Generate report
        self.generate_summary_report()

        # Save processed data
        self.save_processed_data()

        logger.info("✅ Data Processing Pipeline Complete!\n")
        return self.df_processed


def main():
    """Main execution"""
    try:
        # Initialize processor with your CSV file
        processor = DataProcessor(r"C:\Users\abina\Downloads\Nassau Candy Distributor.csv")

        # Run full pipeline
        processed_df = processor.run_full_pipeline()

        # Display sample of processed data
        logger.info("\nSample of processed data:")
        logger.info(f"\n{processed_df.head(10)}")

        logger.info("\nProcessed data columns:")
        logger.info(f"{list(processed_df.columns)}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
