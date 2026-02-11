"""
Checker Utilities - Adapted from nicer_than_human's llm_utils.py

Provides prompt generation functions for hallucination checkers:
- generate_game_rules_prompt: Creates context about game rules and payoffs
- generate_history_prompt: Creates history of past rounds
- generate_prompt_from_sub_prompts: Combines prompts in instruction format
"""

from typing import List, Dict, Any, Set
from src.checkers.checker_translations import get_translation

def to_nat_lang(text: str, string_of_string: bool = False) -> str:
    """Convert text to natural language format."""
    return str(text)

def generate_game_rules_prompt(action_space: Set[str], payoff_matrix, n_iterations: int, 
                              agent_names: List[str], language: str = "en", is_penalty: bool = False) -> str:
    """
    Generate game rules prompt with payoff information for N players.
    
    Args:
        action_space: Set of available actions
        payoff_matrix: PayoffMatrix object
        n_iterations: Total rounds
        agent_names: List of agent names
        language: Language code ('en', 'vn', etc.)
        is_penalty: If True, uses "penalty" logic (minimize); else "points" (maximize)
    """
    payoff_lines = []
    strategies = payoff_matrix.strategies
    combinations = payoff_matrix.matrix_data.get('combinations', {})
    matrix = payoff_matrix.matrix_data.get('matrix', {})
    weights = payoff_matrix.weights
    n_players = len(agent_names)
    
    unit_key = "unit_penalty" if is_penalty else "unit_points"
    unit = get_translation(language, unit_key)
    join_and = get_translation(language, "join_and")
    join_comma = get_translation(language, "join_comma")
    
    # Generate intro line
    players_str = join_and.join([f"player {name}" for name in agent_names])
    action_list = join_comma.join([f'"{a}"' for a in action_space])

    # Generate payoff descriptions
    for combo_key, strategy_keys in combinations.items():
        if combo_key in matrix:
            # Describe actions
            actions_desc_parts = []
            for i, strat_index in enumerate(strategy_keys):
                action = strategies[strat_index]
                # "player {player} plays '{action}'"
                part = get_translation(language, "condition_play", player=agent_names[i], action=action)
                actions_desc_parts.append(part)
            
            condition = join_and.join(actions_desc_parts)
            
            # Describe payoffs
            payoff_keys = matrix[combo_key]
            payoffs_desc_parts = []
            for i, p_key in enumerate(payoff_keys):
                val = weights[p_key]
                # "player {player} collects {val} {unit}s" or "gets a {unit} of {val}"
                desc_key = "payoff_description_penalty" if is_penalty else "payoff_description_points"
                part = get_translation(language, desc_key, player=agent_names[i], value=val, unit=unit)
                payoffs_desc_parts.append(part)
            
            consequence = join_and.join(payoffs_desc_parts)
            
            payoff_lines.append(f'If {condition}, {consequence}.')
    
    payoff_prompt_str = "\n".join(payoff_lines)
    
    # Get translated context strings
    context_intro = get_translation(language, "context_intro", players=players_str)
    context_action = get_translation(language, "context_action", players=players_str, actions=action_list)
    context_payoff_intro = get_translation(language, "context_payoff_intro", unit=unit)
    context_rounds = get_translation(language, "context_rounds", n_rounds=n_iterations)
    
    obj_key = "context_objective_min" if is_penalty else "context_objective_max"
    context_objective = get_translation(language, obj_key, unit=unit)
    
    game_rules_prompt = (
        f"<<SYS>>\n"
        f"Context: {context_intro}\n"
        f"{context_action}\n"
        f"{context_payoff_intro}\n"
        f"{payoff_prompt_str}\n"
        f"{context_rounds}\n"
        f"{context_objective}<<SYS>>\n"
    )
    
    return game_rules_prompt

def generate_history_prompt_generic(all_histories: List[List[str]], player_index: int,
                                   payoff_matrix, agent_names: List[str], 
                                   window_size: int = None, is_ended: bool = False,
                                   language: str = "en", is_penalty: bool = False) -> str:
    """
    Generate history prompt for N players.
    """
    n_players = len(all_histories)
    if n_players == 0 or len(all_histories[0]) == 0:
        return "This is the first round of the game.\n" # TODO: Translate this too?
        
    n_rounds_played = len(all_histories[0])
    
    unit_key = "unit_penalty" if is_penalty else "unit_points"
    unit = get_translation(language, unit_key)
    join_and = get_translation(language, "join_and")
    
    if window_size is None:
        window_size = n_rounds_played
    
    start = max(0, n_rounds_played - window_size)
    end = n_rounds_played
    
    history_parts = []
    intro = get_translation(language, "history_intro", window=min(n_rounds_played, window_size))
    history_parts.append(intro + "\n")
    
    for r in range(start, end):
        # Get actions for this round
        round_actions = [h[r] for h in all_histories]
        
        # Calculate scores using payoff matrix
        actions_desc_parts = []
        scores_desc_parts = []
        
        # Actions description
        for i in range(n_players):
            # "player {player} played \"{action}\""
            part = get_translation(language, "history_action", player=agent_names[i], action=all_histories[i][r])
            actions_desc_parts.append(part)
            
        try:
            weights = payoff_matrix.get_weights_for_combination(round_actions)
            for i in range(n_players):
                if i < len(weights):
                    # Score description
                    key = "history_score_penalty" if is_penalty else "history_score_points"
                    part = get_translation(language, key, player=agent_names[i], value=weights[i], unit=unit)
                    scores_desc_parts.append(part)
        except Exception:
            pass # Skip scores if calc fails

        actions_str = join_and.join(actions_desc_parts)
        scores_str = join_and.join(scores_desc_parts) if scores_desc_parts else ""
        
        # "Round {r}: {actions}. {scores}."
        line = get_translation(language, "history_round", round=r+1, actions_desc=actions_str, scores_desc=scores_str)
        history_parts.append(line)
        
    if not is_ended:
        current = get_translation(language, "history_current_round", round=n_rounds_played + 1)
        history_parts.append(f"\n{current}")
    else:
        ended = get_translation(language, "history_ended")
        history_parts.append(f"\n{ended}")
        
    return "\n".join(history_parts) + "\n"


def generate_prompt_from_sub_prompts(sub_prompts: List[str], zero_shot: bool = False) -> str:
    """
    Combine sub-prompts into instruction format.
    """
    # Stronger instruction to force JSON
    # TODO: Translate "IMPORTANT: Provide your response..." if strictly needed, 
    # but instructions to model are usually fine in English unless model is weak in EN.
    # VLLMQwen usually understands English instructions well even for other languages.
    # Leaving in English for safety/consistency of JSON format, unless user requests otherwise.
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
