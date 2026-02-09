# Project TRIAD: The Trembling, Welfare, and Heroism Paradoxes in Multi-Agent LLM Systems

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![UAI 2026](https://img.shields.io/badge/UAI-2026-red.svg)](https://www.auai.org/uai2026/)
[![arXiv](https://img.shields.io/badge/arXiv-2601.XXXXX-b31b1b.svg)](https://arxiv.org/)

> **A unified game-theoretic framework for evaluating robustness, cooperation, and strategic reasoning in Large Language Model agents under uncertainty and social pressure.**

This repository contains the complete implementation and experimental framework for our UAI 2026 paper: *"Project TRIAD: The Trembling, Welfare, and Heroism Paradoxes in Multi-Agent LLM Systems"*.

---

## 📜 Abstract

As Large Language Models (LLMs) populate increasingly complex social ecosystems, their ability to maintain robustness against noise and exploitation becomes critical. We present **Project TRIAD**, a unified game-theoretic framework evaluating LLM agents across three canonical environments: **Prisoner's Dilemma**, **Public Goods Game**, and **Volunteer's Dilemma**. Through 15,000+ guided simulation rounds across six languages, we uncover three counter-intuitive phenomena that challenge conventional assumptions about AI alignment and cooperation.

### Three Core Discoveries

1. **The Trembling Paradox**: Moderate execution noise (ε ≈ 0.1) *increases* systemic cooperation by +12% through disrupting "grim trigger" retaliation cycles.

2. **The Welfare Paradox**: Highly aligned agents exhibit "Toxic Kindness"—generating high group welfare while suffering extreme exploitation (3:1 payoff inequality).

3. **The Heroism Paradox**: Advanced reasoning leads to strategic waiting in Volunteer's Dilemma, causing bystander cascades and 4% catastrophic coordination failures.

---

## 🎯 Key Contributions

### Novel Metrics

- **Trembling Robustness Score (TRS)**: Quantifies cooperation resilience under noise: `TRS = ∂(Cooperation)/∂ε`
- **Alignment Gap (Δ)**: Measures value creation vs. capture: `Δᵢ = φᵢ - πᵢ` (Shapley-based)
- **Coalition Entropy**: Tracks alliance stability: `H(S) = -Σ p(s)log p(s)`
- **Toxic Kindness Duration**: Measures exploitation tolerance under repeated defection

### Methodological Innovations

- **Explicit Belief Tracking**: Forces Theory-of-Mind reasoning via structured JSON outputs
- **Trembling Hand Noise Model**: Schelling-inspired bit-flip channel with probability ε
- **Multi-lingual Stress Testing**: 6 languages (English, Vietnamese, French, Italian, Chinese, Arabic)
- **N-Player Extensions**: 3-player variants of classical 2-player games

---

## 🏗️ Repository Structure

```
d:\Triad_Project/
├── src/                          # Core framework implementation
│   ├── agents/                   # Agent architectures with noise handling
│   │   ├── agent.py             # Base Agent with belief tracking
│   │   └── noise_agent.py       # NoiseAgent with trembling hand model
│   ├── game/                     # Game engines
│   │   ├── fairgame.py          # Base FairGame orchestrator
│   │   ├── noise_game.py        # NoiseFairGame with error injection
│   │   └── payoff_matrix.py     # Flexible payoff computation
│   ├── experiments/              # Batch experiment runners
│   │   └── experiment_runner.py # Parameter sweep infrastructure
│   ├── analysis/                 # Post-hoc analysis tools
│   │   ├── data_loader.py       # Result parsing utilities
│   │   └── visualizer.py        # Publication-quality plotting
│   └── llm_connectors/           # LLM inference integrations
│       ├── vllm_connector.py    # vLLM local inference (primary)
│       ├── mock_connector.py    # Mock LLM for testing
│       ├── openai_connector.py  # OpenAI API (optional)
│       └── anthropic_connector.py # Anthropic API (optional)
├── resources/
│   ├── game_templates/           # Game configurations
│   │   ├── prisoner_dilemma_3/  # 3-player IPD
│   │   ├── public_goods_3/      # 3-player PGG
│   │   └── volunteers_dilemma_3/ # 3-player VD
│   ├── config/                   # Experimental configurations
│   └── results/                  # Generated outputs
├── experiment_results/           # Batch experiment outputs
├── uai2026-template/            # Camera-ready LaTeX submission
│   └── submission.tex           # Main paper
├── main.py                       # Single game runner
├── run_experiment_example.py     # Batch experiment example
├── run_analysis_example.py       # Analysis pipeline example
└── requirements.txt              # Python dependencies
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/project-triad/triad.git
cd triad

# Install dependencies
pip install -r requirements.txt

# Install vLLM for local model inference
pip install vllm

# Download models (example for Llama-3.1-8B)
# Models will be automatically downloaded from HuggingFace on first use
# Supported models:
# - meta-llama/Meta-Llama-3.1-8B-Instruct
# - meta-llama/Meta-Llama-3.1-70B-Instruct
# - Qwen/Qwen2.5-32B-Instruct
# - mistralai/Mistral-7B-Instruct-v0.3
```

### Running Experiments

#### 1. Single Game (Quick Test)

```bash
# Run 50-round Prisoner's Dilemma with 10% noise
python main.py api --config pd_noise_round_known_mild \
                   --config-dir prisoner_dilemma_noise \
                   --noise1 0.1 --noise2 0.1 --rounds 50
```

#### 2. Batch Parameter Sweep

```python
# run_experiment_example.py
from src.experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner(output_dir="experiment_results", max_workers=4)

# Sweep noise rates for Public Goods Game
param_grid = {
    'noiseConfig.agent1NoiseRate': [0.0, 0.1, 0.2, 0.3],
    'noiseConfig.agent2NoiseRate': [0.0, 0.1, 0.2, 0.3],
    'noiseConfig.agent3NoiseRate': [0.0, 0.1, 0.2, 0.3]
}

runner.run_experiment(
    base_config_name="public_goods_3_default",
    config_dir="public_goods_3",
    parameter_grid=param_grid,
    experiment_name="pgg_noise_impact_analysis"
)
```

#### 3. Analyze Results

```python
# run_analysis_example.py
from src.analysis.data_loader import DataLoader
from src.analysis.visualizer import Visualizer

loader = DataLoader("experiment_results/pgg_noise_impact_analysis_*.csv")
data = loader.load_all()

viz = Visualizer()
viz.plot_cooperation_by_noise(data, save_path="figures/cooperation_noise.pdf")
viz.plot_alignment_gap_heatmap(data, save_path="figures/alignment_gap.pdf")
```

---

## 📊 Experimental Design

### Game Scenarios

| Game | Players | Actions | Key Tension | Nash Equilibrium |
|------|---------|---------|-------------|------------------|
| **Prisoner's Dilemma (3PD)** | 3 | {Cooperate, Defect} | Individual rationality vs. collective welfare | All Defect |
| **Public Goods Game (PGG)** | 3 | Contribute ∈ [0, E] | Free-riding on public goods | Zero contribution |
| **Volunteer's Dilemma (VD)** | 3 | {Volunteer, Wait} | Cost of heroism vs. bystander effect | Mixed strategy |

### Agent Archetypes

- **Cooperative (Alice)**: Unconditional cooperator (tests exploitation vulnerability)
- **Selfish (Bob)**: Pure utility maximizer (tests competitive pressure)
- **Reciprocal (Charlie)**: Tit-for-Tat (tests adaptive social learning)

### Noise Injection Mechanism

Based on Schelling's "trembling hand" model:
- **Intended action**: aᵢ* (generated by LLM)
- **Observed action**: aᵢᵒᵇˢ with P(aᵢᵒᵇˢ = ¬aᵢ*) = ε
- **Agent knowledge**: Observes aᵢᵒᵇˢ but doesn't know if it was intended

### Explicit Belief Tracking

Agents must output structured beliefs before acting:

```json
{
  "beliefs": {
    "Player_B": 0.85,
    "Player_C": 0.12
  },
  "reason": "Player B has cooperated consistently for 8 rounds...",
  "action": "Cooperate"
}
```

---

## 📈 Expected Results (From Paper)

### Trembling Robustness Scores

| Model | TRS Score | Win Rate (Noisy) | Belief Accuracy |
|-------|-----------|------------------|-----------------|
| Llama-3.1-70B | +0.18 | 62% | 0.85 |
| Qwen-2.5-32B | +0.14 | 59% | 0.89 |
| Llama-3.1-8B | +0.08 | 51% | 0.78 |
| Mistral-7B | -0.03 | 45% | 0.72 |
| Qwen-2.5 | -0.05 | 42% | 0.76 |

*Positive TRS indicates antifragility—models cooperate MORE under noise.*

### Alignment Gap Distribution

- **Alice (Cooperative)**: Δ̄ = +3.5E (severe exploitation)
- **Bob (Selfish)**: Δ̄ = -2.1E (captures disproportionate value)
- **Charlie (Reciprocal)**: Δ̄ = +0.3E (near-equilibrium)

### Volunteer's Dilemma Failure Rates

- **Random baseline**: 1% catastrophic failure (no volunteers)
- **GPT-4o (high reasoning)**: 4% catastrophic failure
- **Mechanism**: "Analysis paralysis" from overfitting probabilities

---

## 🔬 Reproducing Paper Results

### Full Reproduction Script

```bash
# Install dependencies
pip install -r requirements.txt

# Run all experiments (requires API keys and ~48 hours)
python reproduce_paper.py --config full --max-workers 8

# Generate all figures
python generate_figures.py --input experiment_results/ --output paper/figures/

# Compile LaTeX paper
cd uai2026-template/uai2026-template
pdflatex submission.tex
bibtex submission
pdflatex submission.tex
pdflatex submission.tex
```

### Mock Mode (No API/GPU Required)

```bash
# Quick validation with mock LLM (deterministic responses)
python main.py api --config public_goods_3_mock \
                   --config-dir public_goods_3 \
                   --rounds 50
```

---

## 📚 Citation

If you use this code or find our work useful, please cite:

```bibtex
@inproceedings{triad2026,
  title={Project TRIAD: The Trembling, Welfare, and Heroism Paradoxes in Multi-Agent LLM Systems},
  author={Anonymous},
  booktitle={Proceedings of the 40th Conference on Uncertainty in Artificial Intelligence (UAI)},
  year={2026},
  organization={AUAI Press}
}
```

---

## 🛠️ Advanced Usage

### Adding New Games

1. Create payoff matrix in `resources/game_templates/your_game/payoff_matrix.json`
2. Define agent prompts in `resources/game_templates/your_game/agent_prompt_{lang}.txt`
3. Create config in `resources/config/your_game/config.json`

### Custom LLM Connectors

Extend `AbstractConnector`:

```python
from src.llm_connectors.abstract_connector import AbstractConnector

class CustomConnector(AbstractConnector):
    def execute(self, prompt: str, **kwargs) -> str:
        # Your API call logic
        return response_text
```

### Analyzing Custom Metrics

```python
from src.results_processing.results_processor import ResultsProcessor

processor = ResultsProcessor()
df = processor.process(game_results)

# Add custom metrics
df['custom_metric'] = df.apply(lambda row: your_function(row), axis=1)
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📞 Contact

- **Paper Authors**: [Anonymous for review]
- **Issues**: https://github.com/project-triad/triad/issues
- **Discussions**: https://github.com/project-triad/triad/discussions

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This research builds on foundational work in:
- **Cooperative AI** ([Dafoe et al., 2020](https://arxiv.org/abs/2012.08630))
- **LLM Game Theory** ([Akata et al., 2023](https://arxiv.org/abs/2305.16867))
- **Trembling Hand Equilibria** ([Schelling, 1960](https://www.hup.harvard.edu/catalog.php?isbn=9780674840317))

We thank the authors of these works for laying the intellectual foundation for multi-agent AI evaluation
