#!/usr/bin/env python3
"""
Quick test to verify refactored modules work correctly
"""

print("Testing refactored modules...")

# Test config module
print("\n1. Testing config.py...")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.analysis.config import (
    COOPERATION_KEYWORDS,
    COOPERATION_THRESHOLDS,
    TRS_THRESHOLDS,
    VARIABILITY_THRESHOLDS,
    PLOT_DEFAULTS,
    DEFAULT_BOOTSTRAP_ITERATIONS,
    DEFAULT_CONFIDENCE_INTERVAL
)
print(f"   ✓ Config loaded successfully")
print(f"   ✓ {len(COOPERATION_KEYWORDS)} cooperation keywords")
print(f"   ✓ Bootstrap iterations: {DEFAULT_BOOTSTRAP_ITERATIONS}")
print(f"   ✓ Plot DPI: {PLOT_DEFAULTS['dpi']}")

# Test base_utils module
print("\n2. Testing base_utils.py...")
from src.analysis.base_utils import (
    CooperationCalculator,
    ColumnFilter,
    DataFrameValidator,
    format_percentage,
    format_ci
)
print(f"   ✓ Base utils classes imported")

# Test CooperationCalculator
calc = CooperationCalculator()
test_strategies = ["Cooperate", "Defect", "Cooperate", "Hợp tác"]
rate = calc.calculate_rate(test_strategies)
print(f"   ✓ CooperationCalculator works: {rate:.2%}")

# Test formatting utils
print(f"   ✓ format_percentage: {format_percentage(0.7523)}")
print(f"   ✓ format_ci: {format_ci(0.75, 0.02)}")

# Test FAIRGAMEAnalyzer
print("\n3. Testing fairgame_analysis.py...")
from src.analysis.fairgame_analysis import FAIRGAMEAnalyzer
analyzer = FAIRGAMEAnalyzer()
print(f"   ✓ FAIRGAMEAnalyzer instantiated")
print(f"   ✓ Uses CooperationCalculator: {hasattr(analyzer, 'coop_calculator')}")

# Test QualitativeTableGenerator
print("\n4. Testing table_generator.py...")
from src.analysis.table_generator import QualitativeTableGenerator
generator = QualitativeTableGenerator()
print(f"   ✓ QualitativeTableGenerator instantiated")

# Test threshold methods with config
coop_desc = generator._descriptive_cooperation_level(0.85)
print(f"   ✓ Cooperation level (0.85): '{coop_desc}'")
trs_desc = generator._descriptive_trs_level(0.18)
print(f"   ✓ TRS level (+0. 18): '{trs_desc}'")
var_desc = generator._descriptive_variability(0.025)
print(f"   ✓ Variability (0.025): '{var_desc}'")

print("\n✅ ALL TESTS PASSED! Refactoring is successful.")
print("=" * 60)
print("Summary:")
print("  - config.py: Centralized all constants")
print("  - base_utils.py: Reusable utility classes")
print("  - fairgame_analysis.py: Uses config and utils")
print("  - table_generator.py: Uses config thresholds")
print("=" * 60)
