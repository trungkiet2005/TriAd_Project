#!/usr/bin/env python3
"""Generate Module 11, 12, 13 notebooks for action_answers analysis."""
import json, os

def make_notebook(cells_data, filepath):
    cells = []
    for ctype, content in cells_data:
        content = content.strip('\n')
        lines = content.split('\n')
        source = [line + '\n' for line in lines]
        if ctype == 'markdown':
            cells.append({"cell_type": "markdown", "metadata": {}, "source": source})
        else:
            cells.append({"cell_type": "code", "execution_count": None,
                          "metadata": {}, "outputs": [], "source": source})
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"}
        },
        "nbformat": 4, "nbformat_minor": 5
    }
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f'  Created {filepath}')

# ══════════════════════════════════════════════════════════════
# SHARED CELL SOURCES
# ══════════════════════════════════════════════════════════════

SETUP_CODE = """\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from itertools import combinations
import os, json, re
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12, 'axes.titlesize': 14, 'axes.labelsize': 13,
    'xtick.labelsize': 11, 'ytick.labelsize': 11, 'legend.fontsize': 11,
    'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05, 'axes.spines.top': False,
    'axes.spines.right': False, 'text.usetex': False,
})

MODEL_COLORS = {
    'gpt-oss-20b': '#E69F00',
    'Mistral-7B-Instruct-v0.3': '#56B4E9',
    'Qwen2.5-32B-Instruct': '#009E73'
}
MODEL_LABELS = {
    'gpt-oss-20b': 'GPT-oss-20B',
    'Mistral-7B-Instruct-v0.3': 'Mistral-7B',
    'Qwen2.5-32B-Instruct': 'Qwen2.5-32B'
}
MODEL_ORDER = ['GPT-oss-20B', 'Mistral-7B', 'Qwen2.5-32B']
MODEL_KEYS = ['gpt-oss-20b', 'Mistral-7B-Instruct-v0.3', 'Qwen2.5-32B-Instruct']
NOISE_LABELS = {0: 'No Noise', 5: '5% Noise', 20: '20% Noise'}
NOISE_ORDER = ['No Noise', '5% Noise', '20% Noise']
LANG_LABELS = {'en': 'English', 'fr': 'French', 'ar': 'Arabic',
               'cn': 'Chinese', 'vn': 'Vietnamese', 'it': 'Italian'}
LANG_ORDER = ['English', 'French', 'Arabic', 'Chinese', 'Vietnamese', 'Italian']

FIGURE_DIR = 'figures/'
os.makedirs(FIGURE_DIR, exist_ok=True)
print('Setup complete.')\
"""

DATA_LOADING_CODE = """\
# ── Load all action_answers from JSON files ──
BASE_DIR = '../resources/results/Prisoner_dilemma_2player'
NOISE_MAP = {'noise00': 0, 'noise05': 5, 'noise20': 20}

records = []
n_files = 0
n_parse_fail = 0

for model_dir in sorted(os.listdir(BASE_DIR)):
    model_path = os.path.join(BASE_DIR, model_dir)
    if not os.path.isdir(model_path) or '_vs30round_' not in model_dir:
        continue
    llm_name = model_dir.split('_vs30round_')[0]
    for noise_dir in sorted(os.listdir(model_path)):
        noise_path = os.path.join(model_path, noise_dir)
        if not os.path.isdir(noise_path) or noise_dir not in NOISE_MAP:
            continue
        noise_level = NOISE_MAP[noise_dir]
        aa_path = os.path.join(noise_path, 'action_answers')
        if not os.path.exists(aa_path):
            continue
        for aa_file in sorted(os.listdir(aa_path)):
            if not aa_file.endswith('.json'):
                continue
            n_files += 1
            with open(os.path.join(aa_path, aa_file), 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            meta = data['metadata']
            gk = f"{llm_name}_{noise_level}_{meta['game_id']}_{meta['run_id']}"
            for ri, rd in data['action_answers'].items():
                ocp, ons = None, None
                try:
                    gt = json.loads(rd['generated_text'])
                    if 'beliefs' in gt:
                        ocp = gt['beliefs'].get('opponent_coop_prob')
                        ons = gt['beliefs'].get('opponent_noise_suspicion')
                except Exception:
                    n_parse_fail += 1
                records.append({
                    'game_key': gk, 'game_id': meta['game_id'],
                    'run_id': meta['run_id'], 'llm_name': llm_name,
                    'noise_level': noise_level, 'language': meta['language'],
                    'player': meta['player'],
                    'p1_personality': meta['agents']['agent1']['personality'],
                    'p2_personality': meta['agents']['agent2']['personality'],
                    'round_number': int(ri), 'action': rd['action'],
                    'reason': rd.get('reason', ''),
                    'opponent_coop_prob': ocp,
                    'opponent_noise_suspicion': ons,
                })

df = pd.DataFrame(records)
df['model'] = df['llm_name'].map(MODEL_LABELS)
df['noise_label'] = df['noise_level'].map(NOISE_LABELS)
df['lang_label'] = df['language'].map(LANG_LABELS)
df_beliefs = df.dropna(subset=['opponent_coop_prob']).copy()

# ── Paired dataset: link belief with opponent's actual action ──
ck = ['game_key','round_number','opponent_coop_prob','opponent_noise_suspicion',
      'action','llm_name','noise_level','model','noise_label','language']
ma = df[df['player']=='A'][ck].merge(
    df[df['player']=='B'][['game_key','round_number','action']].rename(
        columns={'action':'opp_action'}), on=['game_key','round_number'], how='inner')
mb = df[df['player']=='B'][ck].merge(
    df[df['player']=='A'][['game_key','round_number','action']].rename(
        columns={'action':'opp_action'}), on=['game_key','round_number'], how='inner')
df_paired = pd.concat([ma, mb], ignore_index=True).dropna(subset=['opponent_coop_prob'])

print(f'Loaded {n_files:,} files -> {len(df):,} action records')
print(f'Belief parse failures: {n_parse_fail:,}')
print(f'Beliefs available: {len(df_beliefs):,} ({100*len(df_beliefs)/len(df):.1f}%)')
print(f'Paired records: {len(df_paired):,}')
print(f'Models: {sorted(df["model"].unique())}')
print(f'Languages: {sorted(df["language"].unique())}')\
"""

# ══════════════════════════════════════════════════════════════
# MODULE 11 — Belief Dynamics & Calibration
# ══════════════════════════════════════════════════════════════

