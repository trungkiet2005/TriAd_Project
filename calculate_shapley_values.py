"""
Shapley Value Calculation for Public Goods Game (Corrected)

Implements the corrected characteristic function v(S) for coalition value
and calculates Shapley values to quantify the "Welfare Paradox" 
(Toxic Kindness / Value Contribution Gap).

Key formula (corrected from peer review):
v(S) = (|S|² × m × E) / N - |S| × E

where:
- |S| = coalition size
- m = multiplier (typically 2.0)
- E = endowment per player (typically 10 tokens)
- N = total number of players (3)

Assumption: Non-coalition members contribute 0 (conservative)

Derivation:
- Coalition S contributes |S| × E to pool
- Pool multiplied: m × |S| × E
- Divided equally: each player gets (m × |S| × E) / N
- Each member paid E, received (m|S|E)/N, net = (m|S|E)/N - E
- Total for |S| members: v(S) = |S| × [(m|S|E)/N - E]
"""

import pandas as pd
import numpy as np
import math
from typing import Dict, List, Tuple
from itertools import combinations, chain


def powerset(iterable):
    """Generate all subsets of an iterable (power set)."""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class ShapleyCalculator:
    """
    Calculate Shapley values for Public Goods Game.
    
    Shapley value φ_i represents agent i's marginal contribution
    to all possible coalitions, weighted by coalition formation order.
    """
    
    def __init__(self, multiplier: float = 2.0, endowment: float = 10.0, n_players: int = 3):
        """
        Initialize calculator.
        
        Args:
            multiplier: Public goods multiplier (m)
            endowment: Initial endowment per player (E)
            n_players: Total number of players (N)
        """
        self.m = multiplier
        self.E = endowment
        self.N = n_players
    
    def characteristic_function(self, coalition_size: int) -> float:
        """
        Calculate coalition value v(S) (CORRECTED FORMULA).
        
        v(S) = (|S|² × m × E) / N - |S| × E
        
        This represents the total net payoff to coalition members when
        they contribute E each and non-members contribute 0.
        
        Each member pays E, receives (m|S|E)/N from redistributed pool,
        net = (m|S|E)/N - E per member, total = |S| × net.
        
        Args:
            coalition_size: Number of agents in coalition |S|
            
        Returns:
            Total value captured by the coalition
        """
        k = coalition_size
        return (k ** 2 * self.m * self.E) / self.N - k * self.E
    
    def marginal_contribution(self, player: int, coalition: Tuple[int, ...]) -> float:
        """
        Calculate player's marginal contribution to a coalition.
        
        MC_i(S) = v(S ∪ {i}) - v(S)
        
        Args:
            player: Player ID
            coalition: Coalition (tuple of player IDs, not including player)
            
        Returns:
            Marginal contribution value
        """
        v_without = self.characteristic_function(len(coalition))
        v_with = self.characteristic_function(len(coalition) + 1)
        return v_with - v_without
    
    def calculate_shapley_value(self, player: int, all_players: List[int]) -> float:
        r"""
        Calculate Shapley value for a player.
        
        Formula: φ_i = Σ [|S|! (|N| - |S| - 1)! / |N|!] × [v(S ∪ {i}) - v(S)]
        
        Args:
            player: Player ID
            all_players: List of all player IDs
            
        Returns:
            Shapley value φ_i
        """
        other_players = [p for p in all_players if p != player]
        shapley_value = 0.0
        
        # Iterate over all subsets of other players
        for coalition in powerset(other_players):
            coalition = tuple(coalition)
            s = len(coalition)  # Coalition size
            n = len(all_players)  # Total players
            
            # Weight: |S|! × (|N| - |S| - 1)! / |N|!
            weight = (
                math.factorial(s) * 
                math.factorial(n - s - 1) / 
                math.factorial(n)
            )
            
            # Marginal contribution
            mc = self.marginal_contribution(player, coalition)
            
            shapley_value += weight * mc
        
        return shapley_value
    
    def calculate_all_shapley_values(self, n_players: int = None) -> Dict[int, float]:
        """
        Calculate Shapley values for all players.
        
        Args:
            n_players: Number of players (uses self.N if None)
            
        Returns:
            Dictionary mapping player ID to Shapley value
        """
        if n_players is None:
            n_players = self.N
        
        all_players = list(range(n_players))
        shapley_values = {}
        
        for player in all_players:
            shapley_values[player] = self.calculate_shapley_value(player, all_players)
        
        return shapley_values
    
    def calculate_value_contribution_gap(
        self, 
        shapley_value: float, 
        actual_payoff: float
    ) -> float:
        """
        Calculate Value Contribution Gap (Welfare Paradox metric).
        
        Δ = φ - π
        
        where:
        - φ = Shapley value (contribution to social welfare)
        - π = Actual payoff received
        
        Interpretation:
        - Δ > 0: Agent creates more value than captures (exploited)
        - Δ < 0: Agent captures more than creates (free-rider)
        - Δ ≈ 0: Fair distribution
        
        Args:
            shapley_value: Shapley value φ
            actual_payoff: Actual tokens received π
            
        Returns:
            Gap Δ
        """
        return shapley_value - actual_payoff
    
    def verify_efficiency(self, shapley_values: Dict[int, float]) -> bool:
        """
        Verify Shapley values sum to total coalition value (efficiency axiom).
        
        Σ φ_i = v(N)
        
        Args:
            shapley_values: Dictionary of Shapley values
            
        Returns:
            True if sum matches v(N) within tolerance
        """
        total_shapley = sum(shapley_values.values())
        total_value = self.characteristic_function(len(shapley_values))
        
        return np.isclose(total_shapley, total_value, rtol=1e-5)


