
import itertools
import copy
import time
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from src.io_managers.file_manager import FileManager
from src.noise_fairgame_factory import NoiseFairGameFactory
from src.results_processing.results_processor import ResultsProcessor

# Constants
RESOURCES_PATH = Path("resources")
TEMPLATES_PATH = RESOURCES_PATH / "game_templates"
CONFIG_PATH = RESOURCES_PATH / "config"
RESULTS_PATH = RESOURCES_PATH / "results"

class ExperimentRunner:
    """
    Handles batch execution of games with varying parameters.
    """

    def __init__(self, output_dir: str = "experiment_results", max_workers: int = 4):
        """
        Initialize the ExperimentRunner.

        Args:
            output_dir (str): Directory to save experiment results.
            max_workers (int): Number of parallel threads.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.results_processor = ResultsProcessor()

    def run_experiment(self, base_config_name: str, config_dir: str, 
                       parameter_grid: Dict[str, List[Any]], 
                       experiment_name: str) -> pd.DataFrame:
        """
        Run a batch of experiments by sweeping over a parameter grid.

        Args:
            base_config_name (str): Name of the base JSON config file.
            config_dir (str): Directory containing the config file.
            parameter_grid (Dict[str, List[Any]]): Dictionary where keys are config paths 
                                                   (e.g., 'noiseConfig.agent1NoiseRate') 
                                                   and values are lists of values to test.
            experiment_name (str): Identifier for this experiment batch.

        Returns:
            pd.DataFrame: A DataFrame containing combined results from all runs.
        """
        print(f"Starting Experiment: {experiment_name}")
        
        # Load base config
        base_config = self._load_base_config(config_dir, base_config_name)
        
        # Load templates (pre-load to avoid reading files for every run)
        self._inject_templates(base_config)

        # Generate all combinations of parameters
        keys, values = zip(*parameter_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        print(f"Total runs to execute: {len(combinations)}")
        
        all_results = []
        
        # Run combinations (sequentially or parallel could be implemented here)
        # For simplicity and safety with shared factory state, we'll run batches sequentially
        # but the factory uses parallelism internally for the games within a batch.
        
        for i, params in enumerate(combinations):
            print(f"Run {i+1}/{len(combinations)}: {params}")
            
            # Create a specific config for this run
            run_config = copy.deepcopy(base_config)
            self._apply_parameters(run_config, params)
            
            # Run the games
            factory = NoiseFairGameFactory(max_workers=self.max_workers)
            results = factory.create_and_run_games(run_config)
            
            # Process results into a DataFrame row
            df = self.results_processor.process(results)
            
            # Add experiment parameters to the DataFrame
            for key, val in params.items():
                # clean key for column name (e.g. noiseConfig.agent1NoiseRate -> agent1NoiseRate)
                col_name = key.split('.')[-1]
                df[col_name] = val
            
            df['experiment_run_id'] = i
            all_results.append(df)
            
        # Combine all results
        if not all_results:
            print("No results generated.")
            return pd.DataFrame()
            
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Save aggregated results
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_file = self.output_dir / f"{experiment_name}_{timestamp}.csv"
        final_df.to_csv(output_file, index=False)
        print(f"\nExperiment completed. Results saved to {output_file}")
        
        return final_df

    def _load_base_config(self, config_dir: str, config_name: str) -> Dict[str, Any]:
        config_path = CONFIG_PATH / config_dir / f"{config_name}.json"
        return FileManager.read_json_file(config_path)

    def _inject_templates(self, config: Dict[str, Any]):
        """Load templates and inject them into the config."""
        template_name = config.get('templateFilename', 'prisoner_dilemma_noise') # Default fallback
        config['promptTemplate'] = {}
        
        for language in config.get('languages', ['en']):
            try:
                template_path = TEMPLATES_PATH / f"{template_name}_{language}.txt"
                content = FileManager.read_template_file(template_path)
                config['promptTemplate'][language] = content
            except Exception as e:
                print(f"Warning: Could not load template for {language}: {e}")
                
        # Remove templateFilename to satisfy schema validator if present (factory might check this)
        if 'templateFilename' in config:
            del config['templateFilename']

    def _apply_parameters(self, config: Dict[str, Any], params: Dict[str, Any]):
        """
        Apply parameter overrides to the config dict.
        Supports nested keys using dot notation (e.g. 'noiseConfig.agent1NoiseRate').
        """
        for key, value in params.items():
            parts = key.split('.')
            target = config
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            target[parts[-1]] = value
