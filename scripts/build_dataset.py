"""
build_dataset.py
================
Generate a consolidated analysis CSV from the Prisoner_dilemma_2player results.

Output columns (1 row = 1 game):
    game_id, language, n_rounds_is_known, max_rounds, played_rounds, agents_communicate,
    agent1_name, agent1_llm, agent1_personality, agent1_noise_rate,
    agent1_knows_opponent_with_prob,
    agent1_strategies, agent1_intended_strategies,
    agent1_flipped_count, agent1_flipped_rounds,
    agent1_scores, agent1_messages,
    agent1_total_score, agent1_cooperation_rate, agent1_defection_rate,
    agent1_avg_opponent_coop_prob, agent1_avg_noise_suspicion,
    agent1_opponent_coop_probs, agent1_noise_suspicions, agent1_reasons,
    agent2_name, agent2_llm, agent2_personality, agent2_noise_rate,
    agent2_knows_opponent_with_prob,
    agent2_strategies, agent2_intended_strategies,
    agent2_flipped_count, agent2_flipped_rounds,
    agent2_scores, agent2_messages,
    agent2_total_score, agent2_cooperation_rate, agent2_defection_rate,
    agent2_avg_opponent_coop_prob, agent2_avg_noise_suspicion,
    agent2_opponent_coop_probs, agent2_noise_suspicions, agent2_reasons,
    dataset_source
"""

import json
import os
import re
import csv
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
RESULTS_DIR = Path(__file__).resolve().parents[1] / "resources" / "results"
GAME_TYPE   = "Prisoner_dilemma_2player"
OUTPUT_CSV  = RESULTS_DIR / GAME_TYPE / "consolidated_dataset.csv"

OUTPUT_COLUMNS = [
    "game_id", "language", "n_rounds_is_known", "max_rounds", "played_rounds",
    "agents_communicate",
    # Agent 1
    "agent1_name", "agent1_llm", "agent1_personality", "agent1_noise_rate",
    "agent1_knows_opponent_with_prob",
    "agent1_strategies", "agent1_intended_strategies",
    "agent1_flipped_count", "agent1_flipped_rounds",
    "agent1_scores", "agent1_messages",
    "agent1_total_score", "agent1_cooperation_rate", "agent1_defection_rate",
    "agent1_avg_opponent_coop_prob", "agent1_avg_noise_suspicion",
    "agent1_opponent_coop_probs", "agent1_noise_suspicions", "agent1_reasons",
    # Agent 2
    "agent2_name", "agent2_llm", "agent2_personality", "agent2_noise_rate",
    "agent2_knows_opponent_with_prob",
    "agent2_strategies", "agent2_intended_strategies",
    "agent2_flipped_count", "agent2_flipped_rounds",
    "agent2_scores", "agent2_messages",
    "agent2_total_score", "agent2_cooperation_rate", "agent2_defection_rate",
    "agent2_avg_opponent_coop_prob", "agent2_avg_noise_suspicion",
    "agent2_opponent_coop_probs", "agent2_noise_suspicions", "agent2_reasons",
    # Meta
    "dataset_source",
]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def extract_model_name(folder_name: str) -> str:
    """Extract LLM name from folder like 'Mistral-7B-Instruct-v0.3_vs30round_en_multi'."""
    return folder_name.split("_vs")[0]


def strategy_to_int_list(strategy_str: str) -> list[str]:
    """
    Convert multi-language strategy strings → ['OptionA'/'OptionB',...]
    OptionA = Defect, OptionB = Cooperate

    Supported tokens:
        Cooperate: C, Cooperate, 1,  (fr) C,  (ar) ت,  (cn) 合,  (vn) H
        Defect:    D, Defect,    0,  (fr) T,  (ar) خ,  (cn) 背,  (vn) P
    """
    COOPERATE_TOKENS = {"C", "Cooperate", "1", "ت", "合", "H"}
    DEFECT_TOKENS    = {"D", "Defect",    "0", "T", "خ", "背", "P"}

    if not strategy_str or strategy_str in ("", "[]"):
        return []
    tokens = [t.strip() for t in strategy_str.split(",")]
    result = []
    for t in tokens:
        if t in COOPERATE_TOKENS:
            result.append("OptionB")   # Cooperate
        elif t in DEFECT_TOKENS:
            result.append("OptionA")   # Defect
        else:
            result.append(t)           # keep as-is for unknown values
    return result


