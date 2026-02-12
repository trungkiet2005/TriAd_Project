import json
import copy

# Read original notebook
with open('triad-project.ipynb', 'r', encoding='utf-8') as f:
    original_nb = json.load(f)

print(f"✅ Loaded original notebook with {len(original_nb['cells'])} cells")

# ============================================
# CREATE GPTOSS20B NOTEBOOK
# ============================================
gptoss20b_nb = copy.deepcopy(original_nb)

# Find and update Cell 3 (config file path)
for i, cell in enumerate(gptoss20b_nb['cells']):
    if cell['cell_type'] == 'code' and 'CONFIG_FILE_PATH' in cell['source']:
        # Update to gptoss20b configs
        old_source = cell['source']
        # Replace the config file path
        new_source = old_source.replace(
            'CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/qwen32b_noise05.json"',
            'CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/gptoss20b_noise00.json"'
        )
        cell['source'] = new_source
        print(f"✅ Updated Cell {i+1} config path for gptoss20b")
        break

# Save gptoss20b notebook
with open('gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(gptoss20b_nb, f, indent=2, ensure_ascii=False)

print("✅ Created: gptoss20b_experiments.ipynb")

# ============================================
# CREATE MISTRAL7B NOTEBOOK
# ============================================
mistral7b_nb = copy.deepcopy(original_nb)

# Find and update Cell 3 (config file path)
for i, cell in enumerate(mistral7b_nb['cells']):
    if cell['cell_type'] == 'code' and 'CONFIG_FILE_PATH' in cell['source']:
        # Update to mistral7b configs
        old_source = cell['source']
        # Replace the config file path
        new_source = old_source.replace(
            'CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/qwen32b_noise05.json"',
            'CONFIG_FILE_PATH = "/kaggle/working/TriAd_Project/experiment_configs/mistral7b_noise00.json"'
        )
        cell['source'] = new_source
        print(f"✅ Updated Cell {i+1} config path for mistral7b")
        break

# Save mistral7b notebook
with open('mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(mistral7b_nb, f, indent=2, ensure_ascii=False)

print("✅ Created: mistral7b_experiments.ipynb")

print("\n🎉 Done! Created 2 notebooks with exact structure from triad-project.ipynb")
print("   - gptoss20b_experiments.ipynb (config: gptoss20b_noise00.json)")
print("   - mistral7b_experiments.ipynb (config: mistral7b_noise00.json)")
