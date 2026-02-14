"""
Behavioral Profile Analysis for Prisoner's Dilemma.
Adapted from nicer_than_humans_icwsm25 (Romero & Rosokha, 2018).

Computes 5 behavioral dimensions:
- Niceness: Never defects first
- Forgiveness: Resumes cooperation after opponent defects
- Retaliation: Defects after unprovoked opponent defection
- Troublemaking: Defects when opponent cooperated
- Emulation: Copies opponent's previous action (TFT-like)
"""

import numpy as np


def compute_niceness(main_history, opponent_history):
    """1 if player never defects first (before opponent defects)."""
    n = len(main_history)
    is_nice = 1
    for i in range(n):
        if main_history[i] == 0:  # I defected
            is_nice = 0
            break
        if opponent_history[i] == 0 and main_history[i] == 1:
            # Opponent defected first, but I cooperated
            is_nice = 1
            break
    return is_nice


def compute_forgiveness(main_history, opponent_history):
    """Fraction of times player forgives after opponent defection."""
    n = len(main_history)
    opponent_defection = 0
    penalties = 0
    forgiven = 0
    holding_grudge = False
    for i in range(n):
        if main_history[i] == 1 and holding_grudge:
            forgiven += 1
            holding_grudge = False
        if i < n - 1 and opponent_history[i] == 1 and holding_grudge and main_history[i + 1] == 0:
            penalties += 1
        if opponent_history[i] == 0 and not holding_grudge:
            opponent_defection += 1
            holding_grudge = True
    forgiveness = forgiven / (opponent_defection + penalties) if (opponent_defection + penalties) > 0 else 0
    return forgiveness


def compute_retaliation(main_history, opponent_history):
    """Fraction of times player retaliates after unprovoked opponent defection."""
    n = len(main_history)
    reactions = 0
    provocations = 0
    for i in range(n - 1):
        if opponent_history[i] == 0:  # opponent defected
            if i == 0:
                reactions += 1 if main_history[i + 1] == 0 else 0
                provocations += 1
            else:
                if main_history[i - 1] == 1:  # unprovoked
                    reactions += 1 if main_history[i + 1] == 0 else 0
                    provocations += 1
    provocability = reactions / provocations if provocations > 0 else 0
    return provocability


def compute_troublemaking(main_history, opponent_history):
    """Fraction of times player defects when opponent cooperated."""
    n = len(main_history)
    uncalled_defection = 1 if main_history[0] == 0 else 0
    occasions = 1
    for i in range(n - 1):
        if opponent_history[i] == 1:
            occasions += 1
            uncalled_defection += 1 if main_history[i + 1] == 0 else 0
    troublemaking = uncalled_defection / occasions
    return troublemaking


def compute_emulation(main_history, opponent_history):
    """Fraction of times player copies opponent's previous action."""
    n = len(main_history)
    emulations = 0
    for i in range(n - 1):
        emulations += 1 if main_history[i + 1] == opponent_history[i] else 0
    emulation = emulations / (n - 1) if n > 1 else 0
    return emulation


behavioral_dimensions = {
    "nice": compute_niceness,
    "forgiving": compute_forgiveness,
    "retaliatory": compute_retaliation,
    "troublemaking": compute_troublemaking,
    "emulative": compute_emulation
}


class BehavioralProfile:
    """Behavioral profile for an agent across multiple games."""
    
    def __init__(self, strategy_name, opponent_name="opponent"):
        self.strategy_name = strategy_name
        self.opponent_name = opponent_name
        self.n_games = 0
        self.dimensions = {dim: [] for dim in behavioral_dimensions.keys()}
    
    def compute_dimensions(self, main_history, opponent_history):
        for dimension_name, dimension_function in behavioral_dimensions.items():
            self.dimensions[dimension_name].append(
                dimension_function(main_history, opponent_history)
            )
        self.n_games += 1
    
    def get_means(self):
        return {dim: np.mean(vals) if vals else 0 for dim, vals in self.dimensions.items()}
    
    def get_stds(self):
        return {dim: np.std(vals) if vals else 0 for dim, vals in self.dimensions.items()}
    
    def __sub__(self, other):
        sub_profile = BehavioralProfile(
            f"{self.strategy_name}-{other.strategy_name}", self.opponent_name
        )
        n_games = min(self.n_games, other.n_games)
        sub_profile.n_games = n_games
        for dimension_name in self.dimensions.keys():
            sub_profile.dimensions[dimension_name] = [
                self.dimensions[dimension_name][idx] - other.dimensions[dimension_name][idx]
                for idx in range(n_games)
            ] if dimension_name in other.dimensions else self.dimensions[dimension_name]
        return sub_profile
    
    def __abs__(self):
        abs_profile = BehavioralProfile(f"abs({self.strategy_name})", self.opponent_name)
        abs_profile.n_games = self.n_games
        for dimension_name in self.dimensions.keys():
            abs_profile.dimensions[dimension_name] = [abs(val) for val in self.dimensions[dimension_name]]
        return abs_profile
