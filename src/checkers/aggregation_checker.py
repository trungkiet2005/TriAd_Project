"""
AggregationChecker - Checks if agents understand aggregate game statistics.

Adapted from nicer_than_human's aggregation_checker.py to match original paper format.
Questions about:
- Total number of times each action was chosen
- Total points collected by each player
"""

from typing import Set

from src.checkers.checker import Checker
from src.checkers.checker_utils import (
    player_1_, player_2_,
    generate_game_rules_prompt,
    generate_history_prompt,
    generate_prompt_from_sub_prompts,
    find_first_int,
    to_nat_lang
)


class AggregationChecker(Checker):
    """
    Checker for aggregate statistics understanding.
    
    Verifies if the LLM correctly tracks:
    - How many times each action was chosen
    - Total points accumulated by each player
    """

    def __init__(self):
        questions = [
            f"How many times did player {player_1_} choose {{}}?",
            f"How many times did player {player_2_} choose {{}}?",
            f"What is player {player_1_}'s current total payoff?",
            f"What is player {player_2_}'s current total payoff?",
        ]
        questions_labels = [
            f"#actions_{player_1_}",
            f"#actions_{player_2_}",
            f"total_payoff_{player_1_}",
            f"total_payoff_{player_2_}",
        ]
        super().__init__("aggregation_checker", questions, questions_labels)

    def check_action_chosen(self, action: str, n_times: int, question_idx: int) -> None:
        """Check if LLM knows how many times an action was chosen."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <N_TIMES>}\n'
        question_prompt = f"Answer to the following question: {question.format(to_nat_lang(action))}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = str(n_times)
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def check_total_payoff(self, payoff: int, question_idx: int) -> None:
        """Check if LLM knows the total payoff of a player."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <TOTAL_PAYOFF>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = str(payoff)
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def ask_checker_questions(self, game, player_name: str = "", history_window_size: int = None) -> None:
        """
        Ask all aggregation-related questions about the game.

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
        
        # Skip if no history yet
        if len(own_history) == 0:
            return
        
        # Calculate totals
        own_total_payoff = sum(payoff_function(own_history[i], opponent_history[i]) for i in range(len(own_history)))
        opponent_total_payoff = sum(payoff_function(opponent_history[i], own_history[i]) for i in range(len(opponent_history)))
        
        # Question 0: How many times player A chose each action
        for action in action_space:
            n_times = own_history.count(action)
            self.check_action_chosen(action, n_times, question_idx=0)
        
        # Question 1: How many times player B chose each action
        for action in action_space:
            n_times = opponent_history.count(action)
            self.check_action_chosen(action, n_times, question_idx=1)
        
        # Question 2: Player A's total payoff
        self.check_total_payoff(own_total_payoff, question_idx=2)
        
        # Question 3: Player B's total payoff
        self.check_total_payoff(opponent_total_payoff, question_idx=3)
