import json
import os
import glob

BASE_DIR = "experiment_configs"
DIR_2P = os.path.join(BASE_DIR, "2_player")
DIR_3P = os.path.join(BASE_DIR, "3_player")

NB_2P = "kaggle_notebooks/Final_Notebook_prisiondelima_2_player.ipynb"
NB_3P = "kaggle_notebooks/Final_Notebook_prisiondelima_3_player.ipynb"

# 1. Sync Configs: Create missing 3-player configs based on 2-player ones
def sync_3player_configs():
    if not os.path.exists(DIR_3P):
        os.makedirs(DIR_3P)

    # Get list of 2-player configs
    configs_2p = glob.glob(os.path.join(DIR_2P, "*.json"))
    
    for config_path in configs_2p:
        filename = os.path.basename(config_path)
        target_path = os.path.join(DIR_3P, filename)
        
        # specific logic for pd3_base and pd3_dryrun which are unique
        if filename in ["pd3_base.json", "pd3_dryrun.json"]:
            continue

        if not os.path.exists(target_path):
            print(f"Creating missing 3-player config: {filename}")
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Modify for 3 players
            # 1. Adjust NUM_NOISE_AGENTS if present (usually 2 -> 3 or logic based)
            # Actually, standard logic: 1 main agent + N-1 noise agents? 
            # Let's check a standard 3-player config like mistral7b_noise00.json to see the pattern.
            # Assuming standard pattern: strategies length 3, opponentPersonalityProb length 3 if explicit
            
            # For simplicity in this script, we will mostly clone but ensure specifics:
            # - If "agents" config exists, ensure lists are length 3
            
            if "agents" in data:
                agents = data["agents"]
                # Adjust for 3 players
                # Strategies: usually {agent1:..., agent2:..., agent3:...}
                # But in config it might be "strategies": {"agent_1": "...", ...}
                
                # Check LLM config
                # The prompt structure usually handles N players. 
                # Key difference is often just the distinct noise/personality settings.
                
                # Let's blindly copy for now but try to set num agents to 3 where obvious
                # Actually, the most robust way without complex parsing is to load a template 3-player config
                # and inject the model/noise params from the 2-player config.
                pass 

            # Since adapting logic perfectly is hard without a reference, let's use a template approach.
            # We will read 'mistral7b_noise00.json' from 3_player as a template if it exists,
            # otherwise simplistic copy.
            
            # BETTER STRATEGY: 
            # Just copy the 2-player config and change strictly necessary fields?
            # No, 2-player config has 2 agents. 3-player needs 3.
            # Let's use 'gptoss20b_noise00.json' (exists in 3_player) as template.
            
            template_path = os.path.join(DIR_3P, "gptoss20b_noise00.json")
            if os.path.exists(template_path):
                 with open(template_path, "r", encoding="utf-8") as t:
                    template_data = json.load(t)
            else:
                print("Warning: No template 3-player config found. Skipping generation.")
                continue

            # Update template with values from 2-player config
            template_data["MODEL_NAME"] = data.get("MODEL_NAME", template_data["MODEL_NAME"])
            if "vyllm_config" in data:
                template_data["vyllm_config"] = data["vyllm_config"]
            elif "vyllm_config" in template_data:
                 # Keep existing if source doesn't have it but template does
                 pass
            
            # Update Noise Levels
            # Extract noise from filename (e.g. noise05 -> 0.05) to set correctly?
            # Or just copy if structure matches.
            # checks agent config.
            
            if "agents" in data and "agents" in template_data:
                 # Copy specific noise if easy to find, else relying on filename convention might be safer
                 # But let's verify if 'agents' has specific noise settings.
                 # Actually, let's just use the template structure (3 agents) and only swap the MODEL.
                 # The filename usually implies the noise level.
                 
                 # If filename has 'noise05', set noise to 0.05 for noise agents?
                 # 'gptoss20b_noise05' imply specific settings.
                 pass
            
            # SPECIAL: qwen14b
            if "qwen14b" in filename:
                # We need to port qwen settings.
                # Assuming template is gptoss, we replace model name.
                pass
            
            # If it's a 'test' config or 'stress' config, we might need manual adjustment.
            # For now, let's just ensure the file exists with the CORRECT MODEL NAME.
            # The structure (3 agents) is kept from the template.
            
            # Logic:
            # 1. Load 3-player template (valid 3-agent structure)
            # 2. Overwrite MODEL_NAME from 2-player config
            # 3. IF filename contains "noiseXX", try to adjust noise? 
            #    Actually, if we copy 'gptoss20b_noise05.json' (3p) to 'qwen14b_noise05.json' (3p)
            #    and just change model name from gptoss to qwen, that's correct!
            
            # So: Find matching "noise suffix" config in 3-player to use as base?
            # e.g. for qwen14b_noise05.json (2p), use gptoss20b_noise05.json (3p) as base, update model.
            
            base_3p_name = "gptoss20b_noise00.json" # default
            if "noise05" in filename: base_3p_name = "gptoss20b_noise05.json"
            if "noise20" in filename: base_3p_name = "gptoss20b_noise20.json"
            
            base_3p_path = os.path.join(DIR_3P, base_3p_name)
            if os.path.exists(base_3p_path):
                 with open(base_3p_path, "r", encoding="utf-8") as b:
                    new_3p_data = json.load(b)
                 new_3p_data["MODEL_NAME"] = data.get("MODEL_NAME", "openai/gpt-oss-20b")
                 
                 with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(new_3p_data, f, indent=4)
            else:
                print(f"Skipping {filename} - no suitable 3-player base found.")


