import json

print("=== Updating Model Names in Notebooks ===\n")

# ============================================
# UPDATE MISTRAL7B NOTEBOOK
# ============================================
print("1. Updating mistral7b_experiments.ipynb...")

with open('mistral7b_experiments.ipynb', 'r', encoding='utf-8') as f:
    mistral_nb = json.load(f)

# Find Cell 3 (index 2) which contains MODEL_NAME
for i, cell in enumerate(mistral_nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Check if this cell contains MODEL_NAME
        if 'MODEL_NAME' in source and 'import json' in source:
            print(f"   Found MODEL_NAME in cell {i+1}")
            
            # Update the source - Cell 3 loads config and sets MODEL_NAME
            new_source = """import json
CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise00.json"

with open(CONFIG_FILE_PATH, "r") as file:
    config = json.load(file)

MODEL_NAME = config["MODEL_NAME"]

os.environ["VLLM_BASE_URL"] = "http://localhost:8000/v1"
os.environ["VLLM_API_KEY"] = "EMPTY"

print(f"Model: {MODEL_NAME}")
print(f"Config: {CONFIG_FILE_PATH}")"""
            
            cell['source'] = new_source
            print(f"   ✅ Updated to use MODEL_NAME from config: mistralai/Mistral-7B-Instruct-v0.3")
            break

# Save updated notebook
with open('mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(mistral_nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved mistral7b_experiments.ipynb\n")

# ============================================
# UPDATE GPTOSS20B NOTEBOOK
# ============================================
print("2. Updating gptoss20b_experiments.ipynb...")

with open('gptoss20b_experiments.ipynb', 'r', encoding='utf-8') as f:
    gptoss_nb = json.load(f)

# Find Cell 3 (index 2) which contains MODEL_NAME
for i, cell in enumerate(gptoss_nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Check if this cell contains MODEL_NAME
        if 'MODEL_NAME' in source and 'import json' in source:
            print(f"   Found MODEL_NAME in cell {i+1}")
            
            # Update the source - Cell 3 loads config and sets MODEL_NAME
            new_source = """import json
CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise00.json"

with open(CONFIG_FILE_PATH, "r") as file:
    config = json.load(file)

MODEL_NAME = config["MODEL_NAME"]

os.environ["VLLM_BASE_URL"] = "http://localhost:8000/v1"
os.environ["VLLM_API_KEY"] = "EMPTY"

print(f"Model: {MODEL_NAME}")
print(f"Config: {CONFIG_FILE_PATH}")"""
            
            cell['source'] = new_source
            print(f"   ✅ Updated to use MODEL_NAME from config: openai/gpt-oss-20b")
            break

# Save updated notebook
with open('gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(gptoss_nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved gptoss20b_experiments.ipynb\n")

print("🎉 Done! Both notebooks now load MODEL_NAME from config files.")
print("   - mistral7b will use: mistralai/Mistral-7B-Instruct-v0.3")
print("   - gptoss20b will use: openai/gpt-oss-20b")
