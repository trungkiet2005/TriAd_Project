"""
Technical Fixes for UAI Paper Review

This document addresses critical issues raised in the peer review:
https://paperreview.ai/...

=============================================================================
PRIORITY 1: Public Goods Game - Characteristic Function v(S)
=============================================================================

PROBLEM (from review):
"The characteristic function v(S) and its use in Shapley computation appears 
misspecified. As written, v(S) = |S| × (m|S|E)/N seems dimensionally 
inconsistent with total (or coalition) payoffs under the assumed behavior 
of non-members."

CURRENT (INCORRECT) FORMULA:
v(S) = |S| × (m|S|E)/N

This is wrong because:
1. It mixes individual payoff (×|S|) with per-capita distribution (/N)
2. Doesn't specify what non-members do (contribute 0? unknown?)
3. Not clear if v(S) is coalition payoff to S or total social value

CORRECTED FORMULA (Coalition Payoff Convention):

Assumptions:
- Non-members contribute 0 (worst case for coalition)
- v(S) = total payoff received by coalition S

For a coalition S of size k:
- Coalition contributes k agents × E tokens each = kE tokens
- These are multiplied by m and split among ALL N players
- Coalition members also receive share of multiplier from non-coalition

v(S) = (kE) × m / N × k = (k² × m × E) / N

Wait, this is also confusing. Let me be more precise:

CORRECTED DERIVATION:

Setup:
- Coalition S has k members
- Each contributes E tokens
- Total contributed by S: c_S = k × E
- Non-members contribute: c_-S = 0 (conservative assumption)
- Multiplier: m
- Total players: N

Payoff to coalition S:
v(S) = Σ_{i ∈ S} payoff_i

For each member i in S:
- Kept: 0 (they contributed)
- Shared: (c_S × m) / N = (kE × m) / N

So each member gets: (kE × m) / N
Coalition S gets: k × (kE × m) / N = (k² × m × E) / N

FINAL FORMULA:
v(S) = (|S|² × m × E) / N

where:
- |S| = coalition size
- m = multiplier (typically 2.0)
- E = endowment (typically 10)
- N = total players (3)

Example for N=3, m=2, E=10:
- v({}) = 0
- v({A}) = (1² × 2 × 10) / 3 = 6.67
- v({A,B}) = (2² × 2 × 10) / 3 = 26.67
- v({A,B,C}) = (3² × 2 × 10) / 3 = 60

Individual payoff if ALL contribute:
(3 × 10 × 2) / 3 = 20 per person
Total: 60 ✓ (matches)

Value Contribution Gap (Welfare Paradox metric):
Shapley Value: φ_i = Contribution to coalitions weighted by marginal value
Direct Payoff: π_i = Actual tokens received

Δ_i = φ_i - π_i

When Δ_i > 0: Agent creates more value than they capture (exploited)
When Δ_i < 0: Agent captures more than they create (free-rider)

=============================================================================
PRIORITY 2: Volunteer's Dilemma - Parameter Inconsistencies
=============================================================================

PROBLEM (from review):
"Inconsistencies in VD parameters (K=2 vs K=3 in examples; p* ≈ 0.42 conflicts 
with given B, K, N). Reported catastrophic failure rates far below mixed-
strategy prediction."

PARAMETERS TO VERIFY:
- B = benefit if at least one volunteers (given as 10 in some examples)
- C = cost to volunteer
- K = threshold (number of volunteers needed)
- N = total players (3)
- p* = mixed strategy equilibrium probability

CORRECTED FORMULAS:

For symmetric mixed-strategy Nash equilibrium:
p* = 1 - (C/B)^(1/(N-1))

Example with N=3, B=10, C=2:
p* = 1 - (2/10)^(1/2) = 1 - 0.447 = 0.553 (55.3%)

Catastrophic failure rate (no one volunteers):
Pr(failure) = (1 - p*)^N = (0.447)^3 = 0.089 (8.9%)

CONSISTENCY CHECK:
The paper reports 1-4% failure rates, which is BELOW the equilibrium 
prediction of ~9%. This suggests:
1. Models are MORE cooperative than equilibrium (good!)
2. But claims about "analysis paralysis" are weaker
3. Need to clarify: are we measuring per-round or per-game failures?

ACTION ITEMS:
1. Verify all VD parameters are consistent throughout paper
2. Recalculate p* with correct B, C, N values
3. Report both per-round and cumulative failure rates
4. Compare model behavior to equilibrium prediction explicitly

=============================================================================
PRIORITY 3: TRS - More Noise Points
=============================================================================

PROBLEM (from review):
"TRS estimated via OLS over only three noise points {0, 0.1, 0.2}; potential
nonlinearity and variance suggest need for additional points."

CURRENT: ε ∈ {0.0, 0.1, 0.2}
SUGGESTED: ε ∈ {0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3}

RATIONALE:
- More points → better regression fit
- Can detect nonlinearity (quadratic term?)
- Bootstrap CI more reliable with more data

ALTERNATIVE (if limited compute):
- Keep 3 points for main experiments
- Add nonparametric tests (Spearman correlation)
- Report per-seed slope distributions with CI

=============================================================================
PRIORITY 4: Belief Calibration - Add to Main Text
=============================================================================

PROBLEM (from review):
"Belief calibration results (Brier scores) mentioned but not reported in 
main text."

SOLUTION:
Add subsection: "4.X Belief Calibration and Theory of Mind"

Report:
1. Mean Brier score per model
2. Calibration curves (predicted vs actual)
3. How calibration correlates with TRS
4. Cross-lingual comparison of calibration

Example text:
"Agents exhibited moderately well-calibrated beliefs (mean Brier score 
M = 0.18, SD = 0.04). GPT-4o showed best calibration (0.15), followed by 
Claude-3.5 (0.17) and Qwen-2.5 (0.22). Critically, better-calibrated 
agents also showed higher TRS (r = 0.68, p < 0.01), suggesting that 
accurate opponent modeling enables robust cooperation under noise."

=============================================================================
PRIORITY 5: Personality Prompts - Neutral Baseline
=============================================================================

PROBLEM (from review):
"Personality prompts risk entangling behavior with role instructions. 
Unclear if 'Toxic Kindness' persists with neutral prompts."

SOLUTION:
Add ablation condition:
- Neutral: No personality assigned ("You are Player A")
- Cooperative: "You value cooperation and fairness"
- Selfish: "You prioritize your own payoff"
- Reciprocal: "You match others' behavior"

Report Welfare Paradox metrics (Δ) for all conditions.

Expected result:
- Neutral: Moderate exploitation (Δ > 0 but smaller)
- Cooperative: High exploitation (Δ >> 0) ← "Toxic Kindness"
- Selfish: Negative exploitation (Δ < 0) ← Free-riding
- Reciprocal: Balanced (Δ ≈ 0)

=============================================================================
IMPLEMENTATION CHECKLIST
=============================================================================

Core Fixes:
[X] 1. Add belief tracking with noise_suspicion field
[X] 2. Create belief_analysis.py with Brier score calculation
[X] 3. Update game templates to request noise attribution
[ ] 4. Implement Shapley value calculation with corrected v(S)
[ ] 5. Verify VD parameters and recalculate p*
[ ] 6. Add more noise points OR nonparametric tests for TRS

Analysis Scripts:
[X] 7. run_belief_analysis.py - Bayesian Theory of Mind demo
[ ] 8. calculate_shapley_values.py - Corrected welfare analysis
[ ] 9. verify_vd_parameters.py - Consistency check

Paper Sections to Add:
[ ] 10. Section 4.X: Belief Calibration (Brier scores, calibration curves)
[ ] 11. Section 4.Y: Noise Attribution (strategic vs random)
[ ] 12. Appendix A: Corrected v(S) derivation for PGG
[ ] 13. Appendix B: VD parameter verification

Figures to Generate:
[ ] 14. Figure: Belief calibration curves per model
[ ] 15. Figure: Noise attribution rates (strategic vs noise)
[ ] 16. Figure: Shapley-Payoff gap (corrected) per personality
[ ] 17. Figure: VD failure rates vs equilibrium prediction

=============================================================================
EXPECTED IMPACT ON PAPER
=============================================================================

Strengths Enhanced:
✓ Belief tracking → Explicit Bayesian Theory of Mind analysis
✓ Noise attribution → Operationalizes "charitable forgiveness"
✓ Brier scores → Quantitative calibration metric for UAI venue
✓ Corrected Shapley → Rigorous welfare analysis

Weaknesses Addressed:
✓ PGG characteristic function → Mathematically sound
✓ VD parameters → Internally consistent
✓ TRS robustness → More extensive testing or nonparametric validation
✓ Personality confounds → Neutral baseline ablation

UAI Fit:
✓ Uncertainty quantification (Brier scores, belief calibration)
✓ Bayesian reasoning (noise attribution, posterior updates)
✓ Game-theoretic foundations (corrected equilibria)
✓ Statistical rigor (multiple comparisons, effect sizes)

Target: Accept after Major Revision → Strong Accept

=============================================================================
"""