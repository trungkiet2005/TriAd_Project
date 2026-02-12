import json

# Check gptoss20b notebook
nb = json.load(open('kaggle_notebooks/gptoss20b_experiments.ipynb', 'r', encoding='utf-8'))
print(f"Total cells: {len(nb['cells'])}\n")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        print(f"=== Cell {i+1} (first 200 chars) ===")
        print(source[:200])
        print()
