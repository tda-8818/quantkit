"""
Moving average crossover strategy
Classic trend-following approach
"""
import pandas as pd
from src.strategies.base import Strategy


class SimpleMovingAverageCrossover(Strategy):
    """
    Simple moving average crossover strategy.
    
    Rules:
        - Buy when fast MA crosses above slow MA
        - Sell when fast MA crosses below slow MA
    """
    
    def __init__(self, data: pd.DataFrame, fast_period: int = 50, slow_period: int = 200):
        """
        Args:
            fast_period: Fast moving average period
            slow_period: Slow moving average period
        """
        super().__init__(data)
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self) -> pd.Series:
        """Generate MA crossover signals"""
        # Calculate moving averages
        fast_ma = self.data['close'].rolling(window=self.fast_period).mean()
        slow_ma = self.data['close'].rolling(window=self.slow_period).mean()
        
        # Generate signals (vectorized!)
        signals = pd.Series(0, index=self.data.index)
        signals[fast_ma > slow_ma] = 1   # Long when fast > slow
        signals[fast_ma < slow_ma] = -1  # Short when fast < slow
        
        return signals