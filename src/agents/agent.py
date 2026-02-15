import json
import re
import warnings
from typing import Any, Dict, List, Tuple, Optional
from src.llm_connectors.llm_factory_connector import execute_prompt


def find_json_object(string: str) -> Optional[dict]:
    """Parse JSON object from string (matches original paper's find_json_object)."""
    if not isinstance(string, str):
        return None
    
    # Don't replace apostrophes globally - just extract and parse the JSON as-is
    # The JSON inside should use double quotes, so we don't need to replace quotes
    
    # Find JSON object by matching braces
    start_json = False
    json_end = False
    match = 0
    probably_json_parsable = ""
    
    for char in string:
        if not start_json and char == "{":
            start_json = True
        if start_json and not json_end:
            probably_json_parsable += char
            if char == "{":
                match += 1
            if char == "}" and match > 0:
                match -= 1
                if match == 0:
                    json_end = True
    
    if json_end:
        try:
            return json.loads(probably_json_parsable)
        except json.JSONDecodeError:
            # Try replacing single quotes with double quotes as fallback
            try:
                fixed = probably_json_parsable.replace("'", '"')
                return json.loads(fixed)
            except json.JSONDecodeError:
                return None
    return None


def from_nat_lang(action: str) -> int:
    """Convert action string to integer (matches original paper's from_nat_lang)."""
    action_1_ = "Cooperate"
    action_0_ = "Defect"
    
    if action == action_1_ or action == f'{action_1_}':
        return 1
    if action == action_0_ or action == f'{action_0_}':
        return 0
    
    # Try case-insensitive match
    if action.lower() == action_1_.lower():
        return 1
    if action.lower() == action_0_.lower():
        return 0
    
    warnings.warn(f"Invalid action: {action}. Returning 'Defect' as 0.")
    return 0


