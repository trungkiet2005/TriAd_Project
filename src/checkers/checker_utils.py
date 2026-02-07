"""
Checker Utilities - Adapted from nicer_than_human's llm_utils.py

Provides prompt generation functions for hallucination checkers:
- generate_game_rules_prompt: Creates context about game rules and payoffs
- generate_history_prompt: Creates history of past rounds
- generate_prompt_from_sub_prompts: Combines prompts in instruction format
"""

from typing import List, Dict, Any, Set


# Player name constants (matching original paper)
player_1_ = "A"
player_2_ = "B"


def to_nat_lang(action, string_of_string=True):
    """
    Convert action to natural language.
    
    Args:
        action: The action (can be string or int/bool for Cooperate/Defect)
        string_of_string: Whether to wrap in quotes
        
    Returns:
        str: Natural language representation
    """
    if isinstance(action, str):
        return f'"{action}"' if string_of_string else action
    elif isinstance(action, (set, list)):
        items = [to_nat_lang(a, string_of_string) for a in action]
        return ", ".join(items)
    elif isinstance(action, bool) or isinstance(action, int):
        # 1/True = Cooperate, 0/False = Defect
        name = "Cooperate" if action else "Defect"
        return f'"{name}"' if string_of_string else name
    return str(action)


def generate_game_rules_prompt(action_space: Set[str], payoff_matrix, n_iterations: int) -> str:
    """
    Generate game rules prompt with payoff information.
    
    Args:
        action_space: Set of available actions (e.g., {"Cooperate", "Defect"})
        payoff_matrix: Fairgame PayoffMatrix object
        n_iterations: Total number of rounds
        
    Returns:
        str: Formatted game rules prompt
    """
    # Build payoff descriptions from Fairgame's payoff matrix
    payoff_lines = []
    strategies = payoff_matrix.strategies  # e.g., {"strategy1": "Cooperate", "strategy2": "Defect"}
    combinations = payoff_matrix.matrix_data.get('combinations', {})
    matrix = payoff_matrix.matrix_data.get('matrix', {})
    weights = payoff_matrix.weights
    
    for combo_name, strategy_keys in combinations.items():
        if combo_name in matrix:
            action1 = strategies[strategy_keys[0]]  # e.g., "Cooperate"
            action2 = strategies[strategy_keys[1]]  # e.g., "Defect"
            payoff_keys = matrix[combo_name]
            payoff1 = weights[payoff_keys[0]]
            payoff2 = weights[payoff_keys[1]]
            
            line = (f'If {player_1_} plays "{action1}" and {player_2_} plays "{action2}", '
                   f'{player_1_} collects {payoff1} points and {player_2_} collects {payoff2} points.')
            payoff_lines.append(line)
    
    payoff_prompt = "\n".join(payoff_lines)
    action_list = ", ".join([f'"{a}"' for a in action_space])
    
    game_rules_prompt = (
        f"<<SYS>>\n"
        f"Context: Player {player_1_} and player {player_2_} are playing a multi-round game.\n"
        f"At each turn player {player_1_} and player {player_2_} simultaneously perform one of the following actions: {action_list}\n"
        f"The payoffs for each combination of chosen actions are the following:\n"
        f"{payoff_prompt}\n"
        f"They will play a total of {n_iterations} rounds of this game.\n"
        f"Remember that a player's objective is to get the highest possible amount of points in the long run.<<SYS>>\n"
    )
    
    return game_rules_prompt


def generate_history_prompt(own_history: List[str], opponent_history: List[str], 
                           payoff_function, window_size: int = None, is_ended: bool = False) -> str:
    """
    Generate history prompt with past rounds information.
    
    Args:
        own_history: List of player's past actions (strategy names)
        opponent_history: List of opponent's past actions (strategy names)
        payoff_function: Function(own_action, opp_action) -> payoff
        window_size: Number of past rounds to include (None = all)
        is_ended: Whether the game has ended
        
    Returns:
        str: Formatted history prompt
    """
    if len(own_history) == 0:
        return "This is the first round of the game.\n"
    
    if window_size is None:
        window_size = len(own_history)
    
    start = max(0, len(own_history) - window_size)
    end = len(own_history)
    
    # Count actions
    own_coop = sum(1 for a in own_history if a == "Cooperate")
    own_defect = sum(1 for a in own_history if a == "Defect")
    opponent_coop = sum(1 for a in opponent_history if a == "Cooperate")
    opponent_defect = sum(1 for a in opponent_history if a == "Defect")
    
    # Calculate total payoffs
    own_total_payoff = sum(payoff_function(own_history[i], opponent_history[i]) for i in range(end))
    opponent_total_payoff = sum(payoff_function(opponent_history[i], own_history[i]) for i in range(end))
    
    # Build round-by-round history
    history_parts = [f"The history of the game in the last {min(len(own_history), window_size)} rounds is the following:\n"]
    
    for i in range(start, end):
        own_action = own_history[i]
        opp_action = opponent_history[i]
        own_pts = payoff_function(own_action, opp_action)
        opp_pts = payoff_function(opp_action, own_action)
        
        line = (f'Round {i + 1}: {player_1_} played "{own_action}" and {player_2_} played "{opp_action}" '
               f'{player_1_} collected {own_pts} points and {player_2_} collected {opp_pts} points.')
        history_parts.append(line)
    
    # Add aggregate stats
    history_parts.append(
        f'\nIn total, {player_1_} chose "Cooperate" {own_coop} times and chose "Defect" {own_defect} times, '
        f'{player_2_} chose "Cooperate" {opponent_coop} times and chose "Defect" {opponent_defect} times.'
    )
    history_parts.append(
        f"\nIn total, {player_1_} collected {own_total_payoff} points and {player_2_} collected {opponent_total_payoff} points."
    )
    
    if not is_ended:
        history_parts.append(f"\nCurrent round: {len(own_history) + 1}.")
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
    prompt = "<s>[INST] " + "".join(sub_prompts) + "Remember to answer using the right format.[/INST]\n"
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
    """Find and parse a JSON object in text."""
    import json
    import re
    if text is None:
        return None
    try:
        # Try to find JSON in the text
        match = re.search(r'\{[^{}]*\}', str(text))
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None
