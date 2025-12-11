"""
Base strategy class for all trading strategies
"""
import pandas as pd


class Strategy:
    """
    Base class for trading strategies.
    
    Subclass this and implement generate_signals() method.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize strategy with price data.
        
        Args:
            data: DataFrame with OHLCV columns and datetime index
        """
        self.data = data.copy()
        self.signals = None
    
    def generate_signals(self) -> pd.Series:
        """
        Generate trading signals.
        
        Returns:
            Series with values: 1 (long), 0 (flat), -1 (short)
        """
        raise NotImplementedError("Must implement generate_signals()")