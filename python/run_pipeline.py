#!/usr/bin/env python3
# =============================================================================
# run_pipeline.py - Main Entry Point
# =============================================================================
"""
Redistribution Preferences Analysis Pipeline

This script runs the complete ETL and analysis pipeline:
1. EXTRACT: Load survey (SCoRE) and admin (CBS) data
2. TRANSFORM: Create geographic IDs, prepare admin by level
3. MERGE: Join survey with admin at buurt/wijk/gemeente levels
4. TRANSFORM: Recode variables, standardize context measures
5. ANALYZE: Fit multilevel models, calculate ICC, run diagnostics
6. REPORT: Generate tables and summary report

Usage:
    python run_pipeline.py              # Use local data files
    python run_pipeline.py --use-api    # Download fresh CBS data
    python run_pipeline.py --help       # Show options
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    SURVEY_PATH, ADMIN_PATH, USE_CBS_API,
    PROCESSED_DATA_PATH, REGRESSION_TABLE_PATH,
    OUTPUT_DIR, TABLES_DIR
)


def main(use_cbs_api: bool = False, include_occupation: bool = True):
    """
    Run the complete analysis pipeline.

    Parameters
    ----------
    use_cbs_api : bool
        If True, download fresh data from CBS API
    include_occupation : bool
        If True, require occupation in analysis sample
    """
    print("=" * 60)
    print("REDISTRIBUTION PREFERENCES ANALYSIS PIPELINE")
    print("=" * 60)

    # Import modules
    from src.extract import load_survey_data, load_admin_data, validate_raw_data
    from src.transform import (
        create_geo_ids, prepare_admin_by_level,
        recode_survey_variables, standardize_context_vars,
        create_inequality_indices, add_geographic_names_from_admin
    )
    from src.merge import (
        merge_survey_admin, validate_merge,
        analyze_missingness, compare_matched_unmatched,
        create_analysis_sample
    )
    from src.analyze import (
        fit_two_level_models, calculate_icc,
        run_diagnostics, run_sensitivity,
        fit_four_level_models, calculate_four_level_icc,
        test_h3_cross_level_interaction
    )
    from src.report import create_model_table, generate_report

    # =========================================================================
    # PHASE 1: EXTRACT
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 1: EXTRACT")
    print("=" * 60)

    survey_raw = load_survey_data(SURVEY_PATH)
    admin_raw = load_admin_data(ADMIN_PATH, use_api=use_cbs_api)
    validation = validate_raw_data(survey_raw, admin_raw)

    if not validation["passed"]:
        print("\nWarning: Raw data validation failed. Continuing anyway...")

    # =========================================================================
    # PHASE 2: TRANSFORM (Geographic IDs)
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 2: TRANSFORM (Geographic IDs)")
    print("=" * 60)

    survey_with_geo = create_geo_ids(survey_raw)
    admin_by_level = prepare_admin_by_level(admin_raw)

    # =========================================================================
    # PHASE 3: MERGE
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 3: MERGE")
    print("=" * 60)

    merged_data = merge_survey_admin(survey_with_geo, admin_by_level)
    merge_validation = validate_merge(merged_data)
    missingness = analyze_missingness(merged_data)
    matched_comparison = compare_matched_unmatched(merged_data)

    # =========================================================================
    # PHASE 4: TRANSFORM (Recode)
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 4: TRANSFORM (Recode & Standardize)")
    print("=" * 60)

    data_recoded = recode_survey_variables(merged_data)
    data_with_indices = create_inequality_indices(data_recoded)
    data_with_names = add_geographic_names_from_admin(data_with_indices, admin_raw)
    data_final = standardize_context_vars(data_with_names)
    analysis_sample = create_analysis_sample(data_final, include_occupation)

    # =========================================================================
    # PHASE 5: ANALYZE (Two-Level Models)
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 5a: ANALYZE (Two-Level Buurt Models)")
    print("=" * 60)

    models = fit_two_level_models(analysis_sample)
    icc_results = calculate_icc(models)
    diagnostics = run_diagnostics(models, analysis_sample)
    sensitivity = run_sensitivity(data_final)

    # H3 Test: Cross-level interaction (individual income moderation)
    h3_results = test_h3_cross_level_interaction(data_final)

    # =========================================================================
    # PHASE 5b: ANALYZE (Four-Level Models)
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 5b: ANALYZE (Four-Level Models: buurt/wijk/gemeente)")
    print("=" * 60)

    # Four-level models need wijk_id and gemeente_id
    four_level_models = None
    four_level_icc = None
    if all(col in data_final.columns for col in ["wijk_id", "gemeente_id"]):
        try:
            four_level_models = fit_four_level_models(data_final)
            four_level_icc = calculate_four_level_icc(four_level_models)
        except Exception as e:
            print(f"  Warning: Four-level models failed: {e}")
    else:
        print("  Skipping: wijk_id or gemeente_id not available")

    # =========================================================================
    # PHASE 6: REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 6: REPORT")
    print("=" * 60)

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "tables").mkdir(exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(exist_ok=True)

    # Generate two-level model table
    create_model_table(models, REGRESSION_TABLE_PATH)

    # Generate four-level model table if available
    if four_level_models is not None:
        from src.report import create_four_level_table
        four_level_table_path = TABLES_DIR / "regression_table_four_level.html"
        create_four_level_table(four_level_models, four_level_table_path)

    report = generate_report(
        models=models,
        icc_results=icc_results,
        diagnostics=diagnostics,
        sensitivity=sensitivity,
        merge_validation=merge_validation,
        output_path=OUTPUT_DIR / "analysis_report.txt"
    )

    # Save final data
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    data_final.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"\nFinal data saved to: {PROCESSED_DATA_PATH}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Observations: {report.n_obs}")
    print(f"Clusters: {report.n_clusters}")
    print(f"ICC: {report.icc:.4f}")
    print(f"Key coefficient: {report.key_coef:.3f} (SE={report.key_se:.3f})")
    print(f"\nOutputs saved to: {OUTPUT_DIR}")

    return report


def test_cbs_api():
    """Test CBS API connection."""
    print("Testing CBS API connection...")

    try:
        import cbsodata
        print("  cbsodata package found")

        # Test getting table list
        tables = cbsodata.get_table_list()
        print(f"  Found {len(tables)} CBS tables")

        # Test getting specific table metadata
        meta = cbsodata.get_meta("84286NED", "DataProperties")
        print(f"  Table 84286NED has {len(meta)} variables")

        print("\nCBS API test PASSED")
        return True

    except ImportError:
        print("  Error: cbsodata not installed")
        print("  Run: pip install cbsodata")
        return False

    except Exception as e:
        print(f"  Error: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Redistribution Preferences Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--use-api",
        action="store_true",
        default=USE_CBS_API,
        help="Download fresh data from CBS API (default: use local files)"
    )

    parser.add_argument(
        "--no-occupation",
        action="store_true",
        help="Exclude occupation from analysis (keeps more cases)"
    )

    parser.add_argument(
        "--test-api",
        action="store_true",
        help="Test CBS API connection and exit"
    )

    args = parser.parse_args()

    if args.test_api:
        success = test_cbs_api()
        sys.exit(0 if success else 1)

    main(
        use_cbs_api=args.use_api,
        include_occupation=not args.no_occupation
    )
