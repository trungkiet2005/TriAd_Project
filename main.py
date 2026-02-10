"""
Main Experiment Runner

Configure your experiment in the section below and run this script:
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


#String 'http://localhost:8000/v1' or 'https://api.openai.com/v1'
os.environ["VLLM_BASE_URL"] = "https://0d56-34-6-87-147.ngrok-free.app"
os.environ["VLLM_API_KEY"] = "EMPTY" 

# ==========================================
#              CONFIGURATION
# ==========================================

# 1. Languages to run (list of codes: 'en', 'vn', 'fr', 'cn', 'ar', 'it')
LANGUAGES = ['vn']

# 2. LLM Configuration
LLM_NAME = "VLLMQwen"
LLM_DISPLAY_NAME = "Qwen2.5-32B-Instruct"

# 3. Noise Configuration (0.0 to 1.0)
AGENT1_NOISE_RATE = 0.0
AGENT2_NOISE_RATE = 0.0

# 4. Experiment Settings
NUM_MATCHES = 2        # Number of times to repeat the game (repeats)
NUM_ROUNDS = 10         # Number of rounds per match

# 5. Template Configuration
# Base configuration file to inherit from (defines payoff matrix, agents, etc.)
# Located in resources/config/prisoner_dilemma_noise/
BASE_CONFIG_NAME = "pd_noise_round_known_mild" 
CONFIG_DIR = "prisoner_dilemma_noise"

# Template base name for prompt files
TEMPLATE_NAME = "prisoner_dilemma_noise"

# 6. Checkers (Hallucination Detection)
ENABLE_CHECKERS = True
CHECKERS_List = ['time', 'rule', 'aggregation']




def load_base_config():
    """Load the base configuration file."""
    config_path = Path(__file__).parent / "resources" / "config" / CONFIG_DIR / f"{BASE_CONFIG_NAME}.json"
    print(f"Loading base config from: {config_path}")
    return FileManager.read_json_file(config_path)

def load_template_content(template_base_name, language):
    """Load template content for a specific language."""
    # Try multiple paths since template naming might vary
    paths_to_try = [
        Path(__file__).parent / "resources" / "game_templates" / "prisoner_dilemma_2" / f"{template_base_name}_{language}.txt",
        Path(__file__).parent / "resources" / "game_templates" / "prisoner_dilemma_2" / f"prisoner_dilemma_2_{language}.txt" # Fallback to standard name
    ]
    
    for path in paths_to_try:
        if path.exists():
            return FileManager.read_template_file(path)
            
    print(f"Warning: Could not find template for {language}. Checked: {[str(p) for p in paths_to_try]}")
    return None

def main():
    print(f"--- Starting Experiment Runner ---")
    print(f"Languages: {LANGUAGES}")
    print(f"Model: {LLM_DISPLAY_NAME}")
    print(f"Noise: Agent1={AGENT1_NOISE_RATE}, Agent2={AGENT2_NOISE_RATE}")
    print(f"Settings: {NUM_MATCHES} matches, {NUM_ROUNDS} rounds")
    
    # 1. Load Base Config
    try:
        config = load_base_config()
    except Exception as e:
        print(f"Error loading base config: {e}")
        return

    # 2. Apply Overrides from Configuration Section
    config['nRounds'] = NUM_ROUNDS
    config['repeats'] = NUM_MATCHES
    config['languages'] = LANGUAGES
    config['llm'] = LLM_NAME
    config['llmDisplayName'] = LLM_DISPLAY_NAME
    
    # Update Noise Config
    if 'noiseConfig' not in config:
        config['noiseConfig'] = {}
    config['noiseConfig']['agent1NoiseRate'] = AGENT1_NOISE_RATE
    config['noiseConfig']['agent2NoiseRate'] = AGENT2_NOISE_RATE
    
    # Update Checkers
    config['enableHallucinationChecks'] = ENABLE_CHECKERS
    config['checkers'] = CHECKERS_List
    
    # Disable early stopping (base config stops when both cooperate)
    check_stop = config.get('stopGameWhen', [])
    if check_stop:
        print(f"Overriding stop condition (was {check_stop}) to run full {NUM_ROUNDS} rounds.")
        config['stopGameWhen'] = []
    
    # 3. Load Templates
    prompt_templates = {}
    for lang in LANGUAGES:
        content = load_template_content(TEMPLATE_NAME, lang)
        if content:
            prompt_templates[lang] = content
        else:
            print(f"Skipping {lang} due to missing template.")
            
    if not prompt_templates:
        print("No valid templates found. Exiting.")
        return
        
    config['promptTemplate'] = prompt_templates
    
    # Remove templateFilename if it exists to avoid validation conflict (XOR rule)
    if 'templateFilename' in config:
        del config['templateFilename']
    
    # 4. Initialize Factory and Run
    checkers = []
    if ENABLE_CHECKERS:
        if 'time' in CHECKERS_List: checkers.append(TimeChecker())
        if 'rule' in CHECKERS_List: checkers.append(RuleChecker())
        if 'aggregation' in CHECKERS_List: checkers.append(AggregationChecker())
    
    factory = NoiseFairGameFactory(
        checkers=checkers,
        llm_name=LLM_DISPLAY_NAME
    )

    print("\nRunning games...")
    try:
        results = factory.create_and_run_games(config)
        
        # Save results manually to ensure we have a record
        from datetime import datetime
        import json
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent / "resources" / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = results_dir / f"manual_run_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\nExperiment complete! Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
