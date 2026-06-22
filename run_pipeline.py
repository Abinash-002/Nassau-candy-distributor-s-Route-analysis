"""
Main Orchestration Script - Nassau Candy Distributor Route Analysis
Runs the complete end-to-end pipeline: data processing -> feature engineering -> analysis
"""

import logging
import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer
from analysis import AdvancedAnalysis
from utils import logger, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*80)
    print("🍬 NASSAU CANDY DISTRIBUTOR - ROUTE ANALYSIS PIPELINE 🍬")
    print("="*80)
    print("A comprehensive ML-driven logistics analytics platform")
    print("="*80 + "\n")


def run_pipeline(csv_file: str = None, skip_processing: bool = False, skip_feature_eng: bool = False):
    """Run complete pipeline"""
    print_banner()

    try:
        # Step 1: Data Processing
        if not skip_processing:
            logger.info("\n" + "="*80)
            logger.info("STEP 1: DATA PROCESSING & CLEANING")
            logger.info("="*80 + "\n")

            processor = DataProcessor(csv_file)
            processor.load_data()
            processor.display_data_info()
            processor.validate_and_clean()
            processor.feature_engineering()
            processor.generate_summary_report()
            processor.save_processed_data()

            logger.info("✅ Data processing complete!")

        # Step 2: Feature Engineering
        if not skip_feature_eng:
            logger.info("\n" + "="*80)
            logger.info("STEP 2: FEATURE ENGINEERING & KPI CALCULATION")
            logger.info("="*80 + "\n")

            engineer = FeatureEngineer()
            results = engineer.run_full_feature_engineering()

            logger.info("✅ Feature engineering complete!")

        # Step 3: Advanced Analysis
        logger.info("\n" + "="*80)
        logger.info("STEP 3: ADVANCED ANALYSIS & INSIGHTS")
        logger.info("="*80 + "\n")

        analyzer = AdvancedAnalysis()
        results = analyzer.run_full_analysis()

        logger.info("✅ Analysis complete!")

        # Print executive summary
        print("\n" + "="*80)
        print(results['executive_summary'])
        print("="*80 + "\n")

        # Success message
        logger.info("\n" + "🎉"*40)
        logger.info("PIPELINE EXECUTION SUCCESSFUL!")
        logger.info("🎉"*40)

        logger.info("\n📊 OUTPUT FILES GENERATED:")
        logger.info(f"  Processing Output: {PROCESSED_DATA_DIR}")
        logger.info(f"  Analysis Output: {OUTPUT_DIR}")

        logger.info("\n🚀 NEXT STEPS:")
        logger.info("  1. Launch Streamlit Dashboard:")
        logger.info("     streamlit run dashboard/app.py")
        logger.info("\n  2. Review generated reports in data/outputs/")
        logger.info("\n  3. Analyze insights and recommendations")

        return True

    except Exception as e:
        logger.error(f"\n❌ Pipeline execution failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Nassau Candy Distributor - Route Analysis Pipeline"
    )

    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to CSV file (default: auto-detect from data/raw/)'
    )

    parser.add_argument(
        '--skip-processing',
        action='store_true',
        help='Skip data processing step (use previously processed data)'
    )

    parser.add_argument(
        '--skip-feature-eng',
        action='store_true',
        help='Skip feature engineering step'
    )

    parser.add_argument(
        '--analysis-only',
        action='store_true',
        help='Run only analysis step'
    )

    args = parser.parse_args()

    # Run pipeline
    skip_processing = args.skip_processing or args.analysis_only
    skip_feature_eng = args.skip_feature_eng or args.analysis_only

    success = run_pipeline(
        csv_file=args.csv,
        skip_processing=skip_processing,
        skip_feature_eng=skip_feature_eng
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
