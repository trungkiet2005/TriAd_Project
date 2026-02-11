"""
TimeChecker - Checks if agents understand the temporal sequence of the game.
"""

from typing import Set

from src.checkers.checker import Checker
from src.checkers.checker_utils import (
    generate_game_rules_prompt,
    generate_history_prompt_generic,
    generate_prompt_from_sub_prompts,
    find_first_int,
    find_first_substring,
    to_nat_lang
)
from src.checkers.checker_translations import get_translation


class TimeChecker(Checker):
    """
    Checker for temporal understanding of game state.
    
    Verifies if the LLM correctly remembers:
    - What round the game is currently in
    - What actions were played in specific past rounds
    - What scores were earned in specific past rounds
    """

    def __init__(self):
        # Questions will be generated dynamically
        super().__init__("time_checker", [], [])

    def check_current_round(self, current_round: int, question_idx: int) -> None:
        """Check if LLM knows the current round number."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <CURRENT_ROUND>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = str(current_round)
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def check_action_played(self, inspected_round: int, action_played: str, 
                           action_space: Set[str], player_name: str, question_idx: int) -> None:
        """Check if LLM knows what action was played in a specific round."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <ACTION_PLAYED>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = to_nat_lang(action_played, string_of_string=False)
        nat_action_space = {to_nat_lang(action, string_of_string=False) for action in action_space}
        llm_answer = find_first_substring(self.get_answer_from_llm(prompt, label), nat_action_space)
        self.check_answer(llm_answer, correct_answer, label)

    def check_points_collected(self, inspected_round: int, points_collected: int, 
                               player_name: str, question_idx: int) -> None:
        """Check if LLM knows points collected in a specific round."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <POINTS_COLLECTED>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = str(points_collected)
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def ask_checker_questions(self, game, player_name: str = "", history_window_size: int = None) -> None:
        """
        Ask all time-related questions about the game.

        Args:
            game: The NoiseFairGame instance
            player_name: Name of the player being checked (e.g., "agent1")
            history_window_size: Number of past rounds to include in context
        """
        # Get game state
        current_round = len(game.choices_made) + 1
        n_iterations = game.n_rounds
        is_ended = current_round > n_iterations
        n_players = len(game.agents)
        agent_names = list(game.agents.keys())
        
        # Get Language and Penalty Mode
        language = getattr(game, 'language', 'en')
        is_penalty = getattr(game, 'is_penalty', False)
        
        # Get action space from payoff matrix
        action_space = set(game.payoff_matrix.strategies.values())
        
        # Identify player index
        player_idx = agent_names.index(player_name) if player_name in agent_names else 0
        
        # Get histories for ALL players
        all_histories = []
        for name in agent_names:
            all_histories.append([s for s in game.agents[name].strategies])
            
        # Generate generic system prompt
        game_rules_prompt = generate_game_rules_prompt(
            action_space, game.payoff_matrix, n_iterations, 
            agent_names, language=language, is_penalty=is_penalty
        )
        
        history_prompt = generate_history_prompt_generic(
            all_histories, player_idx, game.payoff_matrix, agent_names,
            window_size=history_window_size, is_ended=is_ended,
            language=language, is_penalty=is_penalty
        )
        self.system_prompt = game_rules_prompt + history_prompt

        # Reset questions for dynamic generation
        self.questions = []
        self.questions_labels = []

        # Question 0: Current round (only if game not ended)
        if not is_ended:
            q_text = get_translation(language, "time_current_round")
            self.questions.append(q_text)
            self.questions_labels.append("current_round")
            
            if "current_round" not in self.questions_results:
                self._init_question_result("current_round", q_text)
                
            self.check_current_round(current_round, len(self.questions) - 1)
        
        # Only ask about past rounds if there is history
        if len(all_histories[0]) == 0:
            return
        
        # Limit questions to avoid too many API calls
        max_rounds_to_check = min(history_window_size or 5, len(all_histories[0]), 3)
        rounds_to_check = range(max(1, len(all_histories[0]) - max_rounds_to_check + 1), len(all_histories[0]) + 1)
        
        unit_key = "unit_penalty" if is_penalty else "unit_points"
        unit = get_translation(language, unit_key)

        # Ask about EACH player's actions and points
        for i, name in enumerate(agent_names):
             p_label = name
             
             # Check Actions
             for r_num in rounds_to_check:
                 round_idx = r_num - 1
                 action_played = all_histories[i][round_idx]
                 
                 # "Which action did player {player} play in round {round}?"
                 q_text = get_translation(language, "time_action_round", player=p_label, round=r_num)
                 
                 self.questions.append(q_text)
                 label = f"action_{p_label}_{r_num}"
                 self.questions_labels.append(label)
                 
                 if label not in self.questions_results:
                     self._init_question_result(label, q_text)
                 
                 self.check_action_played(r_num, action_played, action_space, p_label, len(self.questions)-1)
                 
             # Check Points
             # Only if we can calculate them
             for r_num in rounds_to_check:
                round_idx = r_num - 1
                round_actions = [h[round_idx] for h in all_histories]
                try:
                    weights = game.payoff_matrix.get_weights_for_combination(round_actions)
                    points = weights[i] # Points for this player
                    
                    # "How many {unit}s did player {player} collect in round {round}?"
                    q_text = get_translation(language, "time_score_round", player=p_label, unit=unit, round=r_num)
                    
                    self.questions.append(q_text)
                    label = f"points_{p_label}_{r_num}"
                    self.questions_labels.append(label)
                    
                    if label not in self.questions_results:
                         self._init_question_result(label, q_text)

                    self.check_points_collected(r_num, points, p_label, len(self.questions)-1)
                except Exception:
                    continue

    def _init_question_result(self, label: str, question: str):
        """Helper to initialize result structure for a dynamically added question."""
        self.questions_results[label] = {
            self.checker_str: self.name,
            self.question_str: question,
            self.sample_mean_str: 0,
            self.sample_variance_str: 0,
            self.total_str: 0,
            self.positives_str: 0,
            self.squared_diffs_sum_str: 0,
            self.prompt_str: [],
            self.generated_text_str: [],
            self.answer_str: [],
        }
