import json
import copy

print("=== Recreating Notebooks - Simple Style (Y Chang Template) ===\n")

with open('kaggle_notebooks/triad-project.ipynb', 'r', encoding='utf-8') as f:
    template_nb = json.load(f)

print(f"Template loaded: {len(template_nb['cells'])} cells\n")

# ============================================
# MISTRAL7B
# ============================================
print("1. Creating mistral7b_experiments.ipynb...")
mistral_nb = copy.deepcopy(template_nb)

for i, cell in enumerate(mistral_nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    # Update CONFIG_FILE_PATH cell
    if 'CONFIG_FILE_PATH' in source and 'EDIT THIS LINE' in source:
        cell['source'] = 'import json\nCONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise00.json"  # <--- EDIT THIS LINE\n\nwith open(CONFIG_FILE_PATH, "r") as file:\n    config = json.load(file)\n\nMODEL_NAME = config["MODEL_NAME"]\n\nos.environ["VLLM_BASE_URL"] = "http://localhost:8000/v1"\nos.environ["VLLM_API_KEY"] = "EMPTY"'
        print(f"   Cell {i+1}: Updated CONFIG_FILE_PATH")
    
    # Update python main.py cell to use variable
    if '!python main.py' in source and 'experiment_configs' not in source:
        cell['source'] = '%cd /kaggle/working/TriAd_Project\n!export VLLM_BASE_URL="http://localhost:8000/v1"\n!export VLLM_API_KEY="EMPTY"\n\n# Chạy script experiment đã config ở trên\n!python main.py {CONFIG_FILE_PATH}'
        print(f"   Cell {i+1}: Updated to use {{CONFIG_FILE_PATH}}")

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(mistral_nb, f, indent=2, ensure_ascii=False)
print("   ✅ Saved\n")

# ============================================
# GPTOSS20B
# ============================================
print("2. Creating gptoss20b_experiments.ipynb...")
gptoss_nb = copy.deepcopy(template_nb)

for i, cell in enumerate(gptoss_nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    # Update CONFIG_FILE_PATH cell
    if 'CONFIG_FILE_PATH' in source and 'EDIT THIS LINE' in source:
        cell['source'] = 'import json\nCONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise00.json"  # <--- EDIT THIS LINE\n\nwith open(CONFIG_FILE_PATH, "r") as file:\n    config = json.load(file)\n\nMODEL_NAME = config["MODEL_NAME"]\n\nos.environ["VLLM_BASE_URL"] = "http://localhost:8000/v1"\nos.environ["VLLM_API_KEY"] = "EMPTY"'
        print(f"   Cell {i+1}: Updated CONFIG_FILE_PATH")
    
    # Update python main.py cell to use variable
    if '!python main.py' in source and 'experiment_configs' not in source:
        cell['source'] = '%cd /kaggle/working/TriAd_Project\n!export VLLM_BASE_URL="http://localhost:8000/v1"\n!export VLLM_API_KEY="EMPTY"\n\n# Chạy script experiment đã config ở trên\n!python main.py {CONFIG_FILE_PATH}'
        print(f"   Cell {i+1}: Updated to use {{CONFIG_FILE_PATH}}")

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(gptoss_nb, f, indent=2, ensure_ascii=False)
print("   ✅ Saved\n")

print("🎉 Done!")
print("Notebooks now y chang template:")
print("  Cell 3: CONFIG_FILE_PATH = '...'  # <--- EDIT THIS LINE")
print("  Cell 6: !python main.py {CONFIG_FILE_PATH}")
