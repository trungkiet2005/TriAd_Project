
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional

class Visualizer:
    """
    Generates plots for experiment analysis.
    """
    
    def __init__(self, style: str = "whitegrid"):
        """
        Initialize visualizer with a specific style.
        """
        self.style = style
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
        """
        plt.figure(figsize=(10, 8))
        
        coop_keywords = ["Cooperate", "Volunteer", "Contribute", "Hợp tác", "Tình nguyện", "Đóng góp", "Collaborer", "Contribuer", "Offrirsi volontario", "Contribuire", "志愿", "贡献", "تطوع", "مساهمة"]
        
        # Identify strategy columns
        exclude_agents = ['noise'] # filtering
        strategy_cols = [c for c in df.columns if 'strategies' in c and not any(ex in c for ex in exclude_agents)]
        
        def calculate_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0

        # Calculate rate for each game
        df['game_coop_rate'] = df.apply(calculate_game_coop_rate, axis=1)
        
        # Pivot table
        pivot_table = df.pivot_table(index=y_col, columns=x_col, values='game_coop_rate', aggfunc='mean')
        
        sns.heatmap(pivot_table, annot=True, cmap="YlGnBu", fmt=".2f", vmin=0, vmax=1)
        plt.title(title)
        plt.ylabel(y_col)
        plt.xlabel(x_col)
        
        if output_path:
            plt.savefig(output_path)
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
        """
        plt.figure(figsize=(12, 6))
        
        score_cols = [c for c in df.columns if 'scores' in c]
        
        def calculate_total_score(row):
            total = 0
            for col in score_cols:
                scores = row[col]
                if isinstance(scores, list):
                    total += sum(scores)
            return total

        df['total_game_score'] = df.apply(calculate_total_score, axis=1)
        
        sns.boxplot(x=group_col, y='total_game_score', data=df)
        plt.title(title)
        plt.grid(True, alpha=0.3)
        
        if output_path:
            plt.savefig(output_path)
            print(f"Boxplot saved to {output_path}")
        else:
            plt.show()
        plt.close()
