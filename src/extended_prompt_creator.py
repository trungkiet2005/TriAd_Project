"""
ExtendedPromptCreator - Extends PromptCreator with noise information.

Adds support for:
1. Noise info placeholders ({noiseIntro}, {opponentNoiseRate})
2. History note about noised actions
"""

import re
from src.prompt_creator import PromptCreator


class ExtendedPromptCreator(PromptCreator):
    """
    Extended PromptCreator that adds noise-related placeholders to prompts.
    
    This allows agents to know about their opponent's noise rate, helping
    them make more informed decisions in the Prisoner's Dilemma.
    """

    def __init__(self, lang, prompt_template, n_rounds, n_rounds_known, payoff_matrix):
        """
        Initialize the ExtendedPromptCreator.

        Args:
            lang (str): The language code.
            prompt_template (str): The template string with placeholders.
            n_rounds (int): Total number of rounds.
            n_rounds_known (bool): Whether agents know the total rounds.
            payoff_matrix: The PayoffMatrix object.
        """
        super().__init__(lang, prompt_template, n_rounds, n_rounds_known, payoff_matrix)

    def process_noise_intro(self, agent, opponents, pv_dict):
        """
        Process the {noiseIntro}: [...] block in the template.
        
        If any opponent has a non-zero noise rate, include the noise intro.
        Otherwise, remove the block.

        Args:
            agent: The current agent.
            opponents: List of opponent agents.
            pv_dict: The placeholder-value dictionary to update.
        """
        noise_intro = self._find_part('noiseIntro')
        if noise_intro is None:
            return
        
        # Check if any opponent has noise
        has_noise = any(
            hasattr(opp, 'noise_rate') and opp.noise_rate > 0
            for opp in opponents
        )
        
        if has_noise:
            self._replace_part(noise_intro)
            # Add noise rates for each opponent
            for i, opp in enumerate(opponents, start=1):
                if hasattr(opp, 'noise_rate'):
                    # Convert to percentage for display
                    pv_dict[f"opponentNoiseRate{i}"] = round(opp.noise_rate * 100, 1)
                    # Also add as opponentNoiseRate for single-opponent templates
                    if i == 1:
                        pv_dict["opponentNoiseRate"] = round(opp.noise_rate * 100, 1)
                else:
                    pv_dict[f"opponentNoiseRate{i}"] = 0
                    if i == 1:
                        pv_dict["opponentNoiseRate"] = 0
        else:
            self._remove_part(noise_intro)

    def process_history_note(self, pv_dict):
        """
        Process the {historyNote}: [...] block in the template.
        
        Always includes the history note to remind agents that
        history shows final actions after noise was applied.

        Args:
            pv_dict: The placeholder-value dictionary.
        """
        history_note = self._find_part('historyNote')
        if history_note is not None:
            self._replace_part(history_note)

    def process_optional_parts(self, agent, opponents, pv_dict):
        """
        Override parent method to include noise-related processing.

        Args:
            agent: The current agent.
            opponents: List of opponent agents.
            pv_dict: The placeholder-value dictionary to update.
        """
        # Call parent processing
        super().process_optional_parts(agent, opponents, pv_dict)
        
        # Add noise-specific processing
        self.process_noise_intro(agent, opponents, pv_dict)
        self.process_history_note(pv_dict)

    def map_placeholders(self, agent_name, opponents, current_round, history):
        """
        Override to add noise-related placeholders.

        Args:
            agent_name (str): Name of the current agent.
            opponents: List of opponent agents.
            current_round (int): Current round number.
            history: Game history object.

        Returns:
            dict: Dictionary of placeholder names to values.
        """
        values = super().map_placeholders(agent_name, opponents, current_round, history)
        
        # Add opponent noise rates to placeholders
        for i, opp in enumerate(opponents, start=1):
            if hasattr(opp, 'noise_rate'):
                values[f"opponentNoiseRate{i}"] = round(opp.noise_rate * 100, 1)
                if i == 1:
                    values["opponentNoiseRate"] = round(opp.noise_rate * 100, 1)
            else:
                values[f"opponentNoiseRate{i}"] = 0
                if i == 1:
                    values["opponentNoiseRate"] = 0
        
        return values
