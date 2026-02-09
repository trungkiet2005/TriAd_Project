"""
Generate Paper-Ready Tables and Narratives (FAIRGAME-Style)
Converts raw data into qualitative descriptions with inline metrics
"""

from pathlib import Path

from src.utils.utils import setup_project_path, get_results_dir, load_csv_with_fallback
from src.analysis.data_loader import DataLoader
from src.analysis.table_generator import QualitativeTableGenerator


def main():
    """Generate paper-ready qualitative tables and narratives."""
    # Setup paths
    setup_project_path()
    
    # Initialize generator
    table_gen = QualitativeTableGenerator()
    
    # Load experiment data
    results_dir = get_results_dir()
    csv_file = results_dir / "results_pd3_mock.csv"
    
    if not load_csv_with_fallback(csv_file):
        return
    
    print(f"Loading data from {csv_file}...")
    df = DataLoader.load_experiment_results(csv_file)
    print(f"Loaded {len(df)} games\n")
    
    # ===== TABLE 2 STYLE: Model Comparison with Qualitative Descriptions =====
    print("=" * 80)
    print("TABLE 2 STYLE - Qualitative Model Comparison")
    print("=" * 80)
    print()
    
    table2 = table_gen.generate_model_comparison_table(
        df,
        group_by=['language', 'agent1NoiseRate'],
        show_metrics=True,
        output_latex="experiment_results/table2_qualitative.tex"
    )
    
    print(table2.to_string(index=False))
    print()
    
    # ===== NARRATIVE: Cross-Lingual Results =====
    print("=" * 80)
    print("CROSS-LINGUAL RESULTS NARRATIVE")
    print("=" * 80)
    print()
    
    if 'language' in df.columns and len(df['language'].unique()) > 1:
        language_narrative = table_gen.generate_language_comparison_narrative(df)
        print(language_narrative)
        print()
        
        # Save to file
        with open("experiment_results/language_narrative.txt", "w") as f:
            f.write(language_narrative)
        print("✓ Saved to: experiment_results/language_narrative.txt")
    
    print()
    
    # ===== NARRATIVE: Condition Comparison =====
    print("=" * 80)
    print("CONDITION COMPARISON NARRATIVE")
    print("=" * 80)
    print()
    
    if 'n_rounds_is_known' in df.columns:
        condition_narrative = table_gen.generate_condition_comparison_narrative(
            df,
            condition_col='n_rounds_is_known',
            condition_labels={True: "known rounds", False: "unknown rounds"}
        )
        print(condition_narrative)
        print()
        
        # Save to file
        with open("experiment_results/condition_narrative.txt", "w") as f:
            f.write(condition_narrative)
        print("✓ Saved to: experiment_results/condition_narrative.txt")
    
    print()
    
    # ===== ALTERNATIVE: Without Inline Metrics (Pure Qualitative) =====
    print("=" * 80)
    print("PURE QUALITATIVE VERSION (No Numbers)")
    print("=" * 80)
    print()
    
    table2_pure = table_gen.generate_model_comparison_table(
        df,
        group_by=['language', 'agent1NoiseRate'],
        show_metrics=False
    )
    
    print(table2_pure[['language', 'agent1NoiseRate', 'description']].to_string(index=False))
    
    # ===== SUMMARY =====
    print("\n" + "=" * 80)
    print("PAPER-READY OUTPUTS GENERATED")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • experiment_results/table2_qualitative.tex - LaTeX table")
    print("  • experiment_results/language_narrative.txt - Cross-lingual narrative")
    print("  • experiment_results/condition_narrative.txt - Condition comparison")
    print("\nUsage: Copy narratives directly into Results section")


if __name__ == "__main__":
    main()
