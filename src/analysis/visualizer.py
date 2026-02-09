
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional
from src.analysis.config import COOPERATION_KEYWORDS, PLOT_DEFAULTS
from src.analysis.base_utils import (
    CooperationCalculator,
    ColumnFilter,
    ScoreCalculator
)

class Visualizer:
    """
    Generates plots for experiment analysis.
    """
    
    def __init__(self, style: str = "whitegrid"):
        """
        Initialize visualizer with a specific style.
        """
        self.style = style
        self.coop_calculator = CooperationCalculator()
        # seaborn.set_theme(style=style) is deprecated in some versions, using simpler approach if needed
        # but let's try standard matplotlib style for safety if seaborn fails
        try:
            sns.set_style(style)
        except:
            plt.style.use('ggplot')

    def plot_cooperation_rate_heatmap(self, df: pd.DataFrame, 
                                     x_col: str, y_col: str, 
                                     title: str = "Average Cooperation Rate Calculation",
                                     output_path: Optional[str] = None):
        """
        Plot a heatmap of average cooperation rates.
        Calculates the mean cooperation rate across all agents in the game.
        
        Args:
            df: DataFrame containing experiment results
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Plot title
            output_path: Optional path to save the plot
        """
        plt.figure(figsize=(10, 8))
        
        # Identify strategy columns
        strategy_cols = ColumnFilter.get_strategy_columns(df, exclude_pattern='noise')
        
        # Calculate rate for each game
        df['game_coop_rate'] = df.apply(
            lambda row: self.coop_calculator.calculate_game_rate(row, strategy_cols),
            axis=1
        )
        
        # Pivot table
        pivot_table = df.pivot_table(index=y_col, columns=x_col, values='game_coop_rate', aggfunc='mean')
        
        sns.heatmap(pivot_table, annot=True, cmap="YlGnBu", fmt=".2f", vmin=0, vmax=1)
        plt.title(title)
        plt.ylabel(y_col)
        plt.xlabel(x_col)
        
        if output_path:
            plt.savefig(output_path, dpi=PLOT_DEFAULTS['dpi'])
            print(f"Heatmap saved to {output_path}")
        else:
            plt.show()
        plt.close()

    def plot_score_distribution(self, df: pd.DataFrame, 
                               group_col: str, 
                               title: str = "Total Score Distribution",
                               output_path: Optional[str] = None):
        """
        Plot boxplots of TOTAL scores (sum of all agents) grouped by a parameter.
        
        Args:
            df: DataFrame containing experiment results
            group_col: Column name to group by
            title: Plot title
            output_path: Optional path to save the plot
        """
        plt.figure(figsize=PLOT_DEFAULTS['figsize'])
        
        score_cols = ColumnFilter.get_score_columns(df)
        
        df['total_game_score'] = df.apply(
            lambda row: ScoreCalculator.calculate_total_score(row, score_cols),
            axis=1
        )
        
        sns.boxplot(x=group_col, y='total_game_score', data=df)
        plt.title(title)
        plt.grid(True, alpha=0.3)
        
        if output_path:
            plt.savefig(output_path, dpi=PLOT_DEFAULTS['dpi'])
            print(f"Boxplot saved to {output_path}")
        else:
            plt.show()
        plt.close()
