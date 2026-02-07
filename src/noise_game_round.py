"""
NoiseGameRound - GameRound with noise injection after agent decisions.

Extends GameRound to:
1. Apply noise to agent actions after they decide
2. Track noise events in history
3. Use ExtendedPromptCreator for noise-aware prompts
"""

from src.game_round import GameRound
from src.extended_prompt_creator import ExtendedPromptCreator
from src.noise_agent import NoiseAgent
from retry import retry


class NoiseGameRound(GameRound):
    """
    A game round that applies noise to agent actions after they make decisions.
    
    This simulates communication errors or implementation mistakes where
    an agent intends one action but a different action is executed.
    """

    def __init__(self, game):
        """
        Initialize with a reference to the NoiseFairGame instance.

        Args:
            game: The game object containing all configuration and agents.
        """
        super().__init__(game)
        self.noise_info = {}  # Track noise events for this round

    def run(self):
        """
        Execute one round of the game with noise injection.

        Returns:
            list of str: The list of FINAL strategy keys after noise application.
        """
        if self.game.agents_communicate:
            self._execute_communication_phase()

        round_strategies = []
        self.noise_info = {}

        for agent in self.game.agents.values():
            prompt = self.create_prompt(agent, phase='choose')
            original_strategy = self._execute_agent_strategy(agent, prompt)
            
            # Apply noise if agent supports it
            if isinstance(agent, NoiseAgent):
                final_strategy, was_flipped = agent.apply_noise(
                    original_strategy, self.game.payoff_matrix
                )
                
                # Record the noise event
                agent.record_noise_event(
                    original_strategy, final_strategy, was_flipped, self.game.payoff_matrix
                )
                
                # Store noise info for history
                self.noise_info[agent.name] = {
                    'original_strategy': self.game.payoff_matrix.strategies[original_strategy],
                    'final_strategy': self.game.payoff_matrix.strategies[final_strategy],
                    'was_flipped': was_flipped,
                    'noise_rate': agent.noise_rate
                }
                
                if was_flipped:
                    print(f"NOISE APPLIED to {agent.name}: {original_strategy} -> {final_strategy}")
            else:
                final_strategy = original_strategy
                self.noise_info[agent.name] = {
                    'original_strategy': self.game.payoff_matrix.strategies[original_strategy],
                    'final_strategy': self.game.payoff_matrix.strategies[original_strategy],
                    'was_flipped': False,
                    'noise_rate': 0.0
                }

            round_strategies.append(final_strategy)

        return round_strategies

    def create_prompt(self, agent, phase):
        """
        Create a prompt using ExtendedPromptCreator for noise support.

        Args:
            agent: The agent object to create the prompt for.
            phase (str): The phase of the round ('communicate' or 'choose').

        Returns:
            str: The prompt to be sent to the agent.
        """
        opponents = self._get_opponents(agent)
        prompt_creator = ExtendedPromptCreator(
            self.game.language,
            self.game.prompt_template,
            self.game.n_rounds,
            self.game.n_rounds_known,
            self.game.payoff_matrix
        )
        return prompt_creator.fill_template(
            agent,
            opponents,
            self.round_number,
            self.game.history.rounds,
            phase
        )

    @retry(tries=10, delay=1)
    def _execute_agent_strategy(self, agent, prompt):
        """
        Get strategy from agent, with retry for robustness.
        
        Note: This returns the ORIGINAL strategy key before noise.

        Args:
            agent: The agent object.
            prompt (str): The strategy prompt.

        Returns:
            str: The strategy key selected by the agent (before noise).

        Raises:
            ValueError: If no matching strategy is found.
        """
        response = agent.execute_round(prompt)
        print(f"RESPONSE from {agent.name}: {response}")
        
        found_strategy = next(
            (key for key, val in self.game.payoff_matrix.strategies.items()
             if val.lower() in response.lower()),
            None
        )
        
        if found_strategy:
            # Don't add to strategies list yet - that happens after noise
            return found_strategy
        raise ValueError(f"No matching strategy found in response: {response}")

    def _update_round_history(self):
        """
        Update the game history with final (post-noise) strategies and scores.
        Also records noise information.
        """
        for agent in self.game.agents.values():
            # Get the final strategy (after noise)
            final_strategy = agent.strategies[-1] if agent.strategies else None
            
            history_data = {
                'strategy': final_strategy,
                'score': agent.last_score() if agent.scores else 0
            }
            
            # Add noise info if available
            if agent.name in self.noise_info:
                history_data['noise_info'] = self.noise_info[agent.name]
            
            self.game.history.update_round(self.round_number, agent.name, history_data)
