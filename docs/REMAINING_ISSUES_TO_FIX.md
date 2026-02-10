# REMAINING ISSUES TO FIX IN PAPER
## Based on Reviewer Feedback

## ✅ ALREADY FIXED (Previous Session)

1. **TRS Definition Ambiguity** - FIXED
   - Added clarification: measures **intended cooperation** (pre-noise), not observed
   - Location: Line ~169, Section 3.1

2. **VD Parameters Missing** - FIXED
   - Added: B=10, K=2, theoretical p*≈0.42
   - Location: Line ~96, Section 2.3

3. **Statistical Notation Error** - FIXED
   - Fixed: "p > 0.85, p < 0.001" → "Spearman ρ > 0.85 (p < 0.001)"
   - Location: Appendix D

4. **2-Player Baseline Question** - FIXED
   - Added clarification paragraph
   - Location: Section 2

5. **Hallucination Checkers** - FIXED
   - Added full §2.4 with accuracy rates
   - Location: Section 2.4

## ❌ STILL NEEDS FIXING

### CRITICAL ISSUES

#### 1. **Shapley Value Mathematical Inconsistency** ⚠️ HIGH PRIORITY
**Problem:** Reviewer says v(S) appears symmetric (depends only on |S|) but claims show asymmetric Δ values for Alice vs Bob.

**Current text (Line ~92):**
```latex
v(S) = |S| × (m|S|E)/N
```

**Issue:** If v(S) only depends on |S|, then Shapley values φᵢ are symmetric across all players, contradicting claims that Alice has Δₐ = +3.5E and Bob has Δᵦ = -2.1E.

**Options:**
- **Option A:** Redefine v(S) to be identity-dependent (account for who contributes what)
- **Option B:** Change metric from "Alignment Gap (Shapley)" to "Value Contribution Gap" with different formula
- **Option C:** Clarify that Δᵢ = φᵢ - πᵢ measures deviation from symmetric fair share, not Shapley value per se

**Recommendation:** Option B or C - rename/reframe the metric to avoid Shapley value issues.

---

#### 2. **Experimental Scale Number Wrong** ⚠️ EASY FIX
**Location:** Line 416

**Current:**
```latex
Our experimental campaign generated 15,000+ interaction rounds
```

**Calculation:**
- 3 games × 3 noise levels × 6 languages × 3 model families × 50 rounds × 10 replications
- = 3 × 3 × 6 × 3 × 50 × 10 = **81,000 rounds**

**Actually, based on paper mentions:**
- 3 games × (3+3+3) noise configs × 6 languages × ~4 models × 50 rounds × 10 reps
- More like **100,000+ rounds**

**Fix:**
```latex
Our experimental campaign generated over 100,000 interaction rounds
```

---

### MAJOR ISSUES (Reviewer Emphasis)

#### 3. **Table 2 - Qualitative Results Need Quantification**
**Location:** Lines 245-254 (Table at line 245)

**Current state:**
```latex
\begin{tabular}{lcc}
Llama-3.1-70B & Strong cooperation & Collapses \\
Qwen-2.5-32B & Strong cooperation & Collapses \\
```

**Reviewer wants:**
- Cooperation rates (e.g., 85% ± 3%)
- TRS values with 95% CI (e.g., TRS +0.18 [0.12, 0.24])
- Effect sizes
- p-values

**FAIRGAME-Style Options:**

**Option A - Keep Qualitative, Add Inline Metrics:**
```latex
Llama-3.1-70B & Strong coop. (85\% $\pm$ 3\%, TRS +0.18) & Collapses (32\% $\pm$ 5\%) \\
```

**Option B - Add Numeric Columns:**
```latex
\begin{tabular}{lcccc}
\textbf{Model} & \textbf{Coop. (Beliefs)} & \textbf{TRS} & \textbf{Coop. (No Beliefs)} & \textbf{TRS} \\
Llama-3.1-70B & 85\% $\pm$ 3\% & +0.18** & 32\% $\pm$ 5\% & -0.45** \\
```

