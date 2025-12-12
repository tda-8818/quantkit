"""
Portfolio construction from factor rankings
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Portfolio:
    """Portfolio holdings"""
    date: pd.Timestamp
    holdings: Dict[str, float]  # {ticker: weight}
    
    def __repr__(self):
        total_weight = sum(self.holdings.values())
        return (f"Portfolio(date={self.date.date()}, "
                f"n_stocks={len(self.holdings)}, "
                f"total_weight={total_weight:.2%})")


class PortfolioConstructor:
    """
    Construct portfolios from factor rankings
    """
    
    def __init__(self, n_stocks: int = 20):
        """
        Args:
            n_stocks: Number of stocks in portfolio
        """
        self.n_stocks = n_stocks
        
    def construct_equal_weight(self, 
                               ranked_stocks: pd.DataFrame) -> Portfolio:
        """
        Construct equal-weighted portfolio
        
        Args:
            ranked_stocks: DataFrame with 'ticker' and 'combined_score' columns,
                          sorted by score (best first)
        
        Returns:
            Portfolio with equal weights
        """
        top_stocks = ranked_stocks.head(self.n_stocks)
        weight = 1.0 / len(top_stocks)
        
        holdings = {row['ticker']: weight for _, row in top_stocks.iterrows()}
        
        # Date from index or use first available date
        date = ranked_stocks.iloc[0].get('date', pd.Timestamp.now())
        
        return Portfolio(date=date, holdings=holdings)
    
    def construct_score_weighted(self,
                                 ranked_stocks: pd.DataFrame,
                                 score_col: str = 'combined_score') -> Portfolio:
        """
        Construct score-weighted portfolio
        Higher scoring stocks get larger weights
        
        Args:
            ranked_stocks: DataFrame with scores
            score_col: Column name for scores
        
        Returns:
            Portfolio with score-based weights
        """
        top_stocks = ranked_stocks.head(self.n_stocks).copy()
        
        # Normalise scores to sum to 1
        total_score = top_stocks[score_col].sum()
        top_stocks['weight'] = top_stocks[score_col] / total_score
        
        holdings = {row['ticker']: row['weight'] 
                   for _, row in top_stocks.iterrows()}
        
        date = ranked_stocks.iloc[0].get('date', pd.Timestamp.now())
        
        return Portfolio(date=date, holdings=holdings)
    
    def construct_minimum_variance(self,
                                   ranked_stocks: pd.DataFrame,
                                   returns_data: Dict[str, pd.DataFrame]) -> Portfolio:
        """
        Construct minimum variance portfolio (advanced)
        Optimises weights to minimise portfolio volatility
        
        Args:
            ranked_stocks: Top ranked stocks
            returns_data: Historical returns for each stock
        
        Returns:
            Portfolio with optimised weights
        """
        # This would use quadratic programming (scipy.optimise)
        # For now, fallback to equal weight
        print("⚠ Minimum variance optimisation not yet implemented, using equal weight")
        return self.construct_equal_weight(ranked_stocks)
    
    def print_portfolio(self, portfolio: Portfolio):
        """Print portfolio holdings"""
        print("\n" + "=" * 60)
        print(f"PORTFOLIO - {portfolio.date.date()}")
        print("=" * 60)
        print(f"Number of holdings: {len(portfolio.holdings)}")
        print(f"Total weight: {sum(portfolio.holdings.values()):.2%}")
        print("\nHoldings:")
        
        sorted_holdings = sorted(portfolio.holdings.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        for ticker, weight in sorted_holdings:
            print(f"  {ticker:6s}  {weight:6.2%}")