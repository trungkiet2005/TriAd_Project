"""
Configuration constants for FAIRGAME-style analysis.
Centralizes magic numbers and configuration values.
"""

from typing import List, Dict


# Statistical Analysis Constants
DEFAULT_BOOTSTRAP_ITERATIONS = 1000
DEFAULT_CONFIDENCE_INTERVAL = 0.95
ALPHA_LEVEL = 0.05

# Cooperation Keywords (Multi-language)
COOPERATION_KEYWORDS: List[str] = [
    # English
    "Cooperate", "Volunteer", "Contribute",
    # Vietnamese
    "Hợp tác", "Tình nguyện", "Đóng góp",
    # French
    "Collaborer", "Contribuer",
    # Italian
    "Offrirsi volontario", "Contribuire",
    # Chinese
    "志愿", "贡献",
    # Arabic
    "تطوع", "مساهمة"
]

# Qualitative Description Thresholds
COOPERATION_THRESHOLDS: Dict[str, float] = {
    'high': 0.80,
    'strong': 0.65,
    'moderate': 0.50,
    'weak': 0.35,
    'low': 0.20
}

TRS_THRESHOLDS: Dict[str, float] = {
    'strong_positive': 0.15,
    'moderate_positive': 0.05,
    'stable': -0.05,
    'moderate_decline': -0.20
}

VARIABILITY_THRESHOLDS: Dict[str, float] = {
    'low': 0.03,       # Low variability (high consistency)
    'moderate': 0.06   # Moderate variability
}

# Plot Configuration
PLOT_DEFAULTS: Dict[str, any] = {
    'figsize': (12, 6),
    'dpi': 300,
    'style': 'seaborn-v0_8-whitegrid',
    'color_positive': 'lightgreen',
    'color_negative': 'lightcoral',
    'color_bar': 'steelblue',
    'alpha': 0.8,
    'capsize': 5
}

# File Patterns
DEFAULT_RESULTS_DIR = "resources/results"
DEFAULT_OUTPUT_DIR = "experiment_results"
CSV_FILE_PATTERN = "*.csv"
JSON_FILE_PATTERN = "*.json"

# Column Name Patterns
STRATEGY_COL_PATTERN = "strategies"
SCORE_COL_PATTERN = "scores"
NOISE_COL_EXCLUDED = "noise"

# Language Codes
SUPPORTED_LANGUAGES: List[str] = ['en', 'vi', 'fr', 'it', 'zh', 'ar']

# Statistical Test Parameters
SIGNIFICANCE_LEVELS: Dict[str, float] = {
    'p_001': 0.001,
    'p_01': 0.01,
    'p_05': 0.05
}

# Output Format Templates
LATEX_TABLE_HEADER = r"\begin{table}[h]"
LATEX_TABLE_FOOTER = r"\end{table}"