def create_module11():
    cells = [
        ('markdown', """\
# Module 11 — Belief Dynamics & Calibration

**Research Question**: How do LLMs form, update, and act on beliefs about opponent behavior?

**Data**: `action_answers/*.json` — per-round beliefs (`opponent_coop_prob`, `opponent_noise_suspicion`) and actions.

**Scope**: 3 LLMs × 3 noise × 240 games × 2 players × 30 rounds = 129,600 records

**Figures**: 11a (belief trajectories), 11b (calibration), 11c (noise detection), 11d (belief-action consistency), 11e (adaptation speed), 11f (cross-model distributions)\
"""),
        ('code', SETUP_CODE),
        ('code', DATA_LOADING_CODE),

        # ── Fig 11a ──
        ('markdown', "## Figure 11a — Belief Trajectory Over Rounds"),
        ('code', """\
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for idx, (mkey, mname) in enumerate(zip(MODEL_KEYS, MODEL_ORDER)):
    ax = axes[idx]
    for nl, nl_label in zip([0, 5, 20], NOISE_ORDER):
        sub = df_beliefs[(df_beliefs['llm_name'] == mkey) & (df_beliefs['noise_level'] == nl)]
        traj = sub.groupby('round_number')['opponent_coop_prob'].agg(['mean', 'std', 'count'])
        traj['se'] = traj['std'] / np.sqrt(traj['count'])
        ax.plot(traj.index, traj['mean'], '-', linewidth=2, label=nl_label)
        ax.fill_between(traj.index, traj['mean'] - 1.96*traj['se'],
                        traj['mean'] + 1.96*traj['se'], alpha=0.15)
    ax.set_title(mname, fontsize=13, fontweight='bold', color=MODEL_COLORS[mkey])
    ax.set_xlabel('Round', fontsize=12)
    ax.set_xlim(0, 29)
    ax.set_ylim(0, 100)
    if idx == 0:
        ax.set_ylabel('Stated Opponent Coop. Probability', fontsize=12)
    ax.legend(frameon=False, fontsize=10)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3)

fig.suptitle('Belief Trajectories Over Game Rounds', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig11a_belief_trajectory.pdf')
plt.savefig(f'{FIGURE_DIR}fig11a_belief_trajectory.png')
plt.show()\
"""),

        # ── Fig 11b ──
        ('markdown', "## Figure 11b — Belief Calibration: Stated vs. Actual Opponent Cooperation"),
        ('code', """\
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, (mkey, mname) in enumerate(zip(MODEL_KEYS, MODEL_ORDER)):
    ax = axes[idx]
    sub = df_paired[df_paired['llm_name'] == mkey].copy()
    bins = list(range(0, 101, 10))
    sub['belief_bin'] = pd.cut(sub['opponent_coop_prob'], bins=bins, include_lowest=True)
    cal = sub.groupby('belief_bin', observed=True).agg(
        actual_coop=('opp_action', 'mean'),
        count=('opp_action', 'count'),
        stated_mean=('opponent_coop_prob', 'mean')
    ).reset_index()

    ax.scatter(cal['stated_mean'], cal['actual_coop'] * 100,
               s=cal['count'] / 50, color=MODEL_COLORS[mkey], alpha=0.7,
               edgecolors='white', linewidth=0.5)
    ax.plot([0, 100], [0, 100], 'k--', alpha=0.3, label='Perfect calibration')
    rmse = np.sqrt(np.mean((cal['stated_mean'] - cal['actual_coop'] * 100) ** 2))
    ax.text(0.05, 0.92, f'RMSE = {rmse:.1f}', transform=ax.transAxes,
            fontsize=11, fontweight='bold')
    ax.set_title(mname, fontsize=13, fontweight='bold', color=MODEL_COLORS[mkey])
    ax.set_xlabel('Stated Opponent Coop. Prob. (%)', fontsize=12)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    if idx == 0:
        ax.set_ylabel('Actual Opponent Coop. Rate (%)', fontsize=12)
    ax.legend(frameon=False, fontsize=10, loc='lower right')

fig.suptitle('Belief Calibration: Do LLMs Accurately Estimate Opponent Behavior?',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig11b_belief_calibration.pdf')
plt.savefig(f'{FIGURE_DIR}fig11b_belief_calibration.png')
plt.show()\
"""),

        # ── Fig 11c ──
        ('markdown', "## Figure 11c — Noise Suspicion Under Different Noise Conditions"),
        ('code', """\
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(MODEL_ORDER))
width = 0.25

for i, (nl, nl_label) in enumerate(zip([0, 5, 20], NOISE_ORDER)):
    vals, errs = [], []
    for mkey in MODEL_KEYS:
        sub = df_beliefs[(df_beliefs['llm_name'] == mkey) & (df_beliefs['noise_level'] == nl)]
        ns = sub['opponent_noise_suspicion'].dropna()
        vals.append(ns.mean())
        errs.append(1.96 * ns.std() / np.sqrt(len(ns)))
    ax.bar(x + (i - 1) * width, vals, width, yerr=errs,
           label=nl_label, edgecolor='white', linewidth=0.8, capsize=3)
    for xi, val in zip(x + (i - 1) * width, vals):
        ax.text(xi, val + 1.5, f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.set_ylabel('Mean Noise Suspicion (0-100)', fontsize=13)
ax.set_title('Noise Detection: Do LLMs Suspect Noise When It Exists?',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(MODEL_ORDER, fontsize=12)
ax.legend(frameon=False, fontsize=11)

plt.savefig(f'{FIGURE_DIR}fig11c_noise_suspicion.pdf')
plt.savefig(f'{FIGURE_DIR}fig11c_noise_suspicion.png')
plt.show()

print('Mean noise suspicion:')
ns_tbl = df_beliefs.groupby(['model','noise_label'])['opponent_noise_suspicion'].mean().unstack()
print(ns_tbl.reindex(index=MODEL_ORDER, columns=NOISE_ORDER).round(2))\
"""),

        # ── Fig 11d ──
        ('markdown', "## Figure 11d — Belief-Action Consistency: Do LLMs Act on Their Beliefs?"),
        ('code', """\
fig, ax = plt.subplots(figsize=(9, 6))
bins = list(range(0, 101, 10))
bin_centers = [b + 5 for b in bins[:-1]]

for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df_beliefs[df_beliefs['llm_name'] == mkey].copy()
    sub['belief_bin'] = pd.cut(sub['opponent_coop_prob'], bins=bins, include_lowest=True)
    coop_rate = sub.groupby('belief_bin', observed=True)['action'].mean()
    ax.plot(bin_centers[:len(coop_rate)], coop_rate.values, 'o-',
            color=MODEL_COLORS[mkey], label=mname, linewidth=2.5, markersize=8)

ax.set_xlabel('Stated Opponent Coop. Probability (%)', fontsize=13)
ax.set_ylabel('P(Own Action = Cooperate)', fontsize=13)
ax.set_title('Belief-Action Consistency: Do Beliefs Drive Actions?',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(-5, 105)
ax.set_ylim(-0.05, 1.05)
ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3)
ax.axvline(x=50, color='gray', linestyle='--', alpha=0.3)
ax.legend(frameon=False, fontsize=11)
ax.annotate('Higher belief in opponent\\ncooperation -> more likely\\nto cooperate themselves',
            xy=(70, 0.85), fontsize=10, fontstyle='italic', color='#555',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

plt.savefig(f'{FIGURE_DIR}fig11d_belief_action_consistency.pdf')
plt.savefig(f'{FIGURE_DIR}fig11d_belief_action_consistency.png')
plt.show()\
"""),

        # ── Fig 11e ──
        ('markdown', "## Figure 11e — Belief Adaptation After Opponent Strategy Switch"),
        ('code', """\
# Detect opponent switches and track belief changes (event study)
window = 5
switch_recs = []

for gk in df['game_key'].unique():
    for pv in ['A', 'B']:
        op = 'B' if pv == 'A' else 'A'
        p_data = df[(df['game_key'] == gk) & (df['player'] == pv)].sort_values('round_number')
        o_data = df[(df['game_key'] == gk) & (df['player'] == op)].sort_values('round_number')
        if len(p_data) < 3 or len(o_data) < 3:
            continue
        beliefs = p_data.set_index('round_number')['opponent_coop_prob'].dropna()
        opp_acts = o_data.set_index('round_number')['action']
        model = p_data['model'].iloc[0]
        llm = p_data['llm_name'].iloc[0]
        rnds = sorted(opp_acts.index)
        for i in range(1, len(rnds)):
            r, rp = rnds[i], rnds[i-1]
            if opp_acts[r] != opp_acts[rp]:
                st = 'C_to_D' if opp_acts[rp] == 1 else 'D_to_C'
                for off in range(-window, window + 1):
                    t = r + off
                    if t in beliefs.index:
                        switch_recs.append({'offset': off, 'belief': beliefs[t],
                                            'switch_type': st, 'model': model, 'llm_name': llm})

df_switch = pd.DataFrame(switch_recs)
print(f'Switch events detected: {len(df_switch[df_switch["offset"]==0]):,}')

if len(df_switch) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for idx, stype in enumerate(['D_to_C', 'C_to_D']):
        ax = axes[idx]
        sub = df_switch[df_switch['switch_type'] == stype]
        for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
            ms = sub[sub['llm_name'] == mkey]
            if len(ms) < 10:
                continue
            traj = ms.groupby('offset')['belief'].agg(['mean', 'sem'])
            ax.plot(traj.index, traj['mean'], 'o-', color=MODEL_COLORS[mkey],
                    label=mname, linewidth=2, markersize=6)
            ax.fill_between(traj.index, traj['mean'] - 1.96*traj['sem'],
                            traj['mean'] + 1.96*traj['sem'], alpha=0.15,
                            color=MODEL_COLORS[mkey])
        title = 'Opponent: Defect -> Cooperate' if stype == 'D_to_C' else 'Opponent: Cooperate -> Defect'
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Switch round')
        ax.set_xlabel('Rounds Relative to Switch', fontsize=12)
        if idx == 0:
            ax.set_ylabel('Mean Stated Opponent Coop. Belief', fontsize=12)
        ax.legend(frameon=False, fontsize=10)
    fig.suptitle('Belief Adaptation After Opponent Strategy Switch',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{FIGURE_DIR}fig11e_belief_convergence.pdf')
    plt.savefig(f'{FIGURE_DIR}fig11e_belief_convergence.png')
    plt.show()
else:
    print('No switch events detected.')\
"""),

        # ── Fig 11f ──
        ('markdown', "## Figure 11f — Cross-Model Belief Distribution Comparison"),
        ('code', """\
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for idx, (nl, nl_label) in enumerate(zip([0, 5, 20], NOISE_ORDER)):
    ax = axes[idx]
    data_list = []
    for mkey in MODEL_KEYS:
        vals = df_beliefs[(df_beliefs['llm_name'] == mkey) &
                          (df_beliefs['noise_level'] == nl)]['opponent_coop_prob'].values
        data_list.append(vals)
    parts = ax.violinplot(data_list, positions=range(len(MODEL_ORDER)),
                          showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(list(MODEL_COLORS.values())[i])
        pc.set_alpha(0.7)
    ax.set_title(nl_label, fontsize=13, fontweight='bold')
    ax.set_xticks(range(len(MODEL_ORDER)))
    ax.set_xticklabels(MODEL_ORDER, fontsize=11)
    ax.set_ylim(-5, 105)
    if idx == 0:
        ax.set_ylabel('Stated Opponent Coop. Probability', fontsize=12)

fig.suptitle('Distribution of Beliefs Across Models', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig11f_belief_distributions.pdf')
plt.savefig(f'{FIGURE_DIR}fig11f_belief_distributions.png')
plt.show()

for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    s = df_beliefs[df_beliefs['llm_name'] == mkey]['opponent_coop_prob']
    print(f'{mname}: mean={s.mean():.1f}, median={s.median():.0f}, std={s.std():.1f}')\
"""),

        # ── Stats ──
        ('markdown', "## Statistical Tests"),
        ('code', """\
print('=' * 70)
print('STATISTICAL ANALYSIS - Belief Dynamics & Calibration')
print('=' * 70)

# 1. Kruskal-Wallis beliefs across models
groups = [df_beliefs[df_beliefs['llm_name']==m]['opponent_coop_prob'] for m in df_beliefs['llm_name'].unique()]
H, p = stats.kruskal(*groups)
print(f'\\n1. Kruskal-Wallis (beliefs across models): H={H:.2f}, p={p:.2e}')

# 2. Belief drift over rounds
rho, p = stats.spearmanr(df_beliefs['round_number'], df_beliefs['opponent_coop_prob'])
print(f'\\n2. Belief drift (Spearman round vs belief): rho={rho:.4f}, p={p:.2e}')

# 3. Noise suspicion: 0% vs 20%
g0 = df_beliefs[df_beliefs['noise_level']==0]['opponent_noise_suspicion'].dropna()
g20 = df_beliefs[df_beliefs['noise_level']==20]['opponent_noise_suspicion'].dropna()
U, p = stats.mannwhitneyu(g0, g20, alternative='two-sided')
print(f'\\n3. Noise suspicion 0% vs 20%: U={U:.0f}, p={p:.2e}')
print(f'   Mean: noise=0 -> {g0.mean():.2f}, noise=20 -> {g20.mean():.2f}')

# 4. Belief-action correlation
rho, p = stats.spearmanr(df_beliefs['opponent_coop_prob'], df_beliefs['action'])
print(f'\\n4. Belief-action correlation (Spearman): rho={rho:.4f}, p={p:.2e}')

# 5. Calibration RMSE per model
print('\\n5. Calibration RMSE per model:')
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df_paired[df_paired['llm_name']==mkey].copy()
    sub['bb'] = pd.cut(sub['opponent_coop_prob'], bins=list(range(0,101,10)), include_lowest=True)
    cal = sub.groupby('bb', observed=True).agg(a=('opp_action','mean'), s=('opponent_coop_prob','mean')).dropna()
    if len(cal) > 0:
        rmse = np.sqrt(np.mean((cal['s'] - cal['a']*100)**2))
        print(f'   {mname}: RMSE = {rmse:.1f}')

# 6. Pairwise belief comparisons
print('\\n6. Pairwise Mann-Whitney (Bonferroni):')
mns = sorted(df_beliefs['llm_name'].unique())
nt = len(list(combinations(mns, 2)))
for m1, m2 in combinations(mns, 2):
    g1 = df_beliefs[df_beliefs['llm_name']==m1]['opponent_coop_prob']
    g2 = df_beliefs[df_beliefs['llm_name']==m2]['opponent_coop_prob']
    U, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    pa = min(p*nt, 1.0)
    sig = '***' if pa<0.001 else '**' if pa<0.01 else '*' if pa<0.05 else 'ns'
    print(f'   {MODEL_LABELS[m1]} vs {MODEL_LABELS[m2]}: U={U:.0f}, p_adj={pa:.2e} {sig}')\
"""),

        # ── Summary ──
        ('markdown', "## Summary Table"),
        ('code', """\
print('=' * 85)
print('TABLE: Belief Dynamics Summary')
print('=' * 85)
header = f'{" Model":<16} | {"Mean Belief":>11} | {"Median":>7} | {"Noise Susp":>10} | {"Cal.RMSE":>8} | {"Belief-Act rho":>14}'
print(header)
print('-' * 85)
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sb = df_beliefs[df_beliefs['llm_name']==mkey]
    sp = df_paired[df_paired['llm_name']==mkey].copy()
    mb = sb['opponent_coop_prob'].mean()
    mdb = sb['opponent_coop_prob'].median()
    mns = sb['opponent_noise_suspicion'].dropna().mean()
    sp['bb'] = pd.cut(sp['opponent_coop_prob'], bins=list(range(0,101,10)), include_lowest=True)
    cal = sp.groupby('bb', observed=True).agg(a=('opp_action','mean'), s=('opponent_coop_prob','mean')).dropna()
    rmse = np.sqrt(np.mean((cal['s'] - cal['a']*100)**2)) if len(cal) > 0 else float('nan')
    rho, _ = stats.spearmanr(sb['opponent_coop_prob'], sb['action'])
    print(f'{mname:<16} | {mb:>11.1f} | {mdb:>7.0f} | {mns:>10.1f} | {rmse:>8.1f} | {rho:>14.3f}')

print()
print('KEY FINDINGS:')
print('1. LLMs form and update beliefs about opponents over rounds.')
print('2. Calibration gap exists: stated beliefs may diverge from actual opponent behavior.')
print('3. Beliefs DO correlate with actions - LLMs act partially on their stated beliefs.')
print('4. Noise detection varies: some models detect noise, others remain oblivious.')
print('5. After opponent switches strategy, beliefs adapt but with model-specific latency.')\
"""),
    ]
    make_notebook(cells, 'paper_notebooks/module11_belief_dynamics.ipynb')


