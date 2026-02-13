"""
Triad Analysis Module
Specially designed for 3-Player Prisoner's Dilemma (Project TRIAD).
Focuses on Coalition Detection, Alignment Gaps, and State Distribution Analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from src.analysis.base_utils import ColumnFilter, CooperationCalculator
from src.analysis.config import PLOT_DEFAULTS

class TriadAnalyzer:
    """
    Analyzer for 3-player specific dynamics.
    Identifies states:
    - CCC (All Cooperate) -> Welfare Maximization
    - DDD (All Defect) -> Nash Equilibrium (usually)
    - 2C (2 Coop, 1 Defect) -> Exploitation (Single Defector exploits 2 Cooperators)
    - 1C (1 Coop, 2 Defect) -> Bullying/Sacrifice (Single Cooperator exploited by 2 Defectors)
    """
    
    def __init__(self):
        self.coop_calculator = CooperationCalculator()

    def _classify_round_state(self, strategies: List[str]) -> str:
        """
        Classify a single round's strategy set into a state.
        Assumes strategies are strings containing "Cooperate" (or keyword) or "Defect".
        """
        coop_count = sum(1 for s in strategies if 'Cooperate' in s or 'Hop tac' in s or 'Hợp tác' in s)
        n = len(strategies)
        
        if coop_count == n:
            return "CCC (Universal Coop)"
        elif coop_count == 0:
            return "DDD (Universal Defect)"
        elif coop_count == 2:
            return "2C-1D (Exploitation)"
        elif coop_count == 1:
            return "1C-2D (Bullying)"
        else:
            return "Mixed" # Should cover all for N=3, but good fallback

    def analyze_state_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the frequency of each state (CCC, DDD, 2C, 1C) for each game or group.
        
        Args:
            df: DataFrame containing experiment results (games_summary or similar).
                MUST contain strategy lists or stringified strategies.
                
        Returns:
            DataFrame with state counts/percentages.
        """
        # We need row-level strategy access. 
        # games_summary.csv usually has 'agent1_strategies', 'agent2_strategies', etc.
        # strings "C,D,C..." or full lists.
        
        strategy_cols = ColumnFilter.get_strategy_columns(df)
        if not strategy_cols:
            return pd.DataFrame()

        dataset_states = []

        for idx, row in df.iterrows():
            # Extract strategies for this game
            # Assuming comma-separated strings if loaded from CSV, or lists if loaded directly
            game_strats = []
            
            # Determine number of rounds from the first agent
            raw_s1 = row[strategy_cols[0]]
            if isinstance(raw_s1, str):
                s1_list = raw_s1.split(',')
            else:
                s1_list = raw_s1
            
            n_rounds = len(s1_list)
            
            # Build list of [ [s1_r1, s2_r1, s3_r1], [s1_r2, ...], ... ]
            round_strategies = [[] for _ in range(n_rounds)]
            
            valid_game = True
            for col in strategy_cols:
                val = row[col]
                if isinstance(val, str):
                    s_list = val.split(',')
                else:
                    s_list = val
                
                if len(s_list) != n_rounds:
                    valid_game = False
                    break
                    
                for r_idx, s in enumerate(s_list):
                    # Map single chars to full names for classifier
                    if s.strip().upper() == 'C': s = 'Cooperate'
                    if s.strip().upper() == 'D': s = 'Defect'
                    round_strategies[r_idx].append(s)
            
            if not valid_game:
                continue

            # Classify each round
            game_state_counts = {
                "CCC (Universal Coop)": 0,
                "DDD (Universal Defect)": 0,
                "2C-1D (Exploitation)": 0,
                "1C-2D (Bullying)": 0
            }
            
            for r_strats in round_strategies:
                state = self._classify_round_state(r_strats)
                if state in game_state_counts:
                    game_state_counts[state] += 1
            
            # Normalize to percentages
            for k in game_state_counts:
                game_state_counts[k] /= n_rounds if n_rounds > 0 else 1
            
            # Add metadata keys if available
            meta = {}
            if 'language' in row: meta['language'] = row['language']
            if 'agent1_noise_rate' in row: meta['noise_rate'] = row['agent1_noise_rate']
            elif 'agent1NoiseRate' in row: meta['noise_rate'] = row['agent1NoiseRate']
            
            entry = {**meta, **game_state_counts}
            dataset_states.append(entry)
            
        return pd.DataFrame(dataset_states)


class TriadVisualizer:
    """
    Visualizer for Triad Analysis results.
    """
    
    def __init__(self):
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def plot_state_distribution(self, df_states: pd.DataFrame, 
                               group_col: str = 'language',
                               title: str = "Distribution of Game States (3-Player)",
                               output_path: Optional[str] = None):
        """
        Plot stacked bar chart of state distributions (CCC, DDD, 2C1D, 1C2D).
        """
        if df_states.empty:
            print("No data to plot.")
            return

        # Aggregate by group
        state_cols = ["CCC (Universal Coop)", "2C-1D (Exploitation)", "1C-2D (Bullying)", "DDD (Universal Defect)"]
        grouped = df_states.groupby(group_col)[state_cols].mean()
        
        # Plot
        ax = grouped.plot(kind='bar', stacked=True, figsize=(10, 6), 
                         colormap='RdYlGn_r', edgecolor='black', alpha=0.8)
        
        # 'RdYlGn_r' makes CCC (Green) -> DDD (Red) typically? 
        # Actually Reverse Red-Yellow-Green: Red (high), Green (low).
        # Standard: CCC=Green, DDD=Red. 
        # Let's use custom colors for clarity
        colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'] 
        # Green (CCC), Blue (2C1D), Orange (1C2D), Red (DDD)
        
        # Re-plot with custom colors
        plt.close() # Close previous
        ax = grouped.plot(kind='bar', stacked=True, figsize=(10, 6), 
                         color=colors, edgecolor='black', alpha=0.9)

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(group_col.replace('_', ' ').title(), fontsize=12)
        plt.ylabel('Proportion of Rounds', fontsize=12)
        plt.legend(title='Game State', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"State distribution plot saved to {output_path}")
        else:
            plt.show()
        plt.close()

    def plot_coalition_heatmap(self, df_states: pd.DataFrame,
                             x_col: str = 'noise_rate',
                             y_col: str = 'language',
                             output_path: Optional[str] = None):
        """
        Heatmap showing the frequency of 'Coalition/Exploitation' strategies (2C-1D).
        """
        if df_states.empty:
            return
            
        pivot = df_states.pivot_table(
            values='2C-1D (Exploitation)', 
            index=y_col, 
            columns=x_col, 
            aggfunc='mean'
        )
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot, annot=True, fmt=".1%", cmap="Blues", cbar_kws={'label': 'Frequency of 2C-1D State'})
        plt.title("Frequency of Exploitation (2 Coop vs 1 Defect)", fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