def parse_beliefs_from_generated_text(generated_text: str) -> tuple[int | None, int | None]:
    """
    Extract opponent_coop_prob and opponent_noise_suspicion
    from the JSON string embedded in 'generated_text'.
    Returns (coop_prob, noise_suspicion) or (None, None) if not found.
    """
    try:
        # Find JSON block inside the generated text
        match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if not match:
            return None, None
        data = json.loads(match.group())
        beliefs = data.get("beliefs", {})
        coop_prob = beliefs.get("opponent_coop_prob")
        noise_sus = beliefs.get("opponent_noise_suspicion")
        return coop_prob, noise_sus
    except Exception:
        return None, None


def load_action_answers(action_answers_dir: Path, game_id: int, run_id: int,
                        player: str) -> dict:
    """
    Load A or B action_answers JSON.
    Returns dict with:
      avg_opponent_coop_prob, avg_noise_suspicion,
      opponent_coop_probs  (list per round),
      noise_suspicions     (list per round),
      reasons              (list per round)
    player: 'A' or 'B'
    """
    empty = {
        "avg_coop": None, "avg_noise": None,
        "coop_probs": [], "noise_suspicions": [], "reasons": []
    }

    filename = f"{player}_action_answers_game{game_id}_run{run_id}.json"
    filepath = action_answers_dir / filename
    if not filepath.exists():
        return empty

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    coop_probs = []
    noise_suspicions = []
    reasons = []

    # Sort rounds numerically to keep order
    for round_key in sorted(data.get("action_answers", {}).keys(), key=int):
        round_data    = data["action_answers"][round_key]
        generated_text = round_data.get("generated_text", "")
        coop_prob, noise_sus = parse_beliefs_from_generated_text(generated_text)

        if coop_prob is not None:
            try:
                coop_probs.append(float(coop_prob))
            except (ValueError, TypeError):
                coop_probs.append(None)
        else:
            coop_probs.append(None)

        if noise_sus is not None:
            try:
                noise_suspicions.append(float(noise_sus))
            except (ValueError, TypeError):
                noise_suspicions.append(None)
        else:
            noise_suspicions.append(None)

        reasons.append(round_data.get("reason", ""))

    valid_coops  = [v for v in coop_probs       if v is not None]
    valid_noises = [v for v in noise_suspicions  if v is not None]
    avg_coop  = round(sum(valid_coops)  / len(valid_coops),  2) if valid_coops  else None
    avg_noise = round(sum(valid_noises) / len(valid_noises), 2) if valid_noises else None

    return {
        "avg_coop":          avg_coop,
        "avg_noise":         avg_noise,
        "coop_probs":        coop_probs,
        "noise_suspicions":  noise_suspicions,
        "reasons":           reasons,
    }


def load_scores_from_rounds(rounds_detail: list[dict], game_id: str, agent_name: str) -> list[int]:
    """
    From pre-loaded rounds_detail, return ordered list of round scores
    for a specific game_id + agent_name.
    """
    rows = [
        r for r in rounds_detail
        if r["game_id"] == game_id and r["agent_name"] == agent_name
    ]
    rows.sort(key=lambda r: int(r["round_number"]))
    return [int(r["score"]) for r in rows]


# ─────────────────────────────────────────────
# MAIN BUILD FUNCTION
# ─────────────────────────────────────────────

