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
    player_1_, player_2_,
    generate_game_rules_prompt,
    generate_history_prompt,
    generate_prompt_from_sub_prompts,
    find_first_int,
    find_first_substring,
    to_nat_lang
)


class RuleChecker(Checker):
    """
    Checker for game rules understanding.
    
    Verifies if the LLM correctly understands:
    - The maximum and minimum possible payoffs
    - Which actions are allowed
    - The payoff for specific action combinations
    """

    def __init__(self):
        questions = [
            f"What is the highest payoff player {player_1_} can get in a single round?",
            f"What is the lowest payoff player {player_1_} can get in a single round?",
            f"Which actions is player {player_1_} allowed to play?",
            f"Which is player {player_1_}'s payoff in a single round if {player_1_} plays {{}} and {player_2_} plays {{}}?",
            f"Which is player {player_2_}'s payoff in a single round if {player_1_} plays {{}} and {player_2_} plays {{}}?",
        ]
        questions_labels = [
            "max_payoff",
            "min_payoff",
            "allowed_actions",
            f"round_payoff_{player_1_}",
            f"round_payoff_{player_2_}",
        ]
        super().__init__("rule_checker", questions, questions_labels)

    def check_payoff_bounds(self, is_max: bool, action_space: Set[str], 
                           payoff_function, question_idx: int) -> None:
        """Check if LLM knows the max/min possible payoff."""
        min_payoff = None
        max_payoff = None
        
        for primary_action in action_space:
            for secondary_action in action_space:
                payoff = payoff_function(primary_action, secondary_action)
                if min_payoff is None or payoff < min_payoff:
                    min_payoff = payoff
                if max_payoff is None or payoff > max_payoff:
                    max_payoff = payoff
        
        if is_max:
            correct_answer = str(max_payoff)
            json_prompt = 'Remember to use the following JSON format: {"answer": <MAX_PAYOFF>}\n'
        else:
            correct_answer = str(min_payoff)
            json_prompt = 'Remember to use the following JSON format: {"answer": <MIN_PAYOFF>}\n'
        
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def check_allowed_actions(self, action_space: Set[str], question_idx: int) -> None:
        """Check if LLM knows the allowed actions."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        correct_answer = {to_nat_lang(action, string_of_string=False) for action in action_space}
        json_prompt = 'Remember to use the following JSON format: {"answer": [<LIST_OF_AVAILABLE_ACTIONS>]}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = set(self.get_answer_from_llm(prompt, label, need_str=False))
        self.check_answer(llm_answer, correct_answer, label)

    def check_payoff_of_combo(self, primary_action: str, secondary_action: str, 
                              payoff_function, question_idx: int, is_inverse: bool = False) -> None:
        """Check if LLM knows the payoff for a specific action combination."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        correct_answer = str(payoff_function(primary_action, secondary_action))
        json_prompt = 'Remember to use the following JSON format: {"answer": <PAYOFF>}\n'
        
        if is_inverse:
            question_prompt = f"Answer to the following question: {question.format(to_nat_lang(secondary_action), to_nat_lang(primary_action))}\n"
        else:
            question_prompt = f"Answer to the following question: {question.format(to_nat_lang(primary_action), to_nat_lang(secondary_action))}\n"
        
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def ask_checker_questions(self, game, player_name: str = "", history_window_size: int = None) -> None:
        """
        Ask all rule-related questions about the game.

        Args:
            game: The NoiseFairGame instance
            player_name: Name of the player being checked
            history_window_size: Number of past rounds to include in context
        """
        # Get game state
        n_iterations = game.n_rounds
        current_round = len(game.choices_made) + 1
        is_ended = current_round > n_iterations
        
        # Get action space
        action_space = set(game.payoff_matrix.strategies.values())
        
        # Get player names
        agent_names = list(game.agents.keys())
        player_idx = agent_names.index(player_name) if player_name in agent_names else 0
        opponent_idx = 1 - player_idx
        opponent_name = agent_names[opponent_idx]
        
        # Get histories
        own_history = [s for s in game.agents[player_name].strategies]
        opponent_history = [s for s in game.agents[opponent_name].strategies]
        
        # Create payoff function
        def payoff_function(own_action: str, opp_action: str) -> int:
            return game.payoff_matrix.get_score(own_action, opp_action)
        
        # Generate system prompt
        game_rules_prompt = generate_game_rules_prompt(action_space, game.payoff_matrix, n_iterations)
        history_prompt = generate_history_prompt(
            own_history, opponent_history, payoff_function,
            window_size=history_window_size, is_ended=is_ended
        )
        self.system_prompt = game_rules_prompt + history_prompt

        # Question 0: Max payoff
        self.check_payoff_bounds(True, action_space, payoff_function, question_idx=0)
        
        # Question 1: Min payoff
        self.check_payoff_bounds(False, action_space, payoff_function, question_idx=1)
        
        # Question 2: Allowed actions
        self.check_allowed_actions(action_space, question_idx=2)
        
        # Questions 3-4: Payoff for each action combination
        for primary_action in action_space:
            for secondary_action in action_space:
                # Question 3: Player A's payoff
                self.check_payoff_of_combo(primary_action, secondary_action, payoff_function, question_idx=3)
                # Question 4: Player B's payoff
                self.check_payoff_of_combo(primary_action, secondary_action, payoff_function, is_inverse=True, question_idx=4)
