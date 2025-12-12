"""
Momentum Factor: Identify rising stocks
Academic research: Jegadeesh & Titman (1993), "Returns to Buying Winners"
"""
import pandas as pd
import numpy as np
from typing import Optional


class MomentumFactor:
    """
    Momentum factor based on 12-month returns (skip last month)
    Skipping last month avoids short-term reversal effect
    """
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        
    def calculate_score(self, ticker: str, date: pd.Timestamp) -> Optional[float]:
        """
        Calculate 12-month momentum score
        Returns: Raw 12-month return (will be ranked later)
        """
        try:
            # Get price data
            data = self.pipeline.get_data(ticker, end_date=date)
            
            if len(data) < 252:  # Need 12 months
                return None
                
            # Price 12 months ago
            price_12m = data['close'].iloc[-252]
            
            # Price 1 month ago (skip last month)
            price_1m = data['close'].iloc[-20] if len(data) >= 20 else data['close'].iloc[-1]
            
            # Calculate return
            momentum = (price_1m / price_12m) - 1
            
            return momentum
            
        except Exception as e:
            return None
            
    def calculate_batch(self, tickers: list, date: pd.Timestamp) -> pd.Series:
        """Calculate momentum for all stocks"""
        scores = {}
        
        for ticker in tickers:
            score = self.calculate_score(ticker, date)
            if score is not None:
                scores[ticker] = score
                
        return pd.Series(scores)