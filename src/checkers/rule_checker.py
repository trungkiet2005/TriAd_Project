"""
RuleChecker - Checks if agents understand the game rules.

Adapted from nicer_than_human's rule_checker.py to match original paper format.
Questions about:
- Maximum and minimum possible payoffs
- Allowed actions
- Payoff values for different action combinations
"""

from typing import Set

from src.checkers.checker import Checker
from src.checkers.checker_utils import (
    generate_game_rules_prompt,
    generate_history_prompt_generic,
    generate_prompt_from_sub_prompts,
    find_first_int,
    to_nat_lang
)
from src.checkers.checker_translations import get_translation


class RuleChecker(Checker):
    """
    Checker for game rules understanding.
    
    Verifies if the LLM correctly understands:
    - The maximum and minimum possible payoffs
    - Which actions are allowed
    - The payoff for specific action combinations
    """

    def __init__(self):
        # We initialize with basic questions. 
        # Specific payoff combination questions will be generated dynamically.
        super().__init__("rule_checker", [], [])

    def check_payoff_bounds(self, is_max: bool, action_space: Set[str], 
                           payoff_function, question_idx: int) -> None:
        """Check if LLM knows the max/min possible payoff."""
        # Deprecated in favor of generic method below
        pass

    def check_allowed_actions(self, action_space: Set[str], agent_name: str, 
                              language: str, question_idx: int) -> None:
        """Check if LLM knows the allowed actions."""
        # Dynamic question
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        correct_answer = {to_nat_lang(action, string_of_string=False) for action in action_space}
        json_prompt = 'Remember to use the following JSON format: {"answer": [<LIST_OF_AVAILABLE_ACTIONS>]}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = set(self.get_answer_from_llm(prompt, label, need_str=False))
        self.check_answer(llm_answer, correct_answer, label)

    def check_payoff_of_combo_dynamic(self, actions: list, payoff_matrix, agent_names: list, 
                                      target_player_idx: int, language: str, is_penalty: bool) -> None:
        """
        Check if LLM knows the payoff for a specific action combination (N-player supported).
        """
        # Calculate correct answer
        try:
            weights = payoff_matrix.get_weights_for_combination(actions)
            correct_answer = str(weights[target_player_idx])
        except Exception as e:
            print(f"Error calculating payoff for {actions}: {e}")
            return

        target_name = agent_names[target_player_idx]
        
        # Construct dynamic question using translations
        # "What is player {Target}'s {unit} in a single round if {conditions}?"
        condition_parts = []
        for i, action in enumerate(actions):
            # "player {player} plays '{action}'"
            part = get_translation(language, "condition_play", player=agent_names[i], action=to_nat_lang(action))
            condition_parts.append(part)
            
        join_and = get_translation(language, "join_and")
        condition_str = join_and.join(condition_parts)
        
        unit_key = "unit_penalty" if is_penalty else "unit_points"
        unit = get_translation(language, unit_key)
        
        question = get_translation(language, "rule_combo_payoff", 
                                  player=target_name, unit=unit, conditions=condition_str)
        
        label = f"payoff_check_p{target_player_idx}_{'_'.join([str(a)[:3] for a in actions])}"
        
        # Add to local tracking if not present (though we probably add it in ask_checker_questions loop)
        self.questions.append(question)
        self.questions_labels.append(label)
        if label not in self.questions_results:
             self._init_question_result(label, question)
        
        json_prompt = 'Remember to use the following JSON format: {"answer": <PAYOFF>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)
        
    def _init_question_result(self, label: str, question: str):
        """Helper to initialize result structure."""
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

    def ask_checker_questions(self, game, player_name: str = "", history_window_size: int = None) -> None:
        """
        Ask all rule-related questions about the game.
        """
        # Get game state
        n_iterations = game.n_rounds
        n_players = len(game.agents)
        agent_names = list(game.agents.keys())
        
        # Get Language and Penalty Mode from game config (or assume defaults)
        # We need to access game.config if available, or pass it down.
        # Assuming we can inspect game object for these properties if added, 
        # or defaults.
        # The user requested reading from config. The game object is created from config.
        # But `game` object might not have direct `language` attribute on root.
        # It has `agents` dict.
        # We check `game.game_config` if it exists (from Factory).
        # Fallback: check kwargs or similar?
        # For now, let's look for known attributes or default to 'en'
        
        # Typically configurations are passed to the factory.
        # Let's try to detect language from agent personalities or simply default to 'vn' if requested.
        # But we need to support dynamic run.
        # Is there a global config attached to game?
        # In `NoiseFairGameFactory`: `game = NoiseFairGame(...)`
        # In `NoiseFairGame`: `self.payoff_matrix = ...`
        
        # Let's assume for this refactor we might need to update `NoiseFairGame` to store `language` and `is_penalty`.
        # OR we try to deduce it.
        # If `payoffMatrix` has "penalty" word, maybe implies penalty?
        # The user said "game dùng hình phạt nha" (game uses penalty).
        
        language = getattr(game, 'language', 'en')
        is_penalty = getattr(game, 'is_penalty', False)
        
        # Get action space
        action_space = set(game.payoff_matrix.strategies.values())
        
        # Generate generic system prompt
        game_rules_prompt = generate_game_rules_prompt(
            action_space, game.payoff_matrix, n_iterations, 
            agent_names, language=language, is_penalty=is_penalty
        )
        
        # Gather histories
        all_histories = []
        for name in agent_names:
            all_histories.append([s for s in game.agents[name].strategies])
            
        # Determine player index
        player_idx = agent_names.index(player_name) if player_name in agent_names else 0

        history_prompt = generate_history_prompt_generic(
            all_histories, player_idx, game.payoff_matrix, agent_names,
            window_size=history_window_size, is_ended=(len(all_histories[0]) >= n_iterations),
            language=language, is_penalty=is_penalty
        )
        self.system_prompt = game_rules_prompt + history_prompt
        
        # Reset questions
        self.questions = []
        self.questions_labels = []

        # Question 0 & 1: Max/Min bounds (Dynamic generation logic)
        self._check_payoff_bounds_generic_dynamic(True, game.payoff_matrix, agent_names, 0, language, is_penalty)
        self._check_payoff_bounds_generic_dynamic(False, game.payoff_matrix, agent_names, 0, language, is_penalty)
        
        # Question 2: Allowed actions
        q_text = get_translation(language, "rule_allowed_actions", player=agent_names[0])
        self.questions.append(q_text)
        self.questions_labels.append("allowed_actions")
        self._init_question_result("allowed_actions", q_text)
        
        self.check_allowed_actions(action_space, agent_names[0], language, len(self.questions)-1)
        
        # Payoff checks: Testing specific combinations
        sorted_actions = sorted(list(action_space))
        if len(sorted_actions) >= 2:
            action1 = sorted_actions[0] 
            action2 = sorted_actions[1] 
            
            # Test 1: Everyone plays Action 1
            actions_all_1 = [action1] * n_players
            self.check_payoff_of_combo_dynamic(actions_all_1, game.payoff_matrix, agent_names, 0, language, is_penalty)
            
            # Test 2: Everyone plays Action 2
            actions_all_2 = [action2] * n_players
            self.check_payoff_of_combo_dynamic(actions_all_2, game.payoff_matrix, agent_names, 0, language, is_penalty)
            
            # Test 3: Mixed
            if n_players >= 2:
                actions_mixed = [action1] + [action2] * (n_players - 1)
                self.check_payoff_of_combo_dynamic(actions_mixed, game.payoff_matrix, agent_names, 0, language, is_penalty)
                self.check_payoff_of_combo_dynamic(actions_mixed, game.payoff_matrix, agent_names, 1, language, is_penalty)

    def _check_payoff_bounds_generic_dynamic(self, check_highest: bool, payoff_matrix, agent_names, 
                                             target_player_idx: int, language: str, is_penalty: bool) -> None:
        """
        Measure max/min payoff from the matrix data and ask LLM.
        
        Args:
            check_highest: If True, asks for the "Highest" value. If False, "Lowest".
            ...
        """
        weights = payoff_matrix.weights.values()
        if not weights:
            return
            
        max_val = max(weights)
        min_val = min(weights)
        
        # Decision Logic:
        # If is_penalty=True (minimization):
        #   - "Highest penalty" -> max_val (Worst outcome)
        #   - "Lowest penalty" -> min_val (Best outcome)
        # If is_penalty=False (maximization):
        #   - "Highest payoff" -> max_val (Best outcome)
        #   - "Lowest payoff" -> min_val (Worst outcome)
        
        target_val = max_val if check_highest else min_val
        
        correct_answer = str(target_val)
        
        unit_key = "unit_penalty" if is_penalty else "unit_points"
        unit = get_translation(language, unit_key)
        
        player_name = agent_names[target_player_idx]
        
        if check_highest:
             # "What is the highest {unit} player {player} can get?"
             question = get_translation(language, "rule_max_val", unit=unit, player=player_name)
             label = "max_bound"
             json_prompt = 'Remember to use the following JSON format: {"answer": <MAX_VAL>}\n'
        else:
             # "What is the lowest {unit} player {player} can get?"
             question = get_translation(language, "rule_min_val", unit=unit, player=player_name)
             label = "min_bound"
             json_prompt = 'Remember to use the following JSON format: {"answer": <MIN_VAL>}\n'
             
        self.questions.append(question)
        self.questions_labels.append(label)
        if label not in self.questions_results:
             self._init_question_result(label, question)
        
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

