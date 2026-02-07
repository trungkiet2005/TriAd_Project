"""
NoiseFairGame - Extended FairGame with noise support.

Extends FairGame to:
1. Use NoiseGameRound instead of GameRound
2. Apply noise to agent strategies and record properly
3. Support NoiseAgent instances
4. Run hallucination checkers after each round
"""

from src.fairgame import FairGame
from src.noise_game_round import NoiseGameRound
from src.noise_agent import NoiseAgent


class NoiseFairGame(FairGame):
    """
    FairGame extended with noise injection support.
    
    Uses NoiseGameRound for rounds and properly handles
    the recording of strategies after noise is applied.
    """

    def __init__(self, name, language, agents, n_rounds, n_rounds_known,
                 payoff_matrix_data, prompt_template, stop_conditions,
                 agents_communicate, checkers=None):
        """
        Initialize the NoiseFairGame.

        Args:
            Same as FairGame, but agents can be NoiseAgent instances.
            checkers: Optional list of Checker instances for hallucination detection.
        """
        super().__init__(
            name, language, agents, n_rounds, n_rounds_known,
            payoff_matrix_data, prompt_template, stop_conditions,
            agents_communicate
        )
        self.checkers = checkers or []
        self.checker_results = {}

    def run_round(self):
        """
        Run a single round using NoiseGameRound for noise support.
        """
        round_runner = NoiseGameRound(self)
        round_strategies = round_runner.run()
        
        # Apply the FINAL strategies (after noise) to agents
        for agent, strategy_key in zip(self.agents.values(), round_strategies):
            strategy_name = self.payoff_matrix.strategies[strategy_key]
            agent.add_strategy(strategy_name)
        
        self.choices_made.append(round_strategies)
        self.payoff_matrix.attribute_scores(list(self.agents.values()), round_strategies)
        round_runner._update_round_history()
        
        # Run checkers after each round
        if self.checkers:
            self._run_checkers_for_round()

    def _run_checkers_for_round(self):
        """Run all checkers for the current round using LLM connector directly."""
        from src.llm_connectors.llm_factory_connector import ChatModelFactory
        
        # Get the LLM service name from first agent
        first_agent = list(self.agents.values())[0]
        llm_service = first_agent.llm_service
        
        # Create LLM connector for checkers
        llm_connector = ChatModelFactory.get_model(llm_service)
        
        for checker in self.checkers:
            for agent_name in self.agents.keys():
                try:
                    # Set the LLM connector for the checker
                    checker.set_llm_connector(llm_connector)
                    # Ask checker questions
                    checker.ask_checker_questions(
                        game=self,
                        player_name=agent_name,
                        history_window_size=5  # Last 5 rounds for context
                    )
                except Exception as e:
                    print(f"Checker {checker.name} error for {agent_name}: {e}")

    def get_checker_results(self):
        """Get results from all checkers."""
        results = {}
        for checker in self.checkers:
            results[checker.name] = checker.get_summary()
        return results

    @property
    def description(self):
        """
        Extended description including noise configuration.

        Returns:
            dict: Game description with noise info.
        """
        base_desc = {
            "name": self.name,
            "language": self.language,
            "agents": {name: agent.get_info() for name, agent in self.agents.items()},
            "n_rounds": self.n_rounds,
            "number_of_rounds_is_known": self.n_rounds_known,
            "payoff_matrix": self.payoff_matrix.matrix_data,
            "agents_communicate": self.agents_communicate
        }
        
        # Add noise summary
        noise_summary = {}
        for name, agent in self.agents.items():
            if isinstance(agent, NoiseAgent):
                noise_summary[name] = {
                    "noise_rate": agent.noise_rate,
                    "opponent_noise_rate": agent.opponent_noise_rate
                }
        
        if noise_summary:
            base_desc["noise_config"] = noise_summary
        
        return base_desc

    def get_noise_report(self):
        """
        Generate a report of all noise events in the game.

        Returns:
            dict: Dictionary mapping agent names to their noise event history.
        """
        report = {}
        for name, agent in self.agents.items():
            if isinstance(agent, NoiseAgent):
                report[name] = agent.get_noise_info()
        return report