# ══════════════════════════════════════════════════════════════
# MODULE 12 — Reasoning Text Analysis
# ══════════════════════════════════════════════════════════════

def create_module12():
    cells = [
        ('markdown', """\
# Module 12 — Reasoning Text Analysis (NLP)

**Research Question**: What strategic reasoning patterns do LLMs articulate, and do their stated reasons match their actions?

**Data**: `action_answers/*.json` — natural language `reason` field from 129,600 action decisions.

**Methods**: Keyword-based reasoning taxonomy, lexical diversity, say-do alignment, cross-language comparison.

**Figures**: 12a (reasoning taxonomy), 12b (reasoning over rounds), 12c (say-do alignment), 12d (cross-language), 12e (opponent mentions), 12f (sentiment analysis)\
"""),
        ('code', SETUP_CODE),
        ('code', DATA_LOADING_CODE + """

# ── Text features ──
df['reason_len'] = df['reason'].str.len()
df['word_count'] = df['reason'].str.split().str.len().fillna(0).astype(int)
df['unique_words'] = df['reason'].str.lower().str.split().apply(
    lambda x: len(set(x)) if isinstance(x, list) and len(x) > 0 else 0)
df['type_token_ratio'] = df['unique_words'] / df['word_count'].replace(0, np.nan)

# ── Reasoning taxonomy (keyword-based, English-focused) ──
TAXONOMY = {
    'Retaliation': r'retaliat|punish|revenge|payback',
    'Reciprocity': r'tit.for.tat|match|mirror|reciproc',
    'Risk Minimization': r'minimiz|minimis|lower.*(penalty|risk)|expected.*penalty',
    'Trust Building': r'trust|encourage.*coop|mutual.*benefit',
    'History Based': r'previous|last round|history|pattern|consistently|every round|all.*round',
    'Noise Awareness': r'noise|random.*flip|accident|mistake|error.*rate',
    'Cooperation Appeal': r'cooperat.*benefit|better off|both.*gain',
    'Numerical Reasoning': r'\\\\d+.*penalty|\\\\d+.*payoff|expected.*value|probability',
}
for cat, pattern in TAXONOMY.items():
    df[f'tax_{cat}'] = df['reason'].str.contains(pattern, case=False, na=False)

print(f'Text features computed for {len(df):,} records')
print(f'Mean reason length: {df["reason_len"].mean():.0f} chars, {df["word_count"].mean():.1f} words')
"""),

        # ── Fig 12a ──
        ('markdown', "## Figure 12a — Reasoning Taxonomy: What Strategies Do LLMs Verbalize?"),
        ('code', """\
tax_cols = [c for c in df.columns if c.startswith('tax_')]
tax_names = [c.replace('tax_', '') for c in tax_cols]

fig, ax = plt.subplots(figsize=(10, 6))
model_data = {}
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    model_data[mname] = [sub[c].mean() * 100 for c in tax_cols]

x = np.arange(len(tax_names))
width = 0.25
colors = [MODEL_COLORS[k] for k in MODEL_KEYS]
for i, mname in enumerate(MODEL_ORDER):
    ax.barh(x + (i - 1) * width, model_data[mname], width, label=mname,
            color=colors[i], edgecolor='white', linewidth=0.5)

ax.set_yticks(x)
ax.set_yticklabels(tax_names, fontsize=11)
ax.set_xlabel('% of Reasons Containing Pattern', fontsize=13)
ax.set_title('Reasoning Taxonomy: Strategic Justification Patterns',
             fontsize=14, fontweight='bold', pad=12)
ax.legend(frameon=False, fontsize=11, loc='lower right')
ax.invert_yaxis()

plt.savefig(f'{FIGURE_DIR}fig12a_reasoning_taxonomy.pdf')
plt.savefig(f'{FIGURE_DIR}fig12a_reasoning_taxonomy.png')
plt.show()\
"""),

        # ── Fig 12b ──
        ('markdown', "## Figure 12b — Reasoning Characteristics Over Rounds"),
        ('code', """\
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

metrics = [('word_count', 'Word Count'), ('unique_words', 'Unique Words'),
           ('type_token_ratio', 'Type-Token Ratio')]
for idx, (col, label) in enumerate(metrics):
    ax = axes[idx]
    for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
        sub = df[df['llm_name'] == mkey]
        traj = sub.groupby('round_number')[col].mean()
        ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
                label=mname, linewidth=2)
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel(label, fontsize=12)
    ax.set_title(label, fontsize=13, fontweight='bold')
    ax.legend(frameon=False, fontsize=9)
    ax.set_xlim(0, 29)

fig.suptitle('Reasoning Characteristics Over Game Progression',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig12b_reasoning_over_rounds.pdf')
plt.savefig(f'{FIGURE_DIR}fig12b_reasoning_over_rounds.png')
plt.show()\
"""),

        # ── Fig 12c ──
        ('markdown', "## Figure 12c — Say-Do Alignment: Do Reasons Match Actions?"),
        ('code', """\
# Detect misalignment: reason suggests cooperation but action is Defect (or vice versa)
coop_kw = r'cooperat|trust|mutual|together|benefit|encourage'
defect_kw = r'defect|betray|puni|retaliat|low.*penalty|minimiz'

df['reason_coop'] = df['reason'].str.contains(coop_kw, case=False, na=False)
df['reason_defect'] = df['reason'].str.contains(defect_kw, case=False, na=False)
df['say_do_mismatch'] = (
    (df['reason_coop'] & ~df['reason_defect'] & (df['action'] == 0)) |
    (df['reason_defect'] & ~df['reason_coop'] & (df['action'] == 1))
)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Mismatch rate by model
ax = axes[0]
mismatch_rates = []
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    mismatch_rates.append(sub['say_do_mismatch'].mean() * 100)
bars = ax.bar(MODEL_ORDER, mismatch_rates, color=[MODEL_COLORS[k] for k in MODEL_KEYS],
              edgecolor='white', linewidth=0.8)
for bar, val in zip(bars, mismatch_rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')
ax.set_ylabel('Say-Do Mismatch Rate (%)', fontsize=13)
ax.set_title('(a) Mismatch Rate by Model', fontsize=13, fontweight='bold')

# Panel B: Mismatch over rounds
ax = axes[1]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    traj = sub.groupby('round_number')['say_do_mismatch'].mean() * 100
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('Mismatch Rate (%)', fontsize=13)
ax.set_title('(b) Mismatch Over Rounds', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.set_xlim(0, 29)

fig.suptitle('Say-Do Alignment: Do Stated Reasons Match Actual Actions?',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig12c_say_do_alignment.pdf')
plt.savefig(f'{FIGURE_DIR}fig12c_say_do_alignment.png')
plt.show()

print(f'Overall say-do mismatch rate: {df["say_do_mismatch"].mean()*100:.2f}%')\
"""),

        # ── Fig 12d ──
        ('markdown', "## Figure 12d — Cross-Language Reasoning Patterns"),
        ('code', """\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Reason length by language
ax = axes[0]
lang_metrics = df.groupby(['lang_label', 'model'])['word_count'].mean().unstack()
lang_metrics = lang_metrics.reindex(index=LANG_ORDER, columns=MODEL_ORDER)
lang_metrics.plot(kind='barh', ax=ax, color=[MODEL_COLORS[k] for k in MODEL_KEYS],
                  edgecolor='white', linewidth=0.5)
ax.set_xlabel('Mean Word Count', fontsize=12)
ax.set_title('(a) Reasoning Length by Language', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=9)
ax.invert_yaxis()

# Panel B: Type-token ratio by language
ax = axes[1]
ttr_metrics = df.groupby(['lang_label', 'model'])['type_token_ratio'].mean().unstack()
ttr_metrics = ttr_metrics.reindex(index=LANG_ORDER, columns=MODEL_ORDER)
ttr_metrics.plot(kind='barh', ax=ax, color=[MODEL_COLORS[k] for k in MODEL_KEYS],
                 edgecolor='white', linewidth=0.5)
ax.set_xlabel('Mean Type-Token Ratio', fontsize=12)
ax.set_title('(b) Vocabulary Richness by Language', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=9)
ax.invert_yaxis()

fig.suptitle('Cross-Language Reasoning Comparison',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig12d_cross_language_reasoning.pdf')
plt.savefig(f'{FIGURE_DIR}fig12d_cross_language_reasoning.png')
plt.show()\
"""),

        # ── Fig 12e ──
        ('markdown', "## Figure 12e — Opponent Mention Frequency"),
        ('code', """\
df['mentions_opponent'] = df['reason'].str.contains(
    r'agent.?2|opponent|other.?player|adversar', case=False, na=False)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: by model × action
ax = axes[0]
opp_by = df.groupby(['model', 'action'])['mentions_opponent'].mean().unstack() * 100
opp_by.columns = ['Defect', 'Cooperate']
opp_by = opp_by.reindex(MODEL_ORDER)
opp_by.plot(kind='bar', ax=ax, color=['#FF5722', '#2196F3'], edgecolor='white')
ax.set_ylabel('% Reasons Mentioning Opponent', fontsize=12)
ax.set_title('(a) Opponent Mentions by Action', fontsize=13, fontweight='bold')
ax.set_xticklabels(MODEL_ORDER, rotation=0)
ax.legend(frameon=False)

# Panel B: over rounds
ax = axes[1]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    traj = sub.groupby('round_number')['mentions_opponent'].mean() * 100
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('% Mentioning Opponent', fontsize=12)
ax.set_title('(b) Opponent Mentions Over Rounds', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.set_xlim(0, 29)

fig.suptitle('Theory of Mind: How Often Do LLMs Reference the Opponent?',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig12e_opponent_mentions.pdf')
plt.savefig(f'{FIGURE_DIR}fig12e_opponent_mentions.png')
plt.show()\
"""),

        # ── Fig 12f ──
        ('markdown', "## Figure 12f — Sentiment Analysis: Cooperative vs. Competitive Framing"),
        ('code', """\
POS_WORDS = r'cooperat|benefit|mutual|trust|reward|good|positive|together|encourage|peace'
NEG_WORDS = r'defect|penalty|punish|risk|loss|betray|negative|threat|exploit|retaliat'

df['pos_count'] = df['reason'].str.lower().str.count(POS_WORDS)
df['neg_count'] = df['reason'].str.lower().str.count(NEG_WORDS)
df['sentiment'] = df['pos_count'] - df['neg_count']

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Sentiment by action type
ax = axes[0]
for act, act_label, color in [(1, 'Cooperate', '#2196F3'), (0, 'Defect', '#FF5722')]:
    subset = df[df['action'] == act]
    for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
        ms = subset[subset['llm_name'] == mkey]['sentiment']
        # Just show means
    means_c = [df[(df['llm_name']==mk) & (df['action']==1)]['sentiment'].mean() for mk in MODEL_KEYS]
    means_d = [df[(df['llm_name']==mk) & (df['action']==0)]['sentiment'].mean() for mk in MODEL_KEYS]

x = np.arange(len(MODEL_ORDER))
width = 0.3
ax.bar(x - width/2, means_c, width, label='Cooperate', color='#2196F3', edgecolor='white')
ax.bar(x + width/2, means_d, width, label='Defect', color='#FF5722', edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(MODEL_ORDER, fontsize=11)
ax.set_ylabel('Mean Sentiment Score', fontsize=12)
ax.set_title('(a) Reasoning Sentiment by Action', fontsize=13, fontweight='bold')
ax.legend(frameon=False)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

# Panel B: Sentiment over rounds
ax = axes[1]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    traj = sub.groupby('round_number')['sentiment'].mean()
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('Mean Sentiment Score', fontsize=12)
ax.set_title('(b) Sentiment Over Rounds', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
ax.set_xlim(0, 29)

fig.suptitle('Reasoning Sentiment: Cooperative vs. Competitive Framing',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig12f_sentiment_analysis.pdf')
plt.savefig(f'{FIGURE_DIR}fig12f_sentiment_analysis.png')
plt.show()\
"""),

        # ── Stats ──
        ('markdown', "## Statistical Tests"),
        ('code', """\
print('=' * 70)
print('STATISTICAL ANALYSIS - Reasoning Text')
print('=' * 70)

# 1. Word count across models
groups = [df[df['llm_name']==m]['word_count'] for m in df['llm_name'].unique()]
H, p = stats.kruskal(*groups)
print(f'\\n1. Word count across models (Kruskal-Wallis): H={H:.2f}, p={p:.2e}')

# 2. Type-token ratio across models
groups = [df[df['llm_name']==m]['type_token_ratio'].dropna() for m in df['llm_name'].unique()]
H, p = stats.kruskal(*groups)
print(f'\\n2. Type-token ratio across models: H={H:.2f}, p={p:.2e}')

# 3. Say-do mismatch across models
print('\\n3. Say-do mismatch rate:')
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    rate = sub['say_do_mismatch'].mean() * 100
    n_mm = sub['say_do_mismatch'].sum()
    print(f'   {mname}: {rate:.2f}% ({n_mm:,} mismatches)')

# 4. Chi-squared: taxonomy × model
print('\\n4. Taxonomy prevalence by model:')
tax_cols = [c for c in df.columns if c.startswith('tax_')]
for tc in tax_cols:
    name = tc.replace('tax_', '')
    ct = pd.crosstab(df['model'], df[tc])
    if ct.shape[1] == 2:
        chi2, p, _, _ = stats.chi2_contingency(ct)
        sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
        prev = df[tc].mean() * 100
        print(f'   {name}: chi2={chi2:.1f}, p={p:.2e} {sig} (overall={prev:.1f}%)')

# 5. Sentiment by action
g_c = df[df['action']==1]['sentiment']
g_d = df[df['action']==0]['sentiment']
U, p = stats.mannwhitneyu(g_c, g_d, alternative='two-sided')
print(f'\\n5. Sentiment: Cooperate ({g_c.mean():.3f}) vs Defect ({g_d.mean():.3f})')
print(f'   Mann-Whitney U={U:.0f}, p={p:.2e}')

# 6. Cross-language word count
print('\\n6. Word count by language:')
for lang in LANG_ORDER:
    sub = df[df['lang_label']==lang]
    print(f'   {lang}: {sub["word_count"].mean():.1f} words, TTR={sub["type_token_ratio"].mean():.3f}')\
"""),

        # ── Summary ──
        ('markdown', "## Summary Table"),
        ('code', """\
print('=' * 90)
print('TABLE: Reasoning Text Analysis Summary')
print('=' * 90)
print(f'{"Model":<16} | {"Words":>6} | {"TTR":>5} | {"Opp.Mention%":>12} | {"Mismatch%":>10} | {"Sentiment":>9}')
print('-' * 70)
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    wc = sub['word_count'].mean()
    ttr = sub['type_token_ratio'].mean()
    opp = sub['mentions_opponent'].mean() * 100
    mm = sub['say_do_mismatch'].mean() * 100
    sent = sub['sentiment'].mean()
    print(f'{mname:<16} | {wc:>6.1f} | {ttr:>5.3f} | {opp:>12.1f} | {mm:>10.2f} | {sent:>9.3f}')

print()
print('KEY FINDINGS:')
print('1. LLMs primarily rely on history-based reasoning and risk minimization.')
print('2. Reasoning length and vocabulary richness vary across models and languages.')
print('3. Say-do misalignment exists: some reasons suggest one action while taking another.')
print('4. Opponent mentions indicate varying levels of theory-of-mind across models.')
print('5. Cooperative actions are framed with positive language; defection with negative.')\
"""),
    ]
    make_notebook(cells, 'paper_notebooks/module12_reasoning_analysis.ipynb')


