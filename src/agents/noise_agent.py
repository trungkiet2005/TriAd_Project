"""
NoiseAgent - Agent with configurable noise rate for action flipping.

This extends the base Agent to support:
1. Noise rate for this agent (probability of flipping own action)
2. Opponent noise rate (shown in prompt so agent knows about it)
3. Tracking of original vs noised actions
"""

import random
from typing import Any, Dict, List, Tuple
from src.agents.agent import Agent
from src.game.payoff_matrix import PayoffMatrix


class NoiseAgent(Agent):
    """
    An agent that can have its actions flipped based on a noise rate.
    
    The noise is applied AFTER the agent makes a decision, simulating
    communication errors or implementation mistakes in the Prisoner's Dilemma.
    """

    def __init__(
        self, 
        name: str, 
        llm_service: str, 
        personality: str, 
        opponent_personality_prob: int,
        noise_rate: float = 0.0,
        opponent_noise_rate: float = 0.0,
        strategies: Dict[str, str] = None
    ) -> None:
        """
        Initialize the NoiseAgent instance.

        Args:
            name (str): The name of the agent.
            llm_service (str): Identifier for the LLM service used.
            personality (str): The personality descriptor for the agent.
            opponent_personality_prob (int): Probability that opponent is cooperative.
            noise_rate (float): Probability (0.0-1.0) that this agent's action will be flipped.
            opponent_noise_rate (float): The opponent's noise rate (for prompt display).
        """
        super().__init__(name, llm_service, personality, opponent_personality_prob, strategies=strategies)
        self.noise_rate: float = max(0.0, min(1.0, noise_rate))  # Clamp to [0, 1]
        self.opponent_noise_rate: float = max(0.0, min(1.0, opponent_noise_rate))
        
        # Track original (before noise) and final (after noise) strategies
        self.original_strategies: List[str] = []
        self.noised_strategies: List[str] = []
        self.noise_events: List[bool] = []  # True if noise was applied in each round

    def apply_noise(self, strategy_key: str, payoff_matrix) -> Tuple[str, bool]:
        """
        Apply noise to the agent's chosen strategy.
        
        With probability equal to noise_rate, the strategy will be flipped
        to the opposite strategy.

        Args:
            strategy_key (str): The strategy key chosen by the agent (e.g., 'strategy1').
            payoff_matrix: The PayoffMatrix object containing strategy mappings.

        Returns:
            Tuple[str, bool]: (final_strategy_key, was_flipped)
                - final_strategy_key: The strategy after noise application
                - was_flipped: True if noise caused the strategy to flip
        """
        if random.random() < self.noise_rate:
            # Flip the strategy
            flipped_key = self._flip_strategy(strategy_key, payoff_matrix)
            return flipped_key, True
        return strategy_key, False

    def _flip_strategy(self, strategy_key: str, payoff_matrix) -> str:
        """
        Flip a strategy to its opposite.
        
        In a 2-strategy game (like Prisoner's Dilemma), this swaps
        strategy1 <-> strategy2.

        Args:
            strategy_key (str): The current strategy key.
            payoff_matrix: The PayoffMatrix object.

        Returns:
            str: The flipped strategy key.
        """
        strategy_keys = list(payoff_matrix.strategies.keys())
        
        if len(strategy_keys) != 2:
            raise ValueError(f"Noise flip only supports 2-strategy games, got {len(strategy_keys)}")
        
        # Return the other strategy
        if strategy_key == strategy_keys[0]:
            return strategy_keys[1]
        else:
            return strategy_keys[0]

    def record_noise_event(self, original_key: str, final_key: str, was_flipped: bool, payoff_matrix) -> None:
        """
        Record the noise event for this round.

        Args:
            original_key (str): The original strategy key before noise.
            final_key (str): The final strategy key after noise.
            was_flipped (bool): Whether noise was applied.
            payoff_matrix: The PayoffMatrix object for strategy name lookup.
        """
        self.original_strategies.append(payoff_matrix.strategies[original_key])
        self.noised_strategies.append(payoff_matrix.strategies[final_key])
        self.noise_events.append(was_flipped)

    def get_noise_info(self) -> Dict[str, Any]:
        """
        Get information about this agent's noise configuration and history.

        Returns:
            dict: Dictionary containing noise rate and history of noise events.
        """
        return {
            "noise_rate": self.noise_rate,
            "opponent_noise_rate": self.opponent_noise_rate,
            "total_rounds": len(self.noise_events),
            "times_flipped": sum(self.noise_events),
            "original_strategies": self.original_strategies,
            "final_strategies": self.noised_strategies,
            "noise_events": self.noise_events
        }

    def get_info(self) -> Dict[str, Any]:
        """
        Retrieve all pertinent information about the agent, including noise config.

        Returns:
            dict: A dictionary containing the agent's info plus noise settings.
        """
        base_info = super().get_info()
        base_info.update({
            "noise_rate": self.noise_rate,
            "opponent_noise_rate": self.opponent_noise_rate
        })
        return base_info
