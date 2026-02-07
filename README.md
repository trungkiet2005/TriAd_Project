# Nicer Fairgame Combined

A project combining the **Fairgame** framework with **nicer_than_human** features for Prisoner's Dilemma with noise injection and hallucination tracking.

## Features

- **Two LLM agents** playing Prisoner's Dilemma
- **Noise injection**: Agent actions can be flipped (Cooperate ↔ Defect) based on configurable noise rate
- **Opponent noise awareness**: Agents know their opponent's noise rate in prompts
- **Hallucination tracking**: Comprehension questions (TimeChecker, RuleChecker, AggregationChecker) to detect if agents hallucinate about game state

## Installation

```bash
cd nicer_fairgame_combined
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Run
```bash
python main.py local --config pd_noise_default
```

### With Custom Noise Rates
```bash
# Agent1 has 20% noise, Agent2 has 10% noise
python main.py local --noise1 0.2 --noise2 0.1

# No noise for agent1, 30% noise for agent2
python main.py local --noise1 0.0 --noise2 0.3
```

### With Custom Number of Rounds
```bash
python main.py local --rounds 20 --noise1 0.1 --noise2 0.1
```

### Enable Hallucination Checking
```bash
python main.py local --enable-checkers --checkers time rule aggregation
```

## Project Structure

```
nicer_fairgame_combined/
├── main.py                           # CLI entry point
├── requirements.txt
├── .env.example
├── resources/
│   ├── config/prisoner_dilemma_noise/
│   │   └── pd_noise_default.json     # Default config
│   ├── game_templates/
│   │   └── prisoner_dilemma_noise_en.txt
│   └── results/                      # Output directory
└── src/
    ├── noise_agent.py                # Agent with noise flipping
    ├── noise_game.py                 # Extended FairGame
    ├── noise_game_round.py           # Round with noise injection
    ├── noise_fairgame_factory.py     # Factory for noise games
    ├── extended_prompt_creator.py    # Prompts with noise info
    ├── checkers/
    │   ├── checker.py                # Base checker
    │   ├── time_checker.py           # Round/action questions
    │   ├── rule_checker.py           # Payoff/rules questions
    │   └── aggregation_checker.py    # Total points questions
    └── [Fairgame base files...]
```

## How Noise Works

1. Agent receives prompt (including opponent's noise rate info)
2. Agent chooses an action (Cooperate or Defect)
3. **After** the agent responds, noise is applied:
   - With probability `noise_rate`, the action is **flipped**
   - e.g., if noise_rate=0.1 and agent said "Cooperate", 10% chance it becomes "Defect"
4. The **final** action (after noise) is recorded in history
5. History notes remind agents that shown actions are final (post-noise)

## Configuration

Edit `resources/config/prisoner_dilemma_noise/pd_noise_default.json`:

```json
{
    "noiseConfig": {
        "agent1NoiseRate": 0.1,    // 10% noise for agent1
        "agent2NoiseRate": 0.1     // 10% noise for agent2
    },
    "enableHallucinationChecks": true,
    "checkers": ["time", "rule", "aggregation"],
    ...
}
```

## Hallucination Checkers

- **TimeChecker**: Asks about current round, past actions, past scores
- **RuleChecker**: Asks about payoff values, available actions
- **AggregationChecker**: Asks about total points, action counts
