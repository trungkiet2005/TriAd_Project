"""
Detailed Output Manager - Save results like original nicer_than_human paper.

Creates the following output structure:
- action_answers/: LLM responses with reasoning for each round
- game_histories/: Action sequences for each game
- time_checker/: Per-question stats for time checker
- rule_checker/: Per-question stats for rule checker  
- aggregation_checker/: Per-question stats for aggregation checker
- comprehension_questions_results.csv: Summary with accuracy and CI
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import math


class DetailedOutputManager:
    """
    Manager for saving detailed outputs matching original paper format.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the output manager.
        
        Args:
            output_dir: Directory for outputs (will be used directly, no subfolder created)
        """
        self.base_dir = Path(output_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.action_answers_dir = self.base_dir / "action_answers"
        self.game_histories_dir = self.base_dir / "game_histories"
        self.time_checker_dir = self.base_dir / "time_checker"
        self.rule_checker_dir = self.base_dir / "rule_checker"
        self.aggregation_checker_dir = self.base_dir / "aggregation_checker"
        
        for d in [self.action_answers_dir, self.game_histories_dir, 
                  self.time_checker_dir, self.rule_checker_dir, 
                  self.aggregation_checker_dir]:
            d.mkdir(exist_ok=True)
        
        # Storage for accumulating data
        self.action_answers: Dict[str, Dict[int, Dict]] = {}  # {player: {round: {...}}}
        self.game_histories: Dict[str, List[int]] = {}  # {player: [0, 1, 0, ...]}
        self.checker_results: Dict[str, Any] = {}  # Checker objects
        
        # Strategy name to int mapping (for game_histories)
        self.strategy_to_int = {"Cooperate": 1, "Defect": 0}
        
        # Game metadata for tracking
        self.current_game_id: int = 0
        self.current_game_metadata: Dict[str, Any] = {}
        
        # Accumulate all games data for summary CSV
        self.games_summary: List[Dict[str, Any]] = []
        
        # Initialize run ID by checking existing files
        self.run_id = self._find_next_run_id()

    def _find_next_run_id(self) -> int:
        """Find the next available run ID based on existing files."""
        if not self.game_histories_dir.exists():
            return 1
            
        max_id = 0
        for file in self.game_histories_dir.glob("game_history_*.json"):
            try:
                # Extract ID from filename "game_history_123.json"
                file_id = int(file.stem.split("_")[-1])
                max_id = max(max_id, file_id)
            except ValueError:
                continue
                
        return max_id + 1

    def set_run_id(self, run_id: int) -> None:
        """Set the current run ID."""
        self.run_id = run_id

    def set_game_metadata(self, game_id: int, metadata: Dict[str, Any] = None) -> None:
        """
        Set metadata for current game being saved.
        
        Args:
            game_id: Unique identifier for this game
            metadata: Additional metadata (language, agents, personalities, etc.)
        """
        self.current_game_id = game_id
        self.current_game_metadata = metadata or {}

    def record_action(self, player: str, round_num: int, 
                      generated_text: str, action: str, reason: str = "") -> None:
        """
        Record an action taken by a player.
        
        Args:
            player: Player name (e.g., "A", "agent1")
            round_num: Round number (0-indexed)
            generated_text: Raw LLM response
            action: Action taken ("Cooperate" or "Defect")
            reason: Extracted reasoning
        """
        if player not in self.action_answers:
            self.action_answers[player] = {}
        
        self.action_answers[player][round_num] = {
            "generated_text": generated_text,
            "action": self.strategy_to_int.get(action, action),
            "reason": reason
        }
        
        # Also record to game history
        if player not in self.game_histories:
            self.game_histories[player] = []
        
        # Extend list if needed
        while len(self.game_histories[player]) <= round_num:
            self.game_histories[player].append(0)
        
        self.game_histories[player][round_num] = self.strategy_to_int.get(action, 0)

    def record_game_history(self, players_histories: Dict[str, List[str]]) -> None:
        """
        Record complete game history from a finished game.
        
        Args:
            players_histories: {player_name: [action1, action2, ...]}
        """
        for player, actions in players_histories.items():
            # Map player names to A/B for compatibility
            mapped_name = self._map_player_name(player)
            self.game_histories[mapped_name] = [
                self.strategy_to_int.get(a, 0) for a in actions
            ]

    def _map_player_name(self, name: str) -> str:
        """Map agent names to A/B format."""
        if name in ["agent1", "A", "player_1"]:
            return "A"
        elif name in ["agent2", "B", "player_2"]:
            return "B"
        return name

    def save_action_answers(self, player: str, run_id: int = None) -> None:
        """Save action answers for a player to JSON file with game_id."""
        if run_id is None:
            run_id = self.run_id
        
        if player not in self.action_answers:
            return
        
        mapped_name = self._map_player_name(player)
        game_id = self.current_game_id
        filename = self.action_answers_dir / f"{mapped_name}_action_answers_game{game_id}_run{run_id}.json"
        
        # Build output with metadata
        output = {
            "metadata": {
                "game_id": game_id,
                "run_id": run_id,
                "player": mapped_name,
                **self.current_game_metadata
            },
            "action_answers": self.action_answers[player]
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

    def save_game_history(self, run_id: int = None) -> None:
        """Save game history to JSON file with game_id."""
        if run_id is None:
            run_id = self.run_id
        
        game_id = self.current_game_id
        filename = self.game_histories_dir / f"game_history_game{game_id}_run{run_id}.json"
        
        # Convert to A/B format
        players_history = {}
        for player, history in self.game_histories.items():
            mapped = self._map_player_name(player)
            players_history[mapped] = history
        
        # Build output with metadata
        output = {
            "metadata": {
                "game_id": game_id,
                "run_id": run_id,
                **self.current_game_metadata
            },
            "history": players_history
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

    def save_checker_results(self, checker, run_id: int = None) -> None:
        """
        Save checker results to JSON file with game_id.
        
        Args:
            checker: Checker object with questions_results
            run_id: Run ID for filename
        """
        if run_id is None:
            run_id = self.run_id
        
        game_id = self.current_game_id
        checker_name = checker.name
        checker_dir = self.base_dir / checker_name
        checker_dir.mkdir(exist_ok=True)
        
        # Build output dict with metadata
        output = {
            "metadata": {
                "game_id": game_id,
                "run_id": run_id,
                "checker": checker_name,
                **self.current_game_metadata
            },
            checker_name: {
                "checker": checker_name,
                "question": checker_name,
                "sample_mean": checker.sample_mean,
                "sample_variance": checker.sample_variance,
                "total": float(checker.total),
                "positives": float(checker.positives),
                "squared_diffs_sum": checker.squared_diffs_sum
            }
        }
        
        # Add per-question results
        for label, data in checker.questions_results.items():
            output[label] = {
                "checker": checker_name,
                "question": data.get("question", label),
                "sample_mean": data.get("sample_mean", 0),
                "sample_variance": data.get("sample_variance", 0),
                "total": float(data.get("total", 0)),
                "positives": float(data.get("positives", 0)),
                "squared_diffs_sum": data.get("squared_diffs_sum", 0)
            }
        
        filename = checker_dir / f"{checker_name}_game{game_id}_run{run_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)
        
        # Also save complete_answers and light_answers with game_id
        try:
            checker.save_complete_answers(self.base_dir, infix=f"game{game_id}_run{run_id}")
        except Exception as e:
            print(f"Warning: Could not save complete_answers for {checker_name}: {e}")
        
        # Store for later CSV generation
        self.checker_results[checker_name] = output

    def save_all_checker_results(self, checkers: List, run_id: int = None) -> None:
        """Save results for all checkers."""
        for checker in checkers:
            self.save_checker_results(checker, run_id)

    def _calculate_ci(self, mean: float, variance: float, n: int, 
                      confidence: float = 0.95) -> tuple:
        """
        Calculate confidence interval.
        
        Returns:
            (lower_bound, upper_bound)
        """
        if n <= 1:
            return (mean, mean)
        
        # Standard error
        se = math.sqrt(variance / n) if variance > 0 else 0
        
        # Z-score for 95% CI
        z = 1.96
        
        lb = max(0, mean - z * se)
        ub = min(1, mean + z * se)
        
        return (lb, ub)

    def generate_summary_csv(self) -> None:
        """Generate comprehension_questions_results.csv from checker results."""
        filename = self.base_dir / "comprehension_questions_results.csv"
        
        rows = []
        idx = 0
        
        # Process each checker type
        checker_type_map = {
            "time_checker": "time",
            "rule_checker": "rules",
            "aggregation_checker": "state"
        }
        
        for checker_name, results in self.checker_results.items():
            ctype = checker_type_map.get(checker_name, "other")
            
            for label, data in results.items():
                if label == checker_name:
                    continue  # Skip aggregate row
                
                mean = data.get("sample_mean", 0)
                var = data.get("sample_variance", 0)
                total = int(data.get("total", 0))
                
                lb, ub = self._calculate_ci(mean, var, total)
                
                rows.append({
                    "": idx,
                    "type": ctype,
                    "full_question": data.get("question", label),
                    "label": label,
                    "accuracy": mean,
                    "ci_lb": lb,
                    "ci_ub": ub
                })
                idx += 1
        
        # Write CSV
        if rows:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["", "type", "full_question", 
                                                       "label", "accuracy", "ci_lb", "ci_ub"])
                writer.writeheader()
                writer.writerows(rows)

    def clear_round_data(self) -> None:
        """Clear accumulated data for next run."""
        self.action_answers = {}
        self.game_histories = {}

    def finalize_run(self, run_id: int = None) -> None:
        """
        Finalize a run by saving all accumulated data.
        
        Args:
            run_id: Run ID (defaults to self.run_id)
        """
        if run_id is None:
            run_id = self.run_id
        
        # Save action answers for all players
        for player in self.action_answers:
            self.save_action_answers(player, run_id)
        
        # Save game history
        self.save_game_history(run_id)
        
        # Clear for next run
        self.clear_round_data()
        
        # Increment run ID
        self.run_id += 1

    def record_game_summary(self, game_data: Dict[str, Any]) -> None:
        """
        Record a single game's summary data for later CSV export.
        
        Args:
            game_data: Dict with game info including:
                - game_id, language, n_rounds_is_known, max_rounds, played_rounds
                - agent info: name, llm, personality, strategies, scores, noise_rate
                - checker accuracies (optional)
        """
        self.games_summary.append(game_data)

    def save_games_summary_csv(self) -> None:
        """
        Save comprehensive games_summary.csv with all game data.
        
        Includes FAIRGAME columns + noise features:
        - game_id, language, n_rounds_is_known, max_rounds, played_rounds
        - agent1/agent2: name, llm, personality, strategies, scores, noise_rate, flipped_count
        - checker accuracies
        """
        if not self.games_summary:
            return
        
        filename = self.base_dir / "games_summary.csv"
        
        # Define CSV columns
        fieldnames = [
            "game_id", "language", "n_rounds_is_known", "max_rounds", "played_rounds",
            "agent1_name", "agent1_llm", "agent1_personality", "agent1_noise_rate",
            "agent1_strategies", "agent1_intended_strategies", "agent1_flipped_count",
            "agent1_scores", "agent1_total_score",
            "agent2_name", "agent2_llm", "agent2_personality", "agent2_noise_rate", 
            "agent2_strategies", "agent2_intended_strategies", "agent2_flipped_count",
            "agent2_scores", "agent2_total_score",
            "time_checker_accuracy", "rule_checker_accuracy", "aggregation_checker_accuracy"
        ]
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for game_data in self.games_summary:
                writer.writerow(game_data)
        
        print(f"Games summary saved to: {filename}")

    def finalize_all(self, checkers: List = None) -> None:
        """
        Finalize all runs and generate summary files.
        
        Args:
            checkers: List of checker objects to save (legacy, for comprehension CSV)
        """
        # Generate comprehension questions CSV (legacy format)
        self.generate_summary_csv()
        
        # Generate comprehensive games summary CSV
        self.save_games_summary_csv()
        
        # Write log file with timestamp
        log_file = self.base_dir / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        with open(log_file, "w") as f:
            f.write(f"Run completed at {datetime.now().isoformat()}\n")
            f.write(f"Total runs: {self.run_id}\n")
            f.write(f"Checkers: {list(self.checker_results.keys())}\n")
            f.write(f"Total games: {len(self.games_summary)}\n")
