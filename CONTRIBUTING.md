# Contributing to Project TRIAD

Thank you for your interest in contributing to Project TRIAD! This document provides guidelines for contributing to the codebase.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Adding New Games](#adding-new-games)
- [Adding New LLM Connectors](#adding-new-llm-connectors)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and constructive in discussions
- Focus on the technical merits of contributions
- Help newcomers get oriented
- Report any unacceptable behavior to the maintainers

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/triad.git
   cd triad
   ```
3. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy pylint

# Setup pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run mock experiments (no API required)
python main.py api --config public_goods_3_mock --config-dir public_goods_3
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes `"` for strings
- **Imports**: Group into stdlib, third-party, local (separated by blank lines)

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Check style with flake8
flake8 src/ tests/ --max-line-length=100

# Type checking with mypy
mypy src/ --ignore-missing-imports
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all function signatures
- **Comments**: Explain "why" not "what" (code should be self-explanatory)

Example:
```python
def calculate_trs(cooperation_rates: Dict[float, float]) -> float:
    """
    Calculate Trembling Robustness Score from cooperation rates.
    
    The TRS measures how cooperation changes with noise: TRS = ∂CR/∂ε
    
    Args:
        cooperation_rates: Mapping from noise level (ε) to cooperation rate
        
    Returns:
        TRS score (positive indicates antifragility)
        
    Raises:
        ValueError: If cooperation_rates is empty or missing baseline (ε=0.0)
    """
    if 0.0 not in cooperation_rates:
        raise ValueError("Baseline cooperation rate (ε=0.0) required")
    
    # Calculate gradient approximation
    baseline = cooperation_rates[0.0]
    noisy = cooperation_rates.get(0.1, baseline)
    return (noisy - baseline) / 0.1
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for workflows
└── fixtures/       # Test data and configurations
```

### Writing Tests

```python
import pytest
from src.agents.agent import Agent

class TestAgent:
    """Test suite for Agent class."""
    
    @pytest.fixture
    def sample_agent(self):
        """Create a sample agent for testing."""
        return Agent(
            name="TestAgent",
            llm_service="mock",
            personality="cooperative",
            opponent_personality_prob=80
        )
    
    def test_agent_initialization(self, sample_agent):
        """Test that agent initializes with correct attributes."""
        assert sample_agent.name == "TestAgent"
        assert sample_agent.personality == "cooperative"
        assert len(sample_agent.strategies) == 0
    
    def test_action_parsing(self, sample_agent):
        """Test that agent correctly parses LLM responses."""
        response = '{"action": "Cooperate", "beliefs": {"Player_B": 0.8}}'
        action = sample_agent.parse_action(response)
        assert action == 1  # 1 = Cooperate
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage for core game logic
- **Run before committing**: `pytest --cov=src`

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `pytest`
2. **Format code**: `black src/ tests/`
3. **Check style**: `flake8 src/ tests/`
4. **Update documentation**: Add docstrings and update README if needed
5. **Add tests**: Cover new functionality

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change necessary? What problem does it solve?

## Changes
- List the main changes
- In bullet points
- Be specific

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Tested with mock LLMs
- [ ] Tested with real LLMs (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented if unavoidable)
- [ ] Added entry to CHANGELOG.md
```

### Review Process

1. Maintainers will review your PR within 3-5 business days
2. Address any requested changes
3. Once approved, a maintainer will merge your PR
4. Your contribution will be credited in the next release

## Adding New Games

To add a new game type (e.g., Hawk-Dove, Stag Hunt):

### 1. Create Game Template Directory

```
resources/game_templates/your_game_name/
├── payoff_matrix.json          # Define payoffs
├── agent_prompt_en.txt         # English prompt
├── agent_prompt_vn.txt         # Vietnamese prompt
└── game_description.md         # Game rules documentation
```

### 2. Define Payoff Matrix

```json
{
  "strategies": {
    "strategy1": "Action1",
    "strategy2": "Action2"
  },
  "combinations": {
    "combination1": ["Action1", "Action1", "Action1"],
    "combination2": ["Action1", "Action1", "Action2"]
  },
  "payoffs": {
    "combination1": [5, 5, 5],
    "combination2": [3, 3, 6]
  }
}
```

### 3. Create Configuration File

```json
{
  "name": "your_game_name",
  "language": ["en", "vn"],
  "agents": {
    "names": ["Agent1", "Agent2", "Agent3"],
    "personalities": {
      "en": ["cooperative", "selfish", "reciprocal"]
    }
  },
  "llm": "MockLLM",
  "n_rounds": 50,
  "noiseConfig": {
    "agent1NoiseRate": 0.1,
    "agent2NoiseRate": 0.1,
    "agent3NoiseRate": 0.1
  }
}
```

### 4. Add Tests

```python
def test_your_game_payoffs():
    """Test that payoffs are calculated correctly."""
    # Load game config
    # Run sample rounds
    # Assert expected payoffs
    pass
```

### 5. Document in README

Add a section describing the game's strategic structure and contribution to the framework.

## Adding New LLM Connectors

To integrate a new LLM provider:

### 1. Implement Connector Class

```python
# src/llm_connectors/your_connector.py

from src.llm_connectors.abstract_connector import AbstractConnector
from typing import Dict, Any

class YourConnector(AbstractConnector):
    """
    Connector for Your LLM Provider API.
    
    Args:
        api_key: API key for authentication
        model: Model identifier (e.g., "your-model-v1")
        **kwargs: Additional provider-specific parameters
    """
    
    def __init__(self, api_key: str, model: str = "your-model-v1", **kwargs):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
    
    def execute(self, prompt: str, **kwargs) -> str:
        """
        Execute prompt and return response.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
            
        Raises:
            ConnectionError: If API request fails
        """
        # Implement API call logic here
        # Handle retries and errors
        # Return response text
        pass
    
    def validate_config(self) -> bool:
        """Validate that connector is properly configured."""
        return self.api_key is not None
```

### 2. Register in Factory

```python
# src/llm_connectors/llm_factory_connector.py

def get_connector(llm_name: str) -> AbstractConnector:
    """Factory function for creating LLM connectors."""
    if llm_name == "YourLLM":
        return YourConnector(
            api_key=os.getenv("YOUR_API_KEY"),
            model="your-model-v1"
        )
    # ... existing connectors
```

### 3. Add Tests

```python
def test_your_connector():
    """Test YourConnector with sample prompts."""
    connector = YourConnector(api_key="test_key")
    response = connector.execute("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0
```

### 4. Document Usage

Add to README.md:
- Installation requirements
- API key setup instructions
- Pricing considerations
- Rate limits

---

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [maintainers email - anonymous for review]

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to Project TRIAD! 🎯
