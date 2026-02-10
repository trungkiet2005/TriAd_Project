
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.experiments.experiment_runner import ExperimentRunner

def main():
    runner = ExperimentRunner(output_dir="experiment_results", max_workers=4)
    
    # Define parameter grid
    # We want to test how noise affects cooperation
    param_grid = {
        'noiseConfig.agent1NoiseRate': [0.0, 0.1, 0.2, 0.3],
        'noiseConfig.agent2NoiseRate': [0.0, 0.1, 0.2, 0.3]
    }
    
    # We use the Public Goods Mock config as a base
    # In a real scenario, use 'public_goods_3_default' with a real LLM
    runner.run_experiment(
        base_config_name="public_goods_3_mock", 
        config_dir="public_goods_3",
        parameter_grid=param_grid,
        experiment_name="pgg_noise_impact_analysis"
    )

if __name__ == "__main__":
    main()
