"""
AggregationChecker - Checks if agents understand aggregate statistics.
"""

from src.checkers.checker import Checker
from src.checkers.checker_utils import (
    generate_game_rules_prompt,
    generate_history_prompt_generic,
    generate_prompt_from_sub_prompts,
    find_first_int,
    to_nat_lang
)
from src.checkers.checker_translations import get_translation


class AggregationChecker(Checker):
    """
    Checker for aggregate statistics understanding.
    
    Verifies if the LLM correctly tracks:
    - How many times each action was chosen
    - Total points accumulated by each player
    """

    def __init__(self):
        # Questions will be generated dynamically in ask_checker_questions
        # We initialize with empty templates to be filled
        super().__init__("aggregation_checker", [], [])

    def check_action_chosen(self, action: str, n_times: int, player_name: str, question_idx: int) -> None:
        """Check if LLM knows how many times an action was chosen."""
        # Use dynamic question text
        question = self.questions[question_idx]
        label = self.questions_labels[question_idx]
        
        json_prompt = 'Remember to use the following JSON format: {"answer": <N_TIMES>}\n'
        question_prompt = f"Answer to the following question: {question}\n"
        prompt = generate_prompt_from_sub_prompts([self.system_prompt, json_prompt, question_prompt])
        correct_answer = str(n_times)
        llm_answer = find_first_int(self.get_answer_from_llm(prompt, label))
        self.check_answer(llm_answer, correct_answer, label)

    def check_total_payoff(self, payoff: int, player_name: str, question_idx: int) -> None:
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
        n_players = len(game.agents)
        agent_names = list(game.agents.keys())
        
        # Get Language and Penalty Mode
        language = getattr(game, 'language', 'en')
        is_penalty = getattr(game, 'is_penalty', False)
        
        # Determine current player index for context
        player_idx = agent_names.index(player_name) if player_name in agent_names else 0
        
        # Get histories for ALL players
        all_histories = []
        for name in agent_names:
            all_histories.append([s for s in game.agents[name].strategies])
            
        # Action space
        action_space = set(game.payoff_matrix.strategies.values())
        
        # Generate generic system prompt
        game_rules_prompt = generate_game_rules_prompt(
            action_space, game.payoff_matrix, n_iterations, 
            agent_names, language=language, is_penalty=is_penalty
        )
        
        history_prompt = generate_history_prompt_generic(
            all_histories, player_idx, game.payoff_matrix, agent_names,
            window_size=None, is_ended=is_ended,  # Aggregation needs full history
            language=language, is_penalty=is_penalty
        )
        self.system_prompt = game_rules_prompt + history_prompt
        
        # Skip if no history yet
        if len(all_histories[0]) == 0:
            return
            
        # Calculate totals for ALL players
        total_payoffs = [0] * n_players
        n_rounds_played = len(all_histories[0])
        
        for r in range(n_rounds_played):
            # Get actions for this round
            round_actions = [h[r] for h in all_histories]
            
            # Calculate payoffs
            try:
                weights = game.payoff_matrix.get_weights_for_combination(round_actions)
                for i in range(len(weights)):
                    if i < n_players:
                        total_payoffs[i] += weights[i]
            except Exception:
                continue

        # Reset questions for this check (since they are dynamic per game)
        self.questions = []
        self.questions_labels = []
        
        # 1. Ask about action counts for each player
        for i, name in enumerate(agent_names):
             p_label = name
             p_history = all_histories[i]
             for action in action_space:
                 n_times = p_history.count(action)
                 
                 # "How many times did player {player} choose {action}?"
                 q_text = get_translation(language, "agg_action_count", player=p_label, action=to_nat_lang(action))
                 
                 self.questions.append(q_text)
                 label = f"#actions_{p_label}_{action}"
                 self.questions_labels.append(label)
                 
                 if label not in self.questions_results:
                     self._init_question_result(label, q_text)
                     
                 self.check_action_chosen(action, n_times, p_label, len(self.questions) - 1)

        # 2. Ask about total payoff for each player
        unit_key = "unit_penalty" if is_penalty else "unit_points"
        unit = get_translation(language, unit_key)
        
        for i, name in enumerate(agent_names):
             p_label = name
             
             # "What is player {player}'s current total {unit}?"
             q_text = get_translation(language, "agg_total_score", player=p_label, unit=unit)
             
             self.questions.append(q_text)
             label = f"total_payoff_{p_label}"
             self.questions_labels.append(label)
             
             if label not in self.questions_results:
                 self._init_question_result(label, q_text)
                 
             self.check_total_payoff(int(total_payoffs[i]), p_label, len(self.questions) - 1)

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
