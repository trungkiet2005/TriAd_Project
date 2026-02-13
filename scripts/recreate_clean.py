import json
import copy

print("=== Recreating Notebooks from Template (CLEAN) ===\n")

with open('kaggle_notebooks/triad-project.ipynb', 'r', encoding='utf-8') as f:
    template_nb = json.load(f)

print(f"Template: {len(template_nb['cells'])} cells\n")

# Print template cells for reference
for i, cell in enumerate(template_nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        print(f"  Cell {i+1}: {source[:80]}...")

print()

# ============================================
# MISTRAL7B - Deep copy + only change CONFIG_FILE_PATH
# ============================================
print("1. Creating mistral7b_experiments.ipynb...")
mistral_nb = copy.deepcopy(template_nb)

for i, cell in enumerate(mistral_nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    # Only change the CONFIG_FILE_PATH line
    if 'qwen32b_noise05.json' in source:
        if isinstance(cell['source'], list):
            cell['source'] = [s.replace('qwen32b_noise05.json', 'mistral7b_noise00.json') for s in cell['source']]
        else:
            cell['source'] = source.replace('qwen32b_noise05.json', 'mistral7b_noise00.json')
        print(f"   Cell {i+1}: Changed config path to mistral7b_noise00.json")

    # Update the %%writefile main.py cell - add CONFIG_FILE_PATH = None
    if '%%writefile' in source and 'CONFIG_FILE_PATH' in source and 'if CONFIG_FILE_PATH:' in source:
        if isinstance(cell['source'], list):
            # Find the line before "def main():" and add CONFIG_FILE_PATH = None
            new_source = []
            for line in cell['source']:
                if line.strip().startswith('def main():'):
                    new_source.append('CONFIG_FILE_PATH = None  # Set via notebook or command-line args\n')
                    new_source.append('\n')
                new_source.append(line)
            cell['source'] = new_source
        else:
            source = source.replace(
                '\ndef main():',
                '\nCONFIG_FILE_PATH = None  # Set via notebook or command-line args\n\ndef main():'
            )
            cell['source'] = source
        print(f"   Cell {i+1}: Added CONFIG_FILE_PATH = None in %%writefile main.py")

    # Update python main.py cell to pass CONFIG_FILE_PATH as arg
    if '!python main.py' in source and 'CONFIG_FILE_PATH' not in source:
        if isinstance(cell['source'], list):
            cell['source'] = [s.replace('!python main.py', '!python main.py {CONFIG_FILE_PATH}') for s in cell['source']]
        else:
            cell['source'] = source.replace('!python main.py', '!python main.py {CONFIG_FILE_PATH}')
        print(f"   Cell {i+1}: Changed to !python main.py {{CONFIG_FILE_PATH}}")

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(mistral_nb, f, indent=2, ensure_ascii=False)
print("   ✅ Saved\n")

# ============================================
# GPTOSS20B - Deep copy + only change CONFIG_FILE_PATH
# ============================================
print("2. Creating gptoss20b_experiments.ipynb...")
gptoss_nb = copy.deepcopy(template_nb)

for i, cell in enumerate(gptoss_nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    # Only change the CONFIG_FILE_PATH line
    if 'qwen32b_noise05.json' in source:
        if isinstance(cell['source'], list):
            cell['source'] = [s.replace('qwen32b_noise05.json', 'gptoss20b_noise00.json') for s in cell['source']]
        else:
            cell['source'] = source.replace('qwen32b_noise05.json', 'gptoss20b_noise00.json')
        print(f"   Cell {i+1}: Changed config path to gptoss20b_noise00.json")

    # Update the %%writefile main.py cell
    if '%%writefile' in source and 'CONFIG_FILE_PATH' in source and 'if CONFIG_FILE_PATH:' in source:
        if isinstance(cell['source'], list):
            new_source = []
            for line in cell['source']:
                if line.strip().startswith('def main():'):
                    new_source.append('CONFIG_FILE_PATH = None  # Set via notebook or command-line args\n')
                    new_source.append('\n')
                new_source.append(line)
            cell['source'] = new_source
        else:
            source = source.replace(
                '\ndef main():',
                '\nCONFIG_FILE_PATH = None  # Set via notebook or command-line args\n\ndef main():'
            )
            cell['source'] = source
        print(f"   Cell {i+1}: Added CONFIG_FILE_PATH = None in %%writefile main.py")

    # Update python main.py cell
    if '!python main.py' in source and 'CONFIG_FILE_PATH' not in source:
        if isinstance(cell['source'], list):
            cell['source'] = [s.replace('!python main.py', '!python main.py {CONFIG_FILE_PATH}') for s in cell['source']]
        else:
            cell['source'] = source.replace('!python main.py', '!python main.py {CONFIG_FILE_PATH}')
        print(f"   Cell {i+1}: Changed to !python main.py {{CONFIG_FILE_PATH}}")

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(gptoss_nb, f, indent=2, ensure_ascii=False)
print("   ✅ Saved\n")

# ============================================
# VERIFY
# ============================================
print("=== VERIFICATION ===\n")
for name in ['mistral7b_experiments', 'gptoss20b_experiments']:
    nb = json.load(open(f'kaggle_notebooks/{name}.ipynb', 'r', encoding='utf-8'))
    print(f"{name}.ipynb ({len(nb['cells'])} cells):")
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'CONFIG_FILE_PATH' in source and 'EDIT THIS LINE' in source:
                # Extract just the path
                for line in source.split('\n'):
                    if 'CONFIG_FILE_PATH' in line and '=' in line and 'EDIT' in line:
                        print(f"  Cell {i+1}: {line.strip()}")
            if '!python main.py' in source:
                for line in source.split('\n'):
                    if '!python main.py' in line:
                        print(f"  Cell {i+1}: {line.strip()}")
    print()

print("🎉 Done!")
