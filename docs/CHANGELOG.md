# Project TRIAD - Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-09

### Added - Initial Release for UAI 2026 Submission

#### Core Framework
- **Game Engines**: Implemented FairGame, NoiseFairGame for orchestrating multi-round games
- **Agent System**: Base Agent class with explicit belief tracking via JSON-structured outputs
- **Noise Model**: NoiseAgent with Schelling-inspired trembling-hand mechanism (bit-flip channel)
- **Payoff Matrix**: Flexible payoff computation supporting N-player arbitrary games

#### Three Game Scenarios
- **Prisoner's Dilemma (3-player)**: Extended classical 2-player version with coalition dynamics
- **Public Goods Game (3-player)**: Contribution/free-riding dynamics with synergy multiplier
- **Volunteer's Dilemma (3-player)**: Asymmetric costly heroism scenario

#### Novel Metrics
- **Trembling Robustness Score (TRS)**: Measures cooperation resilience under noise (∂CR/∂ε)
- **Alignment Gap (Δ)**: Shapley value - payoff to quantify exploitation
- **Coalition Entropy**: Measures alliance stability in N-player settings

#### LLM Connectors
- OpenAI connector (GPT-4, GPT-4o)
- Anthropic connector (Claude 3.5 Sonnet)
- Mistral connector
- vLLM connector (for local models like Qwen, Llama)
- Mock connector (deterministic testing without API/GPU)

#### Experimental Infrastructure
- **ExperimentRunner**: Batch parameter sweep functionality
- **Parallel execution**: Multi-threaded game running with configurable workers
- **Detailed logging**: Complete reasoning traces, beliefs, and action histories
- **Multi-language support**: 6 languages (English, Vietnamese, French, Italian, Chinese, Arabic)

#### Analysis Tools
- DataLoader for parsing experimental results
- Visualizer for publication-quality plots
- Results processor for structured output (CSV, JSON)

#### Documentation
- Comprehensive README with Quick Start, experimental setup, and reproduction instructions
- CONTRIBUTING.md with coding standards and development guidelines
- CITATION.cff for structured citation information
- Paper LaTeX source (UAI 2026 format) with full bibliography

#### Paper Contributions
- **Trembling Paradox**: Documented +12% cooperation increase under noise with belief tracking
- **Welfare Paradox**: Identified "Toxic Kindness" - exploitation of aligned agents (3:1 inequality)
- **Heroism Paradox**: Found 4% coordination failure from strategic over-reasoning

#### Reproducibility
- `reproduce_paper.py`: One-command script to regenerate all paper results
- Mock mode for quick validation without API costs
- Complete configuration files for all experiments in paper

### Research Findings
- 15,000+ simulation rounds across 3 games × 3 noise levels × 6 languages × 3 models
- GPT-4o TRS: +0.20 (antifragile to noise)
- Claude 3.5 TRS: +0.12
- Qwen-2.5 TRS: -0.05 (noise-sensitive)
- Alignment Gap: Alice = +3.5E (exploited), Bob = -2.1E (exploiter)
- VD Failure Rate: 4% (GPT-4o) vs 1% (random baseline)

### Technical Details
- Python 3.10+ compatibility
- Efficient parallel game execution (4-8 workers typical)
- Extensive error handling and retry logic for API reliability
- Modular architecture for easy extension (new games, models, metrics)

### Known Limitations
- Fixed 50-round horizon (future: adaptive stopping)
- Symmetric noise model (future: heterogeneous reliability)
- Limited to 3-player games (future: scale to N>3)
- English prompt templates most extensively tested

---

## [Unreleased] - Future Work

### Planned Features
- **Adaptive Personalities**: Meta-learning over repeated game episodes
- **Human-AI Mixed Games**: Integration with human player interfaces
- **Communication Protocols**: Cheap talk and commitment mechanisms
- **Larger Coalitions**: Support for N>3 with k-way alliances
- **Advanced Metrics**: Finer-grained belief accuracy tracking, counterfactual reasoning analysis
- **Adversarial Robustness**: Agents trained to exploit Toxic Kindness

### Under Consideration
- Web UI for interactive game simulation
- Real-time leaderboard for comparing models
- Integration with reinforcement learning baselines
- Support for partial observability and signaling games

---

## Version History

- **1.0.0** (2026-02-09): Initial public release accompanying UAI 2026 paper submission
