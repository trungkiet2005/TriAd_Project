from typing import List, Dict, Any, Union
from src.game.payoff_matrix import PayoffMatrix
from src.game.game_history import GameHistory
# Avoid circular import by importing inside method or using string forward references if needed.
# For now, let's see if we can import GameRound. 
# GameRound imports FairGame for type hinting usually.
# Let's import GameRound inside the method where it's used to be safe.

class FairGame:
    """
    Top-level game engine that orchestrates multiple rounds, applies payoff matrices,
    and checks for stop conditions.
    """

    def __init__(self, name: str, language: str, agents: Dict[str, Any], n_rounds: int, 
                 n_rounds_known: Union[str, bool], payoff_matrix_data: Dict[str, Any], 
                 prompt_template: str, stop_conditions: List[str], 
                 agents_communicate: Union[str, bool], is_penalty: bool = True) -> None:
        """
        Initialize the FairGame with all required parameters.

        Args:
            name (str): The name of the game.
            language (str): The language used by the game and payoff matrix.
            agents (Dict[str, Any]): A dictionary mapping agent names to agent objects.
            n_rounds (int): The total number of rounds to play.
            n_rounds_known (Union[str, bool]): If the number of rounds is known to agents.
            payoff_matrix_data (Dict[str, Any]): The data defining the payoff matrix.
            prompt_template (str): The template used to generate prompts for agents.
            stop_conditions (List[str]): A list of combinations that end the game early if chosen.
            agents_communicate (Union[str, bool]): Whether agents communicate before choosing strategies.
            is_penalty (bool): If True, the game payoffs are penalties (minimization). Default False.
        """
        self.name = name
        self.language = language
        self.agents = agents
        self.n_rounds = int(n_rounds)
        self.n_rounds_known = self._str2bool(n_rounds_known)
        self.prompt_template = prompt_template
        self.stop_conditions = stop_conditions
        self.agents_communicate = self._str2bool(agents_communicate)
        self.current_round = 1
        self.history = GameHistory()
        self.choices_made: List[List[str]] = []
        self.payoff_matrix = PayoffMatrix(payoff_matrix_data, language)
        self.is_penalty = is_penalty

    def _str2bool(self, value: Union[str, bool]) -> bool:
        """
        Convert a string or bool to a boolean value.

        Args:
            value (Union[str, bool]): The value to interpret as bool.

        Returns:
            bool: The interpreted boolean value.
        """
        return value if isinstance(value, bool) else value.strip().lower() == 'true'

    @property
    def description(self) -> Dict[str, Any]:
        """
        dict: A description of the game settings, including agents, language,
              number of rounds, and payoff matrix data.
        """
        return {
            "name": self.name,
            "language": self.language,
            "agents": {name: agent.get_info() for name, agent in self.agents.items()},
            "n_rounds": self.n_rounds,
            "number_of_rounds_is_known": self.n_rounds_known,
            "payoff_matrix": self.payoff_matrix.matrix_data,
            "agents_communicate": self.agents_communicate
        }

    def run_round(self) -> None:
        """
        Run a single round of the game using the GameRound helper class.
        Record the strategies chosen and update agent scores.

        This method increments the current_round after execution.
        """
        from src.game.game_round import GameRound
        round_runner = GameRound(self)
        round_strategies = round_runner.run()
        self.choices_made.append(round_strategies)
        self.payoff_matrix.attribute_scores(list(self.agents.values()), round_strategies)
        round_runner._update_round_history()

    def stop_condition_is_met(self) -> bool:
        """
        Check whether the stop condition is met based on the last round's choices.

        Returns:
            bool: True if the last round's combination matches any stop condition,
                  False otherwise.
        """
        if self.choices_made:
            last_round_choices = self.choices_made[-1]
            # Look up the combination key based on the round choices.
            combination = next(
                (k for k, v in self.payoff_matrix.matrix_data['combinations'].items()
                 if v == last_round_choices),
                None
            )
            if combination in self.stop_conditions:
                return True
        return False

    def run(self) -> GameHistory:
        """
        Runs the simulation until all rounds are complete or a stop condition is met.

        Returns:
            GameHistory: The history object containing all round data.
        """
        while self.current_round <= self.n_rounds and not self.stop_condition_is_met():
            self.run_round()
            self.current_round += 1

        return self.history
