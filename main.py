"""
Nicer Fairgame Combined - Main Entry Point

Fairgame framework with nicer_than_human features:
- Multi-agent Prisoner's Dilemma
- Noise injection with configurable rates
- Hallucination tracking via comprehension questions
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.io_managers.file_manager import FileManager
from src.results_processing.results_processor import ResultsProcessor
from src.noise_fairgame_factory import NoiseFairGameFactory
from src.checkers.time_checker import TimeChecker
from src.checkers.rule_checker import RuleChecker
from src.checkers.aggregation_checker import AggregationChecker
from src.game.payoff_matrix import PayoffMatrix

RESOURCES_PATH = Path(__file__).parent / "resources"
TEMPLATES_PATH = RESOURCES_PATH / "game_templates"
CONFIG_PATH = RESOURCES_PATH / "config"
RESULTS_PATH = RESOURCES_PATH / "results"


def load_env_variables() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Prisoner's Dilemma games with noise and hallucination tracking"
    )
    parser.add_argument(
        'call_type',
        choices=['local', 'api'],
        help="Whether to run locally or via API"
    )
    parser.add_argument(
        '--config',
        default='pd_noise_round_known_mild',
        help="Name of the config file (without .json extension)"
    )
    parser.add_argument(
        '--config-dir',
        default='prisoner_dilemma_noise',
        help="Directory containing the config file"
    )
    parser.add_argument(
        '--noise1',
        type=float,
        help="Override noise rate for agent1 (0.0-1.0)"
    )
    parser.add_argument(
        '--noise2',
        type=float,
        help="Override noise rate for agent2 (0.0-1.0)"
    )
    parser.add_argument(
        '--rounds',
        type=int,
        help="Override number of rounds"
    )
    parser.add_argument(
        '--enable-checkers',
        action='store_true',
        default=False,
        help="Enable hallucination checking"
    )
    parser.add_argument(
        '--checkers',
        nargs='+',
        choices=['time', 'rule', 'aggregation'],
        default=['time', 'rule', 'aggregation'],
        help="Which checkers to enable"
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help="Maximum number of parallel game threads (default: 4)"
    )
    
    return parser.parse_args()


def load_template_file(template_name: str, language: str) -> str:
    """Load a game template file."""
    template_filepath = TEMPLATES_PATH / f"{template_name}_{language}.txt"
    return FileManager.read_template_file(template_filepath)


def load_config_file(config_dir: str, config_name: str) -> Dict[str, Any]:
    """Load a JSON config file."""
    config_filepath = CONFIG_PATH / config_dir / f"{config_name}.json"
    return FileManager.read_json_file(config_filepath)


def apply_cli_overrides(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Apply command line overrides to config."""
    if args.noise1 is not None:
        config.setdefault('noiseConfig', {})
        config['noiseConfig']['agent1NoiseRate'] = args.noise1
    
    if args.noise2 is not None:
        config.setdefault('noiseConfig', {})
        config['noiseConfig']['agent2NoiseRate'] = args.noise2
    
    if args.rounds is not None:
        config['nRounds'] = args.rounds
    
    if args.enable_checkers:
        config['enableHallucinationChecks'] = True
        config['checkers'] = args.checkers
    
    return config


def get_checkers(checker_names: list) -> list:
    """Get checker instances by name."""
    checkers = []
    checker_map = {
        'time': TimeChecker,
        'rule': RuleChecker,
        'aggregation': AggregationChecker
    }
    
    for name in checker_names:
        if name in checker_map:
            checkers.append(checker_map[name]())
    
    return checkers


def save_results(results: Dict[str, Any], config_name: str) -> None:
    """Save results to CSV and JSON files."""
    import json
    
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    
    # Save JSON results
    results_json_path = RESULTS_PATH / f"results_{config_name}.json"
    with open(results_json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {results_json_path}")
    
    # Save CSV format
    try:
        results_processor = ResultsProcessor()
        df = results_processor.process(results)
        results_csv_path = RESULTS_PATH / f"results_{config_name}.csv"
        FileManager.save_results_csv(df, results_csv_path)
        print(f"CSV results saved to {results_csv_path}")
    except Exception as e:
        print(f"Warning: Could not save CSV - {e}")


def print_noise_report(results: Dict[str, Any]) -> None:
    """Print a summary of noise events."""
    print("\n" + "="*50)
    print("NOISE REPORT")
    print("="*50)
    
    for game_key, game_data in results.items():
        print(f"\n{game_key}:")
        noise_report = game_data.get('noise_report', {})
        
        for agent_name, agent_noise in noise_report.items():
            noise_rate = agent_noise.get('noise_rate', 0) * 100
            times_flipped = agent_noise.get('times_flipped', 0)
            total_rounds = agent_noise.get('total_rounds', 0)
            
            print(f"  {agent_name}:")
            print(f"    Noise rate: {noise_rate:.1f}%")
            print(f"    Times flipped: {times_flipped}/{total_rounds}")
            if agent_noise.get('noise_events'):
                flip_rounds = [i+1 for i, flipped in enumerate(agent_noise['noise_events']) if flipped]
                if flip_rounds:
                    print(f"    Flipped in rounds: {flip_rounds}")


def main() -> None:
    """Main entry point."""
    load_env_variables()
    args = parse_arguments()
    
    print(f"Running Prisoner's Dilemma with Noise")
    print(f"Mode: {args.call_type} | Config: {args.config}")
    
    # Load config
    config = load_config_file(args.config_dir, args.config)
    config = apply_cli_overrides(config, args)
    
    # Load template
    template_name = config.get('templateFilename', 'prisoner_dilemma_noise')
    config['promptTemplate'] = {}
    
    for language in config['languages']:
        try:
            template_content = load_template_file(template_name, language)
            config['promptTemplate'][language] = template_content
        except Exception as e:
            print(f"Warning: Could not load template for {language}: {e}")
    
    # Remove templateFilename (validator requires XOR with promptTemplate)
    config.pop('templateFilename', None)
    
    # Print noise config
    noise_config = config.get('noiseConfig', {})
    print(f"Agent1 noise rate: {noise_config.get('agent1NoiseRate', 0)*100:.1f}%")
    print(f"Agent2 noise rate: {noise_config.get('agent2NoiseRate', 0)*100:.1f}%")
    print(f"Rounds: {config['nRounds']}")
    
    # Create checkers if enabled
    checkers = []
    if config.get('enableHallucinationChecks', False):
        checker_names = config.get('checkers', ['time', 'rule', 'aggregation'])
        checkers = get_checkers(checker_names)
        print(f"Hallucination checkers enabled: {[c.name for c in checkers]}")
    
    # Run games
    factory = NoiseFairGameFactory(checkers=checkers, max_workers=args.max_workers)
    results = factory.create_and_run_games(config)
    
    # Print noise report
    print_noise_report(results)
    
    # Save results
    save_results(results, args.config)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
