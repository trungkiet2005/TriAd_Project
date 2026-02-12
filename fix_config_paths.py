import json

print("=== Fixing Config Paths to Match Template ===\n")

# ============================================
# FIX MISTRAL7B NOTEBOOK
# ============================================
print("1. Fixing mistral7b_experiments.ipynb...")

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Find config variables cell
        if 'CONFIG_NOISE_00' in source and 'experiment_configs/mistral7b' in source:
            new_source = """# Configuration paths for Mistral-7B experiments
CONFIG_NOISE_00 = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise00.json"
CONFIG_NOISE_05 = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise05.json"
CONFIG_NOISE_20 = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise20.json"

print(f"Config paths defined for Mistral-7B")
print(f"  - Noise 0.0: {CONFIG_NOISE_00}")
print(f"  - Noise 0.05: {CONFIG_NOISE_05}")
print(f"  - Noise 0.2: {CONFIG_NOISE_20}")"""
            cell['source'] = new_source
            print(f"   Updated config paths with full Kaggle path")
            break

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved mistral7b_experiments.ipynb\n")

# ============================================
# FIX GPTOSS20B NOTEBOOK
# ============================================
print("2. Fixing gptoss20b_experiments.ipynb...")

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Find config variables cell
        if 'CONFIG_NOISE_00' in source and 'experiment_configs/gptoss20b' in source:
            new_source = """# Configuration paths for GPT-OSS-20B experiments
CONFIG_NOISE_00 = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise00.json"
CONFIG_NOISE_05 = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise05.json"
CONFIG_NOISE_20 = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise20.json"

print(f"Config paths defined for GPT-OSS-20B")
print(f"  - Noise 0.0: {CONFIG_NOISE_00}")
print(f"  - Noise 0.05: {CONFIG_NOISE_05}")
print(f"  - Noise 0.2: {CONFIG_NOISE_20}")"""
            cell['source'] = new_source
            print(f"   Updated config paths with full Kaggle path")
            break

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved gptoss20b_experiments.ipynb\n")

print("🎉 Done! Config paths now match template format with full Kaggle paths")