def build_dataset():
    game_type_dir = RESULTS_DIR / GAME_TYPE
    all_rows = []

    # Walk: model_folder / noise_folder
    for model_folder in sorted(game_type_dir.iterdir()):
        if not model_folder.is_dir():
            continue

        llm_name = extract_model_name(model_folder.name)

        for noise_folder in sorted(model_folder.iterdir()):
            if not noise_folder.is_dir():
                continue

            noise_config = noise_folder.name  # e.g. 'noise00', 'noise05', 'noise20'
            games_summary_path  = noise_folder / "games_summary.csv"
            rounds_detail_path  = noise_folder / "rounds_detail.csv"
            action_answers_dir  = noise_folder / "action_answers"

            if not games_summary_path.exists():
                print(f"  [SKIP] No games_summary.csv in {noise_folder}")
                continue

            # ── Load rounds_detail once per noise folder ──────────────
            rounds_detail = []
            if rounds_detail_path.exists():
                with open(rounds_detail_path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rounds_detail = list(reader)

            # ── Process each game in games_summary ────────────────────
            with open(games_summary_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    game_id_raw = row["game_id"]          # e.g. 'game_0'
                    run_id      = int(row["run_id"])
                    game_id_num = int(game_id_raw.replace("game_", ""))

                    # ── Strategies: C/D → [1/0] ──
                    a1_strategies          = strategy_to_int_list(row.get("agent1_strategies", ""))
                    a1_intended_strategies = strategy_to_int_list(row.get("agent1_intended_strategies", ""))
                    a2_strategies          = strategy_to_int_list(row.get("agent2_strategies", ""))
                    a2_intended_strategies = strategy_to_int_list(row.get("agent2_intended_strategies", ""))

                    # ── Flipped rounds: '2,3,17' → [2,3,17] ──
                    def parse_int_list(s: str) -> list:
                        if not s or s.strip() in ("", "[]"):
                            return []
                        return [int(x.strip()) for x in s.split(",") if x.strip().isdigit()]

                    a1_flipped_rounds = parse_int_list(row.get("agent1_flipped_rounds", ""))
                    a2_flipped_rounds = parse_int_list(row.get("agent2_flipped_rounds", ""))

                    # ── Per-round scores from rounds_detail ──
                    a1_scores = load_scores_from_rounds(rounds_detail, game_id_raw, "agent1")
                    a2_scores = load_scores_from_rounds(rounds_detail, game_id_raw, "agent2")

                    # ── Beliefs from action_answers JSON ──
                    a1_beliefs = load_action_answers(action_answers_dir, game_id_num, run_id, "A")
                    a2_beliefs = load_action_answers(action_answers_dir, game_id_num, run_id, "B")

                    out_row = {
                        "game_id":                        game_id_raw,
                        "language":                       row.get("language", "en"),
                        "n_rounds_is_known":              row.get("n_rounds_known", True),
                        "max_rounds":                     row.get("max_rounds"),
                        "played_rounds":                  row.get("played_rounds"),
                        "agents_communicate":             False,
                        # Agent 1
                        "agent1_name":                    row.get("agent1_name"),
                        "agent1_llm":                     llm_name,
                        "agent1_personality":             row.get("agent1_personality"),
                        "agent1_noise_rate":              row.get("agent1_noise_rate"),
                        "agent1_knows_opponent_with_prob":  0,
                        "agent1_strategies":               a1_strategies,
                        "agent1_intended_strategies":      a1_intended_strategies,
                        "agent1_flipped_count":            row.get("agent1_flipped_count"),
                        "agent1_flipped_rounds":           a1_flipped_rounds,
                        "agent1_scores":                   a1_scores,
                        "agent1_messages":                 [],
                        "agent1_total_score":              row.get("agent1_total_score"),
                        "agent1_cooperation_rate":         row.get("agent1_cooperation_rate"),
                        "agent1_defection_rate":           row.get("agent1_defection_rate"),
                        "agent1_avg_opponent_coop_prob":   a1_beliefs["avg_coop"],
                        "agent1_avg_noise_suspicion":      a1_beliefs["avg_noise"],
                        "agent1_opponent_coop_probs":      a1_beliefs["coop_probs"],
                        "agent1_noise_suspicions":         a1_beliefs["noise_suspicions"],
                        "agent1_reasons":                  a1_beliefs["reasons"],
                        # Agent 2
                        "agent2_name":                     row.get("agent2_name"),
                        "agent2_llm":                      llm_name,
                        "agent2_personality":              row.get("agent2_personality"),
                        "agent2_noise_rate":               row.get("agent2_noise_rate"),
                        "agent2_knows_opponent_with_prob":  0,
                        "agent2_strategies":               a2_strategies,
                        "agent2_intended_strategies":      a2_intended_strategies,
                        "agent2_flipped_count":            row.get("agent2_flipped_count"),
                        "agent2_flipped_rounds":           a2_flipped_rounds,
                        "agent2_scores":                   a2_scores,
                        "agent2_messages":                 [],
                        "agent2_total_score":              row.get("agent2_total_score"),
                        "agent2_cooperation_rate":         row.get("agent2_cooperation_rate"),
                        "agent2_defection_rate":           row.get("agent2_defection_rate"),
                        "agent2_avg_opponent_coop_prob":   a2_beliefs["avg_coop"],
                        "agent2_avg_noise_suspicion":      a2_beliefs["avg_noise"],
                        "agent2_opponent_coop_probs":      a2_beliefs["coop_probs"],
                        "agent2_noise_suspicions":         a2_beliefs["noise_suspicions"],
                        "agent2_reasons":                  a2_beliefs["reasons"],
                        # Meta
                        "dataset_source":                 GAME_TYPE,
                    }
                    all_rows.append(out_row)

            print(f"  [OK] {model_folder.name} / {noise_config} → {len(all_rows)} rows total")

    # ── Write output CSV ──────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✓ Done! {len(all_rows)} rows saved to:\n  {OUTPUT_CSV}")


if __name__ == "__main__":
    build_dataset()
