# FAIRGAME-Style Analysis Guide

This guide explains how to generate **FAIRGAME-style** qualitative results with inline metrics, following the approach used in successful papers like the FAIRGAME paper.

## Philosophy

**FAIRGAME-style** focuses on:
- **Qualitative narratives** in main text (e.g., "High cooperation," "Collapses rapidly")
- **Inline metrics** in parentheses (e.g., "85% ± 3%, TRS +0.18")
- **Error bar plots** (95% CI) instead of dense numeric tables
- **Detailed numbers** moved to Appendix/Supplementary Material
- **Statistical significance** mentioned without overwhelming the reader

## Quick Start

### 1. Run FAIRGAME-Style Analysis

```bash
python run_fairgame_analysis.py
```

**Outputs:**
- Qualitative summary with inline metrics
- Cooperation rate plots with 95% CI error bars
- TRS (Trembling Robustness Score) analysis
- Statistical comparisons
- Detailed appendix table (CSV)

### 2. Generate Paper-Ready Tables

```bash
python generate_paper_tables.py
```

**Outputs:**
- LaTeX table with qualitative descriptions
- Cross-lingual results narrative paragraph
- Condition comparison narrative
- Both versions: with/without inline metrics

## Key Features

### TRS (Trembling Robustness Score)

Measures cooperation resilience under noise:
- **Positive TRS (+)**: Cooperation increases/maintains under noise
- **Negative TRS (−)**: Cooperation declines under noise
- **Calculation**: Linear regression slope of `cooperation_rate ~ noise_rate`

```python
from src.analysis.fairgame_analysis import FAIRGAMEAnalyzer

analyzer = FAIRGAMEAnalyzer()
trs_result = analyzer.calculate_trs(df, language='en')
print(f"TRS = {trs_result['slope']:+.3f} (p = {trs_result['p_value']:.4f})")
```

### Confidence Intervals (Bootstrap)

All plots include **95% CI** error bars calculated via bootstrap resampling (1000 iterations):

```python
mean, lower, upper = analyzer.calculate_ci_bootstrap(data, ci=0.95)
print(f"{mean*100:.1f}% ± {(upper-lower)/2*100:.1f}%")
```

### Qualitative Descriptions

Automatic conversion of numeric results to narrative descriptions:

| Cooperation Rate | Description |
|------------------|-------------|
| ≥ 0.80 | High cooperation |
| ≥ 0.65 | Strong cooperation |
| ≥ 0.50 | Moderate cooperation |
| ≥ 0.35 | Weak cooperation |
| ≥ 0.20 | Low cooperation |
| < 0.20 | Collapses rapidly |

| TRS Value | Description |
|-----------|-------------|
| ≥ +0.15 | Strong robustness |
| ≥ +0.05 | Moderate robustness |
| ≥ −0.05 | Stable under noise |
| ≥ −0.20 | Moderate decline |
| < −0.20 | Poor robustness |

## Usage Examples

### Example 1: Generate Summary Paragraph

```python
from src.analysis.fairgame_analysis import FAIRGAMEAnalyzer
from src.analysis.data_loader import DataLoader

df = DataLoader.load_experiment_results("resources/results/results_pd3_mock.csv")
analyzer = FAIRGAMEAnalyzer()

summary = analyzer.generate_qualitative_summary(df, group_by='language')
print(summary)
```

**Output:**
```
English agents showed high cooperation (72.3% ± 3.1%) with strong robustness 
under noise (TRS +0.18, p<0.001); Vietnamese agents showed moderate cooperation 
(58.4% ± 4.7%) with moderate decline under noise (TRS -0.12, p=0.023).
```

### Example 2: Create Error Bar Plot

```python
analyzer.plot_cooperation_with_ci(
    df,
    group_by='language',
    title="Intended Cooperation Rate by Language (95% CI)",
    output_path="figures/cooperation_by_language.png"
)
```

### Example 3: Generate Table 2 (Qualitative Model Comparison)

```python
from src.analysis.table_generator import QualitativeTableGenerator

table_gen = QualitativeTableGenerator()
table2 = table_gen.generate_model_comparison_table(
    df,
    group_by=['language', 'agent1NoiseRate'],
    show_metrics=True,  # Include numbers in parentheses
    output_latex="tables/table2_qualitative.tex"
)
```

**Output:**

| Language | Noise Rate | Description |
|----------|------------|-------------|
| en | 0.0 | High cooperation (85% ± 3%), strong robustness (TRS +0.18), high consistency |
| en | 0.2 | Moderate cooperation (67% ± 4%), moderate decline (TRS -0.12), moderate consistency |
| vi | 0.0 | Strong cooperation (72% ± 5%), moderate robustness (TRS +0.08), high variability |

### Example 4: Cross-Lingual Narrative

```python
narrative = table_gen.generate_language_comparison_narrative(df)
print(narrative)
```

**Output:**
```
Cooperation rates varied across languages, with English agents showing notably 
higher stability (TRS +0.18) compared to Vietnamese agents (TRS -0.12). French 
agents exhibited broader variability in outcomes, suggesting inconsistent 
strategic adaptation under noise. Overall, most languages demonstrated positive 
trembling robustness, indicating strategic compensation under noise perturbations.
```

