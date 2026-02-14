import json
import os

NB_PATH = "kaggle_notebooks/Final_Notebook_prisiondelima_3_player.ipynb"

import time
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

NEW_SETUP_CODE = [
    "# --- CELL 1: SETUP & START SERVER ---\n",
    f"# UPDATED BY AGENT AT {TIMESTAMP}\n",
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

NEW_CONFIG_CODE = [
    "import json\n",
    "import os\n",
    "\n",
    "# CHOOSE CONFIGURATION (Uncomment one)\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_noise00.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_noise05.json\"\n",
    "CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_noise20.json\"  # <--- ACTIVE\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_test.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_test_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/gptoss20b_test_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/llama70b_noise00.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/llama70b_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/llama70b_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_noise00.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_test.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_test_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/mistral7b_test_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/pd3_base.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/pd3_dryrun.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen14b_noise00.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen14b_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen14b_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen32b_noise00.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen32b_noise05.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/qwen32b_noise20.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/stress_test_mistral7b_vn.json\"\n",
    "# CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/3_player/test.json\"\n",
    "\n",
    "with open(CONFIG_FILE_PATH, \"r\") as file:\n",
    "    config = json.load(file)\n",
    "\n",
    "MODEL_NAME = config[\"MODEL_NAME\"]\n",
    "\n",
    "os.environ[\"VLLM_BASE_URL\"] = \"http://localhost:8000/v1\"\n",
    "os.environ[\"VLLM_API_KEY\"] = \"EMPTY\"\n"
]

def fix_notebook():
    print(f"Force patching {NB_PATH}...")
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
                print("Replacing SETUP cell...")
                cell["source"] = NEW_SETUP_CODE
                setup_fixed = True
            
            # 2. Fix Config Path (Cell 2/3)
            # Find where CONFIG_FILE_PATH is defined
            if "CONFIG_FILE_PATH =" in source:
                print("Replacing CONFIG cell with detailed list...")
                cell["source"] = NEW_CONFIG_CODE
                config_fixed = True

    if setup_fixed or config_fixed:
        with open(NB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        print(f"Successfully patched {NB_PATH}")
    else:
        print("No matching cells found to fix.")

if __name__ == "__main__":
    fix_notebook()
