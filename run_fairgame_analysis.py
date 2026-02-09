"""
FAIRGAME-Style Analysis Example
Demonstrates qualitative narratives with inline metrics + error bar plots
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.analysis.data_loader import DataLoader
from src.analysis.fairgame_analysis import FAIRGAMEAnalyzer
import pandas as pd


def main():
    """
    Run FAIRGAME-style analysis on experiment results.
    """
    
    # Initialize analyzer
    analyzer = FAIRGAMEAnalyzer()
    
    # Load experiment data
    results_dir = Path("resources/results")
    
    # Example: Load Prisoner's Dilemma results
    csv_file = results_dir / "results_pd3_mock.csv"
    
    if not csv_file.exists():
        print(f"File not found: {csv_file}")
        print("Using example with mock data structure...")
        # You can generate mock data here or use actual results
        return
    
    print(f"Loading data from {csv_file}...")
    df = DataLoader.load_experiment_results(csv_file)
    
    print(f"Loaded {len(df)} games\n")
    
    # ===== FAIRGAME-STYLE ANALYSIS =====
    
    # 1. Generate Qualitative Summary with Inline Metrics
    print("=" * 80)
    print("QUALITATIVE SUMMARY (FAIRGAME-Style)")
    print("=" * 80)
    
    summary = analyzer.generate_qualitative_summary(
        df, 
        group_by='language',
        noise_col='agent1NoiseRate'
    )
    print(summary)
    print()
    
    # 2. Plot Cooperation with 95% CI Error Bars
    print("Generating cooperation rate plot with 95% CI...")
    analyzer.plot_cooperation_with_ci(
        df,
        group_by='language',
        title="Intended Cooperation Rate by Language (95% CI)",
        output_path="experiment_results/fairgame_cooperation_by_language.png"
    )
    
    # 3. Calculate and Plot TRS (Trembling Robustness Score)
    print("\nCalculating TRS for each language...")
    print("-" * 80)
    
    for language in df['language'].unique():
        trs_result = analyzer.calculate_trs(df, language=language)
        print(f"{language:>12}: TRS = {trs_result['slope']:+.4f} "
              f"(R² = {trs_result['r_squared']:.3f}, p = {trs_result['p_value']:.4f})")
    
    print("\nGenerating TRS comparison plot...")
    analyzer.plot_trs_comparison(
        df,
        group_by='language',
        title="Trembling Robustness Score (TRS) by Language",
        output_path="experiment_results/fairgame_trs_comparison.png"
    )
    
    # 4. Statistical Comparison Between Conditions
    print("\n" + "=" * 80)
    print("STATISTICAL COMPARISONS")
    print("=" * 80)
    
    if 'n_rounds_is_known' in df.columns:
        comparison = analyzer.compare_conditions(
            df,
            condition_col='n_rounds_is_known',
            condition_a=True,
            condition_b=False
        )
        
        print(f"\nRounds Known vs Unknown:")
        print(f"  Known:   {comparison['mean_a']*100:.1f}% cooperation")
        print(f"  Unknown: {comparison['mean_b']*100:.1f}% cooperation")
        print(f"  t = {comparison['t_statistic']:.3f}, p = {comparison['p_value']:.4f}")
        print(f"  Cohen's d = {comparison['effect_size']:.3f}")
    
    # 5. Create Detailed Appendix Table
    print("\n" + "=" * 80)
    print("GENERATING APPENDIX TABLE")
    print("=" * 80)
    
    appendix_table = analyzer.create_appendix_table(
        df,
        group_by=['language', 'n_rounds_is_known'],
        output_csv="experiment_results/appendix_detailed_results.csv"
    )
    
    print("\nAppendix Table Preview:")
    print(appendix_table.head(10).to_string(index=False))
    
    # 6. Plot by Multiple Conditions
    if 'n_rounds_is_known' in df.columns:
        print("\n" + "=" * 80)
        print("GENERATING CONDITION-SPECIFIC PLOTS")
        print("=" * 80)
        
        for known in [True, False]:
            df_subset = df[df['n_rounds_is_known'] == known]
            label = "Known" if known else "Unknown"
            
            print(f"\nAnalyzing {label} rounds condition...")
            analyzer.plot_cooperation_with_ci(
                df_subset,
                group_by='language',
                title=f"Cooperation Rate - {label} Number of Rounds (95% CI)",
                output_path=f"experiment_results/fairgame_cooperation_{label.lower()}_rounds.png"
            )
    
    print("\n" + "=" * 80)
    print("FAIRGAME-STYLE ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nGenerated outputs:")
    print("  - Qualitative summary with inline metrics")
    print("  - Cooperation rate plots with 95% CI")
    print("  - TRS (Trembling Robustness Score) analysis")
    print("  - Statistical comparisons")
    print("  - Detailed appendix table (CSV)")
    print("\nAll plots saved to: experiment_results/")


if __name__ == "__main__":
    main()
