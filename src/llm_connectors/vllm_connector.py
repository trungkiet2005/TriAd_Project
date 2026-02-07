"""
vLLM Connector - For connecting to vLLM servers with OpenAI-compatible API.

vLLM provides an OpenAI-compatible API, so we can use the OpenAI client
but point it to a custom base URL (e.g., ngrok URL).
"""

from openai import OpenAI
import os

from src.llm_connectors.abstract_connector import AbstractConnector


class VLLMConnector(AbstractConnector):
    """
    Chat model implementation for vLLM servers with OpenAI-compatible API.
    
    vLLM exposes an OpenAI-compatible endpoint, so we can use the OpenAI
    Python client with a custom base_url.
    """

    def __init__(self, provider_model: str, temperature: float = 0.7, 
                 base_url: str = None, api_key: str = None):
        """
        Initialize the vLLM connector.
        
        Args:
            provider_model (str): The model name (e.g., "Qwen/Qwen2.5-32B-Instruct").
            temperature (float): Sampling temperature.
            base_url (str): The vLLM server URL. If None, uses VLLM_BASE_URL env var.
            api_key (str): API key (often "EMPTY" for local vLLM). Uses VLLM_API_KEY env var if None.
        """
        # Get base URL from parameter or environment
        self.base_url = base_url or os.getenv("VLLM_BASE_URL")
        if not self.base_url:
            raise EnvironmentError(
                "VLLM_BASE_URL not found. Please set VLLM_BASE_URL environment variable "
                "or pass base_url parameter."
            )
        
        # Ensure base_url ends with /v1
        if not self.base_url.endswith("/v1"):
            self.base_url = self.base_url.rstrip("/") + "/v1"
        
        # API key (vLLM often uses "EMPTY" or any string)
        self.api_key = api_key or os.getenv("VLLM_API_KEY", "EMPTY")
        
        self.provider_model = provider_model
        self.temperature = temperature
        
        # Create OpenAI client with custom base_url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def send_prompt(self, prompt: str, max_tokens: int = 256) -> str:
        """
        Send a prompt to the vLLM server and return the response.
        
        Args:
            prompt (str): The prompt text.
            max_tokens (int): Maximum tokens to generate.
            
        Returns:
            str: The generated response text.
        """
        messages = [{"role": "user", "content": prompt}]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.provider_model,
                temperature=self.temperature,
                max_tokens=max_tokens,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling vLLM server: {e}")
            raise


class VLLMQwenConnector(VLLMConnector):
    """
    Convenience connector specifically for Qwen2.5-32B-Instruct on vLLM.
    """
    
    def __init__(self, temperature: float = 0.7, base_url: str = None):
        super().__init__(
            provider_model="Qwen/Qwen2.5-32B-Instruct",
            temperature=temperature,
            base_url=base_url
        )
