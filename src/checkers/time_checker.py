"""
TimeChecker - Checks if agents understand temporal aspects of the game.

Adapted from nicer_than_human's time_checker.py to match original paper format.
Questions about:
- Current round number
- Actions taken in specific rounds
- Points collected in specific rounds
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


class TimeChecker(Checker):
    """
    Checker for temporal understanding of game state.
    
    Verifies if the LLM correctly remembers:
    - What round the game is currently in
    - What actions were played in specific past rounds
    - What scores were earned in specific past rounds
    """

    def __init__(self):
        questions = [
            "Which is the current round of the game?",
            f"Which action did player {player_1_} play in round {{}}?",
            f"Which action did player {player_2_} play in round {{}}?",
            f"How many points did player {player_1_} collect in round {{}}?",
            f"How many points did player {player_2_} collect in round {{}}?",
        ]
        questions_labels = [
            "current_round",
            f"action_{player_1_}",
            f"action_{player_2_}",
            f"points_{player_1_}",
            f"points_{player_2_}",
        ]
        super().__init__("time_checker", questions, questions_labels)

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
                           action_space: Set[str], question_idx: int) -> None:
        """Check if LLM knows what action was played in a specific round."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <ACTION_PLAYED>}\n'
        question_prompt = f"Answer to the following question: {question.format(inspected_round)}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = to_nat_lang(action_played, string_of_string=False)
        nat_action_space = {to_nat_lang(action, string_of_string=False) for action in action_space}
        llm_answer = find_first_substring(self.get_answer_from_llm(prompt, label), nat_action_space)
        self.check_answer(llm_answer, correct_answer, label)

    def check_points_collected(self, inspected_round: int, points_collected: int, 
                               question_idx: int) -> None:
        """Check if LLM knows points collected in a specific round."""
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        json_prompt = 'Remember to use the following JSON format: {"answer": <POINTS_COLLECTED>}\n'
        question_prompt = f"Answer to the following question: {question.format(inspected_round)}\n"
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
        
        # Get action space from payoff matrix
        action_space = set(game.payoff_matrix.strategies.values())  # e.g., {"Cooperate", "Defect"}
        
        # Get player names (map to A/B for original format)
        agent_names = list(game.agents.keys())
        player_idx = agent_names.index(player_name) if player_name in agent_names else 0
        opponent_idx = 1 - player_idx
        opponent_name = agent_names[opponent_idx]
        
        # Get histories
        own_history = [s for s in game.agents[player_name].strategies]
        opponent_history = [s for s in game.agents[opponent_name].strategies]
        
        # Create payoff function using game's payoff matrix
        def payoff_function(own_action: str, opp_action: str) -> int:
            return game.payoff_matrix.get_score(own_action, opp_action)
        
        # Generate system prompt
        game_rules_prompt = generate_game_rules_prompt(action_space, game.payoff_matrix, n_iterations)
        history_prompt = generate_history_prompt(
            own_history, opponent_history, payoff_function, 
            window_size=history_window_size, is_ended=is_ended
        )
        self.system_prompt = game_rules_prompt + history_prompt

        # Question 0: Current round (only if game not ended)
        if not is_ended:
            self.check_current_round(current_round, question_idx=0)
        
        # Only ask about past rounds if there is history
        if len(own_history) == 0:
            return
        
        # Limit questions to avoid too many API calls
        max_rounds_to_check = min(history_window_size or 5, len(own_history), 3)
        rounds_to_check = range(max(1, len(own_history) - max_rounds_to_check + 1), len(own_history) + 1)
        
        # Question 1: Actions player A played
        for i in rounds_to_check:
            self.check_action_played(i, own_history[i - 1], action_space, question_idx=1)
        
        # Question 2: Actions player B played
        for i in rounds_to_check:
            self.check_action_played(i, opponent_history[i - 1], action_space, question_idx=2)
        
        # Question 3: Points player A collected
        for i in rounds_to_check:
            points = payoff_function(own_history[i - 1], opponent_history[i - 1])
            self.check_points_collected(i, points, question_idx=3)
        
        # Question 4: Points player B collected
        for i in rounds_to_check:
            points = payoff_function(opponent_history[i - 1], own_history[i - 1])
            self.check_points_collected(i, points, question_idx=4)
