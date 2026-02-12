import json
import copy

print("=== Recreating Notebooks from triad-project.ipynb Template ===\n")

# Load the template notebook
with open('kaggle_notebooks/triad-project.ipynb', 'r', encoding='utf-8') as f:
    template_nb = json.load(f)

print(f"✅ Loaded template with {len(template_nb['cells'])} cells\n")

# ============================================
# CREATE MISTRAL7B NOTEBOOK
# ============================================
print("1. Creating mistral7b_experiments.ipynb from template...")

mistral_nb = copy.deepcopy(template_nb)

# Find and update cells
for i, cell in enumerate(mistral_nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Cell with imports - add config variables after it
        if i == 1 and 'import os' in source and 'import subprocess' in source:
            # Insert config cell after this one
            config_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": "# Configuration paths for Mistral-7B experiments\nCONFIG_NOISE_00 = \"experiment_configs/mistral7b_noise00.json\"\nCONFIG_NOISE_05 = \"experiment_configs/mistral7b_noise05.json\"\nCONFIG_NOISE_20 = \"experiment_configs/mistral7b_noise20.json\"\n\nprint(f\"Config paths defined for Mistral-7B\")\nprint(f\"  - Noise 0.0: {CONFIG_NOISE_00}\")\nprint(f\"  - Noise 0.05: {CONFIG_NOISE_05}\")\nprint(f\"  - Noise 0.2: {CONFIG_NOISE_20}\")"
            }
            mistral_nb['cells'].insert(i + 1, config_cell)
            print(f"   Added config variables cell")
            
        # Update vLLM server cell
        if 'STARTING VLLM SERVER' in source:
            cell['source'] = cell['source'].replace(
                'Qwen/Qwen2.5-32B-Instruct',
                'mistralai/Mistral-7B-Instruct-v0.3'
            ).replace(
                'Qwen2.5-32B-Instruct',
                'Mistral-7B-Instruct-v0.3'
            )
            print(f"   Updated vLLM server cell (Cell {i+1})")
            
        # Update experiment run cell to use config variables
        if 'python main.py' in source and 'experiment_configs' in source:
            new_source = "%cd /kaggle/working/TriAd_Project\n!python main.py {CONFIG_NOISE_00}\n!python main.py {CONFIG_NOISE_05}\n!python main.py {CONFIG_NOISE_20}"
            cell['source'] = new_source
            print(f"   Updated experiment run cell to use variables (Cell {i+1})")

# Save mistral7b notebook
with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(mistral_nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved mistral7b_experiments.ipynb\n")

# ============================================
# CREATE GPTOSS20B NOTEBOOK
# ============================================
print("2. Creating gptoss20b_experiments.ipynb from template...")

gptoss_nb = copy.deepcopy(template_nb)

# Find and update cells
for i, cell in enumerate(gptoss_nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Cell with imports - add config variables after it
        if i == 1 and 'import os' in source and 'import subprocess' in source:
            config_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": "# Configuration paths for GPT-OSS-20B experiments\nCONFIG_NOISE_00 = \"experiment_configs/gptoss20b_noise00.json\"\nCONFIG_NOISE_05 = \"experiment_configs/gptoss20b_noise05.json\"\nCONFIG_NOISE_20 = \"experiment_configs/gptoss20b_noise20.json\"\n\nprint(f\"Config paths defined for GPT-OSS-20B\")\nprint(f\"  - Noise 0.0: {CONFIG_NOISE_00}\")\nprint(f\"  - Noise 0.05: {CONFIG_NOISE_05}\")\nprint(f\"  - Noise 0.2: {CONFIG_NOISE_20}\")"
            }
            gptoss_nb['cells'].insert(i + 1, config_cell)
            print(f"   Added config variables cell")
            
        # Update vLLM server cell
        if 'STARTING VLLM SERVER' in source:
            cell['source'] = cell['source'].replace(
                'Qwen/Qwen2.5-32B-Instruct',
                'openai/gpt-oss-20b'
            ).replace(
                'Qwen2.5-32B-Instruct',
                'openai/gpt-oss-20b'
            )
            print(f"   Updated vLLM server cell (Cell {i+1})")
            
        # Update experiment run cell
        if 'python main.py' in source and 'experiment_configs' in source:
            new_source = "%cd /kaggle/working/TriAd_Project\n!python main.py {CONFIG_NOISE_00}\n!python main.py {CONFIG_NOISE_05}\n!python main.py {CONFIG_NOISE_20}"
            cell['source'] = new_source
            print(f"   Updated experiment run cell to use variables (Cell {i+1})")

# Save gptoss20b notebook
with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(gptoss_nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved gptoss20b_experiments.ipynb\n")

print("🎉 Done! Created 2 notebooks with exact structure from template")
print("   Only changes: model names and config variable paths")
