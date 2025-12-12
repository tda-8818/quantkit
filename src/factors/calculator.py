"""
Multi-factor model calculator
Combines value, momentum, quality, and volatility factors
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from src.data.pipeline import MarketDataPipeline
from src.data.storage.database import Database
from src.factors.value import ValueFactor
from src.factors.momentum import MomentumFactor
from src.factors.quality import QualityFactor
from src.factors.volatility import VolatilityFactor


class FactorCalculator:
    """
    Calculate and combine multiple factors for stock ranking
    """
    
    def __init__(self, pipeline: MarketDataPipeline):
        self.pipeline = pipeline
        self.db = Database()
        
        # Initialize factor calculators
        self.value = ValueFactor()
        self.momentum = MomentumFactor(pipeline)
        self.quality = QualityFactor()
        self.volatility = VolatilityFactor(pipeline)
        
    def calculate_all_factors(self, 
                             tickers: List[str], 
                             date: pd.Timestamp,
                             weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        Calculate all factor scores for a universe of stocks
        
        Args:
            tickers: List of ticker symbols
            date: As-of date for calculation
            weights: Factor weights (default: equal weight)
                Example: {'value': 0.25, 'momentum': 0.25, 'quality': 0.25, 'volatility': 0.25}
        
        Returns:
            DataFrame with columns: ticker, value_score, momentum_score, quality_score, 
                                   volatility_score, combined_score
        """
        if weights is None:
            weights = {
                'value': 0.25,
                'momentum': 0.25,
                'quality': 0.25,
                'volatility': 0.25
            }
        
        print(f"\nCalculating factors for {len(tickers)} stocks as of {date.date()}")
        print(f"Factor weights: {weights}")
        
        results = []
        
        # Get fundamentals from database
        fundamentals_df = self.db.get_fundamentals()
        
        for i, ticker in enumerate(tickers):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(tickers)}")
            
            try:
                # Get fundamental data for this ticker
                fund = fundamentals_df[fundamentals_df['ticker'] == ticker]
                
                if fund.empty:
                    print(f"  ⚠ No fundamentals for {ticker}, skipping")
                    continue
                
                fund_dict = fund.iloc[0].to_dict()
                
                # Calculate individual factor scores
                value_score = self.value.calculate_score(fund_dict)
                momentum_score = self.momentum.calculate_score(ticker, date)
                quality_score = self.quality.calculate_score(fund_dict)
                volatility_score = self.volatility.calculate_score(ticker, date)
                
                # Skip if missing too many factors
                available_factors = sum([
                    value_score is not None,
                    momentum_score is not None,
                    quality_score is not None,
                    volatility_score is not None
                ])
                
                if available_factors < 3:
                    print(f"  ⚠ {ticker} missing too many factors, skipping")
                    continue
                
                results.append({
                    'ticker': ticker,
                    'value_score': value_score or 0,
                    'momentum_score': momentum_score or 0,
                    'quality_score': quality_score or 0,
                    'volatility_score': volatility_score or 0
                })
                
            except Exception as e:
                print(f"  ✗ Error processing {ticker}: {e}")
                continue
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Convert raw scores to percentile ranks (0-1)
        df['value_rank'] = df['value_score'].rank(pct=True)
        df['momentum_rank'] = df['momentum_score'].rank(pct=True)
        df['quality_rank'] = df['quality_score'].rank(pct=True)
        df['volatility_rank'] = df['volatility_score'].rank(pct=True)
        
        # Calculate combined score (weighted average of ranks)
        df['combined_score'] = (
            df['value_rank'] * weights['value'] +
            df['momentum_rank'] * weights['momentum'] +
            df['quality_rank'] * weights['quality'] +
            df['volatility_rank'] * weights['volatility']
        )
        
        # Sort by combined score (best first)
        df = df.sort_values('combined_score', ascending=False).reset_index(drop=True)
        
        print(f"\n✓ Calculated factors for {len(df)} stocks")
        
        return df
    
    def get_top_stocks(self, 
                      tickers: List[str],
                      date: pd.Timestamp,
                      n: int = 20,
                      weights: Dict[str, float] = None) -> List[str]:
        """
        Get top N stocks by combined factor score
        
        Args:
            tickers: Universe of stocks
            date: As-of date
            n: Number of top stocks to return
            weights: Factor weights
        
        Returns:
            List of top N ticker symbols
        """
        df = self.calculate_all_factors(tickers, date, weights)
        
        if df.empty:
            return []
        
        top_stocks = df.head(n)['ticker'].tolist()
        
        print(f"\nTop {n} stocks:")
        for i, row in df.head(n).iterrows():
            print(f"  {i+1}. {row['ticker']:6s} - Score: {row['combined_score']:.3f} "
                  f"(V:{row['value_rank']:.2f} M:{row['momentum_rank']:.2f} "
                  f"Q:{row['quality_rank']:.2f} Vol:{row['volatility_rank']:.2f})")
        
        return top_stocks