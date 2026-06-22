"""
Feature Engineering Module - Nassau Candy Distributor Route Analysis
Handles route definition, KPI calculation, and advanced feature engineering
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    haversine_distance, calculate_efficiency_score, classify_efficiency,
    FACTORY_COORDS, DELAY_DAYS, PROCESSED_DATA_DIR, OUTPUT_DIR,
    save_dataframe, load_dataframe, logger
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for route analysis"""

    def __init__(self, processed_df: pd.DataFrame = None, file_path: str = None):
        """Initialize feature engineer"""
        if processed_df is not None:
            self.df = processed_df.copy()
        elif file_path:
            self.df = load_dataframe(file_path, data_type='processed')
        else:
            self.df = load_dataframe("processed_orders.csv", data_type='processed')

        self.route_metrics = None
        self.regional_metrics = None
        self.shipmode_metrics = None
        logger.info(f"Initialized FeatureEngineer with {len(self.df)} records")

    def calculate_route_metrics(self) -> pd.DataFrame:
        """Calculate comprehensive route metrics"""
        logger.info("Calculating route metrics...")

        route_metrics = self.df.groupby('Route_ID').agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'median', 'std', 'min', 'max'],
            'Sales': 'sum',
            'Units': 'sum',
            'Gross Profit': 'sum',
            'Is_Delayed': 'sum'
        }).round(2)

        route_metrics.columns = [
            'Total_Shipments',
            'Avg_Lead_Time',
            'Median_Lead_Time',
            'Std_Lead_Time',
            'Min_Lead_Time',
            'Max_Lead_Time',
            'Total_Sales',
            'Total_Units',
            'Total_Profit',
            'Delayed_Shipments'
        ]

        route_metrics = route_metrics.reset_index()

        # Add calculated metrics
        route_metrics['On_Time_Shipments'] = (
            route_metrics['Total_Shipments'] - route_metrics['Delayed_Shipments']
        )
        route_metrics['On_Time_Rate'] = (
            (route_metrics['On_Time_Shipments'] / route_metrics['Total_Shipments'] * 100).round(2)
        )
        route_metrics['Delay_Rate'] = (
            (route_metrics['Delayed_Shipments'] / route_metrics['Total_Shipments'] * 100).round(2)
        )

        # Efficiency score
        route_metrics['Efficiency_Score'] = route_metrics['Avg_Lead_Time'].apply(
            calculate_efficiency_score
        )
        route_metrics['Efficiency_Class'] = route_metrics['Efficiency_Score'].apply(
            classify_efficiency
        )

        # Profit metrics
        route_metrics['Avg_Profit_Per_Shipment'] = (
            (route_metrics['Total_Profit'] / route_metrics['Total_Shipments']).round(2)
        )

        # Volume classification
        def classify_volume(count):
            if count < 50:
                return 'Low'
            elif count < 200:
                return 'Medium'
            else:
                return 'High'

        route_metrics['Volume_Class'] = route_metrics['Total_Shipments'].apply(classify_volume)

        # Risk classification: High volume + Poor efficiency
        route_metrics['Risk_Level'] = route_metrics.apply(
            lambda row: 'Critical' if (row['Volume_Class'] == 'High' and row['Efficiency_Class'] == 'Poor')
            else 'High' if (row['Volume_Class'] in ['High', 'Medium'] and row['Efficiency_Score'] < 70)
            else 'Medium' if (row['Efficiency_Class'] == 'Poor')
            else 'Low',
            axis=1
        )

        # Sort by efficiency score
        route_metrics = route_metrics.sort_values('Efficiency_Score', ascending=False).reset_index(drop=True)
        route_metrics['Efficiency_Rank'] = range(1, len(route_metrics) + 1)

        self.route_metrics = route_metrics
        logger.info(f"Route metrics calculated for {len(route_metrics)} unique routes")

        return route_metrics

    def calculate_regional_metrics(self) -> pd.DataFrame:
        """Calculate regional performance metrics"""
        logger.info("Calculating regional metrics...")

        regional_metrics = self.df.groupby('Region_Mapped').agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'median', 'std'],
            'Is_Delayed': ['sum', 'mean'],
            'Sales': 'sum',
            'Gross Profit': 'sum'
        }).round(2)

        regional_metrics.columns = [
            'Total_Shipments',
            'Avg_Lead_Time',
            'Median_Lead_Time',
            'Std_Lead_Time',
            'Delayed_Shipments',
            'Delay_Rate',
            'Total_Sales',
            'Total_Profit'
        ]

        regional_metrics = regional_metrics.reset_index()
        regional_metrics['Delay_Rate'] = (regional_metrics['Delay_Rate'] * 100).round(2)

        # Efficiency score
        regional_metrics['Efficiency_Score'] = regional_metrics['Avg_Lead_Time'].apply(
            calculate_efficiency_score
        )
        regional_metrics['Efficiency_Class'] = regional_metrics['Efficiency_Score'].apply(
            classify_efficiency
        )

        regional_metrics = regional_metrics.sort_values('Efficiency_Score', ascending=False)

        self.regional_metrics = regional_metrics
        logger.info(f"Regional metrics calculated for {len(regional_metrics)} regions")

        return regional_metrics

    def calculate_shipmode_metrics(self) -> pd.DataFrame:
        """Calculate ship mode performance metrics"""
        logger.info("Calculating ship mode metrics...")

        shipmode_metrics = self.df.groupby('Ship Mode').agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'median', 'std', 'min', 'max'],
            'Is_Delayed': ['sum', 'mean'],
            'Sales': 'sum',
            'Gross Profit': 'sum'
        }).round(2)

        shipmode_metrics.columns = [
            'Total_Shipments',
            'Avg_Lead_Time',
            'Median_Lead_Time',
            'Std_Lead_Time',
            'Min_Lead_Time',
            'Max_Lead_Time',
            'Delayed_Shipments',
            'Delay_Rate',
            'Total_Sales',
            'Total_Profit'
        ]

        shipmode_metrics = shipmode_metrics.reset_index()
        shipmode_metrics['Delay_Rate'] = (shipmode_metrics['Delay_Rate'] * 100).round(2)

        # Efficiency score
        shipmode_metrics['Efficiency_Score'] = shipmode_metrics['Avg_Lead_Time'].apply(
            calculate_efficiency_score
        )

        # Cost per shipment
        shipmode_metrics['Avg_Sales_Per_Shipment'] = (
            (shipmode_metrics['Total_Sales'] / shipmode_metrics['Total_Shipments']).round(2)
        )

        self.shipmode_metrics = shipmode_metrics
        logger.info(f"Ship mode metrics calculated for {len(shipmode_metrics)} ship modes")

        return shipmode_metrics

    def identify_top_bottom_routes(self, top_n: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Identify top and bottom performing routes"""
        logger.info(f"Identifying top {top_n} and bottom {top_n} routes...")

        if self.route_metrics is None:
            self.calculate_route_metrics()

        top_routes = self.route_metrics.head(top_n).copy()
        bottom_routes = self.route_metrics.tail(top_n).copy()

        logger.info(f"Top routes identified (Efficiency Score >= {top_routes['Efficiency_Score'].min():.2f})")
        logger.info(f"Bottom routes identified (Efficiency Score <= {bottom_routes['Efficiency_Score'].max():.2f})")

        return top_routes, bottom_routes

    def identify_bottlenecks(self) -> pd.DataFrame:
        """Identify geographic and operational bottlenecks"""
        logger.info("Identifying bottlenecks...")

        bottleneck_analysis = self.df.groupby(['Region_Mapped', 'State_Code']).agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'std'],
            'Is_Delayed': 'mean',
            'Sales': 'sum'
        }).round(2)

        bottleneck_analysis.columns = [
            'Shipment_Volume',
            'Avg_Lead_Time',
            'Std_Lead_Time',
            'Delay_Rate',
            'Total_Sales'
        ]

        bottleneck_analysis = bottleneck_analysis.reset_index()
        bottleneck_analysis['Delay_Rate'] = (bottleneck_analysis['Delay_Rate'] * 100).round(2)

        # Identify bottlenecks: High volume + High delays + High variability
        bottleneck_analysis['Bottleneck_Score'] = (
            (bottleneck_analysis['Shipment_Volume'] / bottleneck_analysis['Shipment_Volume'].max() * 100 * 0.4) +
            (bottleneck_analysis['Delay_Rate'] / 100 * 100 * 0.4) +
            (bottleneck_analysis['Std_Lead_Time'] / bottleneck_analysis['Std_Lead_Time'].max() * 100 * 0.2)
        ).round(2)

        bottleneck_analysis['Bottleneck_Level'] = bottleneck_analysis['Bottleneck_Score'].apply(
            lambda x: 'Critical' if x > 70 else 'High' if x > 50 else 'Medium' if x > 30 else 'Low'
        )

        bottleneck_analysis = bottleneck_analysis.sort_values('Bottleneck_Score', ascending=False)

        logger.info(f"Bottleneck analysis complete. Identified {len(bottleneck_analysis)} regions/states")

        return bottleneck_analysis

    def create_state_performance_map(self) -> pd.DataFrame:
        """Create state-level performance data for mapping"""
        logger.info("Creating state performance mapping...")

        state_performance = self.df.groupby('State_Code').agg({
            'Order ID': 'count',
            'Lead_Time_Days': 'mean',
            'Is_Delayed': 'mean',
            'Sales': 'sum',
            'Gross Profit': 'sum'
        }).round(2)

        state_performance.columns = [
            'Total_Shipments',
            'Avg_Lead_Time',
            'Delay_Rate',
            'Total_Sales',
            'Total_Profit'
        ]

        state_performance = state_performance.reset_index()
        state_performance['Delay_Rate'] = (state_performance['Delay_Rate'] * 100).round(2)

        # Efficiency score
        state_performance['Efficiency_Score'] = state_performance['Avg_Lead_Time'].apply(
            calculate_efficiency_score
        )

        # Normalize for heatmap (0-100)
        state_performance['Efficiency_Normalized'] = (
            ((100 - state_performance['Efficiency_Score']) / 100 * 100).round(2)
        )

        state_performance = state_performance.sort_values('Efficiency_Score', ascending=False)

        logger.info(f"State performance mapping created for {len(state_performance)} states")

        return state_performance

    def create_factory_route_matrix(self) -> pd.DataFrame:
        """Create factory-to-region performance matrix"""
        logger.info("Creating factory-route matrix...")

        factory_matrix = self.df.groupby(['Origin_Factory', 'Region_Mapped']).agg({
            'Order ID': 'count',
            'Lead_Time_Days': 'mean',
            'Is_Delayed': 'mean',
            'Sales': 'sum'
        }).round(2)

        factory_matrix.columns = [
            'Shipments',
            'Avg_Lead_Time',
            'Delay_Rate',
            'Total_Sales'
        ]

        factory_matrix = factory_matrix.reset_index()
        factory_matrix['Delay_Rate'] = (factory_matrix['Delay_Rate'] * 100).round(2)

        # Efficiency score
        factory_matrix['Efficiency_Score'] = factory_matrix['Avg_Lead_Time'].apply(
            calculate_efficiency_score
        )

        logger.info(f"Factory-route matrix created with {len(factory_matrix)} combinations")

        return factory_matrix

    def generate_feature_summary(self):
        """Generate comprehensive feature summary report"""
        logger.info("\n" + "="*80)
        logger.info("FEATURE ENGINEERING SUMMARY REPORT")
        logger.info("="*80)

        if self.route_metrics is not None:
            logger.info(f"\n--- ROUTE METRICS ---")
            logger.info(f"  Total Routes: {len(self.route_metrics)}")
            logger.info(f"  Routes with Excellent Efficiency: {(self.route_metrics['Efficiency_Class'] == 'Excellent').sum()}")
            logger.info(f"  Routes with Good Efficiency: {(self.route_metrics['Efficiency_Class'] == 'Good').sum()}")
            logger.info(f"  Routes with Poor Efficiency: {(self.route_metrics['Efficiency_Class'] == 'Poor').sum()}")
            logger.info(f"  Average Route Efficiency Score: {self.route_metrics['Efficiency_Score'].mean():.2f}")

        if self.regional_metrics is not None:
            logger.info(f"\n--- REGIONAL METRICS ---")
            best_region = self.regional_metrics.iloc[0]
            worst_region = self.regional_metrics.iloc[-1]
            logger.info(f"  Best Performing Region: {best_region['Region_Mapped']} ({best_region['Efficiency_Score']:.2f})")
            logger.info(f"  Worst Performing Region: {worst_region['Region_Mapped']} ({worst_region['Efficiency_Score']:.2f})")

        if self.shipmode_metrics is not None:
            logger.info(f"\n--- SHIP MODE METRICS ---")
            for _, row in self.shipmode_metrics.iterrows():
                logger.info(f"  {row['Ship Mode']}: {row['Total_Shipments']:,} shipments, "
                          f"Avg Lead Time: {row['Avg_Lead_Time']:.2f} days, "
                          f"Delay Rate: {row['Delay_Rate']:.2f}%")

        logger.info("="*80 + "\n")

    def run_full_feature_engineering(self) -> Dict:
        """Run complete feature engineering pipeline"""
        logger.info("\n" + "🚀"*40)
        logger.info("STARTING FEATURE ENGINEERING PIPELINE")
        logger.info("🚀"*40 + "\n")

        results = {}

        # Calculate all metrics
        results['route_metrics'] = self.calculate_route_metrics()
        results['regional_metrics'] = self.calculate_regional_metrics()
        results['shipmode_metrics'] = self.calculate_shipmode_metrics()
        results['top_routes'], results['bottom_routes'] = self.identify_top_bottom_routes()
        results['bottlenecks'] = self.identify_bottlenecks()
        results['state_performance'] = self.create_state_performance_map()
        results['factory_matrix'] = self.create_factory_route_matrix()

        # Generate report
        self.generate_feature_summary()

        # Save all results
        logger.info("Saving feature engineering results...")
        save_dataframe(results['route_metrics'], "route_metrics.csv", data_type='output')
        save_dataframe(results['regional_metrics'], "regional_metrics.csv", data_type='output')
        save_dataframe(results['shipmode_metrics'], "shipmode_metrics.csv", data_type='output')
        save_dataframe(results['top_routes'], "top_10_routes.csv", data_type='output')
        save_dataframe(results['bottom_routes'], "bottom_10_routes.csv", data_type='output')
        save_dataframe(results['bottlenecks'], "bottleneck_analysis.csv", data_type='output')
        save_dataframe(results['state_performance'], "state_performance.csv", data_type='output')
        save_dataframe(results['factory_matrix'], "factory_route_matrix.csv", data_type='output')

        logger.info("✅ Feature Engineering Pipeline Complete!\n")
        return results


def main():
    """Main execution"""
    try:
        # Initialize feature engineer
        engineer = FeatureEngineer()

        # Run full pipeline
        results = engineer.run_full_feature_engineering()

        # Display top routes
        logger.info("\nTop 5 Routes:")
        logger.info(f"\n{results['top_routes'][['Route_ID', 'Total_Shipments', 'Avg_Lead_Time', 'Efficiency_Score']].head()}")

        # Display bottom routes
        logger.info("\nBottom 5 Routes:")
        logger.info(f"\n{results['bottom_routes'][['Route_ID', 'Total_Shipments', 'Avg_Lead_Time', 'Efficiency_Score']].tail()}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