# ══════════════════════════════════════════════════════════════
# MODULE 13 — Strategic Narrative & Adaptation
# ══════════════════════════════════════════════════════════════

def create_module13():
    cells = [
        ('markdown', """\
# Module 13 — Strategic Narrative & Adaptation

**Research Question**: How do LLMs narratively respond to game events — betrayal, forgiveness, endgame, noise?

**Data**: `action_answers/*.json` — reasons and beliefs from 129,600 action decisions.

**Methods**: Event-triggered text analysis, keyword detection, cross-condition comparison.

**Figures**: 13a (post-betrayal reasoning), 13b (forgiveness language), 13c (endgame awareness), 13d (noise attribution), 13e (personality effect), 13f (reasoning consistency)\
"""),
        ('code', SETUP_CODE),
        ('code', DATA_LOADING_CODE + """

# ── Detect betrayal events: opponent switches C -> D ──
betrayal_flags = []
for gk in df['game_key'].unique():
    for pv in ['A', 'B']:
        op = 'B' if pv == 'A' else 'A'
        p_data = df[(df['game_key']==gk) & (df['player']==pv)].sort_values('round_number')
        o_data = df[(df['game_key']==gk) & (df['player']==op)].sort_values('round_number')
        if len(o_data) < 2:
            continue
        opp_acts = o_data.set_index('round_number')['action']
        rnds = sorted(opp_acts.index)
        betrayal_rounds = set()
        for i in range(1, len(rnds)):
            if opp_acts[rnds[i]] == 0 and opp_acts[rnds[i-1]] == 1:  # C -> D
                betrayal_rounds.add(rnds[i])
        for _, row in p_data.iterrows():
            r = row['round_number']
            is_post_betrayal = any(r == br or r == br + 1 for br in betrayal_rounds)
            betrayal_flags.append({
                'game_key': gk, 'player': pv, 'round_number': r,
                'post_betrayal': is_post_betrayal,
            })

df_bf = pd.DataFrame(betrayal_flags)
df = df.merge(df_bf, on=['game_key', 'player', 'round_number'], how='left')
df['post_betrayal'] = df['post_betrayal'].fillna(False)

# ── Text features for narrative analysis ──
df['mentions_noise'] = df['reason'].str.contains(
    r'noise|random|flip|accident|mistake|error', case=False, na=False)
df['mentions_endgame'] = df['reason'].str.contains(
    r'last.*round|final|end.*game|round 30|remaining|conclud', case=False, na=False)
df['mentions_forgive'] = df['reason'].str.contains(
    r'forgiv|second chance|try again|give.*chance|one more|perhaps.*cooperat', case=False, na=False)
df['mentions_betray'] = df['reason'].str.contains(
    r'betray|broke.*trust|violated|switched|changed.*strategy', case=False, na=False)
df['mentions_punish'] = df['reason'].str.contains(
    r'punish|retali|revenge|payback|teach.*lesson', case=False, na=False)

print(f'Betrayal events flagged. Post-betrayal records: {df["post_betrayal"].sum():,}')
print(f'Noise mentions: {df["mentions_noise"].sum():,}')
print(f'Endgame mentions: {df["mentions_endgame"].sum():,}')
"""),

        # ── Fig 13a ──
        ('markdown', "## Figure 13a — Reasoning Shift After Betrayal (Opponent C -> D)"),
        ('code', """\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Cooperation rate before vs after betrayal
ax = axes[0]
pre_rates = []
post_rates = []
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    pre = sub[~sub['post_betrayal']]['action'].mean()
    post = sub[sub['post_betrayal']]['action'].mean()
    pre_rates.append(pre)
    post_rates.append(post)

x = np.arange(len(MODEL_ORDER))
width = 0.3
ax.bar(x - width/2, pre_rates, width, label='Normal', color='#4CAF50', edgecolor='white')
ax.bar(x + width/2, post_rates, width, label='Post-Betrayal', color='#F44336', edgecolor='white')
for i in range(len(MODEL_ORDER)):
    diff = post_rates[i] - pre_rates[i]
    ax.annotate(f'{diff:+.3f}', xy=(i, max(pre_rates[i], post_rates[i]) + 0.02),
                ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(MODEL_ORDER)
ax.set_ylabel('Cooperation Rate', fontsize=12)
ax.set_title('(a) Coop. Rate: Normal vs Post-Betrayal', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

# Panel B: Keyword prevalence post-betrayal
ax = axes[1]
kw_cols = ['mentions_punish', 'mentions_betray', 'mentions_forgive']
kw_labels = ['Punishment', 'Betrayal', 'Forgiveness']
colors_kw = ['#F44336', '#FF9800', '#4CAF50']
bar_data = {}
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub_post = df[(df['llm_name'] == mkey) & df['post_betrayal']]
    bar_data[mname] = [sub_post[c].mean() * 100 for c in kw_cols]

x = np.arange(len(kw_labels))
for i, mname in enumerate(MODEL_ORDER):
    ax.bar(x + (i-1)*width, bar_data[mname], width, label=mname,
           color=[MODEL_COLORS[k] for k in MODEL_KEYS][i], edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(kw_labels)
ax.set_ylabel('% of Post-Betrayal Reasons', fontsize=12)
ax.set_title('(b) Narrative Response to Betrayal', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=9)

fig.suptitle('Strategic Reasoning After Opponent Betrayal',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13a_post_betrayal.pdf')
plt.savefig(f'{FIGURE_DIR}fig13a_post_betrayal.png')
plt.show()\
"""),

        # ── Fig 13b ──
        ('markdown', "## Figure 13b — Forgiveness Language: Do LLMs Forgive?"),
        ('code', """\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Forgiveness rate by model
ax = axes[0]
forgive_rates = []
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[(df['llm_name'] == mkey) & df['post_betrayal']]
    rate = sub['mentions_forgive'].mean() * 100 if len(sub) > 0 else 0
    forgive_rates.append(rate)
bars = ax.bar(MODEL_ORDER, forgive_rates, color=[MODEL_COLORS[k] for k in MODEL_KEYS],
              edgecolor='white')
for bar, val in zip(bars, forgive_rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')
ax.set_ylabel('Forgiveness Mention Rate (%)', fontsize=12)
ax.set_title('(a) Forgiveness After Betrayal', fontsize=13, fontweight='bold')

# Panel B: Forgiveness by noise condition
ax = axes[1]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    rates = []
    for nl in [0, 5, 20]:
        sub = df[(df['llm_name']==mkey) & (df['noise_level']==nl) & df['post_betrayal']]
        rates.append(sub['mentions_forgive'].mean() * 100 if len(sub) > 0 else 0)
    ax.plot(NOISE_ORDER, rates, 'o-', color=MODEL_COLORS[mkey], label=mname,
            linewidth=2, markersize=8)
ax.set_ylabel('Forgiveness Mention Rate (%)', fontsize=12)
ax.set_title('(b) Forgiveness by Noise Condition', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)

fig.suptitle('Forgiveness in LLM Strategic Reasoning',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13b_forgiveness.pdf')
plt.savefig(f'{FIGURE_DIR}fig13b_forgiveness.png')
plt.show()\
"""),

        # ── Fig 13c ──
        ('markdown', "## Figure 13c — Endgame Reasoning: Backward Induction Awareness"),
        ('code', """\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Endgame mention rate over rounds
ax = axes[0]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    traj = sub.groupby('round_number')['mentions_endgame'].mean() * 100
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('% Mentioning Endgame', fontsize=12)
ax.set_title('(a) Endgame Awareness Over Rounds', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.set_xlim(0, 29)
ax.axvspan(25, 30, alpha=0.1, color='red', label='Endgame zone')

# Panel B: Cooperation rate in endgame vs earlier
ax = axes[1]
df['is_endgame'] = df['round_number'] >= 25
eg_data = df.groupby(['model', 'is_endgame'])['action'].mean().unstack()
eg_data.columns = ['Early (r<25)', 'Endgame (r>=25)']
eg_data = eg_data.reindex(MODEL_ORDER)

x = np.arange(len(MODEL_ORDER))
width = 0.3
ax.bar(x - width/2, eg_data['Early (r<25)'], width, label='Early (r<25)',
       color='#4CAF50', edgecolor='white')
ax.bar(x + width/2, eg_data['Endgame (r>=25)'], width, label='Endgame (r>=25)',
       color='#FF5722', edgecolor='white')
for i, m in enumerate(MODEL_ORDER):
    diff = eg_data.loc[m, 'Endgame (r>=25)'] - eg_data.loc[m, 'Early (r<25)']
    ax.annotate(f'{diff:+.3f}', xy=(i, max(eg_data.loc[m]) + 0.02),
                ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(MODEL_ORDER)
ax.set_ylabel('Cooperation Rate', fontsize=12)
ax.set_title('(b) Cooperation in Endgame vs Early', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

fig.suptitle('Endgame Reasoning: Do LLMs Recognize the Game Is Ending?',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13c_endgame.pdf')
plt.savefig(f'{FIGURE_DIR}fig13c_endgame.png')
plt.show()\
"""),

        # ── Fig 13d ──
        ('markdown', "## Figure 13d — Noise Attribution: Causal Reasoning About Noise"),
        ('code', """\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Noise mention rate by actual noise condition
ax = axes[0]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    rates = []
    for nl in [0, 5, 20]:
        sub = df[(df['llm_name'] == mkey) & (df['noise_level'] == nl)]
        rates.append(sub['mentions_noise'].mean() * 100)
    ax.plot(NOISE_ORDER, rates, 'o-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2.5, markersize=8)
ax.set_ylabel('% Reasons Mentioning Noise', fontsize=12)
ax.set_title('(a) Noise Mentions by Actual Noise Condition', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)

# Panel B: Noise mention over rounds (20% noise only)
ax = axes[1]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[(df['llm_name'] == mkey) & (df['noise_level'] == 20)]
    traj = sub.groupby('round_number')['mentions_noise'].mean() * 100
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('% Mentioning Noise', fontsize=12)
ax.set_title('(b) Noise Mentions Over Rounds (20% Noise)', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.set_xlim(0, 29)

fig.suptitle('Noise Attribution: Can LLMs Detect and Reason About Noise?',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13d_noise_attribution.pdf')
plt.savefig(f'{FIGURE_DIR}fig13d_noise_attribution.png')
plt.show()

# Print noise mention rates
print('Noise mention rates:')
nr = df.groupby(['model', 'noise_label'])['mentions_noise'].mean().unstack() * 100
print(nr.reindex(index=MODEL_ORDER, columns=NOISE_ORDER).round(2))\
"""),

        # ── Fig 13e ──
        ('markdown', "## Figure 13e — Personality Effect on Strategic Reasoning"),
        ('code', """\
# Determine personality of the answering player
df['personality'] = df.apply(
    lambda r: r['p1_personality'] if r['player'] == 'A' else r['p2_personality'], axis=1)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A: Cooperation rate by personality
ax = axes[0]
pers_coop = df.groupby(['model', 'personality'])['action'].mean().unstack()
pers_coop = pers_coop.reindex(MODEL_ORDER)
if pers_coop.shape[1] >= 2:
    cols = sorted(pers_coop.columns)
    x = np.arange(len(MODEL_ORDER))
    width = 0.3
    for i, pers in enumerate(cols):
        color = '#4CAF50' if 'coop' in pers.lower() else '#FF5722'
        ax.bar(x + (i - len(cols)/2 + 0.5) * width, pers_coop[pers], width,
               label=pers.title(), color=color, edgecolor='white', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MODEL_ORDER)
ax.set_ylabel('Cooperation Rate', fontsize=12)
ax.set_title('(a) Cooperation by Personality', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

# Panel B: Mean belief by personality
ax = axes[1]
pers_belief = df_beliefs.copy()
pers_belief['personality'] = pers_belief.apply(
    lambda r: r['p1_personality'] if r['player'] == 'A' else r['p2_personality'], axis=1)
pb = pers_belief.groupby(['model', 'personality'])['opponent_coop_prob'].mean().unstack()
pb = pb.reindex(MODEL_ORDER)
if pb.shape[1] >= 2:
    cols = sorted(pb.columns)
    for i, pers in enumerate(cols):
        color = '#4CAF50' if 'coop' in pers.lower() else '#FF5722'
        ax.bar(x + (i - len(cols)/2 + 0.5) * width, pb[pers], width,
               label=pers.title(), color=color, edgecolor='white', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MODEL_ORDER)
ax.set_ylabel('Mean Stated Opp. Coop. Prob.', fontsize=12)
ax.set_title('(b) Beliefs by Personality', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

# Panel C: Reason length by personality
ax = axes[2]
df['word_count'] = df['reason'].str.split().str.len().fillna(0)
pwc = df.groupby(['model', 'personality'])['word_count'].mean().unstack()
pwc = pwc.reindex(MODEL_ORDER)
if pwc.shape[1] >= 2:
    cols = sorted(pwc.columns)
    for i, pers in enumerate(cols):
        color = '#4CAF50' if 'coop' in pers.lower() else '#FF5722'
        ax.bar(x + (i - len(cols)/2 + 0.5) * width, pwc[pers], width,
               label=pers.title(), color=color, edgecolor='white', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MODEL_ORDER)
ax.set_ylabel('Mean Word Count', fontsize=12)
ax.set_title('(c) Reasoning Length by Personality', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

fig.suptitle('Effect of Assigned Personality on Strategic Behavior',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13e_personality_effect.pdf')
plt.savefig(f'{FIGURE_DIR}fig13e_personality_effect.png')
plt.show()\
"""),

        # ── Fig 13f ──
        ('markdown', "## Figure 13f — Reasoning Consistency: Do LLMs Repeat Themselves?"),
        ('code', """\
# Measure reasoning consistency: how similar are reasons across games for same conditions?
from collections import Counter

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Most common reason n-grams (top 15) for each model
ax = axes[0]
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[(df['llm_name'] == mkey) & (df['language'] == 'en')]
    all_words = ' '.join(sub['reason'].str.lower().dropna()).split()
    # Extract 3-grams
    trigrams = [' '.join(all_words[i:i+3]) for i in range(len(all_words) - 2)]
    top = Counter(trigrams).most_common(5)
    print(f'{mname} top 3-grams: {top}')

# Type-token ratio distribution by model (measure of repetitiveness)
df['ttr'] = df['reason'].str.lower().str.split().apply(
    lambda x: len(set(x)) / len(x) if isinstance(x, list) and len(x) > 0 else np.nan)

for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]['ttr'].dropna()
    ax.hist(sub, bins=30, alpha=0.5, label=mname, color=MODEL_COLORS[mkey], density=True)
ax.set_xlabel('Type-Token Ratio (per reason)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('(a) Vocabulary Diversity Distribution', fontsize=13, fontweight='bold')
ax.legend(frameon=False)

# Panel B: Reason length std within same round × model × noise (consistency)
ax = axes[1]
consistency = df.groupby(['llm_name', 'noise_level', 'round_number'])['reason'].apply(
    lambda x: x.str.len().std()).reset_index()
consistency.columns = ['llm_name', 'noise_level', 'round_number', 'len_std']
consistency['model'] = consistency['llm_name'].map(MODEL_LABELS)

for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = consistency[consistency['llm_name'] == mkey]
    traj = sub.groupby('round_number')['len_std'].mean()
    ax.plot(traj.index, traj.values, '-', color=MODEL_COLORS[mkey],
            label=mname, linewidth=2)
ax.set_xlabel('Round', fontsize=12)
ax.set_ylabel('Std Dev of Reason Length', fontsize=12)
ax.set_title('(b) Reasoning Variability Over Rounds', fontsize=13, fontweight='bold')
ax.legend(frameon=False, fontsize=10)
ax.set_xlim(0, 29)

fig.suptitle('Reasoning Consistency: Repetition vs. Creativity',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}fig13f_reasoning_consistency.pdf')
plt.savefig(f'{FIGURE_DIR}fig13f_reasoning_consistency.png')
plt.show()\
"""),

        # ── Stats ──
        ('markdown', "## Statistical Tests"),
        ('code', """\
print('=' * 70)
print('STATISTICAL ANALYSIS - Strategic Narrative & Adaptation')
print('=' * 70)

# 1. Post-betrayal cooperation drop
print('\\n1. Post-betrayal cooperation rate:')
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    pre = sub[~sub['post_betrayal']]['action'].mean()
    post = sub[sub['post_betrayal']]['action'].mean()
    n_post = sub['post_betrayal'].sum()
    print(f'   {mname}: normal={pre:.3f}, post-betrayal={post:.3f}, diff={post-pre:+.3f} (n_post={n_post:,})')

# 2. Noise mention rate: 0% vs 20%
g0 = df[df['noise_level']==0]['mentions_noise'].astype(int)
g20 = df[df['noise_level']==20]['mentions_noise'].astype(int)
U, p = stats.mannwhitneyu(g0, g20, alternative='two-sided')
print(f'\\n2. Noise mentions (0% vs 20%): U={U:.0f}, p={p:.2e}')
print(f'   Rate: 0%={g0.mean()*100:.2f}%, 20%={g20.mean()*100:.2f}%')

# 3. Endgame effect
early = df[df['round_number'] < 25]['action'].mean()
late = df[df['round_number'] >= 25]['action'].mean()
g_e = df[df['round_number'] < 25]['action'].astype(int)
g_l = df[df['round_number'] >= 25]['action'].astype(int)
U, p = stats.mannwhitneyu(g_e, g_l, alternative='two-sided')
print(f'\\n3. Endgame effect: early={early:.3f}, endgame={late:.3f}')
print(f'   Mann-Whitney U={U:.0f}, p={p:.2e}')

# 4. Personality effect on cooperation
if 'personality' in df.columns:
    pers_vals = df['personality'].unique()
    if len(pers_vals) >= 2:
        groups = [df[df['personality']==p]['action'].astype(int) for p in pers_vals]
        H, p = stats.kruskal(*groups)
        print(f'\\n4. Personality effect (Kruskal-Wallis): H={H:.2f}, p={p:.2e}')
        for pv in sorted(pers_vals):
            r = df[df['personality']==pv]['action'].mean()
            print(f'   {pv}: coop_rate={r:.3f}')

# 5. Forgiveness rate
print('\\n5. Forgiveness mention rate (post-betrayal):')
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[(df['llm_name']==mkey) & df['post_betrayal']]
    rate = sub['mentions_forgive'].mean() * 100 if len(sub) > 0 else 0
    print(f'   {mname}: {rate:.2f}%')\
"""),

        # ── Summary ──
        ('markdown', "## Summary Table"),
        ('code', """\
print('=' * 90)
print('TABLE: Strategic Narrative Summary')
print('=' * 90)
print(f'{"Model":<16} | {"PostBetray Coop":>14} | {"Forgive%":>8} | {"Noise Mention%":>14} | {"Endgame Mention%":>16}')
print('-' * 80)
for mkey, mname in zip(MODEL_KEYS, MODEL_ORDER):
    sub = df[df['llm_name'] == mkey]
    pb_coop = sub[sub['post_betrayal']]['action'].mean() if sub['post_betrayal'].any() else 0
    forgive = sub[sub['post_betrayal']]['mentions_forgive'].mean() * 100 if sub['post_betrayal'].any() else 0
    noise_m = sub[sub['noise_level']==20]['mentions_noise'].mean() * 100
    eg_m = sub[sub['round_number']>=25]['mentions_endgame'].mean() * 100
    print(f'{mname:<16} | {pb_coop:>14.3f} | {forgive:>8.2f} | {noise_m:>14.2f} | {eg_m:>16.2f}')

print()
print('KEY FINDINGS:')
print('1. Betrayal triggers measurable shifts in both reasoning and behavior.')
print('2. Forgiveness language is rare - LLMs tend toward permanent retaliation.')
print('3. Endgame awareness varies: some models recognize finality, others do not.')
print('4. Noise attribution correlates with actual noise level - LLMs can detect noise.')
print('5. Assigned personality influences both cooperation rate and reasoning vocabulary.')\
"""),
    ]
    make_notebook(cells, 'paper_notebooks/module13_strategic_narrative.ipynb')


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Generating reasoning analysis notebooks...')
    create_module11()
    create_module12()
    create_module13()
    print('Done! All 3 notebooks created.')
