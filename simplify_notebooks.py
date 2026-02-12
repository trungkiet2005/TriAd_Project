import json

# Read original notebooks and simplify them
print("=== Simplifying Notebooks to Use Args ===\n")

# ============================================
# SIMPLIFY GPTOSS20B NOTEBOOK
# ============================================
print("1. Simplifying gptoss20b_experiments.ipynb...")

with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove Cell 3 (the config loading cell) and update Cell 4 & 5
new_cells = []
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        # Skip the config loading cell
        if 'import json' in source and 'CONFIG_FILE_PATH' in source and 'MODEL_NAME' in source:
            print(f"   Removed Cell {i+1} (config loading)")
            continue
    
    new_cells.append(cell)

nb['cells'] = new_cells

# Update the vLLM server cell to read MODEL_NAME from command
# Find and update Cell 3 (now the server start cell after removal)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'STARTING VLLM SERVER' in source and 'MODEL_NAME' in source:
            # Update to use hardcoded model name
            new_source = '''print(f"\\n=== 2. STARTING VLLM SERVER (openai/gpt-oss-20b) ===")
log_file = open("vllm_log.txt", "w")

# Start vLLM background process
MODEL_NAME = "openai/gpt-oss-20b"
cmd = f"python -m vllm.entrypoints.openai.api_server --model {MODEL_NAME} --trust-remote-code --port 8000 --gpu-memory-utilization 0.95"
vllm_process = subprocess.Popen(cmd, shell=True, stdout=log_file, stderr=log_file)

print("Waiting for server readiness...")
for i in range(600): # 10 mins max
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8000/v1/models") as response:
            if response.status == 200:
                print("\\n✅ vLLM Server is READY!")
                break
    except:
        pass
    if i % 10 == 0: print(".", end="", flush=True)
    time.sleep(1)
'''
            cell['source'] = new_source
            print(f"   Updated Cell {i+1} (server start)")

# Update experiment run cells to use args
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'python main.py' in source and 'experiment_configs' not in source:
            # This is the experiment run cell, update it
            new_source = '''%cd /kaggle/working/TriAd_Project
!python main.py experiment_configs/gptoss20b_noise00.json
!python main.py experiment_configs/gptoss20b_noise05.json
!python main.py experiment_configs/gptoss20b_noise20.json
'''
            cell['source'] = new_source
            print(f"   Updated Cell {i+1} (experiment runs)")

# Save
with open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved gptoss20b_experiments.ipynb\n")

# ============================================
# SIMPLIFY MISTRAL7B NOTEBOOK
# ============================================
print("2. Simplifying mistral7b_experiments.ipynb...")

with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove Cell 3
new_cells = []
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'import json' in source and 'CONFIG_FILE_PATH' in source and 'MODEL_NAME' in source:
            print(f"   Removed Cell {i+1} (config loading)")
            continue
    
    new_cells.append(cell)

nb['cells'] = new_cells

# Update server cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'STARTING VLLM SERVER' in source and 'MODEL_NAME' in source:
            new_source = '''print(f"\\n=== 2. STARTING VLLM SERVER (mistralai/Mistral-7B-Instruct-v0.3) ===")
log_file = open("vllm_log.txt", "w")

# Start vLLM background process
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
cmd = f"python -m vllm.entrypoints.openai.api_server --model {MODEL_NAME} --trust-remote-code --port 8000 --gpu-memory-utilization 0.95"
vllm_process = subprocess.Popen(cmd, shell=True, stdout=log_file, stderr=log_file)

print("Waiting for server readiness...")
for i in range(600):
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8000/v1/models") as response:
            if response.status == 200:
                print("\\n✅ vLLM Server is READY!")
                break
    except:
        pass
    if i % 10 == 0: print(".", end="", flush=True)
    time.sleep(1)
'''
            cell['source'] = new_source
            print(f"   Updated Cell {i+1} (server start)")

#Update experiment runs
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        
        if 'python main.py' in source and 'experiment_configs' not in source:
            new_source = '''%cd /kaggle/working/TriAd_Project
!python main.py experiment_configs/mistral7b_noise00.json
!python main.py experiment_configs/mistral7b_noise05.json
!python main.py experiment_configs/mistral7b_noise20.json
'''
            cell['source'] = new_source
            print(f"   Updated Cell {i+1} (experiment runs)")

# Save
with open('kaggle_notebooks/mistral7b_experiments.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("   ✅ Saved mistral7b_experiments.ipynb\n")

print("🎉 Done! Notebooks now use command-line args instead of cell-based config loading.")
