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

# ==========================================
#        MANUAL CONFIGURATION
# ==========================================
# Set this to the path of the config file you want to run.
# If set, this takes precedence over command line arguments and auto-discovery.
# Example: "experiment_configs/llama70b_noise00.json"
CONFIG_FILE_PATH = "experiment_configs/test.json"  # <--- EDIT THIS LINE


def main():
    print(f"--- Starting Experiment Runner ---")
    
    # Determine which config(s) to run
    config_files = []
    
    # 1. Check Manual Config Variable
    if CONFIG_FILE_PATH:
        path = Path(CONFIG_FILE_PATH)
        if path.exists():
            config_files = [path]
            print(f"Running manual config defined in script: {path.name}")
        else:
            print(f"Error: Manual config file not found: {path} (Check CONFIG_FILE_PATH)")
            return
            
    # 2. Check Command Line Argument (if no manual config set)
    elif len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}")
            return
        config_files = [config_path]
        print(f"Running single config from argument: {config_path.name}")
        
    # 3. Default: Run All Files in experiment_configs
    else:
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
        
        print(f"No config file specified. Running ALL {len(config_files)} files in {config_dir}")

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
