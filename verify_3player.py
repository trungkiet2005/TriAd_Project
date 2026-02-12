
import sys
import os
import shutil
from pathlib import Path

# Enable importing from src
sys.path.insert(0, str(Path(__file__).parent))

# Mock missing LLM libraries to avoid ImportErrors
from unittest.mock import MagicMock
sys.modules['anthropic'] = MagicMock()
sys.modules['mistralai'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['vllm'] = MagicMock()
sys.modules['striprtf'] = MagicMock()
sys.modules['striprtf.striprtf'] = MagicMock()

from src.noise_fairgame_factory import NoiseFairGameFactory

def verify_3player_execution():
    print("--- Starting 3-Player Verification with Mock LLM ---")
    
    # Define a test configuration based on pd3_base.json
    config = {
        "name": "Verify3Player",
        "description": "Verification run for 3-player logic",
        "nPlayers": 3,
        "nRounds": 2,
        "nRoundsIsKnown": True,
        "isPenalty": True,
        "agentsCommunicate": False,
        "allAgentPermutations": False, # Just run the agents as defined
        "stopGameWhen": [],
        "checkers": [], # No checkers for speed
        "llm": "MockLLM", # Uses MockConnector
        "languages": ["en"],
        "repeats": 1,
        "agents": {
            "names": ["agent1", "agent2", "agent3"],
            "personalities": {
                "en": ["selfish", "cooperative", "mixed"]
            },
            "opponentPersonalityProb": [100, 100, 100]
        },
        "noiseConfig": {
            "agent1NoiseRate": 0.05,
            "agent2NoiseRate": 0.05,
            "agent3NoiseRate": 0.05
        },
        "payoffMatrix": {
            "weights": {
                "weight_P": 8, "weight_T1": 4, "weight_T2": 0,
                "weight_S0": 10, "weight_S1": 5, "weight_R": 2
            },
            "strategies": {
                "en": {"strategy1": "Defect", "strategy2": "Cooperate"}
            },
            "combinations": {
                "DDD": ["strategy1", "strategy1", "strategy1"],
                "DDC": ["strategy1", "strategy1", "strategy2"],
                "DCD": ["strategy1", "strategy2", "strategy1"],
                "DCC": ["strategy1", "strategy2", "strategy2"],
                "CDD": ["strategy2", "strategy1", "strategy1"],
                "CDC": ["strategy2", "strategy1", "strategy2"],
                "CCD": ["strategy2", "strategy2", "strategy1"],
                "CCC": ["strategy2", "strategy2", "strategy2"]
            },
            "matrix": {
                "DDD": ["weight_P", "weight_P", "weight_P"],
                "DDC": ["weight_P", "weight_P", "weight_S0"],
                "DCD": ["weight_P", "weight_S0", "weight_P"],
                "DCC": ["weight_T1", "weight_S1", "weight_S1"],
                "CDD": ["weight_S0", "weight_P", "weight_P"],
                "CDC": ["weight_S1", "weight_T1", "weight_S1"],
                "CCD": ["weight_S1", "weight_S1", "weight_T1"],
                "CCC": ["weight_R", "weight_R", "weight_R"]
            }
        },
        "promptTemplate": {
             "en": "Test Prompt for {currentPlayerName}. History: {history}"
        }
    }
    
    # Output directory
    output_dir = Path("test_verify_results")
    if output_dir.exists():
        try:
            shutil.rmtree(output_dir)
            print(f"Cleaned output directory: {output_dir}")
        except Exception as e:
            print(f"Warning: Could not clean output directory: {e}")
            
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Create Factory
        # Using output_dir directly. Factory creates subfolders based on llm/noise.
        # We set llm_name="mock_llm" to ensure folder name is predictable
        factory = NoiseFairGameFactory(
            checkers=[],
            output_dir=output_dir,
            llm_name="mock_llm", 
            max_workers=1 # Sequential for safety
        )
        
        # Run
        print("Creating and running games...")
        results = factory.create_and_run_games(config)
        
        print(f"Verification completed. Ran {len(results)} games.")
        print(f"Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_3player_execution()
