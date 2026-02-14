"""
SFEM (Strategy Frequency Estimation Method) for Prisoner's Dilemma.
Adapted from nicer_than_humans_icwsm25.

Based on: Romero, J. and Rosokha, Y. (2018) 'Constructing strategies in the
indefinitely repeated prisoner's dilemma game', European Economic Review.

Computes how well each candidate strategy explains the observed play.
"""

import numpy as np
from scipy.optimize import minimize


# ============================================================================
# Candidate Strategy Implementations (standalone, no game dependency)
# ============================================================================

class CandidateStrategy:
    """Base class for candidate strategies used in SFEM."""
    def __init__(self, name, label):
        self.name = name
        self.label = label
    
    def generate_alternative_history(self, main_history, opponent_history):
        """Generate what this strategy would have played given the opponent's history."""
        raise NotImplementedError


class AlwaysCooperate(CandidateStrategy):
    def __init__(self):
        super().__init__("AlwaysCooperate", "AC")
    
    def generate_alternative_history(self, main_history, opponent_history):
        return [1] * len(main_history)


class AlwaysDefect(CandidateStrategy):
    def __init__(self):
        super().__init__("AlwaysDefect", "AD")
    
    def generate_alternative_history(self, main_history, opponent_history):
        return [0] * len(main_history)


class TitForTat(CandidateStrategy):
    def __init__(self):
        super().__init__("TitForTat", "TFT")
    
    def generate_alternative_history(self, main_history, opponent_history):
        alt = [1]  # Cooperate first
        for i in range(1, len(opponent_history)):
            alt.append(opponent_history[i - 1])
        return alt


class SuspiciousTitForTat(CandidateStrategy):
    def __init__(self):
        super().__init__("SuspiciousTitForTat", "STFT")
    
    def generate_alternative_history(self, main_history, opponent_history):
        alt = [0]  # Defect first
        for i in range(1, len(opponent_history)):
            alt.append(opponent_history[i - 1])
        return alt


class Grim(CandidateStrategy):
    def __init__(self):
        super().__init__("Grim", "GRIM")
    
    def generate_alternative_history(self, main_history, opponent_history):
        alt = [1]  # Cooperate first
        triggered = False
        for i in range(1, len(opponent_history)):
            if opponent_history[i - 1] == 0:
                triggered = True
            alt.append(0 if triggered else 1)
        return alt


class WinStayLoseShift(CandidateStrategy):
    def __init__(self):
        super().__init__("WinStayLoseShift", "WSLS")
    
    def generate_alternative_history(self, main_history, opponent_history):
        alt = [1]  # Cooperate first
        for i in range(1, len(opponent_history)):
            # Win = both same action, Lose = different
            if alt[i - 1] == opponent_history[i - 1]:
                alt.append(1)  # Stay (cooperate)
            else:
                alt.append(0)  # Shift (defect)
        return alt


class RandomStrategy(CandidateStrategy):
    def __init__(self):
        super().__init__("Random", "RND")
    
    def generate_alternative_history(self, main_history, opponent_history):
        rng = np.random.default_rng()
        return list(rng.integers(2, size=len(main_history)))


# ============================================================================
# SFEM Algorithm
# ============================================================================

def get_default_strategies():
    """Return default set of candidate strategies for SFEM."""
    return [
        AlwaysDefect(),
        RandomStrategy(),
        AlwaysCooperate(),
        TitForTat(),
        SuspiciousTitForTat(),
        Grim(),
        WinStayLoseShift(),
    ]


def _objective(x, args):
    """Negative log-likelihood function."""
    C = args[0]
    E = args[1]
    bc = np.power(x[0], C)
    be = np.power(1 - x[0], E)
    prodBce = np.multiply(bc, be)
    res = np.log(np.maximum(np.dot(x[1:], prodBce), np.nextafter(0, 1))).sum()
    return -res


def _constraint(x):
    """Strategy proportions must sum to 1."""
    return x[1:].sum() - 1


def compute_sfem(game_histories, strategies=None, n_restarts=50):
    """
    Compute SFEM scores for a collection of game histories.
    
    Parameters
    ----------
    game_histories : list of dict
        Each dict has 'main_history' (list of 0/1) and 'opponent_history' (list of 0/1)
    strategies : list of CandidateStrategy, optional
        Strategies to evaluate. Default: AD, RND, AC, TFT, STFT, GRIM, WSLS
    n_restarts : int
        Number of random restarts for optimization (default: 50)
    
    Returns
    -------
    sfem_scores : np.ndarray
        Average proportion for each strategy
    strategy_labels : list of str
        Labels for each strategy
    """
    if strategies is None:
        strategies = get_default_strategies()
    
    num_strategies = len(strategies)
    strategy_labels = [s.label for s in strategies]
    n_games = len(game_histories)
    
    sfem_scores = np.zeros(num_strategies)
    
    for game in game_histories:
        main_history = game['main_history']
        opponent_history = game['opponent_history']
        
        # Compare LLM's play with each candidate strategy
        C = np.zeros(num_strategies)
        E = np.zeros(num_strategies)
        
        for k, strategy in enumerate(strategies):
            alt_history = strategy.generate_alternative_history(main_history, opponent_history)
            matched = [1 if main_history[i] == alt_history[i] else 0 
                      for i in range(len(main_history))]
            C[k] = np.sum(matched)
            E[k] = len(main_history) - C[k]
        
        # Optimization setup
        beta_bounds = (np.nextafter(0.5, 1), 1 - np.nextafter(0, 1))
        phi_bounds = (np.nextafter(0, 1), 1 - np.nextafter(0, 1))
        bounds = tuple([beta_bounds] + [phi_bounds] * num_strategies)
        constraints = {'type': 'eq', 'fun': _constraint}
        
        # Random restart optimization
        x0 = np.zeros(num_strategies + 1)
        x0[0] = 0.5 + 0.5 * np.random.random()
        temp = np.random.random(num_strategies)
        x0[1:] = temp / temp.sum()
        
        bestX = x0
        bestObjective = _objective(x0, [C, E])
        
        for _ in range(n_restarts):
            x0 = np.zeros(num_strategies + 1)
            x0[0] = 0.5 + 0.5 * np.random.random()
            temp = np.random.random(num_strategies)
            x0[1:] = temp / temp.sum()
            
            solution = minimize(
                _objective, x0, method='SLSQP',
                bounds=bounds, constraints=constraints, args=([C, E])
            )
            
            if bestObjective > solution.fun and solution.success:
                bestObjective = solution.fun
                bestX = solution.x
        
        sfem_scores += bestX[1:]
    
    sfem_scores = sfem_scores / n_games
    return sfem_scores, strategy_labels
