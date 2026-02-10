# Hướng Dẫn Setup Project Trên Kaggle (H100 GPU) - Tiện Dụng

Tài liệu này hướng dẫn cách chạy project `nicer_fairgame_combined` trên Kaggle Notebook sử dụng GPU H100 với cấu trúc chia thành các cell để bạn **dễ dàng sửa đổi cấu hình** (config) ngay trên notebook.

## 1. Chuẩn Bị Notebook

1.  **Tạo Notebook mới** trên Kaggle.
2.  **Cấu hình Accelerator**: Chọn **GPU H100** (hoặc T4 x2/P100 nếu không có).
3.  **Bật Internet**: Chọn **Internet: On** trong panel bên phải.

## 2. Setup Môi Trường (Cell 1)
Copy đoạn code sau vào cell đầu tiên và chạy. Nó sẽ setup môi trường và chạy vLLM server ngầm.

```python
# --- CELL 1: SETUP & START SERVER ---
import os
import subprocess
import time
import sys

# CẤU HÌNH CƠ BẢN
GIT_REPO_URL = "https://github.com/trungkiet2005/TriAd_Project.git"
PROJECT_DIR_NAME = "TriAd_Project"
SUB_PROJECT_DIR = "nicer_fairgame_combined"
MODEL_NAME = "Qwen/Qwen2.5-32B-Instruct"

def run_command(command, cwd=None, env=None):
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break
        if output: print(output.strip())
    if process.poll() != 0: print(process.stderr.read())

print("=== 1. CLONING & INSTALLING ===")
if not os.path.exists(PROJECT_DIR_NAME):
    run_command(f"git clone {GIT_REPO_URL}")

working_dir = os.path.join(PROJECT_DIR_NAME, SUB_PROJECT_DIR)
run_command(f"pip install -q -r requirements.txt", cwd=working_dir)
run_command("pip install -q vllm openai python-dotenv")

print(f"\n=== 2. STARTING VLLM SERVER ({MODEL_NAME}) ===")
log_file = open("vllm_log.txt", "w")
# Start vLLM background process
cmd = f"python -m vllm.entrypoints.openai.api_server --model {MODEL_NAME} --trust-remote-code --port 8000 --gpu-memory-utilization 0.95"
vllm_process = subprocess.Popen(cmd, shell=True, stdout=log_file, stderr=log_file)

print("Waiting for server readiness...")
for i in range(600): # 10 mins max
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8000/v1/models") as response:
            if response.status == 200:
                print("\n✅ vLLM Server is READY!")
                break
    except:
        pass
    if i % 10 == 0: print(".", end="", flush=True)
    time.sleep(1)
```

## 3. Cấu Hình Experiment (Cell 2)
Copy đoạn này vào cell thứ 2. Đây là nơi bạn **THAY ĐỔI CẤU HÌNH** (ngôn ngữ, noise, số vòng...). Sau khi sửa xong, chạy cell này để nó ghi đè file config.

```python
%%writefile TriAd_Project/nicer_fairgame_combined/run_experiments.py
"""
Script chạy experiment. BẠN CÓ THỂ SỬA CÁC THAM SỐ DƯỚI ĐÂY.
"""
import sys
import os
from pathlib import Path

# Force set environment variables for Kaggle (localhost)
os.environ["VLLM_BASE_URL"] = "http://localhost:8000/v1"
os.environ["VLLM_API_KEY"] = "EMPTY"

# Thêm đường dẫn src
sys.path.insert(0, str(Path(__file__).parent))

from src.noise_fairgame_factory import NoiseFairGameFactory
from src.checkers.time_checker import TimeChecker
from src.checkers.rule_checker import RuleChecker
from src.checkers.aggregation_checker import AggregationChecker
from src.io_managers.file_manager import FileManager

# --- CẤU HÌNH (SỬA Ở ĐÂY) ---
LANGUAGES = ["en", "fr", "ar", "cn", "vn", "it"] # Danh sách ngôn ngữ
NOISE_LEVELS = [0.0, 0.05, 0.2]  # Mức noise (0%, 5%, 20%)
ROUNDS = 30       # Số vòng chơi mỗi game
REPEATS = 40      # Số lần lặp lại mỗi điều kiện (40 game)
MAX_WORKERS = 16  # Số luồng chạy song song (tăng nếu GPU mạnh)
# -----------------------------

LLM_NAME = "VLLMQwen"
LLM_DISPLAY_NAME = "Qwen2_5_32B_Instruct"
CONFIG_DIR = "prisoner_dilemma_noise"
BASE_CONFIG_NAME = "pd_noise_round_known_mild"

def load_base_config():
    config_path = Path(f"resources/config/{CONFIG_DIR}/{BASE_CONFIG_NAME}.json")
    return FileManager.read_json_file(config_path)

def run_experiments():
    print(f"Starting Experiments...")
    print(f"Languages: {LANGUAGES}, Noise: {NOISE_LEVELS}, Rounds: {ROUNDS}, Repeats: {REPEATS}")
    
    base_config = load_base_config()
    
    # Load templates
    prompt_templates = {}
    template_name = base_config.get('templateFilename', 'prisoner_dilemma_noise')
    for lang in LANGUAGES:
        try:
            prompt_templates[lang] = FileManager.read_template_file(
                Path(f"/kaggle/working/TriAd_Project/resources/game_templates/prisoner_dilemma_2/prisoner_dilemma_noise_{lang}.txt")
            )
        except Exception as e:
            print(f"Error loading template {lang}: {e}")

    for noise in NOISE_LEVELS:
        print(f"\n{'='*50}\nRUNNING NOISE LEVEL: {noise*100:.0f}%\n{'='*50}")
        for lang in LANGUAGES:
            print(f"\n--- Language: {lang} | Noise: {noise} ---")
            current_config = base_config.copy()
            current_config.update({
                'nRounds': ROUNDS,
                'languages': [lang],
                'llm': LLM_NAME,
                'llmDisplayName': LLM_DISPLAY_NAME,
                'repeats': REPEATS,
                'promptTemplate': {lang: prompt_templates[lang]},
                'noiseConfig': {'agent1NoiseRate': noise, 'agent2NoiseRate': noise}
            })
            if 'templateFilename' in current_config:
                del current_config['templateFilename']
            
            try:
                factory = NoiseFairGameFactory(
                    checkers=[TimeChecker(), RuleChecker(), AggregationChecker()], 
                    max_workers=MAX_WORKERS,
                    llm_name=LLM_DISPLAY_NAME
                )
                factory.create_and_run_games(current_config)
            except Exception as e:
                print(f"ERROR: {e}")

if __name__ == "__main__":
    run_experiments()
```

## 4. Chạy Experiment (Cell 3)
Copy đoạn lệnh này vào cell thứ 3 để bắt đầu chạy.

```bash
# --- CELL 3: EXECUTE ---
cd TriAd_Project/nicer_fairgame_combined
export VLLM_BASE_URL="http://localhost:8000/v1"
export VLLM_API_KEY="EMPTY"

# Chạy script experiment đã config ở trên
python run_experiments.py
```

### Lưu Kết Quả
Sau khi chạy xong, kết quả nằm trong thư mục `TriAd_Project/nicer_fairgame_combined/resources/results`. Bạn có thể nén và tải về.
