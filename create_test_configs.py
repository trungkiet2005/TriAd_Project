import json
import copy

print("=== Creating Comprehensive Test Configs ===\n")

# Load gptoss20b_noise00.json as base template (has full structure)
with open('experiment_configs/2_player/gptoss20b_noise00.json', 'r', encoding='utf-8') as f:
    base_config = json.load(f)

# Test config modifications: fewer rounds + repeats for quick testing
TEST_OVERRIDES = {
    "nRounds": 3,
    "repeats": 1,
    "checkerEveryNRounds": 3
}

# Define all test configs to create
configs = [
    # GPT-OSS-20B
    {
        "filename": "gptoss20b_test.json",
        "name": "TEST - openai/gpt-oss-20b Noise 0.0",
        "llm": "VLLMGptOss20B",
        "MODEL_NAME": "openai/gpt-oss-20b",
        "llmDisplayName": "openai/gpt-oss-20b",
        "noise": {"agent1NoiseRate": 0.0, "agent2NoiseRate": 0.0}
    },
    {
        "filename": "gptoss20b_test_noise05.json",
        "name": "TEST - openai/gpt-oss-20b Noise 0.05",
        "llm": "VLLMGptOss20B",
        "MODEL_NAME": "openai/gpt-oss-20b",
        "llmDisplayName": "openai/gpt-oss-20b",
        "noise": {"agent1NoiseRate": 0.05, "agent2NoiseRate": 0.05}
    },
    {
        "filename": "gptoss20b_test_noise20.json",
        "name": "TEST - openai/gpt-oss-20b Noise 0.2",
        "llm": "VLLMGptOss20B",
        "MODEL_NAME": "openai/gpt-oss-20b",
        "llmDisplayName": "openai/gpt-oss-20b",
        "noise": {"agent1NoiseRate": 0.2, "agent2NoiseRate": 0.2}
    },
    # Mistral-7B
    {
        "filename": "mistral7b_test.json",
        "name": "TEST - mistralai/Mistral-7B Noise 0.0",
        "llm": "VLLMMistral7B",
        "MODEL_NAME": "mistralai/Mistral-7B-Instruct-v0.3",
        "llmDisplayName": "mistralai/Mistral-7B-Instruct-v0.3",
        "noise": {"agent1NoiseRate": 0.0, "agent2NoiseRate": 0.0}
    },
    {
        "filename": "mistral7b_test_noise05.json",
        "name": "TEST - mistralai/Mistral-7B Noise 0.05",
        "llm": "VLLMMistral7B",
        "MODEL_NAME": "mistralai/Mistral-7B-Instruct-v0.3",
        "llmDisplayName": "mistralai/Mistral-7B-Instruct-v0.3",
        "noise": {"agent1NoiseRate": 0.05, "agent2NoiseRate": 0.05}
    },
    {
        "filename": "mistral7b_test_noise20.json",
        "name": "TEST - mistralai/Mistral-7B Noise 0.2",
        "llm": "VLLMMistral7B",
        "MODEL_NAME": "mistralai/Mistral-7B-Instruct-v0.3",
        "llmDisplayName": "mistralai/Mistral-7B-Instruct-v0.3",
        "noise": {"agent1NoiseRate": 0.2, "agent2NoiseRate": 0.2}
    },
]

for cfg in configs:
    test_config = copy.deepcopy(base_config)
    
    # Apply test overrides
    test_config.update(TEST_OVERRIDES)
    
    # Apply model-specific settings
    test_config["name"] = cfg["name"]
    test_config["llm"] = cfg["llm"]
    test_config["MODEL_NAME"] = cfg["MODEL_NAME"]
    test_config["llmDisplayName"] = cfg["llmDisplayName"]
    test_config["noiseConfig"] = cfg["noise"]
    
    # Write file
    filepath = f'experiment_configs/2_player/{cfg["filename"]}'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    noise_str = cfg["noise"]["agent1NoiseRate"]
    print(f"✅ {cfg['filename']:40s} | {cfg['llmDisplayName']:40s} | noise={noise_str}")

print(f"\n🎉 Created {len(configs)} test configs")
print(f"   - nRounds: {TEST_OVERRIDES['nRounds']} (vs 30 in full)")
print(f"   - repeats: {TEST_OVERRIDES['repeats']} (vs 10 in full)")
print(f"   - All 6 languages: en, fr, ar, cn, vn, it")
print(f"   - allAgentPermutations: true")
