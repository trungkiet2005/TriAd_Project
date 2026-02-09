"""Example script for analyzing experiment results with visualizations."""

from pathlib import Path
import glob

from src.utils.utils import setup_project_path
from src.analysis.data_loader import DataLoader
from src.analysis.visualizer import Visualizer


def main():
    """Generate analysis plots from latest experiment results."""
    setup_project_path()
    
    # Find the latest results file
    results_dir = Path("experiment_results")
    list_of_files = glob.glob(str(results_dir / "*.csv"))
    
    if not list_of_files:
        print("No result files found in experiment_results/")
        return
        
    latest_file = max(list_of_files, key=lambda p: Path(p).stat().st_mtime)
    print(f"Analyzing: {latest_file}")
    
    # Load data
    df = DataLoader.load_experiment_results(latest_file)
    
    # Initialize visualizer
    viz = Visualizer()
    
    # Plot 1: Heatmap of Cooperation Rate vs Noise
    if 'agent1NoiseRate' in df.columns and 'agent2NoiseRate' in df.columns:
        viz.plot_cooperation_rate_heatmap(
            df, 
            x_col='agent1NoiseRate', 
            y_col='agent2NoiseRate', 
            title="Cooperation Rate by Noise Levels",
            output_path="experiment_results/cooperation_heatmap.png"
        )
    
    # Plot 2: Score Distribution vs Agent 1 Noise
    if 'agent1NoiseRate' in df.columns:
        viz.plot_score_distribution(
            df,
            group_col='agent1NoiseRate',
            title="Total Score Distribution vs Agent 1 Noise",
            output_path="experiment_results/score_dist_noise1.png"
        )


if __name__ == "__main__":
    main()
