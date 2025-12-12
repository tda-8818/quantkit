"""
Quality Factor: Identify profitable, stable companies
Academic research: Novy-Marx (2013), "The Other Side of Value"
"""
import pandas as pd
import numpy as np
from typing import Optional


class QualityFactor:
    """
    Quality factor based on:
    - ROE (Return on Equity)
    - Profit margins
    - Low debt
    - Earnings stability
    """
    
    def calculate_score(self, fundamentals: dict) -> Optional[float]:
        """
        Calculate quality score (0-1, higher is better)
        """
        roe = fundamentals.get('roe')
        profit_margin = fundamentals.get('profit_margin')
        debt_to_equity = fundamentals.get('debt_to_equity')
        
        # Need at least 2 metrics
        available = sum([
            roe is not None,
            profit_margin is not None,
            debt_to_equity is not None
        ])
        
        if available < 2:
            return None
            
        scores = []
        
        # ROE: Higher is better
        if roe is not None:
            # Cap at 50%
            roe_pct = roe * 100 if roe < 1 else roe
            roe_capped = min(max(roe_pct, 0), 50)
            roe_score = roe_capped / 50
            scores.append(roe_score)
            
        # Profit margin: Higher is better
        if profit_margin is not None:
            margin_pct = profit_margin * 100 if profit_margin < 1 else profit_margin
            margin_capped = min(max(margin_pct, 0), 50)
            margin_score = margin_capped / 50
            scores.append(margin_score)
            
        # Debt-to-Equity: Lower is better
        if debt_to_equity is not None and debt_to_equity >= 0:
            # Cap at 200%
            debt_capped = min(debt_to_equity, 200)
            debt_score = 1 - (debt_capped / 200)
            scores.append(debt_score)
            
        return np.mean(scores) if scores else None
        
    def calculate_batch(self, fundamentals_df: pd.DataFrame) -> pd.Series:
        """Calculate quality scores for all stocks"""
        scores = fundamentals_df.apply(
            lambda row: self.calculate_score(row.to_dict()),
            axis=1
        )
        return scores