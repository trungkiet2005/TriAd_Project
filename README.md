# Triad Project: Multiplayer Economic Games with Noise

A framework for simulating and studying **3-player economic games** (Prisoner's Dilemma, Public Goods Game, Volunteer's Dilemma) with large language models (LLMs). Features include noise injection (action flipping), multilingual support, and hallucination tracking.

## Supported Games

1.  **Prisoner's Dilemma (3-Player)**
    -   **Dynamics**: Cooperate vs. Defect. Payoffs depend on the number of cooperators.
    -   **Strategies**: `Cooperate`, `Defect`
    -   **Languages**: en, vn, fr, it, cn, ar
2.  **Public Goods Game (3-Player)**
    -   **Dynamics**: Keep vs. Contribute. Contributions are multiplied and shared.
    -   **Strategies**: `Keep`, `Contribute`
    -   **Languages**: en, vn, fr, it, cn, ar
3.  **Volunteer's Dilemma (3-Player)**
    -   **Dynamics**: Volunteer vs. Ignore. If one volunteers, all benefit.
    -   **Strategies**: `Volunteer`, `Ignore`
    -   **Languages**: en, vn, fr, it, cn, ar

## Key Features

-   **Noise Injection**: Configurable probability that an agent's chosen action is flipped (e.g., intended "Cooperate" becomes "Defect").
-   **Noise Awareness**: Agents are explicitly warned about their opponents' noise rates in the prompt.
-   **Multilingual**: Full support for 6 languages (English, Vietnamese, French, Italian, Chinese, Arabic).
-   **Mock Verification**: Includes a `MockLLM` connector to verify game logic without API costs.
-   **Hallucination Checking**: Optional modules to test if agents correctly understand the game state (Time, Rule, Payoff checks).

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
```

## Usage

### Run Public Goods Game (3-Player)
```bash
python main.py local --config public_goods_3_default --config-dir public_goods_3 --rounds 10
```

### Run Volunteer's Dilemma (3-Player)
```bash
python main.py local --config volunteers_dilemma_3_default --config-dir volunteers_dilemma_3 --rounds 10
```

### Run Prisoner's Dilemma (3-Player)
```bash
python main.py local --config pd3_noise_default --config-dir prisoner_dilemma_noise --rounds 10
```

### Verification Mode (Mock LLM)
Run any game with its `_mock` configuration to test logic without LLM calls.
```bash
python main.py local --config volunteers_dilemma_3_mock --config-dir volunteers_dilemma_3
```

## Project Structure

```
Triad_Project/
├── main.py                           # Entry point
├── resources/
│   ├── config/                       # Game configurations (JSON)
│   │   ├── public_goods_3/
│   │   ├── volunteers_dilemma_3/
│   │   └── prisoner_dilemma_noise/
│   ├── game_templates/               # Prompt templates (TXT)
│   └── results/                      # Game outputs
└── src/
    ├── agents/                       # Agent logic (Agent, NoiseAgent)
    ├── game/                         # Core game logic (FairGame, PayoffMatrix)
    ├── prompts/                      # Prompt generation
    └── llm_connectors/               # API connectors (OpenAI, Anthropic, Mock)
```

## Advanced Configuration

Edit the `.json` config files in `resources/config/` to adjust:
-   **Payoff Matrices**: Change the `weights` and `matrix` values.
-   **Noise Rates**: Set `noiseConfig` for each agent.
-   **Languages**: Add or remove languages from the `languages` list.
