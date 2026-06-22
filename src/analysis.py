"""
Analysis Module - Nassau Candy Distributor Route Analysis
Comprehensive bottleneck detection, anomaly detection, and insights generation
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    load_dataframe, save_dataframe, logger, DELAY_DAYS,
    OUTPUT_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedAnalysis:
    """Advanced analytics and insights generation"""

    def __init__(self, processed_df: pd.DataFrame = None, file_path: str = None):
        """Initialize analysis engine"""
        if processed_df is not None:
            self.df = processed_df.copy()
        elif file_path:
            self.df = load_dataframe(file_path, data_type='processed')
        else:
            self.df = load_dataframe("processed_orders.csv", data_type='processed')

        self.anomalies = None
        self.delay_patterns = None
        self.insights = {}
        logger.info(f"Initialized AdvancedAnalysis with {len(self.df)} records")

    def detect_anomalies(self, contamination: float = 0.05) -> pd.DataFrame:
        """Detect anomalous shipments using Isolation Forest"""
        logger.info("Detecting anomalies in shipment data...")

        # Prepare features for anomaly detection
        features = self.df[['Lead_Time_Days', 'Sales', 'Units']].copy()

        # Handle missing values
        features = features.fillna(features.mean())

        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Apply Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(features_scaled)

        # Add anomaly labels to dataframe
        anomalies = self.df.copy()
        anomalies['Anomaly'] = (anomaly_labels == -1).astype(int)
        anomalies['Anomaly_Score'] = iso_forest.score_samples(features_scaled)

        # Sort by anomaly score
        anomalies = anomalies[anomalies['Anomaly'] == 1].sort_values('Anomaly_Score')

        self.anomalies = anomalies
        logger.info(f"Detected {len(anomalies)} anomalies ({len(anomalies)/len(self.df)*100:.2f}% of data)")

        return anomalies

    def analyze_delay_patterns(self) -> Dict:
        """Analyze delay patterns by multiple dimensions"""
        logger.info("Analyzing delay patterns...")

        delay_analysis = {}

        # Overall delay statistics
        delayed = self.df[self.df['Is_Delayed'] == 1]
        delay_analysis['Total_Delayed'] = len(delayed)
        delay_analysis['Delay_Rate'] = (len(delayed) / len(self.df) * 100)
        delay_analysis['Avg_Delay_Days'] = (delayed['Lead_Time_Days'] - DELAY_DAYS).mean()

        # Delays by ship mode
        delay_analysis['By_ShipMode'] = self.df.groupby('Ship Mode').agg({
            'Is_Delayed': ['count', 'sum', 'mean']
        }).round(4)
        delay_analysis['By_ShipMode'].columns = ['Total', 'Delayed', 'Delay_Rate']
        delay_analysis['By_ShipMode']['Delay_Rate'] = (
            delay_analysis['By_ShipMode']['Delay_Rate'] * 100
        ).round(2)

        # Delays by region
        delay_analysis['By_Region'] = self.df.groupby('Region_Mapped').agg({
            'Is_Delayed': ['count', 'sum', 'mean']
        }).round(4)
        delay_analysis['By_Region'].columns = ['Total', 'Delayed', 'Delay_Rate']
        delay_analysis['By_Region']['Delay_Rate'] = (
            delay_analysis['By_Region']['Delay_Rate'] * 100
        ).round(2)

        # Delays by month
        delay_analysis['By_Month'] = self.df.groupby('Order_Month').agg({
            'Is_Delayed': ['count', 'sum', 'mean']
        }).round(4)
        delay_analysis['By_Month'].columns = ['Total', 'Delayed', 'Delay_Rate']
        delay_analysis['By_Month']['Delay_Rate'] = (
            delay_analysis['By_Month']['Delay_Rate'] * 100
        ).round(2)

        # Delays by division
        if 'Division' in self.df.columns:
            delay_analysis['By_Division'] = self.df.groupby('Division').agg({
                'Is_Delayed': ['count', 'sum', 'mean']
            }).round(4)
            delay_analysis['By_Division'].columns = ['Total', 'Delayed', 'Delay_Rate']
            delay_analysis['By_Division']['Delay_Rate'] = (
                delay_analysis['By_Division']['Delay_Rate'] * 100
            ).round(2)

        self.delay_patterns = delay_analysis
        logger.info(f"Delay analysis complete. Overall delay rate: {delay_analysis['Delay_Rate']:.2f}%")

        return delay_analysis

    def identify_critical_bottlenecks(self, volume_threshold: int = 100) -> pd.DataFrame:
        """Identify critical operational bottlenecks"""
        logger.info(f"Identifying critical bottlenecks (volume threshold: {volume_threshold})...")

        # Group by route
        routes = self.df.groupby('Route_ID').agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'std'],
            'Is_Delayed': 'mean',
            'Sales': 'sum'
        })

        routes.columns = ['Volume', 'Avg_Lead_Time', 'Std_Lead_Time', 'Delay_Rate', 'Total_Sales']
        routes = routes.reset_index()
        routes['Delay_Rate'] = (routes['Delay_Rate'] * 100).round(2)

        # Calculate bottleneck score
        # High volume + High delay rate + High variability = Bottleneck
        routes['Bottleneck_Score'] = (
            (routes['Volume'] / routes['Volume'].max() * 100) * 0.4 +
            routes['Delay_Rate'] * 0.4 +
            (routes['Std_Lead_Time'] / routes['Std_Lead_Time'].max() * 100) * 0.2
        ).round(2)

        # Classify bottlenecks
        routes['Bottleneck_Level'] = routes['Bottleneck_Score'].apply(
            lambda x: 'Critical' if x > 70 else 'High' if x > 50 else 'Medium' if x > 30 else 'Low'
        )

        # Filter high-volume bottlenecks
        critical_bottlenecks = routes[
            (routes['Volume'] > volume_threshold) &
            (routes['Bottleneck_Level'].isin(['Critical', 'High']))
        ].sort_values('Bottleneck_Score', ascending=False)

        logger.info(f"Identified {len(critical_bottlenecks)} critical bottlenecks")

        return critical_bottlenecks

    def analyze_temporal_patterns(self) -> Dict:
        """Analyze temporal patterns in shipping"""
        logger.info("Analyzing temporal patterns...")

        temporal = {}

        # Seasonality
        temporal['Seasonality'] = self.df.groupby('Order_Month').agg({
            'Order ID': 'count',
            'Lead_Time_Days': 'mean',
            'Sales': 'sum',
            'Is_Delayed': 'mean'
        }).round(2)
        temporal['Seasonality'].columns = ['Orders', 'Avg_Lead_Time', 'Total_Sales', 'Delay_Rate']
        temporal['Seasonality']['Delay_Rate'] = (temporal['Seasonality']['Delay_Rate'] * 100).round(2)

        # Quarterly trends
        temporal['Quarterly'] = self.df.groupby('Order_Quarter').agg({
            'Order ID': 'count',
            'Lead_Time_Days': 'mean',
            'Sales': 'sum',
            'Is_Delayed': 'mean'
        }).round(2)
        temporal['Quarterly'].columns = ['Orders', 'Avg_Lead_Time', 'Total_Sales', 'Delay_Rate']
        temporal['Quarterly']['Delay_Rate'] = (temporal['Quarterly']['Delay_Rate'] * 100).round(2)

        # Day of week patterns
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        temporal['Day_of_Week'] = self.df.groupby('Order_Day_of_Week').agg({
            'Order ID': 'count',
            'Lead_Time_Days': 'mean',
            'Is_Delayed': 'mean'
        }).round(2)
        temporal['Day_of_Week']['Day_Name'] = temporal['Day_of_Week'].index.map(lambda x: days[x])
        temporal['Day_of_Week'].columns = ['Orders', 'Avg_Lead_Time', 'Delay_Rate', 'Day_Name']
        temporal['Day_of_Week']['Delay_Rate'] = (temporal['Day_of_Week']['Delay_Rate'] * 100).round(2)

        logger.info("Temporal analysis complete")

        return temporal

    def compare_factory_performance(self) -> pd.DataFrame:
        """Compare performance across all factories"""
        logger.info("Comparing factory performance...")

        factory_perf = self.df.groupby('Origin_Factory').agg({
            'Order ID': 'count',
            'Lead_Time_Days': ['mean', 'std', 'min', 'max'],
            'Is_Delayed': 'mean',
            'Sales': 'sum',
            'Gross Profit': 'sum'
        }).round(2)

        factory_perf.columns = [
            'Total_Orders', 'Avg_Lead_Time', 'Std_Lead_Time',
            'Min_Lead_Time', 'Max_Lead_Time', 'Delay_Rate', 'Total_Sales', 'Total_Profit'
        ]

        factory_perf = factory_perf.reset_index()
        factory_perf['Delay_Rate'] = (factory_perf['Delay_Rate'] * 100).round(2)
        factory_perf['Profit_Margin'] = (
            (factory_perf['Total_Profit'] / factory_perf['Total_Sales'] * 100).round(2)
        ).fillna(0)

        factory_perf = factory_perf.sort_values('Avg_Lead_Time')

        logger.info(f"Factory performance analysis complete for {len(factory_perf)} factories")

        return factory_perf

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        logger.info("Generating recommendations...")

        recommendations = []

        # Overall performance
        overall_delay_rate = self.delay_patterns['Delay_Rate']
        if overall_delay_rate > 10:
            recommendations.append(
                f"🚨 HIGH PRIORITY: Overall delay rate is {overall_delay_rate:.2f}%. "
                f"Focus on process optimization to reduce delays below 5%."
            )

        # Bottleneck recommendations
        bottlenecks = self.identify_critical_bottlenecks()
        if len(bottlenecks) > 0:
            top_bottleneck = bottlenecks.iloc[0]
            recommendations.append(
                f"🎯 CRITICAL: Route '{top_bottleneck['Route_ID']}' is a critical bottleneck "
                f"with {top_bottleneck['Volume']} shipments and {top_bottleneck['Delay_Rate']}% delay rate. "
                f"Prioritize resource allocation here."
            )

        # Ship mode recommendations
        shipmode_by_delay = self.delay_patterns['By_ShipMode'].sort_values('Delay_Rate', ascending=False)
        worst_mode = shipmode_by_delay.iloc[0]
        if worst_mode['Delay_Rate'] > overall_delay_rate:
            recommendations.append(
                f"📦 SHIP MODE: '{worst_mode.name}' has higher delays ({worst_mode['Delay_Rate']:.2f}%). "
                f"Review service providers or routing strategies."
            )

        # Regional recommendations
        regional_by_delay = self.delay_patterns['By_Region'].sort_values('Delay_Rate', ascending=False)
        worst_region = regional_by_delay.iloc[0]
        if worst_region['Delay_Rate'] > overall_delay_rate + 5:
            recommendations.append(
                f"🗺️ REGIONAL: '{worst_region.name}' region has high delays ({worst_region['Delay_Rate']:.2f}%). "
                f"Consider establishing regional hubs or improving carrier relationships."
            )

        # Seasonal recommendations
        seasonal = self.analyze_temporal_patterns()['Seasonality']
        peak_month_idx = seasonal['Orders'].idxmax()
        peak_month_delay = seasonal.loc[peak_month_idx, 'Delay_Rate']
        if peak_month_delay > overall_delay_rate + 5:
            recommendations.append(
                f"📅 SEASONAL: Month {peak_month_idx} has peak orders with high delays. "
                f"Prepare contingency plans and increase capacity during peak seasons."
            )

        # Anomaly recommendations
        if self.anomalies is not None and len(self.anomalies) > 0:
            recommendations.append(
                f"⚠️ ANOMALIES: {len(self.anomalies)} anomalous shipments detected. "
                f"Review these records for data quality issues or exceptional circumstances."
            )

        logger.info(f"Generated {len(recommendations)} recommendations")

        return recommendations

    def generate_executive_summary(self) -> str:
        """Generate executive summary report"""
        logger.info("Generating executive summary...")

        summary = []
        summary.append("="*80)
        summary.append("NASSAU CANDY DISTRIBUTOR - ROUTE ANALYSIS EXECUTIVE SUMMARY")
        summary.append("="*80)
        summary.append("")

        # Key metrics
        summary.append("KEY PERFORMANCE INDICATORS:")
        summary.append(f"  • Total Shipments: {len(self.df):,}")
        summary.append(f"  • Average Lead Time: {self.df['Lead_Time_Days'].mean():.2f} days")
        summary.append(f"  • Delay Rate: {self.delay_patterns['Delay_Rate']:.2f}%")
        summary.append(f"  • Total Revenue: ${self.df['Sales'].sum():,.0f}")
        summary.append("")

        # Top bottlenecks
        summary.append("CRITICAL BOTTLENECKS:")
        bottlenecks = self.identify_critical_bottlenecks()
        for idx, (_, bottleneck) in enumerate(bottlenecks.head(3).iterrows(), 1):
            summary.append(f"  {idx}. {bottleneck['Route_ID']}")
            summary.append(f"     - Volume: {bottleneck['Volume']} shipments")
            summary.append(f"     - Delay Rate: {bottleneck['Delay_Rate']:.2f}%")
            summary.append(f"     - Avg Lead Time: {bottleneck['Avg_Lead_Time']:.2f} days")
        summary.append("")

        # Recommendations
        summary.append("TOP RECOMMENDATIONS:")
        recommendations = self.generate_recommendations()
        for idx, rec in enumerate(recommendations[:5], 1):
            summary.append(f"  {idx}. {rec}")
        summary.append("")
        summary.append("="*80)

        summary_text = "\n".join(summary)
        logger.info("Executive summary generated")

        return summary_text

    def run_full_analysis(self) -> Dict:
        """Run complete analysis pipeline"""
        logger.info("\n" + "🚀"*40)
        logger.info("STARTING ADVANCED ANALYSIS PIPELINE")
        logger.info("🚀"*40 + "\n")

        results = {}

        # Run all analyses
        results['anomalies'] = self.detect_anomalies()
        results['delay_patterns'] = self.analyze_delay_patterns()
        results['bottlenecks'] = self.identify_critical_bottlenecks()
        results['temporal_patterns'] = self.analyze_temporal_patterns()
        results['factory_performance'] = self.compare_factory_performance()
        results['recommendations'] = self.generate_recommendations()
        results['executive_summary'] = self.generate_executive_summary()

        # Save results
        logger.info("Saving analysis results...")
        save_dataframe(results['anomalies'], "anomalies_detected.csv", data_type='output')
        save_dataframe(results['bottlenecks'], "critical_bottlenecks.csv", data_type='output')
        save_dataframe(results['factory_performance'], "factory_performance.csv", data_type='output')

        # Save summary
        with open(OUTPUT_DIR / "executive_summary.txt", 'w') as f:
            f.write(results['executive_summary'])

        logger.info("✅ Advanced Analysis Pipeline Complete!\n")
        return results


def main():
    """Main execution"""
    try:
        # Initialize analysis
        analyzer = AdvancedAnalysis()

        # Run full analysis
        results = analyzer.run_full_analysis()

        # Display executive summary
        print("\n")
        print(results['executive_summary'])

        # Display bottlenecks
        print("\nCRITICAL BOTTLENECKS:")
        print(results['bottlenecks'][['Route_ID', 'Volume', 'Avg_Lead_Time', 'Delay_Rate']].head(10))

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
