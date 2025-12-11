import pandas as pd
import numpy as np
from typing import List, Dict
from src.data.pipeline import MarketDataPipeline

class SimpleFactorModel:
    """
    3-Factor model: Value + Momentum + Quality
    Simplified version using price data only (no fundamentals yet)
    """
    
    def __init__(self, pipeline: MarketDataPipeline):
        self.pipeline = pipeline
        
    def calculate_momentum(self, ticker: str, date: pd.Timestamp) -> float:
        """
        12-month momentum (skip last month)
        Returns: Percentile rank (0-1)
        """
        data = self.pipeline.get_data(ticker, end_date=date)
        
        if len(data) < 252:
            return 0.0
            
        # 12-month return, skip last 20 days (1 month)
        price_12m_ago = data['close'].iloc[-252]
        price_1m_ago = data['close'].iloc[-20]
        
        momentum = (price_1m_ago / price_12m_ago) - 1
        return momentum
        
    def calculate_volatility(self, ticker: str, date: pd.Timestamp) -> float:
        """
        Low volatility factor (inverse - lower is better)
        Returns: Negative of volatility (for ranking)
        """
        data = self.pipeline.get_data(ticker, end_date=date)
        
        if len(data) < 60:
            return 0.0
            
        returns = data['close'].pct_change().iloc[-60:]  # 60-day volatility
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        return -volatility  # Negative so low vol ranks high
        
    def calculate_trend_strength(self, ticker: str, date: pd.Timestamp) -> float:
        """
        Quality proxy: Is stock in uptrend?
        Returns: % of days above 50-day MA
        """
        data = self.pipeline.get_data(ticker, end_date=date)
        
        if len(data) < 100:
            return 0.0
            
        ma_50 = data['close'].rolling(50).mean()
        recent_data = data.iloc[-50:]
        recent_ma = ma_50.iloc[-50:]
        
        days_above_ma = (recent_data['close'] > recent_ma).sum()
        trend_strength = days_above_ma / 50
        
        return trend_strength
        
    def rank_universe(self, tickers: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """
        Rank all tickers by combined factor score
        """
        scores = []
        
        for ticker in tickers:
            try:
                momentum = self.calculate_momentum(ticker, date)
                volatility = self.calculate_volatility(ticker, date)
                trend = self.calculate_trend_strength(ticker, date)
                
                scores.append({
                    'ticker': ticker,
                    'momentum': momentum,
                    'volatility': volatility,
                    'trend': trend,
                    'date': date
                })
            except Exception as e:
                print(f"Error calculating factors for {ticker}: {e}")
                
        df = pd.DataFrame(scores)
        
        # Convert to percentile ranks (0-1)
        df['momentum_rank'] = df['momentum'].rank(pct=True)
        df['volatility_rank'] = df['volatility'].rank(pct=True)
        df['trend_rank'] = df['trend'].rank(pct=True)
        
        # Combined score (equal weight)
        df['combined_score'] = (
            df['momentum_rank'] * 0.4 +      # 40% momentum
            df['volatility_rank'] * 0.3 +    # 30% low vol
            df['trend_rank'] * 0.3           # 30% trend
        )
        
        # Sort by combined score
        df = df.sort_values('combined_score', ascending=False)
        
        return df