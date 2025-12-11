"""
Price data cleaner for market data pipeline.

Cleans raw OHLCV data by:
1. Removing zero-volume days (weekends/holidays)
2. Forward-filling missing values (max 5-day gaps)
3. Detecting statistical outliers (>5 std deviations)
4. Validating OHLC relationships (Low ≤ Open/Close ≤ High)
5. Logging all cleaning actions

Usage:
    cleaner = PriceCleaner()
    clean_df = cleaner.clean(raw_df, ticker='AAPL')
    print(cleaner.get_log())  # See what was cleaned
"""

import pandas as pd
import numpy as np

class PriceCleaner:
    def __init__(self):
        self.cleaning_log = []  # Store messages about what was cleaned
    
    def clean(self, df: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
        """Main cleaning function - calls all cleaning steps"""
        
        df = df.copy()  # Don't modify original dataframe
        original_len = len(df)  # Remember how many rows we started with
        
        # Step 1: Remove days with zero volume (weekends/holidays)
        df = self._remove_zero_volume(df)
        
        # Step 2: Fill missing data gaps (forward fill)
        df = self._handle_missing(df)
        
        # Step 3: Find outliers (crazy price moves)
        outliers = self._detect_outliers(df)  # Returns Series of True/False
        outlier_count = int(outliers.sum())  # Count how many True values
        # WHY int()? Because outliers.sum() returns pandas int64, not Python int
        # Python's if statement needs pure Python int, not pandas type
        if outlier_count > 0:
            self.cleaning_log.append(f"{ticker}: {outlier_count} outliers detected")
        
        # Step 4: Find invalid bars (Low > High, etc)
        invalid = self._validate_ohlc(df)  # Returns Series of True/False
        invalid_count = int(invalid.sum())  # Count invalid bars
        # Same reason - convert pandas int64 to Python int
        if invalid_count > 0:
            self.cleaning_log.append(f"{ticker}: {invalid_count} invalid OHLC bars")
            df = df[~invalid]  # Remove invalid rows (~invalid means NOT invalid)
        
        # Step 5: Log how many rows were removed total
        cleaned_len = len(df)
        removed = original_len - cleaned_len
        if removed > 0:
            self.cleaning_log.append(f"{ticker}: Removed {removed} rows")
        
        return df
    
    def _remove_zero_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove days with no trading (weekends/holidays)"""
        return df[df['Volume'] > 0]
        # df['Volume'] > 0 creates True/False for each row
        # df[True/False] keeps only True rows
    
    def _handle_missing(self, df: pd.DataFrame, max_gap: int = 5) -> pd.DataFrame:
        """Fill missing prices (forward fill max 5 days, then drop rest)"""
        df = df.ffill(limit=5)  # Copy previous day's price (max 5 times)
        df = df.dropna()  # Drop any remaining NaN values
        return df
    
    def _detect_outliers(self, df: pd.DataFrame, threshold: float = 5.0) -> pd.Series:
        """Find days with extreme price moves (>5 standard deviations)"""
        returns = df['Close'].pct_change()  # Calculate daily returns
        # Example: If close goes 100 -> 105, return = 0.05 (5%)
        
        z_scores = np.abs((returns - returns.mean()) / returns.std())
        # Z-score = how many std deviations from mean
        # Example: mean=0.01, std=0.02, return=0.11
        # z_score = abs((0.11 - 0.01) / 0.02) = 5.0
        
        return z_scores > threshold
        # Returns True for outliers, False for normal days
    
    def _validate_ohlc(self, df: pd.DataFrame) -> pd.Series:
        """Check if OHLC values make sense (Low should be ≤ High, etc)"""
        invalid = (
            (df['Low'] > df['Open']) |    # Low can't be higher than Open
            (df['Low'] > df['Close']) |   # Low can't be higher than Close
            (df['High'] < df['Open']) |   # High can't be lower than Open
            (df['High'] < df['Close'])    # High can't be lower than Close
        )
        return invalid  # Returns True for bad rows, False for good rows
    
    def get_log(self):
        """Return all cleaning messages"""
        return self.cleaning_log