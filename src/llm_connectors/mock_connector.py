
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
        action = random.choice(["strategy1", "strategy2"])
        # Generate beliefs for up to 2 opponents (covers 2 and 3 player games)
        beliefs = {
            "opponent_coop_prob": random.randint(0, 100),
            "opponent_noise_suspicion": random.randint(0, 100),
            "opponent1_prob": random.randint(0, 100), # For completeness if needed
            "opponent2_prob": random.randint(0, 100)
        }
        response = {
            "action": action, 
            "beliefs": beliefs,
            "reason": "Mock reason for action."
        }
        return json.dumps(response)
