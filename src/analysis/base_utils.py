"""
Base classes and utilities for FAIRGAME analysis.
Provides common functionality used across analysis modules.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from src.analysis.config import COOPERATION_KEYWORDS


class CooperationCalculator:
    """Handles cooperation rate calculations with multi-language support."""
    
    def __init__(self, keywords: Optional[List[str]] = None):
        """
        Initialize with cooperation keywords.
        
        Args:
            keywords: List of cooperation keywords. Uses default if None.
        """
        self.keywords = keywords or COOPERATION_KEYWORDS
    
    def calculate_rate(self, strategies: List[str]) -> float:
        """
        Calculate cooperation rate from strategy list.
        
        Args:
            strategies: List of strategy strings
            
        Returns:
            Cooperation rate between 0.0 and 1.0
        """
        if not strategies:
            return 0.0
        
        coop_count = sum(
            1 for s in strategies 
            if any(k in str(s) for k in self.keywords)
        )
        return coop_count / len(strategies)
    
    def calculate_game_rate(self, row: pd.Series, 
                           strategy_cols: List[str]) -> float:
        """
        Calculate cooperation rate for a single game row.
        
        Args:
            row: DataFrame row containing game data
            strategy_cols: Column names containing strategies
            
        Returns:
            Game-level cooperation rate
        """
        total_actions = 0
        coop_actions = 0
        
        for col in strategy_cols:
            strategies = row[col]
            if isinstance(strategies, list):
                total_actions += len(strategies)
                coop_actions += sum(
                    1 for s in strategies 
                    if any(k in str(s) for k in self.keywords)
                )
        
        return coop_actions / total_actions if total_actions > 0 else 0.0


class ColumnFilter:
    """Utilities for filtering DataFrame columns."""
    
    @staticmethod
    def get_strategy_columns(df: pd.DataFrame, 
                            exclude_pattern: str = 'noise') -> List[str]:
        """
        Get all strategy columns from DataFrame.
        
        Args:
            df: Input DataFrame
            exclude_pattern: Pattern to exclude from column names
            
        Returns:
            List of strategy column names
        """
        return [
            col for col in df.columns 
            if 'strategies' in col and exclude_pattern not in col
        ]
    
    @staticmethod
    def get_score_columns(df: pd.DataFrame, 
                         exclude_pattern: str = 'noise') -> List[str]:
        """
        Get all score columns from DataFrame.
        
        Args:
            df: Input DataFrame
            exclude_pattern: Pattern to exclude from column names
            
        Returns:
            List of score column names
        """
        return [
            col for col in df.columns 
            if 'scores' in col and exclude_pattern not in col
        ]


class DataFrameValidator:
    """Validates DataFrame structure for analysis."""
    
    @staticmethod
    def check_required_columns(df: pd.DataFrame, 
                              required: List[str]) -> None:
        """
        Check if DataFrame contains required columns.
        
        Args:
            df: DataFrame to validate
            required: List of required column names
            
        Raises:
            ValueError: If required columns are missing
        """
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}"
            )
    
    @staticmethod
    def check_minimum_rows(df: pd.DataFrame, minimum: int = 1) -> None:
        """
        Check if DataFrame has minimum number of rows.
        
        Args:
            df: DataFrame to validate
            minimum: Minimum required rows
            
        Raises:
            ValueError: If DataFrame has insufficient rows
        """
        if len(df) < minimum:
            raise ValueError(
                f"DataFrame must have at least {minimum} rows, "
                f"but has {len(df)}"
            )


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format float as percentage string.
    
    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_ci(lower: float, upper: float, decimals: int = 3) -> str:
    """
    Format confidence interval as string.
    
    Args:
        lower: Lower bound
        upper: Upper bound
        decimals: Number of decimal places
        
    Returns:
        Formatted CI string like "[0.123, 0.456]"
    """
    return f"[{lower:.{decimals}f}, {upper:.{decimals}f}]"


def get_significance_symbol(p_value: float) -> str:
    """
    Get significance symbol based on p-value.
    
    Args:
        p_value: P-value from statistical test
        
    Returns:
        Symbol: '***' (p<0.001), '**' (p<0.01), '*' (p<0.05), '' (n.s.)
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return ''
