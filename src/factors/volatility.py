"""
Low Volatility Factor: Identify stable stocks
Academic research: Ang et al. (2006), "The Cross-Section of Volatility and Expected Returns"
Low volatility stocks paradoxically outperform high volatility stocks
"""
import pandas as pd
import numpy as np
from typing import Optional


class VolatilityFactor:
    """
    Low volatility factor
    Calculates 60-day volatility and inverts (lower vol = higher score)
    """
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        
    def calculate_score(self, ticker: str, date: pd.Timestamp) -> Optional[float]:
        """
        Calculate volatility score
        Returns: Negative volatility (so low vol ranks high)
        """
        try:
            # Get price data
            data = self.pipeline.get_data(ticker, end_date=date)
            
            if len(data) < 60:
                return None
                
            # Calculate 60-day volatility
            returns = data['close'].pct_change().iloc[-60:]
            volatility = returns.std() * np.sqrt(252)  # Annualised
            
            # Return negative (so low vol = high score)
            return -volatility
            
        except Exception as e:
            return None
            
    def calculate_batch(self, tickers: list, date: pd.Timestamp) -> pd.Series:
        """Calculate volatility for all stocks"""
        scores = {}
        
        for ticker in tickers:
            score = self.calculate_score(ticker, date)
            if score is not None:
                scores[ticker] = score
                
        return pd.Series(scores)