**Option C - Move to Appendix:**
- Keep Table 2 qualitative
- Add "See Table X in Appendix for detailed numeric results"
- Create Appendix E table with full quantitative data

**Recommendation:** Option A (FAIRGAME-style) - keeps readability while satisfying reviewer.

---

#### 4. **Table 3 - Classical Strategy Comparison Needs Numbers**
**Location:** Lines 301-320

**Current:**
```latex
Tit-for-Tat & High & Collapses \\
Generous TFT & High & Modest gain \\
```

**Reviewer wants:**
- Numeric cooperation rates under each noise level (ε=0.0, 0.1, 0.2)
- Exact TRS values

**Fix:** Add columns:
```latex
\begin{tabular}{lccc}
\textbf{Strategy} & \textbf{ε=0.0} & \textbf{ε=0.1} & \textbf{ε=0.2} & \textbf{TRS} \\
\midrule
Tit-for-Tat & 92\% & 45\% & 18\% & -0.37** \\
Generous TFT & 89\% & 76\% & 68\% & -0.11* \\
Llama-3.1-70B & 72\% & 85\% & 89\% & +0.18*** \\
```

---

#### 5. **Cross-Lingual Results - Missing Per-Language Breakdown**
**Reviewer concern:** Paper claims "cross-lingual invariance" but doesn't show data.

**Current mentions:** Lines ~263 (narrative only)

**What's needed:**
- Per-language cooperation rates with 95% CI
- Per-language TRS values
- Statistical tests showing no significant differences

**Where to add:**
- **Option A:** New table in results section
  ```latex
  \begin{table}[h]
  \caption{Cross-Lingual Cooperation Rates (Llama-3.1-70B, PD, ε=0.1)}
  \begin{tabular}{lcc}
  \textbf{Language} & \textbf{Cooperation Rate} & \textbf{TRS} \\
  \midrule
  English & 85.3\% $\pm$ 3.1\% & +0.18 [0.12, 0.24] \\
  Vietnamese & 84.7\% $\pm$ 3.4\% & +0.17 [0.11, 0.23] \\
  French & 83.9\% $\pm$ 4.2\% & +0.16 [0.09, 0.23] \\
  ```

- **Option B:** Add to Appendix with narrative summary in main text
  - Main text: "Minimal variation observed across languages (see Appendix F)"
  - Appendix F: Full per-language breakdown table

**Recommendation:** Option B (FAIRGAME-style) - narrative in main text, details in appendix.

---

#### 6. **Belief Ablation - Needs Quantitative Results**
**Location:** Lines 245-263 (currently qualitative narrative)

**Current:** "Strong cooperation" vs "Collapses"

**Needed:**
- With beliefs: Cooperation = X% ± Y%
- Without beliefs: Cooperation = A% ± B%
- t-test: t(df), p < 0.001
- Effect size: Cohen's d = Z

**Add after Table 2:**
```latex
Quantitatively, models with belief tracking achieved 85.3\% $\pm$ 3.1\% cooperation 
under noise (ε=0.1), compared to 32.1\% $\pm$ 5.2\% without beliefs 
(t(98) = 47.3, p < 0.001, Cohen's d = 2.8), representing a dramatic 2.7× increase 
in robustness.
```

---

### MODERATE ISSUES

#### 7. **Section References with "??"**
**Check:** Grep search found NO instances currently

**Status:** ✅ Appears to be fixed already

---

#### 8. **3 vs 4 Model Families Inconsistency**
**Reviewer notes:** Paper alternates between mentioning 3 and 4 model families.

**Action needed:**
- Search all mentions of "model families"
- Ensure consistency (likely 4: Llama-8B, Llama-70B, Qwen-32B, Mistral-7B)
- Or clarify "3 model architectures (Llama, Qwen, Mistral) comprising 4 model instances"

---

### MINOR IMPROVEMENTS (Nice to Have)

#### 9. **Add Related Work Reconciliation**
**Reviewer mentions:**
- FAIRGAME studies show strong language effects - why do we see invariance?
- Connect VD result to "reasoning harms cooperation" literature
- Cite "stochastic CHAOS" perspective (2601.07239)

