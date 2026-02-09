"""
FAIRGAME-Style Analysis Module
Provides qualitative narratives with inline metrics, TRS calculation, and error bar visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class FAIRGAMEAnalyzer:
    """
    Analyzer for generating FAIRGAME-style results:
    - Qualitative descriptions with inline metrics
    - Error bar plots (95% CI)
    - TRS (Trembling Robustness Score) calculation
    - Statistical comparisons
    """
    
    def __init__(self):
        self.coop_keywords = [
            "Cooperate", "Volunteer", "Contribute",
            "Hợp tác", "Tình nguyện", "Đóng góp",
            "Collaborer", "Contribuer",
            "Offrirsi volontario", "Contribuire",
            "志愿", "贡献",
            "تطوع", "مساهمة"
        ]
        
    def calculate_cooperation_rate(self, strategies: List[str]) -> float:
        """Calculate cooperation rate from strategy list."""
        if not strategies or len(strategies) == 0:
            return 0.0
        coop_count = sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
        return coop_count / len(strategies)
    
    def calculate_trs(self, df: pd.DataFrame, noise_col: str = 'agent1NoiseRate', 
                     language: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate Trembling Robustness Score (TRS):
        Regression slope of cooperation_rate ~ noise_rate
        
        Returns:
            dict: {'slope': float, 'r_squared': float, 'p_value': float}
        """
        if language:
            df = df[df['language'] == language]
        
        # Calculate cooperation rate per game
        strategy_cols = [c for c in df.columns if 'strategies' in c and 'noise' not in c]
        
        def get_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0
        
        df['coop_rate'] = df.apply(get_game_coop_rate, axis=1)
        
        # Group by noise rate and get mean cooperation
        grouped = df.groupby(noise_col)['coop_rate'].mean().reset_index()
        
        if len(grouped) < 2:
            return {'slope': 0.0, 'r_squared': 0.0, 'p_value': 1.0}
        
        # Linear regression
        x = grouped[noise_col].values
        y = grouped['coop_rate'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_err': std_err
        }
    
    def calculate_ci_bootstrap(self, data: np.ndarray, n_iterations: int = 1000, 
                              ci: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate mean and confidence interval using bootstrap.
        
        Returns:
            tuple: (mean, lower_ci, upper_ci)
        """
        means = []
        for _ in range(n_iterations):
            sample = np.random.choice(data, size=len(data), replace=True)
            means.append(np.mean(sample))
        
        mean = np.mean(data)
        alpha = 1 - ci
        lower = np.percentile(means, alpha/2 * 100)
        upper = np.percentile(means, (1 - alpha/2) * 100)
        
        return mean, lower, upper
    
    def plot_cooperation_with_ci(self, df: pd.DataFrame, 
                                 group_by: str = 'language',
                                 noise_col: str = 'agent1NoiseRate',
                                 title: str = "Cooperation Rate by Condition",
                                 output_path: Optional[str] = None,
                                 figsize: Tuple[int, int] = (12, 6)):
        """
        Create bar plot with 95% CI error bars (FAIRGAME-style).
        """
        strategy_cols = [c for c in df.columns if 'strategies' in c and 'noise' not in c]
        
        def get_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0
        
        df['coop_rate'] = df.apply(get_game_coop_rate, axis=1)
        
        # Calculate stats per group
        groups = df[group_by].unique()
        means = []
        cis = []
        labels = []
        
        for group in groups:
            group_data = df[df[group_by] == group]['coop_rate'].values
            if len(group_data) > 0:
                mean, lower, upper = self.calculate_ci_bootstrap(group_data)
                means.append(mean)
                cis.append((mean - lower, upper - mean))
                labels.append(group)
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        x_pos = np.arange(len(labels))
        
        bars = ax.bar(x_pos, means, yerr=np.array(cis).T, capsize=5, 
                     alpha=0.8, color='steelblue', ecolor='black')
        
        ax.set_xlabel(group_by.replace('_', ' ').title(), fontsize=12)
        ax.set_ylabel('Cooperation Rate', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
        
        return means, cis, labels
    
    def plot_trs_comparison(self, df: pd.DataFrame, 
                           group_by: str = 'language',
                           noise_col: str = 'agent1NoiseRate',
                           title: str = "TRS Comparison Across Conditions",
                           output_path: Optional[str] = None,
                           figsize: Tuple[int, int] = (12, 6)):
        """
        Plot TRS (slope) values with confidence intervals.
        """
        groups = df[group_by].unique()
        trs_values = []
        errors = []
        labels = []
        
        for group in groups:
            group_df = df[df[group_by] == group]
            trs_result = self.calculate_trs(group_df, noise_col=noise_col)
            
            trs_values.append(trs_result['slope'])
            errors.append(1.96 * trs_result['std_err'])  # 95% CI
            labels.append(group)
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        x_pos = np.arange(len(labels))
        
        bars = ax.bar(x_pos, trs_values, yerr=errors, capsize=5,
                     alpha=0.8, color='coral', ecolor='black')
        
        # Color bars by positive/negative TRS
        for i, (bar, val) in enumerate(zip(bars, trs_values)):
            if val > 0:
                bar.set_color('lightgreen')
            else:
                bar.set_color('lightcoral')
        
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel(group_by.replace('_', ' ').title(), fontsize=12)
        ax.set_ylabel('TRS (Cooperation Slope vs Noise)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"TRS plot saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
        
        return trs_values, errors, labels
    
    def generate_qualitative_summary(self, df: pd.DataFrame, 
                                    group_by: str = 'language',
                                    noise_col: str = 'agent1NoiseRate') -> str:
        """
        Generate FAIRGAME-style qualitative summary with inline metrics.
        
        Example output:
        "English agents showed high cooperation (72% ± 3%) with strong robustness 
        (TRS +0.18, p<0.001), while Vietnamese agents exhibited lower cooperation 
        (58% ± 5%) with moderate decline under noise (TRS -0.12)."
        """
        strategy_cols = [c for c in df.columns if 'strategies' in c and 'noise' not in c]
        
        def get_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0
        
        df['coop_rate'] = df.apply(get_game_coop_rate, axis=1)
        
        summaries = []
        groups = sorted(df[group_by].unique())
        
        for group in groups:
            group_df = df[df[group_by] == group]
            coop_data = group_df['coop_rate'].values
            
            # Calculate cooperation stats
            mean, lower, upper = self.calculate_ci_bootstrap(coop_data)
            ci_range = (upper - lower) / 2
            
            # Calculate TRS
            trs_result = self.calculate_trs(group_df, noise_col=noise_col)
            trs_slope = trs_result['slope']
            trs_p = trs_result['p_value']
            
            # Generate description
            coop_level = "high" if mean > 0.7 else "moderate" if mean > 0.5 else "low"
            trs_desc = "strong robustness" if trs_slope > 0.1 else \
                      "moderate robustness" if trs_slope > 0 else \
                      "moderate decline" if trs_slope > -0.2 else "sharp decline"
            
            p_str = "p<0.001" if trs_p < 0.001 else f"p={trs_p:.3f}"
            
            summary = (f"{group} agents showed {coop_level} cooperation "
                      f"({mean*100:.1f}% ± {ci_range*100:.1f}%) with {trs_desc} under noise "
                      f"(TRS {trs_slope:+.3f}, {p_str})")
            
            summaries.append(summary)
        
        return "; ".join(summaries) + "."
    
    def create_appendix_table(self, df: pd.DataFrame,
                             group_by: List[str] = ['language', 'agent1NoiseRate'],
                             output_csv: Optional[str] = None) -> pd.DataFrame:
        """
        Create detailed quantitative table for appendix.
        """
        strategy_cols = [c for c in df.columns if 'strategies' in c and 'noise' not in c]
        score_cols = [c for c in df.columns if 'scores' in c and 'noise' not in c]
        
        def get_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0
        
        def get_total_score(row):
            total = 0
            for col in score_cols:
                scores = row[col]
                if isinstance(scores, list):
                    total += sum(scores)
            return total
        
        df['coop_rate'] = df.apply(get_game_coop_rate, axis=1)
        df['total_score'] = df.apply(get_total_score, axis=1)
        
        # Group and calculate statistics
        results = []
        
        for group_vals, group_df in df.groupby(group_by):
            coop_data = group_df['coop_rate'].values
            score_data = group_df['total_score'].values
            
            coop_mean, coop_lower, coop_upper = self.calculate_ci_bootstrap(coop_data)
            score_mean, score_lower, score_upper = self.calculate_ci_bootstrap(score_data)
            
            row = {}
            for col, val in zip(group_by, group_vals if isinstance(group_vals, tuple) else [group_vals]):
                row[col] = val
            
            row['cooperation_rate'] = f"{coop_mean:.3f}"
            row['cooperation_95ci'] = f"[{coop_lower:.3f}, {coop_upper:.3f}]"
            row['avg_score'] = f"{score_mean:.1f}"
            row['score_95ci'] = f"[{score_lower:.1f}, {score_upper:.1f}]"
            row['n_games'] = len(group_df)
            
            results.append(row)
        
        result_df = pd.DataFrame(results)
        
        if output_csv:
            result_df.to_csv(output_csv, index=False)
            print(f"Appendix table saved to {output_csv}")
        
        return result_df
    
    def compare_conditions(self, df: pd.DataFrame, 
                          condition_col: str,
                          condition_a: str,
                          condition_b: str) -> Dict[str, any]:
        """
        Statistical comparison between two conditions.
        
        Returns:
            dict: {'t_statistic': float, 'p_value': float, 'effect_size': float, 
                   'mean_a': float, 'mean_b': float}
        """
        strategy_cols = [c for c in df.columns if 'strategies' in c and 'noise' not in c]
        
        def get_game_coop_rate(row):
            total_actions = 0
            coop_actions = 0
            for col in strategy_cols:
                strategies = row[col]
                if isinstance(strategies, list):
                    total_actions += len(strategies)
                    coop_actions += sum(1 for s in strategies if any(k in str(s) for k in self.coop_keywords))
            return coop_actions / total_actions if total_actions > 0 else 0
        
        df['coop_rate'] = df.apply(get_game_coop_rate, axis=1)
        
        data_a = df[df[condition_col] == condition_a]['coop_rate'].values
        data_b = df[df[condition_col] == condition_b]['coop_rate'].values
        
        # T-test
        t_stat, p_value = stats.ttest_ind(data_a, data_b)
        
        # Cohen's d effect size
        pooled_std = np.sqrt((np.std(data_a)**2 + np.std(data_b)**2) / 2)
        effect_size = (np.mean(data_a) - np.mean(data_b)) / pooled_std if pooled_std > 0 else 0
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size,
            'mean_a': np.mean(data_a),
            'mean_b': np.mean(data_b),
            'condition_a': condition_a,
            'condition_b': condition_b
        }
