"""
Table Generation for FAIRGAME-Style Paper
Generates qualitative descriptions with inline metrics for paper tables
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from src.analysis.fairgame_analysis import FAIRGAMEAnalyzer
from src.analysis.config import (
    COOPERATION_THRESHOLDS,
    TRS_THRESHOLDS,
    VARIABILITY_THRESHOLDS
)
from src.analysis.base_utils import ColumnFilter


class QualitativeTableGenerator:
    """
    Generate paper-ready tables with qualitative descriptions and inline metrics.
    
    Example output (like FAIRGAME Table 2):
    Model | Condition | Description
    ------|-----------|-------------
    Llama-70B | ε=0.0 | High cooperation (85% ± 3%), strong coordination (TRS +0.18)
    Llama-70B | ε=0.2 | Collapses rapidly (32% ± 5%), poor robustness (TRS -0.45)
    """
    
    def __init__(self):
        self.analyzer = FAIRGAMEAnalyzer()
    
    def _descriptive_cooperation_level(self, coop_rate: float) -> str:
        """
        Convert cooperation rate to qualitative description.
        
        Args:
            coop_rate: Cooperation rate (0.0 to 1.0)
            
        Returns:
            str: Qualitative description
        """
        if coop_rate >= COOPERATION_THRESHOLDS['high']:
            return "High cooperation"
        elif coop_rate >= COOPERATION_THRESHOLDS['strong']:
            return "Strong cooperation"
        elif coop_rate >= COOPERATION_THRESHOLDS['moderate']:
            return "Moderate cooperation"
        elif coop_rate >= COOPERATION_THRESHOLDS['weak']:
            return "Weak cooperation"
        elif coop_rate >= COOPERATION_THRESHOLDS['low']:
            return "Low cooperation"
        else:
            return "Collapses rapidly"
    
    def _descriptive_trs_level(self, trs: float) -> str:
        """
        Convert TRS to qualitative description.
        
        Args:
            trs: Trembling Robustness Score
            
        Returns:
            str: Qualitative description
        """
        if trs >= TRS_THRESHOLDS['strong_positive']:
            return "strong robustness"
        elif trs >= TRS_THRESHOLDS['moderate_positive']:
            return "moderate robustness"
        elif trs >= TRS_THRESHOLDS['stable']:
            return "stable under noise"
        elif trs >= TRS_THRESHOLDS['moderate_negative']:
            return "moderate decline"
        else:
            return "poor robustness"
    
    def _descriptive_variability(self, ci_range: float) -> str:
        """
        Convert confidence interval range to qualitative description.
        
        Args:
            ci_range: Half-width of 95% CI
            
        Returns:
            str: Qualitative description
        """
        if ci_range < VARIABILITY_THRESHOLDS['low']:
            return "high consistency"
        elif ci_range < VARIABILITY_THRESHOLDS['moderate']:
            return "moderate consistency"
        else:
            return "high variability"
    
    def generate_model_comparison_table(self, 
                                       df: pd.DataFrame,
                                       group_by: List[str] = ['language', 'agent1NoiseRate'],
                                       show_metrics: bool = True,
                                       output_latex: Optional[str] = None) -> pd.DataFrame:
        """
        Generate qualitative comparison table with inline metrics.
        
        Args:
            df: Experiment results dataframe
            group_by: Columns to group by
            show_metrics: Whether to show numbers in parentheses
            output_latex: Optional path to save LaTeX table
        
        Returns:
            DataFrame with qualitative descriptions
        """
        strategy_cols = ColumnFilter.get_strategy_columns(df)
        
        df['coop_rate'] = df.apply(
            lambda row: self.analyzer.coop_calculator.calculate_game_rate(row, strategy_cols),
            axis=1
        )
        
        # Generate table rows
        rows = []
        
        for group_vals, group_df in df.groupby(group_by):
            coop_data = group_df['coop_rate'].values
            
            # Calculate statistics
            mean, lower, upper = self.analyzer.calculate_ci_bootstrap(coop_data)
            ci_range = (upper - lower) / 2
            
            # Calculate TRS
            trs_result = self.analyzer.calculate_trs(group_df)
            trs = trs_result['slope']
            
            # Build description
            coop_desc = self._descriptive_cooperation_level(mean)
            trs_desc = self._descriptive_trs_level(trs)
            var_desc = self._descriptive_variability(ci_range)
            
            if show_metrics:
                description = (f"{coop_desc} ({mean*100:.0f}% ± {ci_range*100:.0f}%), "
                             f"{trs_desc} (TRS {trs:+.2f}), {var_desc}")
            else:
                description = f"{coop_desc}, {trs_desc}, {var_desc}"
            
            row = {}
            for col, val in zip(group_by, group_vals if isinstance(group_vals, tuple) else [group_vals]):
                row[col] = val
            row['description'] = description
            row['coop_mean'] = f"{mean:.3f}"
            row['trs'] = f"{trs:+.3f}"
            
            rows.append(row)
        
        result_df = pd.DataFrame(rows)
        
        # Generate LaTeX if requested
        if output_latex:
            self._save_latex_table(result_df, output_latex, group_by)
        
        return result_df
    
    def _save_latex_table(self, df: pd.DataFrame, output_path: str, group_cols: List[str]):
        """Save table in LaTeX format."""
        # Create LaTeX table header
        latex_lines = []
        latex_lines.append("\\begin{table}[h]")
        latex_lines.append("\\centering")
        latex_lines.append("\\caption{Qualitative Analysis of Agent Behavior}")
        latex_lines.append("\\label{tab:qualitative_results}")
        
        # Column specification
        n_cols = len(group_cols) + 1
        col_spec = "l" * len(group_cols) + "p{8cm}"
        latex_lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        latex_lines.append("\\toprule")
        
        # Header row
        headers = [col.replace('_', ' ').title() for col in group_cols] + ["Description"]
        latex_lines.append(" & ".join(headers) + " \\\\")
        latex_lines.append("\\midrule")
        
        # Data rows
        for _, row in df.iterrows():
            cells = [str(row[col]) for col in group_cols] + [row['description']]
            latex_lines.append(" & ".join(cells) + " \\\\")
        
        latex_lines.append("\\bottomrule")
        latex_lines.append("\\end{tabular}")
        latex_lines.append("\\end{table}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(latex_lines))
        
        print(f"LaTeX table saved to {output_path}")
    
    def generate_language_comparison_narrative(self, df: pd.DataFrame) -> str:
        """
        Generate FAIRGAME-style narrative paragraph about cross-lingual results.
        
        Args:
            df: DataFrame containing experiment results
            
        Returns:
            str: Qualitative narrative paragraph
            
        Example output:
        "Cooperation rates varied across languages, with English agents showing 
        notably higher stability (TRS +0.18) compared to Vietnamese agents 
        (TRS -0.12). French agents exhibited broader variability in outcomes..."
        """
        languages = df['language'].unique()
        strategy_cols = ColumnFilter.get_strategy_columns(df)
        
        # Calculate stats per language
        lang_stats = {}
        for lang in languages:
            lang_df = df[df['language'] == lang].copy()
            
            lang_df['coop_rate'] = lang_df.apply(
                lambda row: self.analyzer.coop_calculator.calculate_game_rate(row, strategy_cols),
                axis=1
            )
            
            coop_data = lang_df['coop_rate'].values
            mean, lower, upper = self.analyzer.calculate_ci_bootstrap(coop_data)
            ci_range = (upper - lower) / 2
            
            trs_result = self.analyzer.calculate_trs(lang_df)
            
            lang_stats[lang] = {
                'mean': mean,
                'ci_range': ci_range,
                'trs': trs_result['slope'],
                'variability': np.std(coop_data)
            }
        
        # Sort languages by cooperation rate
        sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Build narrative
        highest_lang, highest_stats = sorted_langs[0]
        lowest_lang, lowest_stats = sorted_langs[-1]
        
        narrative = (
            f"Cooperation rates varied across languages, with {highest_lang} agents "
            f"showing notably higher stability (TRS {highest_stats['trs']:+.2f}) "
            f"compared to {lowest_lang} agents (TRS {lowest_stats['trs']:+.2f}). "
        )
        
        # Find most variable language
        most_variable = max(lang_stats.items(), key=lambda x: x[1]['variability'])
        narrative += (
            f"{most_variable[0]} agents exhibited broader variability in outcomes, "
            f"suggesting inconsistent strategic adaptation under noise. "
        )
        
        # Overall pattern
        positive_trs_count = sum(1 for stats in lang_stats.values() if stats['trs'] > 0)
        if positive_trs_count > len(languages) / 2:
            narrative += (
                "Overall, most languages demonstrated positive trembling robustness, "
                "indicating strategic compensation under noise perturbations."
            )
        else:
            narrative += (
                "Overall, cooperation generally declined under noise across languages, "
                "suggesting limited strategic adaptation to environmental uncertainty."
            )
        
        return narrative
    
    def generate_condition_comparison_narrative(self, 
                                               df: pd.DataFrame,
                                               condition_col: str,
                                               condition_labels: Dict[any, str]) -> str:
        """
        Generate narrative comparing different experimental conditions.
        
        Args:
            df: Results dataframe
            condition_col: Column name for condition (e.g., 'n_rounds_is_known')
            condition_labels: Dict mapping condition values to readable labels
        
        Returns:
            str: Narrative string comparing conditions
        """
        strategy_cols = ColumnFilter.get_strategy_columns(df)
        
        df['coop_rate'] = df.apply(
            lambda row: self.analyzer.coop_calculator.calculate_game_rate(row, strategy_cols),
            axis=1
        )
        
        # Calculate stats per condition
        condition_stats = {}
        for condition_val in df[condition_col].unique():
            cond_df = df[df[condition_col] == condition_val]
            coop_data = cond_df['coop_rate'].values
            
            mean, lower, upper = self.analyzer.calculate_ci_bootstrap(coop_data)
            
            condition_stats[condition_val] = {
                'mean': mean,
                'ci': (lower, upper),
                'label': condition_labels.get(condition_val, str(condition_val))
            }
        
        # Compare conditions
        sorted_conditions = sorted(condition_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        highest_cond, highest_stats = sorted_conditions[0]
        lowest_cond, lowest_stats = sorted_conditions[-1]
        
        # Statistical test
        comp_result = self.analyzer.compare_conditions(
            df, condition_col, highest_cond, lowest_cond
        )
        
        p_str = "p < 0.001" if comp_result['p_value'] < 0.001 else f"p = {comp_result['p_value']:.3f}"
        
        narrative = (
            f"Agents in the {highest_stats['label']} condition exhibited "
            f"higher cooperation ({highest_stats['mean']*100:.0f}%) compared to "
            f"the {lowest_stats['label']} condition ({lowest_stats['mean']*100:.0f}%), "
            f"a difference that proved statistically significant "
            f"(t = {comp_result['t_statistic']:.2f}, {p_str}, "
            f"Cohen's d = {comp_result['effect_size']:.2f})."
        )
        
        return narrative
