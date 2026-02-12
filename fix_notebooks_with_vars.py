import json

print("=== Updating Notebooks to Use Variable + Args ===\n")

# ============================================
# UPDATE GPTOSS20B NOTEBOOK
# ============================================
print("1. Updating gptoss20b_experiments.ipynb...")

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 2 (imports) and add a new cell after it
import_cell_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'import os' in source and 'import subprocess' in source:
            import_cell_idx = i
            break

# Insert config variables cell after imports
if import_cell_idx is not None:
    config_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Configuration paths for experiments\n",
            "CONFIG_NOISE_00 = \"experiment_configs/gptoss20b_noise00.json\"\n",
            "CONFIG_NOISE_05 = \"experiment_configs/gptoss20b_noise05.json\"\n",
            "CONFIG_NOISE_20 = \"experiment_configs/gptoss20b_noise20.json\"\n",
            "\n",
            "print(f\"Config paths defined:\")\n",
            "print(f\"  - Noise 0.0: {CONFIG_NOISE_00}\")\n",
            "print(f\"  - Noise 0.05: {CONFIG_NOISE_05}\")\n",
            "print(f\"  - Noise 0.2: {CONFIG_NOISE_20}\")"
        ]
    }
    nb['cells'].insert(import_cell_idx + 1, config_cell)
    print(f"   Added config variables cell after imports")

# Update experiment run cell to use variables
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'RUN EXPERIMENTS' in source or ('python main.py' in source and 'experiment_configs/gptoss20b' in source):
            new_source = [
                "print(f\"\\n=== 3. RUN EXPERIMENTS ===\\n\")\n",
                "\n",
                "# Noise 0.0\n",
                "print(\"Running Noise 0.0...\")\n",
                "%cd /kaggle/working/TriAd_Project\n",
                "!python main.py {CONFIG_NOISE_00}\n",
                "\n",
                "# Noise 0.05\n",
                "print(\"\\nRunning Noise 0.05...\")\n",
                "!python main.py {CONFIG_NOISE_05}\n",
                "\n",
                "# Noise 0.2\n",
                "print(\"\\nRunning Noise 0.2...\")\n",
                "!python main.py {CONFIG_NOISE_20}"
            ]
            cell['source'] = new_source
            print(f"   Updated experiment run cell to use variables as args")

# Save
with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved gptoss20b_experiments.ipynb\n")

# ============================================
# UPDATE MISTRAL7B NOTEBOOK
# ============================================
print("2. Updating mistral7b_experiments.ipynb...")

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find import cell
import_cell_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'import os' in source and 'import subprocess' in source:
            import_cell_idx = i
            break

# Insert config variables cell
if import_cell_idx is not None:
    config_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Configuration paths for experiments\n",
            "CONFIG_NOISE_00 = \"experiment_configs/mistral7b_noise00.json\"\n",
            "CONFIG_NOISE_05 = \"experiment_configs/mistral7b_noise05.json\"\n",
            "CONFIG_NOISE_20 = \"experiment_configs/mistral7b_noise20.json\"\n",
            "\n",
            "print(f\"Config paths defined:\")\n",
            "print(f\"  - Noise 0.0: {CONFIG_NOISE_00}\")\n",
            "print(f\"  - Noise 0.05: {CONFIG_NOISE_05}\")\n",
            "print(f\"  - Noise 0.2: {CONFIG_NOISE_20}\")"
        ]
    }
    nb['cells'].insert(import_cell_idx + 1, config_cell)
    print(f"   Added config variables cell after imports")

# Update experiment run cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'RUN EXPERIMENTS' in source or ('python main.py' in source and 'experiment_configs/mistral7b' in source):
            new_source = [
                "print(f\"\\n=== 3. RUN EXPERIMENTS ===\\n\")\n",
                "\n",
                "# Noise 0.0\n",
                "print(\"Running Noise 0.0...\")\n",
                "%cd /kaggle/working/TriAd_Project\n",
                "!python main.py {CONFIG_NOISE_00}\n",
                "\n",
                "# Noise 0.05\n",
                "print(\"\\nRunning Noise 0.05...\")\n",
                "!python main.py {CONFIG_NOISE_05}\n",
                "\n",
                "# Noise 0.2\n",
                "print(\"\\nRunning Noise 0.2...\")\n",
                "!python main.py {CONFIG_NOISE_20}"
            ]
            cell['source'] = new_source
            print(f"   Updated experiment run cell to use variables as args")

# Save
with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved mistral7b_experiments.ipynb\n")

print("🎉 Done! Notebooks now define config variables and pass them as args to main.py")