### Example 5: Statistical Comparison

```python
comparison = analyzer.compare_conditions(
    df,
    condition_col='n_rounds_is_known',
    condition_a=True,
    condition_b=False
)

print(f"Known rounds: {comparison['mean_a']*100:.1f}%")
print(f"Unknown rounds: {comparison['mean_b']*100:.1f}%")
print(f"t = {comparison['t_statistic']:.3f}, p = {comparison['p_value']:.4f}")
print(f"Cohen's d = {comparison['effect_size']:.3f}")
```

## File Structure

```
src/analysis/
  ├── fairgame_analysis.py     # TRS, CI, plots, statistical tests
  ├── table_generator.py       # Qualitative tables and narratives
  ├── data_loader.py           # Load and parse CSV/JSON results
  └── visualizer.py            # Legacy plotting functions

run_fairgame_analysis.py       # Main analysis script
generate_paper_tables.py       # Paper-ready table generation
```

## Integration with Paper

### Main Text (Results Section)

Use **qualitative descriptions** with **inline metrics**:

```latex
\section{Results}

\subsection{Intended Cooperation Under Noise}

English agents demonstrated high cooperation (72.3\% $\pm$ 3.1\%) with 
strong robustness under noise (TRS +0.18, $p<0.001$), while Vietnamese 
agents exhibited moderate cooperation (58.4\% $\pm$ 4.7\%) with moderate 
decline (TRS -0.12, $p=0.023$). French agents showed broader variability, 
suggesting inconsistent strategic adaptation.
```

### Figures

Insert error bar plots with 95% CI:

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/cooperation_by_language.png}
  \caption{Intended cooperation rate by language with 95\% confidence intervals.}
  \label{fig:cooperation_language}
\end{figure}
```

### Tables (Qualitative)

Use generated LaTeX table:

```latex
\input{tables/table2_qualitative.tex}
```

### Appendix (Quantitative Details)

Move detailed numbers to appendix:

```latex
\section{Appendix E: Detailed Quantitative Results}

Table~\ref{tab:appendix_full} presents complete numerical results with 
95\% confidence intervals for all experimental conditions.

\input{tables/appendix_detailed_results.tex}
```

## FAIRGAME-Style vs Traditional

| Aspect | Traditional | FAIRGAME-Style |
|--------|-------------|----------------|
| Main text | Dense tables with numbers | Qualitative narratives |
| Metrics | Explicit in tables | Inline in parentheses |
| Figures | Scatter plots, heatmaps | Bar plots with error bars |
| Statistical tests | Detailed reporting | Brief mention (p-values) |
| Detailed numbers | Main text | Appendix/Supplementary |
| Readability | Technical | Story-telling |

## Best Practices

1. **Main Text**: Use qualitative descriptions, mention key metrics inline
2. **Figures**: Always include 95% CI error bars
3. **Tables**: Qualitative descriptions in main text, numbers in appendix
4. **Statistics**: Report significance (p-values), avoid overwhelming details
5. **TRS**: Always report when discussing noise robustness
6. **Narratives**: Tell a story, don't just list numbers

## Example Workflow

### Step 1: Run Experiments
```bash
python run_experiment_example.py
```

### Step 2: Generate FAIRGAME Analysis
```bash
python run_fairgame_analysis.py
```

### Step 3: Generate Paper Tables
```bash
python generate_paper_tables.py
```

### Step 4: Insert into Paper
- Copy narratives → Results section
- Insert LaTeX tables → Main text (Table 2)
- Include figures → Results section
- Add detailed table → Appendix

### Step 5: Verify
- ✓ Main text: Qualitative + inline metrics
- ✓ Figures: Error bars visible
- ✓ Tables: Readable descriptions
- ✓ Appendix: Complete numbers

## Troubleshooting

**Q: No plots showing?**
- Check `output_path` parameter
- Ensure `experiment_results/` directory exists

**Q: TRS calculation fails?**
- Need at least 2 different noise levels
- Check `noise_col` parameter matches CSV column name

**Q: LaTeX table not rendering?**
- Ensure `\usepackage{booktabs}` in preamble
- Check encoding: use UTF-8

**Q: CI too wide?**
- Increase sample size (more games)
- Check for outliers in data

## Advanced Features

### Custom Qualitative Thresholds

Modify thresholds in `table_generator.py`:

```python
def _descriptive_cooperation_level(self, coop_rate: float) -> str:
    if coop_rate >= 0.9:  # Custom threshold
        return "Exceptional cooperation"
    # ... rest of levels
```

### Multiple Grouping Variables

```python
table = table_gen.generate_model_comparison_table(
    df,
    group_by=['language', 'n_rounds_is_known', 'agent1NoiseRate']
)
```

### Export to Multiple Formats

```python
# CSV
table.to_csv("results.csv", index=False)

# LaTeX
table.to_latex("results.tex", index=False)

# Markdown
table.to_markdown("results.md", index=False)
```

## References

This approach follows the style demonstrated in:

**FAIRGAME: A Framework for AI Agents Bias Recognition using Game Theory**
- Qualitative descriptions in main text
- Error bar plots (95% CI)
- Minimal explicit numbers
- Supplementary material for details

---

For questions or issues, see README.md or open an issue.
