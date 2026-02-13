import json
import os

NB_PATH = "kaggle_notebooks/Final_Notebook_prisiondelima_2_player.ipynb"

def update_config_path():
    if not os.path.exists(NB_PATH):
        print(f"Notebook {NB_PATH} not found.")
        return

    with open(NB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for cell in data["cells"]:
        if cell["cell_type"] == "code":
            new_source = []
            for line in cell["source"]:
                if "CONFIG_FILE_PATH =" in line:
                    if "experiment_configs/2_player/gptoss20b_noise20.json" not in line:
                        print(f"Updating CONFIG_FILE_PATH in {NB_PATH}...")
                        new_source.append("CONFIG_FILE_PATH = \"/kaggle/working/TriAd_Project/experiment_configs/2_player/gptoss20b_noise20.json\"  # <--- EDIT THIS LINE\n")
                        updated = True
                    else:
                        new_source.append(line)
                else:
                    new_source.append(line)
            cell["source"] = new_source
            if updated: break # Assume only one config definition
    
    if updated:
        with open(NB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        print(f"Successfully updated configuration path in {NB_PATH}")
    else:
        print("Configuration path already up-to-date or not found.")

if __name__ == "__main__":
    update_config_path()
