"""
Mean reversion strategy implementation
Buy when oversold, sell when overbought
"""
import pandas as pd
from src.strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    """
    Buy when price below moving average (oversold)
    Sell when price above moving average (overbought)
    """
    
    def __init__(self, data: pd.DataFrame, lookback: int = 20):
        super().__init__(data)
        self.lookback = lookback
        
    def generate_signals(self) -> pd.Series:
        """
        Signal logic:
        - Buy (1) when price < MA (expecting reversion up)
        - Sell (-1) when price > MA (expecting reversion down)
        """
        ma = self.data['close'].rolling(window=self.lookback).mean()
        
        signals = pd.Series(0, index=self.data.index)
        signals[self.data['close'] < ma] = 1   # Price below MA = buy
        signals[self.data['close'] > ma] = -1  # Price above MA = sell
        
        return signals