import json
import os

NOTEBOOKS = [
    "kaggle_notebooks/Final_Notebook_prisiondelima_2_player.ipynb",
    "kaggle_notebooks/Final_Notebook_prisiondelima_3_player.ipynb",
    "kaggle_notebooks/gptoss20b_experiments.ipynb",
    "kaggle_notebooks/mistral7b_experiments.ipynb"
]

NEW_SETUP_CODE = [
    "import os",
    "import subprocess",
    "import time",
    "import sys",
    "",
    "# CẤU HÌNH CƠ BẢN",
    "GIT_REPO_URL = \"https://github.com/trungkiet2005/TriAd_Project.git\"",
    "PROJECT_DIR_NAME = \"TriAd_Project\"",
    "SUB_PROJECT_DIR = \"\"",
    "",
    "def run_command(command, cwd=None, env=None):",
    "    print(f\"Running: {command}\")",
    "    try:",
    "        process = subprocess.Popen(command, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)",
    "        while True:",
    "            output = process.stdout.readline()",
    "            if output == '' and process.poll() is not None: break",
    "            if output: print(output.strip())",
    "        if process.poll() != 0:",
    "            print(process.stderr.read())",
    "    except Exception as e:",
    "        print(f\"Command failed: {e}\")",
    "",
    "print(\"=== 1. CLONING & INSTALLING ===\")",
    "if not os.path.exists(PROJECT_DIR_NAME):",
    "    run_command(f\"git clone {GIT_REPO_URL}\")",
    "",
    "working_dir = os.path.join(PROJECT_DIR_NAME, SUB_PROJECT_DIR)",
    "if not os.path.exists(working_dir):",
    "    print(f\"WARNING: Working directory {working_dir} not found. Using current dir.\")",
    "    working_dir = os.getcwd()",
    "",
    "# Try installing from requirements.txt with absolute path",
    "req_path = os.path.join(os.path.abspath(working_dir), \"requirements.txt\")",
    "if os.path.exists(req_path):",
    "    run_command(f\"pip install -q -r \\\"{req_path}\\\"\", cwd=working_dir)",
    "else:",
    "    print(f\"WARNING: requirements.txt not found at {req_path}\")",
    "",
    "run_command(\"pip install -q vllm openai python-dotenv mistralai striprtf retry tqdm pandas numpy scipy anthropic google-generativeai\")"
]

def patch_notebook(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    patched = False
    for cell in data["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "GIT_REPO_URL =" in source and "pip install" in source:
                print(f"Patching setup cell in {filepath}...")
                cell["source"] = [line + "\n" for line in NEW_SETUP_CODE]
                patched = True
                break
    
    if patched:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        print(f"Successfully patched {filepath}")
    else:
        print(f"No matching setup cell found in {filepath}")

if __name__ == "__main__":
    for nb in NOTEBOOKS:
        patch_notebook(nb)
