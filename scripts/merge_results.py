"""
Merge all per-LLM/per-noise CSV result files into 4 consolidated CSV files.

For each (LLM folder, noise folder) combination:
  - Extracts llm_name (e.g. "gpt-oss-20b") and noise_level (e.g. 0, 5, 20)
  - Adds columns: llm_name, noise_level, original_game_id
  - Creates a new globally-unique game_id to avoid collisions
  - Keeps game_id consistent across all tables so joins still work

Output (written to resources/results/):
  - total_games_summary.csv
  - total_rounds_detail.csv
  - total_comprehension_questions_results.csv
  - total_checker_results.csv
"""

import os
import re
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "resources" / "results"
OUTPUT_DIR = RESULTS_DIR  # write totals alongside LLM folders

CSV_FILES = [
    "games_summary.csv",
    "rounds_detail.csv",
    "comprehension_questions_results.csv",
    "checker_results.csv",
]


def extract_llm_name(folder_name: str) -> str:
    """Extract the LLM model name from the folder name.

    Examples:
        gpt-oss-20b_vs30round_en_multi  -> gpt-oss-20b
        Mistral-7B-Instruct-v0.3_vs30round_en_multi -> Mistral-7B-Instruct-v0.3
        Qwen2.5-32B-Instruct_vs30round_en_multi -> Qwen2.5-32B-Instruct
    """
    match = re.match(r"^(.+?)_vs\d+round", folder_name)
    if match:
        return match.group(1)
    return folder_name  # fallback


def extract_noise_level(noise_folder: str) -> int:
    """Extract noise level as integer from folder name.

    Examples:
        noise00 -> 0
        noise05 -> 5
        noise20 -> 20
    """
    match = re.search(r"noise(\d+)", noise_folder)
    if match:
        return int(match.group(1))
    return -1  # fallback


def make_unique_game_id(llm_name: str, noise_level: int, original_game_id: str) -> str:
    """Create a globally-unique game_id.

    Format: {llm_short}__noise{level}__{original_game_id}
    Using double underscores as separator to avoid ambiguity with hyphens in names.
    """
    return f"{llm_name}__noise{noise_level:02d}__{original_game_id}"


def main():
    # Discover all (llm_folder, noise_folder) combinations
    combos = []
    for llm_folder in sorted(os.listdir(RESULTS_DIR)):
        llm_path = RESULTS_DIR / llm_folder
        if not llm_path.is_dir() or llm_folder.startswith("total_"):
            continue
        for noise_folder in sorted(os.listdir(llm_path)):
            noise_path = llm_path / noise_folder
            if not noise_path.is_dir():
                continue
            combos.append((llm_folder, noise_folder, noise_path))

    print(f"Found {len(combos)} (LLM, noise) combinations:")
    for llm_f, noise_f, _ in combos:
        print(f"  {llm_f} / {noise_f}")

    # Accumulators for each CSV type
    all_games_summary = []
    all_rounds_detail = []
    all_comprehension = []
    all_checker = []

    for llm_folder, noise_folder, folder_path in combos:
        llm_name = extract_llm_name(llm_folder)
        noise_level = extract_noise_level(noise_folder)
        print(f"\nProcessing: {llm_name} / noise {noise_level}")

        # --- games_summary ---
        gs_path = folder_path / "games_summary.csv"
        if gs_path.exists():
            df = pd.read_csv(gs_path)
            df["llm_name"] = llm_name
            df["noise_level"] = noise_level
            df["original_game_id"] = df["game_id"]
            df["game_id"] = df["original_game_id"].apply(
                lambda gid: make_unique_game_id(llm_name, noise_level, gid)
            )
            all_games_summary.append(df)
            print(f"  games_summary: {len(df)} rows")

        # --- rounds_detail ---
        rd_path = folder_path / "rounds_detail.csv"
        if rd_path.exists():
            df = pd.read_csv(rd_path)
            df["llm_name"] = llm_name
            df["noise_level"] = noise_level
            df["original_game_id"] = df["game_id"]
            df["game_id"] = df["original_game_id"].apply(
                lambda gid: make_unique_game_id(llm_name, noise_level, gid)
            )
            all_rounds_detail.append(df)
            print(f"  rounds_detail: {len(df)} rows")

        # --- checker_results (has game_id - per-game question results) ---
        cr_path = folder_path / "checker_results.csv"
        if cr_path.exists():
            df = pd.read_csv(cr_path)
            df["llm_name"] = llm_name
            df["noise_level"] = noise_level
            df["original_game_id"] = df["game_id"]
            df["game_id"] = df["original_game_id"].apply(
                lambda gid: make_unique_game_id(llm_name, noise_level, gid)
            )
            all_checker.append(df)
            print(f"  checker_results: {len(df)} rows")

        # --- comprehension_questions_results (aggregated stats, no game_id) ---
        cq_path = folder_path / "comprehension_questions_results.csv"
        if cq_path.exists():
            df = pd.read_csv(cq_path)
            df["llm_name"] = llm_name
            df["noise_level"] = noise_level
            all_comprehension.append(df)
            print(f"  comprehension_questions_results: {len(df)} rows")

    # Concatenate and save
    def save(frames, filename):
        if not frames:
            print(f"  WARNING: No data for {filename}")
            return
        combined = pd.concat(frames, ignore_index=True)
        out_path = OUTPUT_DIR / filename
        combined.to_csv(out_path, index=False)
        print(f"  Saved {filename}: {len(combined)} total rows")
        return combined

    print("\n=== Saving combined files ===")
    df_gs = save(all_games_summary, "total_games_summary.csv")
    df_rd = save(all_rounds_detail, "total_rounds_detail.csv")
    df_cr = save(all_checker, "total_checker_results.csv")
    save(all_comprehension, "total_comprehension_questions_results.csv")

    # Validation: check game_id consistency across tables
    print("\n=== Validation ===")
    if df_gs is not None and df_rd is not None:
        gs_ids = set(df_gs["game_id"].unique())
        rd_ids = set(df_rd["game_id"].unique())
        only_gs = gs_ids - rd_ids
        only_rd = rd_ids - gs_ids
        if only_gs:
            print(f"  WARNING: {len(only_gs)} game_ids in games_summary but NOT in rounds_detail")
        if only_rd:
            print(f"  WARNING: {len(only_rd)} game_ids in rounds_detail but NOT in games_summary")
        if not only_gs and not only_rd:
            print(f"  OK: game_ids match between games_summary ({len(gs_ids)}) and rounds_detail ({len(rd_ids)})")

    if df_gs is not None and df_cr is not None:
        gs_ids = set(df_gs["game_id"].unique())
        cr_ids = set(df_cr["game_id"].unique())
        only_gs = gs_ids - cr_ids
        only_cr = cr_ids - gs_ids
        if only_gs:
            print(f"  INFO: {len(only_gs)} game_ids in games_summary but NOT in checker_results (normal if not all games have questions)")
        if only_cr:
            print(f"  WARNING: {len(only_cr)} game_ids in checker_results but NOT in games_summary")
        if not only_gs and not only_cr:
            print(f"  OK: game_ids match between games_summary and checker_results")

    print("\nDone!")


if __name__ == "__main__":
    main()