class Agent:
    """
    Represents an agent that interacts with a language model service to decide on strategies.
    
    The Agent stores its own history of strategies and scores, and it can execute a round
    by sending a prompt to the LLM service.
    """

    def __init__(self, name: str, llm_service: str, personality: str, opponent_personality_prob: int, 
                 strategies: Dict[str, str] = None) -> None:
        """
        Initialize the Agent instance.

        Args:
            name (str): The name of the agent.
            llm_service (str): Identifier or configuration for the LLM service used to execute prompts.
            personality (str): The personality descriptor for the agent.
            opponent_personality_prob (int): The probability (as an integer percentage) that the opponent
                                             will behave cooperatively.
            strategies (Dict[str, str], optional): A dictionary mapping strategy keys (e.g., 'strategy1') 
                                                   to strategy names (e.g., 'Defect'). 
                                                   Defaults to {'strategy1': 'Defect', 'strategy2': 'Cooperate'}.
        """
        self.name: str = name
        self.strategies: List[str] = []
        self.scores: List[int] = []
        self.llm_service: str = llm_service
        self.personality: str = personality
        self.opponent_personality_prob: int = opponent_personality_prob
        
        # Default strategies if none provided (for backward compatibility)
        if strategies is None:
            self.strategy_names = {'strategy1': 'Defect', 'strategy2': 'Cooperate'}
        else:
            self.strategy_names = strategies

        # Store data for action_answers output (matches original paper format)
        self.action_answers: List[Dict[str, Any]] = []

    def execute_round(self, prompt: str) -> str:
        """
        Execute a round by sending a prompt to the LLM service and returning the agent's choice.

        Args:
            prompt (str): The prompt to send to the language model.

        Returns:
            str: The strategy name extracted from LLM response.
        """
        # Retry loop for LLM call and JSON parsing
        max_retries = 3
        answer = None
        generated_text = ""
        
        for attempt in range(max_retries):
            # Get raw LLM response
            generated_text = execute_prompt(self.llm_service, prompt)
            
            # Parse JSON from response
            answer = find_json_object(generated_text)
            
            if answer is not None:
                # Found valid JSON, break retry loop
                break
            
            # If failed, print warning and retry if attempts remain
            preview = str(generated_text)[:100] if generated_text else "None"
            if attempt < max_retries - 1:
                print(f"[{self.name}] WARNING: No JSON found in response (Attempt {attempt+1}/{max_retries}). Retrying...")
            else:
                # Final failure warning
                warnings.warn(f"No JSON found in: {preview}... Using default.")

        # Build action_answer record (matches original paper format)
        action_answer = {
            "prompt": prompt,
            "generated_text": generated_text,
        }
        
        # Determine strategy from response
        chosen_strategy_key = 'strategy1' # Default fallback
        reason = ""

        if answer is None:
            # No JSON found - try to extract action directly from text
            chosen_strategy_key = self._extract_action_from_text(generated_text)
        else:
            try:
                # Print full JSON for debugging as requested
                print(f"[{self.name}] JSON Response: {json.dumps(answer, ensure_ascii=False)}")
                
                action_str = answer.get("action", "")
                reason = answer.get("reason", "")
                
                # Print beliefs for debugging
                beliefs = answer.get("beliefs")
                if beliefs:
                    print(f"[{self.name}] Beliefs: {beliefs}")
                
                # Normalize action string
                action_norm = str(action_str).lower().strip()
                
                # Check against strategy names
                matched = False
                for key, name in self.strategy_names.items():
                    # Check exact match or if name matches 'action' field
                    if action_norm == name.lower() or action_norm == key.lower():
                        chosen_strategy_key = key
                        matched = True
                        break
                
                if not matched:
                    # Try from_nat_lang style fallback for numbers 0/1 if applicable
                    # or standard Coop/Defect if not found
                    if "cooperate" in action_norm:
                        chosen_strategy_key = 'strategy2'
                    elif "defect" in action_norm:
                        chosen_strategy_key = 'strategy1'
                    else:
                         warnings.warn(f"Unknown action: {action_str}. Using Default.")

            except Exception as e:
                warnings.warn(f"Error parsing action: {e}. Using Default.")
        
        # Get the actual name for the return value
        action_name = self.strategy_names.get(chosen_strategy_key, "Defect")
        
        # Store in action_answer (using 1 for strategy2/Cooperate, 0 for strategy1/Defect for compat)
        # This is a bit of a legacy hack for integer-based history in output manager
        action_int = 1 if chosen_strategy_key == 'strategy2' else 0

        action_answer["action"] = action_int
        action_answer["reason"] = reason
        action_answer["beliefs"] = answer.get("beliefs", {}) if answer else {}
        self.action_answers.append(action_answer)
        
        return action_name
    
    def _extract_action_from_text(self, text: str) -> str:
        """Try to extract action key from plain text when JSON parsing fails."""
        text_lower = text.lower()
        
        # Check for dynamic strategies
        for key, name in self.strategy_names.items():
            if name.lower() in text_lower:
                return key
        
        # Fallback to standard check
        if "cooperate" in text_lower:
            return 'strategy2'
        if "defect" in text_lower:
            return 'strategy1'
        
        # Default
        return 'strategy1'
    

    def add_strategy(self, strategy: str) -> None:
        """
        Record a new strategy choice.

        Args:
            strategy (str): The strategy chosen by the agent.
        """
        self.strategies.append(strategy)

    def last_strategy(self) -> str:
        """
        Retrieve the most recent strategy choice.

        Returns:
            str: The last strategy from the agent's history.
        """
        return self.strategies[-1]

    def add_score(self, score: int) -> None:
        """
        Record a new score for the agent.

        Args:
            score (int): The score to be added.
        """
        self.scores.append(score)

    def last_score(self) -> int:
        """
        Retrieve the most recent score.

        Returns:
            int: The last score recorded.
        """
        return self.scores[-1]

    def get_info(self) -> Dict[str, Any]:
        """
        Retrieve all pertinent information about the agent.

        Returns:
            dict: A dictionary containing the agent's name, LLM service, personality, and
                  opponent personality probability.
        """
        return {
            "name": self.name,
            "llm_service": self.llm_service,
            "personality": self.personality,
            "opponent_personality_probability": self.opponent_personality_prob
        }
