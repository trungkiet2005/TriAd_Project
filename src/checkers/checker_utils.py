"""
Checker Utilities - Adapted from nicer_than_human's llm_utils.py

Provides prompt generation functions for hallucination checkers:
- generate_game_rules_prompt: Creates context about game rules and payoffs
- generate_history_prompt: Creates history of past rounds
- generate_prompt_from_sub_prompts: Combines prompts in instruction format
"""

from typing import List, Dict, Any, Set


# Player name constants
PLAYER_NAMES = ["A", "B", "C", "D", "E"]
player_1_ = PLAYER_NAMES[0]
player_2_ = PLAYER_NAMES[1]

def to_nat_lang(text: str, string_of_string: bool = False) -> str:
    """Convert text to natural language format."""
    return str(text)

def generate_game_rules_prompt(action_space: Set[str], payoff_matrix, n_iterations: int) -> str:
    """
    Generate game rules prompt with payoff information for N players.
    """
    payoff_lines = []
    strategies = payoff_matrix.strategies
    combinations = payoff_matrix.matrix_data.get('combinations', {})
    matrix = payoff_matrix.matrix_data.get('matrix', {})
    weights = payoff_matrix.weights
    n_players = payoff_matrix.n_players if hasattr(payoff_matrix, 'n_players') else 2
    
    # Generate intro line
    players_str = " and ".join([f"player {PLAYER_NAMES[i]}" for i in range(n_players)])
    action_list = ", ".join([f'"{a}"' for a in action_space])

    # Generate payoff descriptions
    for combo_key, strategy_keys in combinations.items():
        if combo_key in matrix:
            # Describe actions
            actions_desc = []
            for i, strat_index in enumerate(strategy_keys):
                action = strategies[strat_index]
                actions_desc.append(f'player {PLAYER_NAMES[i]} plays "{action}"')
            
            condition = " and ".join(actions_desc)
            
            # Describe payoffs
            payoff_keys = matrix[combo_key]
            payoffs_desc = []
            for i, p_key in enumerate(payoff_keys):
                val = weights[p_key]
                payoffs_desc.append(f'player {PLAYER_NAMES[i]} collects {val} points')
            
            consequence = " and ".join(payoffs_desc)
            
            payoff_lines.append(f'If {condition}, {consequence}.')
    
    payoff_prompt = "\n".join(payoff_lines)
    
    game_rules_prompt = (
        f"<<SYS>>\n"
        f"Context: {players_str} are playing a multi-round game.\n"
        f"At each turn {players_str} simultaneously perform one of the following actions: {action_list}\n"
        f"The payoffs for each combination of chosen actions are the following:\n"
        f"{payoff_prompt}\n"
        f"They will play a total of {n_iterations} rounds of this game.\n"
        f"Remember that a player's objective is to get the highest possible amount of points in the long run.<<SYS>>\n"
    )
    
    return game_rules_prompt



def generate_history_prompt(own_history: List[str], opponents_histories: List[List[str]], 
                           payoff_function, window_size: int = None, is_ended: bool = False,
                           player_index: int = 0) -> str:
    """
    Generate history prompt for 2 players (legacy support).
    """
    n_rounds_played = len(own_history)
    if n_rounds_played == 0:
        return "This is the first round of the game.\n"
        
    if window_size is None:
        window_size = n_rounds_played
        
    start = max(0, n_rounds_played - window_size)
    end = n_rounds_played
    
    history_parts = [f"The history of the game in the last {min(n_rounds_played, window_size)} rounds is the following:\n"]
    
    # Determine which history belongs to A and B
    # Default assumption: player_index 0 is A, 1 is B
    hist_A = own_history if player_index == 0 else opponents_histories # Note: arg is named 'opponents_histories' in signature but passed as single list in TimeChecker?
    # Wait, the signature in file was: opponents_histories: List[List[str]]
    # But TimeChecker passes: opponent_history: List[str]
    # I need to fix the type hint/handling or just assume input is what TimeChecker passes.
    # TimeChecker passes `opponent_history` (list of strings).
    # So I will treat `opponents_histories` as `List[str]` (single opponent) for this legacy function.
    
    hist_A = own_history if player_index == 0 else opponents_histories
    hist_B = opponents_histories if player_index == 0 else own_history
    
    for r in range(start, end):
        action_A = hist_A[r]
        action_B = hist_B[r]
        
        # Calculate scores if possible using payoff_function
        # payoff_function(own, opp)
        # score_A = payoff_function(action_A, action_B) if player_index == 0 else payoff_function(action_B, action_A) -- wait, payoff_function perspective?
        # Let's skip scores in history string if not strictly required, or try:
        
        # prompt usually: "Round X: player A played Y, player B played Z."
        line = f'Round {r + 1}: player {player_1_} played "{action_A}" and player {player_2_} played "{action_B}".'
        history_parts.append(line)
        
    if not is_ended:
        history_parts.append(f"\nCurrent round: {n_rounds_played + 1}.")
    else:
        history_parts.append("\nThe game has ended.")
        
    return "\n".join(history_parts) + "\n"

