"""
NoiseFairGameFactory - Factory for creating NoiseFairGame instances.

Extends FairGameFactory to:
1. Create NoiseAgent instances with noise rates
2. Use NoiseFairGame instead of FairGame
3. Handle noise configuration from config files
4. Save detailed outputs matching original paper format
5. Support parallel game execution
"""

import itertools
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import pandas as pd

from src.game.noise_game import NoiseFairGame
from src.agents.noise_agent import NoiseAgent
from src.agents.agent import Agent
from src.io_managers.io_manager import IoManager
from src.output_manager import DetailedOutputManager


class NoiseFairGameFactory:
    """
    Factory class for creating and running NoiseFairGame instances.
    
    Handles loading configuration, generating agent permutations,
    creating games with noise support, and collecting output.
    Supports parallel execution of multiple games.
    """

    def __init__(self, checkers=None, output_dir: Path = None, llm_name: str = None, max_workers: int = 4):
        """Initialize the factory.
        
        Args:
            checkers: Optional list of Checker instances for hallucination detection.
            output_dir: Base directory for outputs (default: resources/results).
            llm_name: LLM name for output folder (will be set from config if not provided).
            max_workers: Maximum number of parallel game threads (default: 4).
        """
        self.io_manager = IoManager()
        self.config_all_langs_df = pd.DataFrame()
        self.games = []
        self.output_dict = {}
        self.checkers = checkers or []
        self.max_workers = max_workers
        self._output_lock = threading.Lock()  # Thread-safe output writing
        
        # Store base output dir and llm_name (detailed_output will be created later)
        self.base_output_dir = Path(output_dir) if output_dir else Path("resources/results")
        self.llm_name = llm_name
        self.detailed_output = None  # Will be initialized in create_games
        self.noise_level = 0.0  # Will be set from config

    def _generate_language_config_df(self, config, lang):
        """Generate configuration DataFrame for a single language."""
        if config.get("allAgentPermutations", False):
            return self.compute_all_game_configurations(
                lang,
                config['agents'],
                config['llm'],
                config.get('noiseConfig', {})
            )
        return self.compute_configuration(lang, config['agents'], config['llm'], config.get('noiseConfig', {}))

    def _compute_agent_configurations(self, lang, config_agents, noise_config):
        """Generate all agent configurations including noise rates."""
        n_agents = len(config_agents['names'])
        agent_combinations = [config_agents['names']]
        personality_permutations = list(
            itertools.product(config_agents['personalities'][lang], repeat=n_agents)
        )
        knowledge_permutations = list(
            itertools.product(config_agents['opponentPersonalityProb'], repeat=n_agents)
        )
        
        # Get noise rates from config
        noise_rates = []
        for i in range(n_agents):
            agent_key = f"agent{i+1}NoiseRate"
            rate = noise_config.get(agent_key, 0.0)
            noise_rates.append(rate)
        
        return (
            agent_combinations,
            personality_permutations,
            knowledge_permutations,
            noise_rates
        )

    def _generate_full_permutations(self, agent_combinations, personality_permutations, 
                                     knowledge_permutations, noise_rates):
        """Generate full configuration permutations for agents."""
        rows = []
        for agents in agent_combinations:
            n_agents = len(agents)
            for personality_tuple, knowledge_tuple in itertools.product(personality_permutations, knowledge_permutations):
                row_dict = {
                    **{f"Agent{i+1}": agents[i] for i in range(n_agents)},
                    **{f"Personality{i+1}": personality_tuple[i] for i in range(n_agents)},
                    **{f"OpponentPersonalityProb{i+1}": knowledge_tuple[i] for i in range(n_agents)},
                    **{f"NoiseRate{i+1}": noise_rates[i] if i < len(noise_rates) else 0.0 for i in range(n_agents)}
                }
                rows.append(row_dict)
        return pd.DataFrame(rows)

    def compute_all_game_configurations(self, lang, config_agents, llm_service, noise_config):
        """Create a DataFrame of all permutations for a given language."""
        agent_combinations, pers_perms, knowledge_perms, noise_rates = self._compute_agent_configurations(
            lang, config_agents, noise_config
        )
        df = self._generate_full_permutations(agent_combinations, pers_perms, knowledge_perms, noise_rates)
        df['LLM'] = llm_service
        df['Language'] = lang
        return df

    def compute_configuration(self, lang, config_agents, llm_service, noise_config):
        """Generate a single configuration DataFrame."""
        n_agents = len(config_agents['names'])
        row_dict = {}
        for i in range(n_agents):
            row_dict[f"Agent{i+1}"] = config_agents['names'][i]
            row_dict[f"Personality{i+1}"] = config_agents['personalities'][lang][i]
            row_dict[f"OpponentPersonalityProb{i+1}"] = config_agents['opponentPersonalityProb'][i]
            agent_key = f"agent{i+1}NoiseRate"
            row_dict[f"NoiseRate{i+1}"] = noise_config.get(agent_key, 0.0)
        row_dict["LLM"] = llm_service
        row_dict["Language"] = lang
        return pd.DataFrame([row_dict])

    def create_noise_agents(self, game_config_row, strategies=None):
        """Create NoiseAgent instances based on the configuration row."""
        agents_dict = {}
        agent_names = []
        
        # First pass: collect all agent names
        i = 1
        while f"Agent{i}" in game_config_row:
            agent_names.append(game_config_row[f"Agent{i}"])
            i += 1
        
        # Second pass: create agents with correct opponent noise rates
        n_agents = len(agent_names)
        for i in range(n_agents):
            agent_name = agent_names[i]
            personality = game_config_row[f"Personality{i+1}"]
            knowledge = game_config_row[f"OpponentPersonalityProb{i+1}"]
            noise_rate = game_config_row.get(f"NoiseRate{i+1}", 0.0)
            
            # For 2-player game, opponent noise rate is the other agent's rate
            if n_agents == 2:
                opponent_noise_rate = game_config_row.get(f"NoiseRate{2 if i == 0 else 1}", 0.0)
            else:
                # For multi-agent, use average of other agents' noise rates
                opponent_rates = [game_config_row.get(f"NoiseRate{j+1}", 0.0) 
                                  for j in range(n_agents) if j != i]
                opponent_noise_rate = sum(opponent_rates) / len(opponent_rates) if opponent_rates else 0.0
            
            agents_dict[agent_name] = NoiseAgent(
                name=agent_name,
                llm_service=game_config_row['LLM'],
                personality=personality,
                opponent_personality_prob=knowledge,
                noise_rate=noise_rate,
                opponent_noise_rate=opponent_noise_rate,
                strategies=strategies
            )
        
        return agents_dict

    def _create_single_game(self, config, game_config_row, payoff_matrix):
        """Instantiate a single NoiseFairGame based on a configuration row."""
        prompt_template = self.build_prompt_template(config, game_config_row['Language'])
        
        # Extract strategies for the current language
        lang = game_config_row['Language']
        strategies = payoff_matrix.get('strategies', {}).get(lang, None)
        
        agents = self.create_noise_agents(game_config_row, strategies=strategies)

        # Create fresh checker instances per game to avoid shared state in parallel threads
        game_checkers = [type(c)() for c in self.checkers] if self.checkers else []

        checker_every_n_rounds = config.get("checkerEveryNRounds", 1)

        return NoiseFairGame(
            config['name'],
            game_config_row['Language'],
            agents,
            config['nRounds'],
            config['nRoundsIsKnown'],
            payoff_matrix,
            prompt_template,
            config.get('stopGameWhen', []),
            config.get('agentsCommunicate', False),
            checkers=game_checkers,
            checker_every_n_rounds=checker_every_n_rounds
        )

    def _upload_output(self, game, game_history, game_n):
        """Store game result in the output dictionary."""
        desc = dict(game.description)
        desc.pop('payoff_matrix', None)
        
        output = {
            'description': desc,
            'history': game_history.describe(),
            'noise_report': game.get_noise_report()
        }
        
        # Add checker results if checkers were enabled
        if game.checkers:
            output['hallucination_check'] = game.get_checker_results()
        
        self.output_dict[f'game_{game_n}'] = output

    def _get_noise_folder_name(self, noise_rate: float) -> str:
        """Convert noise rate to folder name format noiseXX.
        
        Examples:
            0.0  -> noise00
            0.1  -> noise01
            0.5  -> noise05
            1.0  -> noise10
        """
        # Convert to index (0.0 -> 00, 0.1 -> 01, ..., 1.0 -> 10)
        noise_idx = int(round(noise_rate * 10))
        return f"noise{noise_idx:02d}"

    def create_games(self, config):
        """Create NoiseFairGame instances from the configuration dictionary."""
        # Get noise level from config for folder naming
        noise_config = config.get('noiseConfig', {})
        # Use agent1's noise rate as the primary noise level for folder name
        self.noise_level = noise_config.get('agent1NoiseRate', 0.0)
        
        # Initialize detailed output with llm name and noise level from config
        # Use llmDisplayName if provided, otherwise fallback to llm
        llm_name = self.llm_name or config.get('llmDisplayName') or config.get('llm', 'unknown_llm')
        n_rounds = config.get('nRounds', 10)
        
        # Get languages for folder naming (use first language if multiple)
        languages = config.get('languages', ['en'])
        lang_str = "_".join(languages) if len(languages) <= 3 else f"{languages[0]}_multi"
        
        llm_folder = f"{llm_name}_vs{n_rounds}round_{lang_str}"
        noise_folder = self._get_noise_folder_name(self.noise_level)
        output_path = self.base_output_dir / llm_folder / noise_folder
        self.detailed_output = DetailedOutputManager(output_path)
        
        for lang in config['languages']:
            config_df = self._generate_language_config_df(config, lang)
            
            # Apply repeats if configured
            repeats = config.get('repeats', 1)
            if repeats > 1:
                config_df = pd.concat([config_df] * repeats, ignore_index=True)
            
            self.config_all_langs_df = pd.concat(
                [self.config_all_langs_df, config_df],
                ignore_index=True
            )

        self.games = [
            self._create_single_game(config, row, config['payoffMatrix'])
            for _, row in self.config_all_langs_df.iterrows()
        ]
        return self.games

    def run_games(self):
        """Execute all NoiseFairGame instances in parallel and capture their outputs."""
        noise_folder = self._get_noise_folder_name(self.noise_level)
        print(f"RUNNING {len(self.games)} GAMES WITH NOISE (max {self.max_workers} parallel)")
        print(f"Output folder: {self.detailed_output.base_dir}")
        print(f"Noise level: {self.noise_level:.1%} ({noise_folder})")
        
        # Run games in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all games with their assigned run IDs
            futures = {}
            for i, game in enumerate(self.games):
                run_id = self.detailed_output.run_id + i
                future = executor.submit(self._run_single_game, game, i, run_id)
                futures[future] = (i, run_id)
            
            # Collect results as they complete
            for future in as_completed(futures):
                game_idx, run_id = futures[future]
                try:
                    future.result()  # Raises exception if game failed
                    print(f"Game {game_idx} (Run ID: {run_id}): Completed")
                except Exception as e:
                    print(f"Game {game_idx} (Run ID: {run_id}): FAILED - {e}")
        
        # Update run_id to next available
        self.detailed_output.run_id += len(self.games)

        # Finalize all detailed outputs (save CSVs and summary files)
        self.detailed_output.finalize_all()
        print(f"Detailed outputs saved to: {self.detailed_output.base_dir}")

    def _run_single_game(self, game, game_idx: int, run_id: int):
        """Run a single game (called in parallel thread).
        
        Args:
            game: The NoiseFairGame instance to run.
            game_idx: Index of the game in the games list.
            run_id: Run ID for output files.
        """
        game_history = game.run()
        
        # Thread-safe output handling
        with self._output_lock:
            self._upload_output(game, game_history, game_idx)
            self._save_detailed_game_output(game, run_id, game_idx)

    def _save_detailed_game_output(self, game, run_id: int, game_idx: int):
        """Save detailed output for a single game run including checker results."""
        # Set game metadata before saving
        metadata = {
            "language": game.language if hasattr(game, 'language') else "unknown",
            "n_rounds": game.n_rounds if hasattr(game, 'n_rounds') else 0,
            "agents": {},
            "noise_config": {}
        }
        
        # Get agent personalities and noise info
        for agent_name, agent in game.agents.items():
            metadata["agents"][agent_name] = {
                "personality": getattr(agent, 'personality', 'unknown'),
            }
            if hasattr(agent, 'noise_rate'):
                metadata["noise_config"][agent_name] = agent.noise_rate
        
        self.detailed_output.set_game_metadata(game_idx, metadata)
        
        # Save game history (convert to A/B format with 0/1 actions)
        players_histories = {}
        for agent_name, agent in game.agents.items():
            players_histories[agent_name] = list(agent.strategies)
        
        self.detailed_output.record_game_history(players_histories)
        self.detailed_output.save_game_history(run_id)
        
        # Save action_answers for each agent (using new action_answers format from Agent)
        for agent_name, agent in game.agents.items():
            # Convert action_answers list to dict format for output
            action_answers_dict = {}
            for round_idx, action_answer in enumerate(agent.action_answers):
                action_answers_dict[str(round_idx)] = {
                    "generated_text": action_answer.get("generated_text", ""),
                    "action": action_answer.get("action", 0),
                    "reason": action_answer.get("reason", "")
                }
            
            # Save to file
            self.detailed_output.action_answers[agent_name] = action_answers_dict
            self.detailed_output.save_action_answers(agent_name, run_id)
        
        # Save checker results PER GAME (not cumulative)
        if game.checkers:
            for checker in game.checkers:
                self.detailed_output.save_checker_results(checker, run_id)

        # Record CSV rows for analysis-ready output
        self.detailed_output.record_game_summary_row(game, game_idx, run_id)
        self.detailed_output.record_rounds_detail_rows(game, game_idx, run_id)
        self.detailed_output.record_checker_results_rows(game, game_idx, run_id)

    def create_and_run_games(self, config):
        """Validate configuration, create games, execute them, and return results."""
        processed_config = self.io_manager.process_and_validate_configuration(config)
        self.create_games(processed_config)
        self.run_games()
        return self.output_dict

    def build_prompt_template(self, config, lang):
        """Retrieve or load the prompt template for a specific language."""
        try:
            template = config['promptTemplate'][lang]
        except KeyError:
            template = self.io_manager.load_template(config.get('templateFilename', 'prisoner_dilemma_noise'), lang)
        return template

    def results_games(self):
        """Retrieve game results."""
        return self.output_dict

    def all_game_configurations(self):
        """Get all game configurations."""
        return self.config_all_langs_df
