"""
Script to run extensive experiments on Kaggle/local.
Configuration:
- 6 Languages: en, fr, ar, cn, vn, it
- 3 Noise Levels: 0%, 5%, 20%
- 40 Repeats per condition
- 30 Rounds per game
- H100 GPU optimized (parallel workers)
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.noise_fairgame_factory import NoiseFairGameFactory
from src.checkers.time_checker import TimeChecker
from src.checkers.rule_checker import RuleChecker
from src.checkers.aggregation_checker import AggregationChecker
from src.io_managers.file_manager import FileManager

# --- CONFIGURATION ---
LANGUAGES = ["en", "fr", "ar", "cn", "vn", "it"]
NOISE_LEVELS = [0.0, 0.05, 0.2]  # 0%, 5%, 20%
ROUNDS = 30
REPEATS = 40
MAX_WORKERS = 16  # H100 has many cores, can increase this
LLM_NAME = "VLLMQwen"
LLM_DISPLAY_NAME = "Qwen2_5_32B_Instruct"
CONFIG_DIR = "prisoner_dilemma_noise"
BASE_CONFIG_NAME = "pd_noise_round_known_mild"

def load_base_config():
    """Load the base configuration file."""
    config_path = Path(f"resources/config/{CONFIG_DIR}/{BASE_CONFIG_NAME}.json")
    return FileManager.read_json_file(config_path)

def run_experiments():
    print(f"Starting Experiments...")
    print(f"Languages: {LANGUAGES}")
    print(f"Noise Levels: {NOISE_LEVELS}")
    print(f"Rounds: {ROUNDS}")
    print(f"Repeats: {REPEATS}")
    
    base_config = load_base_config()
    
    # Load templates for all languages upfront
    prompt_templates = {}
    template_name = base_config.get('templateFilename', 'prisoner_dilemma_noise')
    for lang in LANGUAGES:
        try:
            template_content = FileManager.read_template_file(
                Path(f"resources/game_templates/prisoner_dilemma_2/prisoner_dilemma_2_{lang}.txt")
            )
            prompt_templates[lang] = template_content
        except Exception as e:
            print(f"Error loading template for {lang}: {e}")
            return

    # Initialize checkers (shared instance or new per run? Factory takes classes or instances?)
    # Factory takes instances.
    # We should create new instances per factory run to avoid state leakage if any.
    
    for noise in NOISE_LEVELS:
        print(f"\n{'='*50}")
        print(f"RUNNING NOISE LEVEL: {noise*100:.0f}%")
        print(f"{'='*50}")
        
        # Prepare configuration for this noise level
        # We run all languages together for this noise level 
        # (or separate if we want granular folders? Factory separates by LLM_Languages_Noise)
        # If we pass all languages, factory creates one folder "en_multi/noiseXX".
        # If we want separate folders per language "en/noiseXX", "fr/noiseXX", loop languages.
        # User request didn't specify folder structure, but separate might be safer for analysis.
        # Let's run all languages together to keep "multi-lingual" context if needed (though games are separate).
        # Actually, factory groups by passed languages list.
        # Let's run per language to be safe and modular.
        
        for lang in LANGUAGES:
            print(f"\n--- Language: {lang} | Noise: {noise} ---")
            
            current_config = base_config.copy()
            current_config['nRounds'] = ROUNDS
            current_config['languages'] = [lang]
            current_config['llm'] = LLM_NAME
            current_config['llmDisplayName'] = LLM_DISPLAY_NAME
            current_config['repeats'] = REPEATS
            current_config['promptTemplate'] = {lang: prompt_templates[lang]}
            if 'templateFilename' in current_config:
                del current_config['templateFilename']
            
            # Set noise
            current_config['noiseConfig'] = {
                'agent1NoiseRate': noise,
                'agent2NoiseRate': noise
            }
            
            # Create checkers
            checkers = [TimeChecker(), RuleChecker(), AggregationChecker()]
            
            # Run factory
            try:
                factory = NoiseFairGameFactory(
                    checkers=checkers, 
                    max_workers=MAX_WORKERS,
                    llm_name=LLM_DISPLAY_NAME
                )
                factory.create_and_run_games(current_config)
            except Exception as e:
                print(f"ERROR running {lang} noise {noise}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    run_experiments()