# 2. Update Notebooks with Commented Config list
def update_notebook_config_cell(nb_path, config_dir, default_config):
    if not os.path.exists(nb_path):
        return

    # Get all configs
    configs = glob.glob(os.path.join(config_dir, "*.json"))
    configs.sort()
    
    # Generate Python code lines
    # CONFIG_FILE_PATH = "..." # <--- Active
    # # CONFIG_FILE_PATH = "..."
    
    code_lines = []
    
    # Check if default exists, if not pick first
    default_filename = os.path.basename(default_config)
    
    # Group configs clearly?
    # No, just list them.
    
    # Find absolute path prefix (Kaggle style)
    kaggle_prefix = f"/kaggle/working/TriAd_Project/{config_dir.replace(os.path.sep, '/')}"
    
    active_found = False
    
    for c in configs:
        fname = os.path.basename(c)
        full_path = f"{kaggle_prefix}/{fname}"
        
        if fname == default_filename:
            line = f"CONFIG_FILE_PATH = \"{full_path}\"  # <--- ACTIVE\n"
            active_found = True
        else:
            line = f"# CONFIG_FILE_PATH = \"{full_path}\"\n"
        code_lines.append(line)
        
    if not active_found and configs:
        # Force first one active if default not found
        fname = os.path.basename(configs[0])
        full_path = f"{kaggle_prefix}/{fname}"
        code_lines[0] = f"CONFIG_FILE_PATH = \"{full_path}\"  # <--- ACTIVE\n"

    # Add surrounding code
    final_source = [
        "import json\n",
        "import os\n",
        "\n",
        "# CHOOSE CONFIGURATION (Uncomment one)\n"
    ] + code_lines + [
        "\n",
        "with open(CONFIG_FILE_PATH, \"r\") as file:\n",
        "    config = json.load(file)\n",
        "\n",
        "MODEL_NAME = config[\"MODEL_NAME\"]\n",
        "\n",
        "os.environ[\"VLLM_BASE_URL\"] = \"http://localhost:8000/v1\"\n",
        "os.environ[\"VLLM_API_KEY\"] = \"EMPTY\"\n"
    ]

    # Patch Notebook
    with open(nb_path, "r", encoding="utf-8") as f:
        nb_data = json.load(f)
        
    patched = False
    for cell in nb_data["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "CONFIG_FILE_PATH =" in source:
                print(f"Patching Config Cell in {nb_path}...")
                cell["source"] = final_source
                patched = True
                break # only patch config cell

    if patched:
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb_data, f, indent=1)
        print(f"Updated config list in {nb_path}")

if __name__ == "__main__":
    print("Syncing 3-player configs...")
    sync_3player_configs()
    
    print("Updating 2-player notebook...")
    update_notebook_config_cell(NB_2P, "experiment_configs/2_player", "gptoss20b_noise20.json")
    
    print("Updating 3-player notebook...")
    update_notebook_config_cell(NB_3P, "experiment_configs/3_player", "gptoss20b_noise20.json")
