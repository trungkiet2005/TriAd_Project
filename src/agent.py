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

    def __init__(self, name: str, llm_service: str, personality: str, opponent_personality_prob: int) -> None:
        """
        Initialize the Agent instance.

        Args:
            name (str): The name of the agent.
            llm_service (str): Identifier or configuration for the LLM service used to execute prompts.
            personality (str): The personality descriptor for the agent.
            opponent_personality_prob (int): The probability (as an integer percentage) that the opponent
                                             will behave cooperatively.
        """
        self.name: str = name
        self.strategies: List[str] = []
        self.scores: List[int] = []
        self.llm_service: str = llm_service
        self.personality: str = personality
        self.opponent_personality_prob: int = opponent_personality_prob
        
        # Store data for action_answers output (matches original paper format)
        self.action_answers: List[Dict[str, Any]] = []

    def execute_round(self, prompt: str) -> str:
        """
        Execute a round by sending a prompt to the LLM service and returning the agent's choice.

        Args:
            prompt (str): The prompt to send to the language model.

        Returns:
            str: The strategy name ("Cooperate" or "Defect") extracted from LLM response.
        """
        # Get raw LLM response
        generated_text = execute_prompt(self.llm_service, prompt)
        
        # Build action_answer record (matches original paper format)
        action_answer = {
            "prompt": prompt,
            "generated_text": generated_text,
        }
        
        # Parse JSON from response
        answer = find_json_object(generated_text)
        
        if answer is None:
            # No JSON found - try to extract action directly from text
            warnings.warn(f"No JSON found in: {generated_text[:100]}... Using default.")
            action_int = self._extract_action_from_text(generated_text)
            reason = ""
        else:
            try:
                action_str = answer.get("action", "")
                action_int = from_nat_lang(str(action_str))
            except Exception as e:
                warnings.warn(f"Error parsing action: {e}. Using Defect.")
                action_int = 0
            
            reason = answer.get("reason", "")
        
        # Convert action_int back to strategy name
        action_name = "Cooperate" if action_int == 1 else "Defect"
        
        # Store in action_answer
        action_answer["action"] = action_int
        action_answer["reason"] = reason
        self.action_answers.append(action_answer)
        
        return action_name
    
    def _extract_action_from_text(self, text: str) -> int:
        """Try to extract action from plain text when JSON parsing fails."""
        text_lower = text.lower()
        
        # Check for Cooperate first
        if "cooperate" in text_lower:
            return 1
        if "defect" in text_lower:
            return 0
        
        # Default to Defect
        return 0

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
