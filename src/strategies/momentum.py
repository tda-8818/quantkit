"""
Momentum strategy implementation
Academic factor: Buy winners, sell losers
"""
import pandas as pd
from src.strategies.base import Strategy


class MomentumStrategy(Strategy):
    """
    12-month momentum strategy (academic factor).
    
    Rules:
        - Buy if 12-month return is positive
        - Sell if 12-month return is negative
    """
    
    def __init__(self, data: pd.DataFrame, lookback: int = 252):
        """
        Args:
            lookback: Lookback period in days (252 = 12 months)
        """
        super().__init__(data)
        self.lookback = lookback
    
    def generate_signals(self) -> pd.Series:
        """Generate momentum signals"""
        # Calculate 12-month returns
        returns_12m = self.data['close'].pct_change(self.lookback)
        
        # Generate signals
        signals = pd.Series(0, index=self.data.index)
        signals[returns_12m > 0] = 1   # Long if positive momentum
        signals[returns_12m < 0] = -1  # Short if negative momentum
        
        return signals