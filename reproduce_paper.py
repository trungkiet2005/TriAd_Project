"""
Reproduce Paper Results - Project TRIAD

This script reproduces all experimental results reported in the UAI 2026 paper:
"Project TRIAD: The Trembling, Welfare, and Heroism Paradoxes in Multi-Agent LLM Systems"

Usage:
    # Full reproduction (requires API keys, ~48 hours)
    python reproduce_paper.py --mode full --max-workers 8

    # Quick validation with mock LLMs (~5 minutes)
    python reproduce_paper.py --mode mock --max-workers 4

    # Single paradox
    python reproduce_paper.py --mode trembling --max-workers 4
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from src.experiments.experiment_runner import ExperimentRunner

# Ensure resources are accessible
RESOURCES_PATH = Path(__file__).parent / "resources"
CONFIG_PATH = RESOURCES_PATH / "config"

def run_trembling_paradox_experiments(runner, use_mock=False):
    """
    Reproduce Trembling Paradox experiments (Section 4.1)
    Tests how noise affects cooperation in Prisoner's Dilemma
    """
    print("\n" + "="*70)
    print("TREMBLING PARADOX EXPERIMENTS")
    print("Testing cooperation under execution noise (ε ∈ {0.0, 0.1, 0.2})")
    print("="*70 + "\n")
    
    config_name = "prisoner_dilemma_3_mock" if use_mock else "prisoner_dilemma_3_default"
    
    # Sweep noise rates for all three agents
    param_grid = {
        'noiseConfig.agent1NoiseRate': [0.0, 0.1, 0.2],
        'noiseConfig.agent2NoiseRate': [0.0, 0.1, 0.2],
        'noiseConfig.agent3NoiseRate': [0.0, 0.1, 0.2]
    }
    
    results = runner.run_experiment(
        base_config_name=config_name,
        config_dir="prisoner_dilemma_3",
        parameter_grid=param_grid,
        experiment_name="trembling_paradox_analysis"
    )
    
    print(f"\n✓ Completed {len(results)} experimental runs")
    print(f"Results saved to: {runner.output_dir}/trembling_paradox_analysis_*.csv")
    
    # Calculate TRS (Trembling Robustness Score)
    if not results.empty:
        # Expected output: TRS calculation for each model
        print("\n--- Trembling Robustness Score (TRS) Preview ---")
        print("(Full analysis requires post-processing with run_analysis_example.py)")
        print(f"Sample cooperation rates by noise level:")
        if 'agent1NoiseRate' in results.columns and 'cooperation_rate' in results.columns:
            print(results.groupby('agent1NoiseRate')['cooperation_rate'].mean())
    
    return results


def run_welfare_paradox_experiments(runner, use_mock=False):
    """
    Reproduce Welfare Paradox experiments (Section 4.2)
    Tests exploitation dynamics in Public Goods Game
    """
    print("\n" + "="*70)
    print("WELFARE PARADOX EXPERIMENTS")
    print("Testing 'Toxic Kindness' and exploitation in Public Goods Game")
    print("="*70 + "\n")
    
    config_name = "public_goods_3_mock" if use_mock else "public_goods_3_default"
    
    # Focus on asymmetric personalities with moderate noise
    param_grid = {
        'noiseConfig.agent1NoiseRate': [0.1],  # Alice (Cooperative)
        'noiseConfig.agent2NoiseRate': [0.1],  # Bob (Selfish)
        'noiseConfig.agent3NoiseRate': [0.1],  # Charlie (Reciprocal)
        'n_rounds': [50]
    }
    
    results = runner.run_experiment(
        base_config_name=config_name,
        config_dir="public_goods_3",
        parameter_grid=param_grid,
        experiment_name="welfare_paradox_analysis"
    )
    
    print(f"\n✓ Completed {len(results)} experimental runs")
    print(f"Results saved to: {runner.output_dir}/welfare_paradox_analysis_*.csv")
    
    # Calculate Alignment Gap (Δ = φ - π)
    if not results.empty:
        print("\n--- Alignment Gap (Δ) Preview ---")
        print("(Full Shapley value calculation requires post-processing)")
        if 'total_payoff' in results.columns:
            print(f"Average payoff distribution:")
            print(results[['agent_name', 'total_payoff']].groupby('agent_name').mean())
    
    return results


def run_heroism_paradox_experiments(runner, use_mock=False):
    """
    Reproduce Heroism Paradox experiments (Section 4.3)
    Tests coordination failures in Volunteer's Dilemma
    """
    print("\n" + "="*70)
    print("HEROISM PARADOX EXPERIMENTS")
    print("Testing strategic waiting and bystander effects in Volunteer's Dilemma")
    print("="*70 + "\n")
    
    config_name = "volunteers_dilemma_3_mock" if use_mock else "volunteers_dilemma_3_default"
    
    # Minimal noise (focus on strategic reasoning)
    param_grid = {
        'noiseConfig.agent1NoiseRate': [0.0, 0.05],
        'noiseConfig.agent2NoiseRate': [0.0, 0.05],
        'noiseConfig.agent3NoiseRate': [0.0, 0.05],
        'n_rounds': [50]
    }
    
    results = runner.run_experiment(
        base_config_name=config_name,
        config_dir="volunteers_dilemma_3",
        parameter_grid=param_grid,
        experiment_name="heroism_paradox_analysis"
    )
    
    print(f"\n✓ Completed {len(results)} experimental runs")
    print(f"Results saved to: {runner.output_dir}/heroism_paradox_analysis_*.csv")
    
    # Calculate catastrophic failure rate (no volunteers)
    if not results.empty:
        print("\n--- Coordination Failure Preview ---")
        print("(Detailed timing analysis requires post-processing)")
        # Approximation: count rounds with no volunteers
        # (Actual implementation depends on result schema)
        print("Failure rate analysis available in detailed logs")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce results from Project TRIAD paper (UAI 2026)"
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'mock', 'trembling', 'welfare', 'heroism'],
        default='mock',
        help="Experiment mode: full (all experiments, real LLMs), "
             "mock (quick validation), or single paradox"
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help="Number of parallel game threads (default: 4)"
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default="paper_reproduction_results",
        help="Directory for output results"
    )
    
    args = parser.parse_args()
    
    # Check if configs exist
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config directory not found at {CONFIG_PATH}")
        print("Please ensure you're running from the project root directory.")
        sys.exit(1)
    
    use_mock = (args.mode == 'mock')
    
    # Setup output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir) / f"run_{timestamp}"
    
    print("\n" + "="*70)
    print("PROJECT TRIAD - PAPER REPRODUCTION")
    print("="*70)
    print(f"Mode: {args.mode.upper()}")
    print(f"Max workers: {args.max_workers}")
    print(f"Output directory: {output_dir}")
    print(f"Using {'MOCK' if use_mock else 'REAL'} LLM connectors")
    print("="*70 + "\n")
    
    if not use_mock:
        print("⚠️  WARNING: Running with real LLM APIs")
        print("   - Ensure API keys are set in .env file")
        print("   - Estimated cost: ~$500-1200 depending on models")
        print("   - Estimated time: 24-48 hours")
        response = input("\nContinue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted by user.")
            sys.exit(0)
    
    # Initialize experiment runner
    runner = ExperimentRunner(
        output_dir=str(output_dir),
        max_workers=args.max_workers
    )
    
    # Run experiments based on mode
    all_results = []
    
    if args.mode in ['full', 'trembling']:
        results = run_trembling_paradox_experiments(runner, use_mock)
        all_results.append(('trembling', results))
    
    if args.mode in ['full', 'welfare']:
        results = run_welfare_paradox_experiments(runner, use_mock)
        all_results.append(('welfare', results))
    
    if args.mode in ['full', 'heroism']:
        results = run_heroism_paradox_experiments(runner, use_mock)
        all_results.append(('heroism', results))
    
    if args.mode == 'mock':
        # Run quick version of all three
        print("\n📋 MOCK MODE: Running abbreviated versions of all experiments\n")
        run_trembling_paradox_experiments(runner, use_mock=True)
        run_welfare_paradox_experiments(runner, use_mock=True)
        run_heroism_paradox_experiments(runner, use_mock=True)
    
    # Summary
    print("\n" + "="*70)
    print("REPRODUCTION COMPLETE")
    print("="*70)
    print(f"\n✓ All results saved to: {output_dir}")
    print(f"\nNext steps:")
    print(f"1. Analyze results:")
    print(f"   python run_analysis_example.py --input {output_dir}")
    print(f"\n2. Generate figures:")
    print(f"   python generate_figures.py --input {output_dir}")
    print(f"\n3. Compile paper:")
    print(f"   cd uai2026-template/uai2026-template")
    print(f"   pdflatex submission.tex && bibtex submission && pdflatex submission.tex\n")
    
    if use_mock:
        print("⚠️  Note: Mock mode uses deterministic placeholder LLM.")
        print("   For paper-quality results, rerun with --mode full")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
