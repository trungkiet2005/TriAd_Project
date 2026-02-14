import json
import os

NB_PATH = "kaggle_notebooks/Final_Notebook_prisiondelima_2_player.ipynb"

NEW_SETUP_CODE = [
    "# --- CELL 1: SETUP & START SERVER ---\n",
    "import os\n",
    "import subprocess\n",
    "import time\n",
    "import sys\n",
    "\n",
    "# CẤU HÌNH CƠ BẢN\n",
    "GIT_REPO_URL = \"https://github.com/trungkiet2005/TriAd_Project.git\"\n",
    "PROJECT_DIR_NAME = \"TriAd_Project\"\n",
    "SUB_PROJECT_DIR = \"\"\n",
    "\n",
    "def run_command(command, cwd=None, env=None):\n",
    "    print(f\"Running: {command}\")\n",
    "    try:\n",
    "        process = subprocess.Popen(command, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)\n",
    "        while True:\n",
    "            output = process.stdout.readline()\n",
    "            if output == '' and process.poll() is not None: break\n",
    "            if output: print(output.strip())\n",
    "        if process.poll() != 0:\n",
    "            print(process.stderr.read())\n",
    "    except Exception as e:\n",
    "        print(f\"Command failed: {e}\")\n",
    "\n",
    "print(\"=== 1. CLONING & INSTALLING ===\")\n",
    "if not os.path.exists(PROJECT_DIR_NAME):\n",
    "    run_command(f\"git clone {GIT_REPO_URL}\")\n",
    "\n",
    "working_dir = os.path.join(PROJECT_DIR_NAME, SUB_PROJECT_DIR)\n",
    "if not os.path.exists(working_dir):\n",
    "    print(f\"WARNING: Working directory {working_dir} not found. Using current dir.\")\n",
    "    working_dir = os.getcwd()\n",
    "\n",
    "# FIX: Dùng đường dẫn tuyệt đối cho requirements.txt\n",
    "req_path = os.path.join(os.path.abspath(working_dir), \"requirements.txt\")\n",
    "if os.path.exists(req_path):\n",
    "    run_command(f\"pip install -q -r \\\"{req_path}\\\"\", cwd=working_dir)\n",
    "else:\n",
    "    print(f\"WARNING: requirements.txt not found at {req_path}\")\n",
    "\n",
    "# FIX: Cài thủ công các thư viện quan trọng\n",
    "run_command(\"pip install -q vllm openai python-dotenv mistralai striprtf retry tqdm pandas numpy scipy anthropic google-generativeai\")\n"
]

def fix_notebook():
    if not os.path.exists(NB_PATH):
        print(f"Error: {NB_PATH} not found")
        return

    with open(NB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    setup_fixed = False
    config_fixed = False

    for cell in data["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            
            # 1. Fix Setup Cell (Cell 1)
            if "GIT_REPO_URL =" in source and "pip install" in source:
                print("Patching SETUP cell...")
                cell["source"] = NEW_SETUP_CODE
                setup_fixed = True
            
            # 2. Fix Config Path (Cell 2 or 3)
            # Look for CONFIG_FILE_PATH assignment
            if "CONFIG_FILE_PATH =" in source:
                print("Patching CONFIG cell...")
                new_source = []
                # Replace the line with the correct config
                config_line = "CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/2_player/gptoss20b_noise20.json\"  # <--- EDIT THIS LINE\n"
                
                # Check if we need to replace just that line or rewrite the cell
                for line in cell["source"]:
                    if "CONFIG_FILE_PATH =" in line:
                        new_source.append(config_line)
                    else:
                        new_source.append(line)
                
                cell["source"] = new_source
                config_fixed = True

    if setup_fixed or config_fixed:
        with open(NB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        print(f"Successfully patched {NB_PATH}")
        print(f"Setup Fixed: {setup_fixed}")
        print(f"Config Fixed: {config_fixed}")
    else:
        print("No matching cells found to fix.")

if __name__ == "__main__":
    fix_notebook()
