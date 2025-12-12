"""
Portfolio rebalancing logic
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from src.portfolio.constructor import Portfolio


@dataclass
class RebalanceAction:
    """Single rebalancing action"""
    ticker: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    old_weight: float
    new_weight: float
    change: float


class Rebalancer:
    """
    Rebalance portfolio monthly
    """
    
    def __init__(self, turnover_constraint: float = 0.5):
        """
        Args:
            turnover_constraint: Max fraction of portfolio to turn over (0.5 = 50%)
        """
        self.turnover_constraint = turnover_constraint
        
    def calculate_rebalance(self,
                           old_portfolio: Portfolio,
                           new_portfolio: Portfolio) -> List[RebalanceAction]:
        """
        Calculate what trades are needed to rebalance
        
        Args:
            old_portfolio: Current holdings
            new_portfolio: Target holdings
        
        Returns:
            List of actions (buy, sell, hold)
        """
        actions = []
        
        all_tickers = set(old_portfolio.holdings.keys()) | set(new_portfolio.holdings.keys())
        
        for ticker in all_tickers:
            old_weight = old_portfolio.holdings.get(ticker, 0.0)
            new_weight = new_portfolio.holdings.get(ticker, 0.0)
            change = new_weight - old_weight
            
            if abs(change) < 0.001:  # Ignore tiny changes
                action = 'HOLD'
            elif change > 0:
                action = 'BUY'
            else:
                action = 'SELL'
            
            actions.append(RebalanceAction(
                ticker=ticker,
                action=action,
                old_weight=old_weight,
                new_weight=new_weight,
                change=change
            ))
        
        # Sort by absolute change (largest first)
        actions.sort(key=lambda x: abs(x.change), reverse=True)
        
        return actions
    
    def calculate_turnover(self, actions: List[RebalanceAction]) -> float:
        """
        Calculate portfolio turnover
        Turnover = sum(abs(weight changes)) / 2
        """
        total_change = sum(abs(action.change) for action in actions)
        return total_change / 2
    
    def apply_turnover_constraint(self,
                                   actions: List[RebalanceAction]) -> List[RebalanceAction]:
        """
        Apply turnover constraint by limiting trades
        Keep largest changes up to turnover limit
        """
        turnover = self.calculate_turnover(actions)
        
        if turnover <= self.turnover_constraint:
            return actions
        
        # Sort by absolute change
        sorted_actions = sorted(actions, key=lambda x: abs(x.change), reverse=True)
        
        constrained_actions = []
        cumulative_turnover = 0
        
        for action in sorted_actions:
            if cumulative_turnover + abs(action.change) / 2 <= self.turnover_constraint:
                constrained_actions.append(action)
                cumulative_turnover += abs(action.change) / 2
            else:
                # Convert to HOLD
                constrained_actions.append(RebalanceAction(
                    ticker=action.ticker,
                    action='HOLD',
                    old_weight=action.old_weight,
                    new_weight=action.old_weight,
                    change=0
                ))
        
        return constrained_actions
    
    def print_rebalance_actions(self, actions: List[RebalanceAction]):
        """Print rebalancing actions"""
        print("\n" + "=" * 70)
        print("REBALANCE ACTIONS")
        print("=" * 70)
        
        buys = [a for a in actions if a.action == 'BUY']
        sells = [a for a in actions if a.action == 'SELL']
        holds = [a for a in actions if a.action == 'HOLD']
        
        turnover = self.calculate_turnover(actions)
        
        print(f"\nSummary:")
        print(f"  Buy:      {len(buys)} positions")
        print(f"  Sell:     {len(sells)} positions")
        print(f"  Hold:     {len(holds)} positions")
        print(f"  Turnover: {turnover:.2%}")
        
        if buys:
            print(f"\nBUY:")
            for action in buys:
                print(f"  {action.ticker:6s}  {action.old_weight:6.2%} → {action.new_weight:6.2%}  (+{action.change:6.2%})")
        
        if sells:
            print(f"\nSELL:")
            for action in sells:
                print(f"  {action.ticker:6s}  {action.old_weight:6.2%} → {action.new_weight:6.2%}  ({action.change:6.2%})")