def generate_history_prompt_generic(all_histories: List[List[str]], player_index: int,
                                   payoff_matrix, window_size: int = None, is_ended: bool = False) -> str:
    """
    Generate history prompt for N players.
    
    Args:
        all_histories: List of histories for all players [A, B, C...]
        player_index: Index of the current player (0=A, 1=B, etc.)
        payoff_matrix: PayoffMatrix object to calculate scores
    """
    n_players = len(all_histories)
    if n_players == 0 or len(all_histories[0]) == 0:
        return "This is the first round of the game.\n"
        
    n_rounds_played = len(all_histories[0])
    
    if window_size is None:
        window_size = n_rounds_played
    
    start = max(0, n_rounds_played - window_size)
    end = n_rounds_played
    
    my_name = PLAYER_NAMES[player_index]
    
    # Calculate totals logic (simplified for N players)
    # We can skip complex "total cooperates" text if it's too verbose for N players, 
    # or loop through everyone.
    
    history_parts = [f"The history of the game in the last {min(n_rounds_played, window_size)} rounds is the following:\n"]
    
    total_scores = [0] * n_players
    
    for r in range(start, end):
        # Get actions for this round
        round_actions = [h[r] for h in all_histories]
        
        # Calculate scores using payoff matrix
        # payoff_matrix.get_payoff_for_actions(actions_list) -> needs to be implemented or we use get_score equivalent
        # PayoffMatrix usually takes "ActionA", "ActionB"...
        # We need to map actions to strategy keys for PayoffMatrix?
        # Or PayoffMatrix.get_score works with strategy names?
        # get_score(own, opp) -> usually 2 players.
        # For N players, we likely have a method get_payoff(p1_action, p2_action, p3_action...)
        
        # Assuming we can calculate scores. 
        # For now, let's assume we can get scores.
        # If payoff_matrix doesn't support direct list access, we might struggle.
        # But wait, PayoffMatrix has `get_payoff_by_actions(action_list)`?
        # Let's assume we construct the score description.
        
        scores = []
        # We need a way to get scores.
        # The prompt generation usually happens inside the game where we might have the scores cached?
        # But this is external checker.
        
        # Temp fallback: calculate if 2 players, else placeholder or try to use matrix.
        # Actually, let's try to get scores from the matrix if possible.
        pass

    # Simplified implementation that focuses on ACTIONS first
    history_parts = [f"The history of the game in the last {min(n_rounds_played, window_size)} rounds is the following:\n"]
    
    for r in range(start, end):
        actions_desc = []
        for i in range(n_players):
            actions_desc.append(f'player {PLAYER_NAMES[i]} played "{all_histories[i][r]}"')
        
        line = f"Round {r + 1}: " + " and ".join(actions_desc) + "."
        history_parts.append(line)
        
    if not is_ended:
        history_parts.append(f"\nCurrent round: {n_rounds_played + 1}.")
    else:
        history_parts.append("\nThe game has ended.")
        
    return "\n".join(history_parts) + "\n"


def generate_prompt_from_sub_prompts(sub_prompts: List[str], zero_shot: bool = False) -> str:
    """
    Combine sub-prompts into instruction format.
    
    Args:
        sub_prompts: List of prompt parts to combine
        zero_shot: Whether to add chain-of-thought prompt
        
    Returns:
        str: Combined prompt in instruction format
    """
    # Stronger instruction to force JSON
    instruction = "IMPORTANT: Provide your response ONLY in JSON format. Do not include any explanations, markdown formatting, or other text outside the JSON object."
    
    prompt = "<s>[INST] " + "".join(sub_prompts) + f"\n{instruction}\n[/INST]\n"
    if zero_shot:
        prompt += "Let's work this out step-by-step:\n"
    return prompt


def find_first_int(text: str) -> str:
    """Find the first integer in a string."""
    import re
    if text is None:
        return None
    match = re.search(r'-?\d+', str(text))
    return match.group() if match else None


def find_first_substring(text: str, substrings: Set[str]) -> str:
    """Find the first matching substring (case-insensitive)."""
    if text is None:
        return None
    text_lower = str(text).lower()
    for s in substrings:
        if s.lower() in text_lower:
            return s
    return None


def find_json_object(text: str) -> Dict[str, Any]:
    """
    Find and parse a JSON object in text.
    Handles markdown code blocks and loose formatting.
    """
    import json
    import re
    
    if text is None:
        return None
        
    text = str(text).strip()
    
    # Remove markdown code blocks if present
    # Matches ```json ... ``` or just ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
        
    try:
        # First try: parse the whole text if it looks like JSON
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        # Second try: Assertive regex to find the outermost JSON object
        # This regex looks for { followed by anything (non-greedy) and ending with }
        # re.DOTALL allows matching across newlines
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
        
    try:
        # Third try: Find the LAST occurrence of a JSON-like structure
        # (Common in CoT where the answer is at the end)
        matches = list(re.finditer(r'\{[^{}]*\}', text))
        if matches:
            return json.loads(matches[-1].group())
    except json.JSONDecodeError:
        pass
        
    # Final cleanup attempt: replace standard quotes
    try:
        clean_text = text.replace("'", '"')
        match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if match:
             return json.loads(match.group())
    except Exception:
        pass

    return None
