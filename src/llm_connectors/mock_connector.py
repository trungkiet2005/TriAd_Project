
import random
import json
from src.llm_connectors.abstract_connector import AbstractConnector

class MockConnector(AbstractConnector):
    """
    A mock LLM connector that returns random valid actions for testing.
    """

    def __init__(self, model_name="mock-model"):
        """
        Initialize the MockConnector.
        """
        self.model_name = model_name

    def send_prompt(self, prompt, temperature=0.7, max_tokens=100):
        """
        Simulate sending a prompt to the LLM.
        
        Returns a random action in JSON format.
        """
        action = random.choice(["Cooperate", "Defect"])
        response = {"action": action}
        return json.dumps(response)
