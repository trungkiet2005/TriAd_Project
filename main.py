"""
Main Experiment Runner

Reads all JSON configuration files from 'experiment_configs' and executes them.
Usage:
    python main.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.io_managers.file_manager import FileManager
from src.noise_fairgame_factory import NoiseFairGameFactory
from src.checkers.time_checker import TimeChecker
from src.checkers.rule_checker import RuleChecker
from src.checkers.aggregation_checker import AggregationChecker

# Load environment variables (API keys)
load_dotenv()

# String 'http://localhost:8000/v1' or 'https://api.openai.com/v1'
# Ensure these are set correctly for your environment
os.environ["VLLM_BASE_URL"] = "https://1888-34-172-165-37.ngrok-free.app"
os.environ["VLLM_API_KEY"] = "EMPTY" 


def main():
    print(f"--- Starting Experiment Runner ---")
    
    # Locate experiment_configs directory
    config_dir = Path(__file__).parent / "experiment_configs"
    if not config_dir.exists():
        print(f"Error: Config directory not found: {config_dir}")
        print("Please run generate_configs.py first.")
        return

    # Find all JSON config files
    config_files = list(config_dir.glob("*.json"))
    if not config_files:
        print(f"No .json files found in {config_dir}")
        return

    print(f"Found {len(config_files)} config files in {config_dir}")

    # Initialize checkers (these are stateless or reset per game in factory)
    checkers = [TimeChecker(), RuleChecker(), AggregationChecker()]

    for i, config_file in enumerate(config_files):
        print(f"\n[{i+1}/{len(config_files)}] Loading config: {config_file.name}")
        try:
            # Load configuration
            config = FileManager.read_json_file(config_file)
            
            # Extract LLM display name for factory/output purposes
            llm_name = config.get('llmDisplayName', config.get('llm', 'UnknownLLM'))
            
            # Create Factory
            factory = NoiseFairGameFactory(
                checkers=checkers,
                llm_name=llm_name
            )

            print(f"Running games for {llm_name}...")
            # Run the experiment defined in this config
            factory.create_and_run_games(config)
            
            print(f"Completed {config_file.name}")
            
        except Exception as e:
            print(f"Error processing {config_file.name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n--- All Experiments Complete ---")

if __name__ == "__main__":
    main()
