import os
import pandas as pd
import glob
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.triad_analysis import TriadAnalyzer, TriadVisualizer

def find_latest_results(base_dir="resources/results"):
    """Find all games_summary.csv files in the results directory."""
    files = glob.glob(f"{base_dir}/**/games_summary.csv", recursive=True)
    return files

def main():
    print("--- Starting 3-Player Triad Analysis ---")
    
    # diverse paths to check
    base_dirs = ["resources/results", "/kaggle/working/results", "results"]
    
    found_files = []
    for d in base_dirs:
        if os.path.exists(d):
            found_files.extend(find_latest_results(d))
            
    if not found_files:
        print("No games_summary.csv found via automated search.")
        # Fallback to manual check or exit
        return

    print(f"Found {len(found_files)} summary files.")
    
    analyzer = TriadAnalyzer()
    visualizer = TriadVisualizer()
    
    # Create analysis output dir
    os.makedirs("analysis_outputs", exist_ok=True)

    for file_path in found_files:
        print(f"\nAnalyzing: {file_path}")
        try:
            df = pd.read_csv(file_path)
            
            # 1. State Distribution Analysis
            print("  - Calculating state distribution (CCC, DDD, 2C1D, 1C2D)...")
            df_states = analyzer.analyze_state_distribution(df)
            
            if not df_states.empty:
                # Save processed states
                base_name = Path(file_path).parent.name
                output_csv = f"analysis_outputs/{base_name}_states.csv"
                df_states.to_csv(output_csv, index=False)
                print(f"    Saved state data to {output_csv}")
                
                # Plot Stacked Bar
                plot_path = f"analysis_outputs/{base_name}_state_dist.png"
                visualizer.plot_state_distribution(
                    df_states, 
                    group_col='noise_rate', # Defaulting to noise comparison
                    title=f"Game State Distribution - {base_name}",
                    output_path=plot_path
                )
                
                # Plot Heatmap
                heatmap_path = f"analysis_outputs/{base_name}_exploitation_heatmap.png"
                visualizer.plot_coalition_heatmap(
                    df_states,
                    x_col='noise_rate',
                    y_col='language', # If multiple languages exist in this file
                    output_path=heatmap_path
                )
            else:
                print("    No valid state data derived.")

        except Exception as e:
            print(f"    Error analyzing {file_path}: {e}")

    print("\n--- Analysis Complete. Check 'analysis_outputs' folder. ---")

if __name__ == "__main__":
    main()