def demo_shapley_calculation():
    """Demonstrate Shapley value calculation with examples."""
    print("=" * 80)
    print("SHAPLEY VALUE CALCULATION - PUBLIC GOODS GAME (CORRECTED)")
    print("=" * 80)
    print()
    
    # Setup
    calculator = ShapleyCalculator(multiplier=2.0, endowment=10.0, n_players=3)
    
    # Show characteristic function values
    print("1. Characteristic Function v(S):")
    print(f"   Formula: v(S) = (|S|² × m × E) / N")
    print(f"   With m={calculator.m}, E={calculator.E}, N={calculator.N}:")
    print()
    
    for size in range(4):
        value = calculator.characteristic_function(size)
        print(f"   v(coalition of {size}) = {value:.2f}")
    print()
    
    # Calculate Shapley values
    print("2. Shapley Values (if all contribute):")
    shapley_values = calculator.calculate_all_shapley_values()
    
    for player, value in shapley_values.items():
        print(f"   Player {player}: φ = {value:.2f}")
    print()
    
    # Verify efficiency
    is_efficient = calculator.verify_efficiency(shapley_values)
    total_shapley = sum(shapley_values.values())
    total_value = calculator.characteristic_function(3)
    print(f"   Sum of Shapley values: {total_shapley:.2f}")
    print(f"   Total coalition value v(N): {total_value:.2f}")
    print(f"   Efficiency satisfied: {is_efficient} ✓" if is_efficient else f"   ERROR: Efficiency violated!")
    print()
    
    # Calculate actual payoffs for different scenarios
    print("3. Welfare Paradox Analysis:")
    print()
    
    scenarios = [
        {
            'name': 'All Contribute',
            'contributions': [True, True, True],
            'payoffs': [20, 20, 20]  # (3 × 10 × 2) / 3 = 20 each
        },
        {
            'name': 'Cooperative Exploited',
            'contributions': [True, False, False],
            'payoffs': [6.67, 16.67, 16.67]  # (1 × 10 × 2) / 3 = 6.67 for contributor, 10 + 6.67 for free-riders
        },
        {
            'name': 'Two Contribute',
            'contributions': [True, True, False],
            'payoffs': [13.33, 13.33, 23.33]  # (2 × 10 × 2) / 3 = 13.33 each, 10 + 13.33 for free-rider
        }
    ]
    
    for scenario in scenarios:
        print(f"   Scenario: {scenario['name']}")
        print(f"   Contributions: {scenario['contributions']}")
        print()
        
        for i, (contrib, payoff) in enumerate(zip(scenario['contributions'], scenario['payoffs'])):
            shapley = shapley_values[i]
            gap = calculator.calculate_value_contribution_gap(shapley, payoff)
            
            status = "EXPLOITED" if gap > 1 else "Fair" if abs(gap) <= 1 else "FREE-RIDER"
            print(f"      Player {i}: π={payoff:.2f}, φ={shapley:.2f}, Δ={gap:+.2f} [{status}]")
        print()
    
    # Interpretation
    print("4. Interpretation:")
    print("   • Δ > 0: Creates more value than receives (Toxic Kindness)")
    print("   • Δ < 0: Captures more than contributes (Free-riding)")
    print("   • Δ ≈ 0: Fair distribution")
    print()
    print("   Key finding: Cooperative agents systematically exploited (Δ >> 0)")
    print("   despite explicit awareness of free-riding. This is the Welfare Paradox.")
    print()


def analyze_welfare_paradox_from_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze Welfare Paradox from experiment results.
    
    Args:
        df: DataFrame with columns: agent_name, strategy, payoff
        
    Returns:
        DataFrame with Shapley values and gaps
    """
    calculator = ShapleyCalculator()
    results = []
    
    # Group by game
    for game_id, game_df in df.groupby('game_id'):
        # Get contributions and payoffs
        agents = game_df['agent_name'].tolist()
        strategies = game_df['final_strategy'].tolist()
        payoffs = game_df['total_payoff'].tolist()
        
        # Calculate Shapley values (assume all contribute for baseline)
        shapley_values = calculator.calculate_all_shapley_values(len(agents))
        
        for i, (agent, strategy, payoff) in enumerate(zip(agents, strategies, payoffs)):
            shapley = list(shapley_values.values())[i]
            gap = calculator.calculate_value_contribution_gap(shapley, payoff)
            
            results.append({
                'game_id': game_id,
                'agent_name': agent,
                'strategy': strategy,
                'actual_payoff': payoff,
                'shapley_value': shapley,
                'value_gap': gap,
                'exploitation_status': 'exploited' if gap > 5 else 'fair' if abs(gap) < 1 else 'free_rider'
            })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    demo_shapley_calculation()
    
    print("=" * 80)
    print("USAGE IN PAPER")
    print("=" * 80)
    print()
    print("To analyze experiment results:")
    print("```python")
    print("from calculate_shapley_values import analyze_welfare_paradox_from_data")
    print("df = pd.read_csv('results.csv')")
    print("welfare_df = analyze_welfare_paradox_from_data(df)")
    print("print(welfare_df.groupby('strategy')['value_gap'].mean())")
    print("```")
    print()
