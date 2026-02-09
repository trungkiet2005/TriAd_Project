"""
Belief Tracking and Bayesian Theory of Mind Analysis

Analyzes whether LLMs can distinguish between:
- Strategic defectors (intentional betrayal)
- Random noise (execution errors)

Key metrics:
- Brier Score: Belief calibration
- Attribution Rate: % times agent correctly attributes defection to noise vs strategy
- Belief Update Dynamics: How beliefs change after observing actions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


class BeliefAnalyzer:
    """
    Analyzes belief tracking in multi-agent games under noise.
    
    UAI Focus: Bayesian Theory of Mind in LLMs
    - Do LLMs maintain accurate beliefs about opponent intentions?
    - Can they separate signal (strategy) from noise (errors)?
    """
    
    def __init__(self):
        """Initialize belief analyzer."""
        pass
    
    def calculate_brier_score(self, predictions: List[float], outcomes: List[int]) -> float:
        """
        Calculate Brier score for belief calibration.
        
        Brier Score = (1/N) * Σ(predicted_prob - actual_outcome)²
        Lower is better (0 = perfect, 1 = worst)
        
        Args:
            predictions: List of predicted probabilities (0-100)
            outcomes: List of actual outcomes (0 or 1, where 1 = cooperate)
            
        Returns:
            Brier score (0-1 scale)
        """
        if len(predictions) != len(outcomes):
            raise ValueError("Predictions and outcomes must have same length")
        
        if not predictions:
            return np.nan
        
        # Convert predictions from 0-100 to 0-1 scale
        probs = np.array(predictions) / 100.0
        actual = np.array(outcomes)
        
        # Calculate Brier score
        brier = np.mean((probs - actual) ** 2)
        return float(brier)
    
    def calculate_agent_brier_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Brier scores for each agent's beliefs about opponents.
        
        Args:
            df: DataFrame with columns: round, agent_name, beliefs, opponent_actions
            
        Returns:
            DataFrame with columns: agent_name, opponent, brier_score, n_predictions
        """
        results = []
        
        # Group by game and agent
        grouped = df.groupby(['game_id', 'agent_name'])
        
        for (game_id, agent_name), game_df in grouped:
            # Get agent's beliefs about each opponent
            for round_idx, row in game_df.iterrows():
                beliefs = row.get('beliefs', {})
                
                if not beliefs:
                    continue
                
                # Extract beliefs about each opponent
                for opp_key, pred_prob in beliefs.items():
                    if not isinstance(pred_prob, (int, float)):
                        continue
                    
                    # Find actual opponent action this round
                    opponent_name = self._extract_opponent_name(opp_key, game_df)
                    if opponent_name:
                        actual_action = self._get_opponent_action(
                            game_df, opponent_name, row['round']
                        )
                        
                        if actual_action is not None:
                            results.append({
                                'game_id': game_id,
                                'round': row['round'],
                                'agent_name': agent_name,
                                'opponent': opponent_name,
                                'predicted_prob': pred_prob,
                                'actual_action': actual_action
                            })
        
        if not results:
            return pd.DataFrame()
        
        results_df = pd.DataFrame(results)
        
        # Calculate Brier score per agent-opponent pair
        brier_scores = []
        for (agent, opponent), group in results_df.groupby(['agent_name', 'opponent']):
            brier = self.calculate_brier_score(
                group['predicted_prob'].tolist(),
                group['actual_action'].tolist()
            )
            brier_scores.append({
                'agent_name': agent,
                'opponent': opponent,
                'brier_score': brier,
                'n_predictions': len(group)
            })
        
        return pd.DataFrame(brier_scores)
    
    def analyze_noise_attribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze whether agents correctly attribute defections to noise vs strategy.
        
        Key question: When opponent defects, does the agent:
        - Update beliefs conservatively (suspect noise)?
        - Update beliefs drastically (suspect strategic betrayal)?
        
        Args:
            df: DataFrame with history of beliefs and actions
            
        Returns:
            DataFrame with attribution analysis
        """
        results = []
        
        grouped = df.groupby(['game_id', 'agent_name'])
        
        for (game_id, agent_name), game_df in grouped:
            game_df = game_df.sort_values('round')
            
            for i in range(1, len(game_df)):
                prev_row = game_df.iloc[i-1]
                curr_row = game_df.iloc[i]
                
                # Get beliefs from both rounds
                prev_beliefs = prev_row.get('beliefs', {})
                curr_beliefs = curr_row.get('beliefs', {})
                
                if not prev_beliefs or not curr_beliefs:
                    continue
                
                # For each opponent, check if they defected
                for opp_key in prev_beliefs.keys():
                    opponent_name = self._extract_opponent_name(opp_key, game_df)
                    if not opponent_name:
                        continue
                    
                    # Check if opponent defected in previous round
                    prev_action = self._get_opponent_action(
                        game_df, opponent_name, prev_row['round']
                    )
                    
                    if prev_action == 0:  # Defected
                        # How did belief change?
                        prev_prob = prev_beliefs.get(opp_key, 50)
                        curr_prob = curr_beliefs.get(opp_key, prev_prob)
                        
                        belief_change = curr_prob - prev_prob
                        
                        # Get opponent's noise rate
                        noise_rate = self._get_opponent_noise_rate(
                            game_df, opponent_name
                        )
                        
                        # Classify attribution
                        # If belief drops a lot (> 20%), suspect strategic
                        # If belief drops little (< 10%), suspect noise
                        attribution = self._classify_attribution(
                            belief_change, noise_rate
                        )
                        
                        results.append({
                            'game_id': game_id,
                            'round': curr_row['round'],
                            'agent_name': agent_name,
                            'opponent': opponent_name,
                            'opponent_noise_rate': noise_rate,
                            'prev_belief': prev_prob,
                            'curr_belief': curr_prob,
                            'belief_change': belief_change,
                            'attribution': attribution
                        })
        
        return pd.DataFrame(results)
    
    def calculate_belief_update_dynamics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze how beliefs evolve over rounds.
        
        Metrics:
        - Belief volatility: Std dev of belief changes
        - Forgiveness rate: % of times belief increases after defection
        - Learning rate: How quickly beliefs converge
        
        Args:
            df: DataFrame with round-by-round beliefs
            
        Returns:
            Dictionary of dynamics metrics
        """
        belief_changes = []
        forgiveness_events = []
        
        grouped = df.groupby(['game_id', 'agent_name'])
        
        for (game_id, agent_name), game_df in grouped:
            game_df = game_df.sort_values('round')
            
            for i in range(1, len(game_df)):
                prev_beliefs = game_df.iloc[i-1].get('beliefs', {})
                curr_beliefs = game_df.iloc[i].get('beliefs', {})
                
                for opp_key in prev_beliefs.keys():
                    if opp_key in curr_beliefs:
                        prev_prob = prev_beliefs[opp_key]
                        curr_prob = curr_beliefs[opp_key]
                        
                        change = curr_prob - prev_prob
                        belief_changes.append(change)
                        
                        # Check if this was after defection
                        opponent_name = self._extract_opponent_name(opp_key, game_df)
                        if opponent_name:
                            prev_action = self._get_opponent_action(
                                game_df, opponent_name, game_df.iloc[i-1]['round']
                            )
                            if prev_action == 0 and change > 0:
                                forgiveness_events.append(1)
                            elif prev_action == 0:
                                forgiveness_events.append(0)
        
        if not belief_changes:
            return {
                'volatility': np.nan,
                'forgiveness_rate': np.nan,
                'mean_change': np.nan
            }
        
        return {
            'volatility': float(np.std(belief_changes)),
            'forgiveness_rate': float(np.mean(forgiveness_events)) if forgiveness_events else np.nan,
            'mean_change': float(np.mean(belief_changes)),
            'median_change': float(np.median(belief_changes))
        }
    
    def generate_belief_summary(self, df: pd.DataFrame) -> str:
        """
        Generate qualitative narrative about belief dynamics.
        
        Args:
            df: DataFrame with belief tracking data
            
        Returns:
            Narrative string suitable for paper
        """
        # Calculate metrics
        brier_scores = self.calculate_agent_brier_scores(df)
        attribution_df = self.analyze_noise_attribution(df)
        dynamics = self.calculate_belief_update_dynamics(df)
        
        if brier_scores.empty or attribution_df.empty:
            return "Insufficient belief data for analysis."
        
        # Calculate summary statistics
        mean_brier = brier_scores['brier_score'].mean()
        calibration = "well-calibrated" if mean_brier < 0.15 else "poorly calibrated"
        
        # Attribution rates
        if 'attribution' in attribution_df.columns:
            noise_attr_rate = (attribution_df['attribution'] == 'noise').mean()
            strategic_attr_rate = (attribution_df['attribution'] == 'strategic').mean()
        else:
            noise_attr_rate = 0
            strategic_attr_rate = 0
        
        forgiveness_rate = dynamics.get('forgiveness_rate', 0)
        
        narrative = f"""
Belief Tracking Analysis (Bayesian Theory of Mind):

Agents exhibited {calibration} beliefs (Brier score = {mean_brier:.3f}). 
When opponents defected, agents attributed {noise_attr_rate*100:.1f}% to noise 
and {strategic_attr_rate*100:.1f}% to strategic betrayal. 

The forgiveness rate was {forgiveness_rate*100:.1f}% (increasing trust after 
defection), suggesting {"charitable" if forgiveness_rate > 0.3 else "punitive"} 
belief updates under uncertainty.

Belief volatility (σ = {dynamics['volatility']:.2f}) indicates 
{"stable" if dynamics['volatility'] < 5 else "unstable"} opponent modeling.
"""
        return narrative.strip()
    
    # Helper methods
    def _extract_opponent_name(self, opp_key: str, game_df: pd.DataFrame) -> Optional[str]:
        """Extract opponent name from belief key like 'opponent1_prob'."""
        # This is a simplified version - you may need to adapt based on your data structure
        if 'opponent1' in opp_key:
            opponents = [name for name in game_df['agent_name'].unique() 
                        if name != game_df['agent_name'].iloc[0]]
            return opponents[0] if opponents else None
        elif 'opponent2' in opp_key:
            opponents = [name for name in game_df['agent_name'].unique() 
                        if name != game_df['agent_name'].iloc[0]]
            return opponents[1] if len(opponents) > 1 else None
        return None
    
    def _get_opponent_action(self, game_df: pd.DataFrame, opponent_name: str, 
                            round_num: int) -> Optional[int]:
        """Get opponent's action (0=defect, 1=cooperate) in a specific round."""
        opp_rows = game_df[(game_df['agent_name'] == opponent_name) & 
                          (game_df['round'] == round_num)]
        if not opp_rows.empty:
            action_str = opp_rows.iloc[0].get('strategy', 'Defect')
            return 1 if 'cooperate' in action_str.lower() else 0
        return None
    
    def _get_opponent_noise_rate(self, game_df: pd.DataFrame, opponent_name: str) -> float:
        """Get opponent's noise rate from game config."""
        # This should be extracted from game metadata
        # For now, return a placeholder
        return 0.1  # 10% noise
    
    def _classify_attribution(self, belief_change: float, noise_rate: float) -> str:
        """
        Classify whether agent attributes defection to noise or strategy.
        
        Heuristic:
        - Small belief drop (< noise_rate * 100) → attributed to noise
        - Large belief drop (> noise_rate * 150) → attributed to strategy
        """
        threshold_noise = -noise_rate * 100  # Convert to percentage
        threshold_strategic = threshold_noise * 1.5
        
        if belief_change > threshold_noise:
            return 'noise'  # Charitable interpretation
        elif belief_change < threshold_strategic:
            return 'strategic'  # Suspicious interpretation
        else:
            return 'uncertain'