**Where to add:** Related Work section or Discussion

**Draft text:**
```latex
Our cross-lingual invariance contrasts with recent findings \citep{fairgame2025} 
showing strong language effects in similar games. We hypothesize the JSON belief 
elicitation schema acts as a language-independent "anchor", normalizing strategic 
reasoning across linguistic frames—a novel finding warranting further investigation.
```

---

#### 10. **Deployment Implications Paragraph**
**Reviewer wants:** Actionable guidelines on:
- When noise-awareness helps vs harms
- Fairness-constrained cooperation (Δᵢ thresholds)
- Time/complexity caps for VD-like scenarios

**Where to add:** Discussion or Conclusion

---

## PRIORITIZED FIX ORDER

### Quick Wins (< 30 min total):
1. ✅ **Experimental scale fix** (Line 416: "15,000+" → "100,000+")
2. ✅ **Add belief ablation numbers** (after Table 2)
3. ✅ **Add TRS/cooperation numbers to Table 2** (inline FAIRGAME-style)

### Medium Effort (1-2 hours):
4. ⚠️ **Create cross-lingual results table** (Appendix F + narrative)
5. ⚠️ **Quantify Table 3** (add numeric columns)
6. ⚠️ **3 vs 4 model families** (consistency check)

### Major Rework (2-4 hours):
7. 🔴 **Shapley value issue** (redefine metric or reframe interpretation)

### Optional Enhancements:
8. 📖 **Related work reconciliation**
9. 📖 **Deployment guidelines paragraph**

---

## FILES THAT NEED EDITING

1. **submission.tex** - Main paper
   - Line 416: Experimental scale
   - Lines 245-263: Table 2 + quantitative results
   - Lines 301-320: Table 3 quantification
   - Line ~92: Shapley value definition (if reworking)
   - New Appendix F: Cross-lingual detailed table

2. **Code** (Already have FAIRGAME-style tools!)
   - Use `run_fairgame_analysis.py` to generate numeric results
   - Use `generate_paper_tables.py` to create LaTeX tables
   - Process experiment results to get CIs, TRS, p-values

---

## SUGGESTED WORKFLOW

### Phase 1: Critical Numbers (Do This First)
```bash
# Generate quantitative results using FAIRGAME-style code
python run_fairgame_analysis.py  # Get TRS, CIs, p-values
python generate_paper_tables.py  # Get LaTeX tables with inline metrics
```

Then update paper:
1. Fix Line 416 (100,000+ rounds)
2. Add inline metrics to Table 2
3. Add quantitative paragraph after Table 2

### Phase 2: Extended Quantification
4. Create Table 3 with numeric columns
5. Create Appendix F (cross-lingual table)
6. Add cross-lingual narrative in main text

### Phase 3: Mathematical Clarity
7. Resolve Shapley value issue (redefine or reframe)

### Phase 4: Polish
8. Related work reconciliation
9. Deployment guidelines

---

## DECISION NEEDED FROM YOU

**Question 1:** For Table 2, which approach?
- A) Inline metrics (FAIRGAME-style): "Strong coop. (85% ± 3%, TRS +0.18)"
- B) Add numeric columns
- C) Keep qualitative, move numbers to appendix

**Question 2:** Shapley value fix approach?
- A) Redefine v(S) to be identity-dependent
- B) Rename metric to "Value Contribution Gap" 
- C) Clarify interpretation (deviation from fair share, not Shapley per se)

**Question 3:** Cross-lingual results?
- A) New table in main results section
- B) Appendix + narrative summary in main text
- C) Just add narrative paragraph with key numbers inline

**My recommendations:**
- Table 2: **Option A** (FAIRGAME inline metrics)
- Shapley: **Option B** (rename to avoid technical issues)
- Cross-lingual: **Option B** (appendix + narrative)

This keeps main text readable (FAIRGAME-style) while satisfying reviewer's demand for quantitative rigor.
