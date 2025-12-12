"""
Value Factor: Identify cheap stocks
Academic research: Fama-French (1992), "The Cross-Section of Expected Stock Returns"
"""
import pandas as pd
import numpy as np
from typing import Optional


class ValueFactor:
    """
    Value factor scoring based on:
    - P/E ratio (lower is better)
    - P/B ratio (lower is better) 
    - Dividend yield (higher is better)
    """
    
    def calculate_score(self, fundamentals: dict) -> Optional[float]:
        """
        Calculate value score (0-1, higher is better)
        
        Returns None if insufficient data
        """
        pe = fundamentals.get('pe_ratio')
        pb = fundamentals.get('pb_ratio')
        div_yield = fundamentals.get('dividend_yield', 0)
        
        # Need at least 2 metrics
        available_metrics = sum([
            pe is not None and pe > 0,
            pb is not None and pb > 0,
            div_yield is not None
        ])
        
        if available_metrics < 2:
            return None
            
        scores = []
        
        # P/E: Lower is better (invert)
        if pe and pe > 0:
            # Cap at 50 to avoid extreme values
            pe_capped = min(pe, 50)
            pe_score = 1 - (pe_capped / 50)  # 0 to 1
            scores.append(pe_score)
            
        # P/B: Lower is better (invert)
        if pb and pb > 0:
            # Cap at 10
            pb_capped = min(pb, 10)
            pb_score = 1 - (pb_capped / 10)
            scores.append(pb_score)
            
        # Dividend yield: Higher is better
        if div_yield is not None:
            # Cap at 10%
            div_capped = min(div_yield * 100, 10)
            div_score = div_capped / 10
            scores.append(div_score)
            
        # Average available scores
        return np.mean(scores) if scores else None
        
    def calculate_batch(self, fundamentals_df: pd.DataFrame) -> pd.Series:
        """Calculate value scores for all stocks"""
        scores = fundamentals_df.apply(
            lambda row: self.calculate_score(row.to_dict()),
            axis=1
        )
        return scores