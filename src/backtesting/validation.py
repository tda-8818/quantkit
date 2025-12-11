"""
Data splitting and validation utilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class DataSplit:
    """Container for train/val/test splits"""
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    
    def __repr__(self):
        return (f"DataSplit(\n"
                f"  Train: {self.train.index[0]} to {self.train.index[-1]} ({len(self.train)} days)\n"
                f"  Val:   {self.validation.index[0]} to {self.validation.index[-1]} ({len(self.validation)} days)\n"
                f"  Test:  {self.test.index[0]} to {self.test.index[-1]} ({len(self.test)} days)\n"
                f")")


def split_data(data: pd.DataFrame, 
               train_pct: float = 0.6, 
               val_pct: float = 0.2, 
               test_pct: float = 0.2) -> DataSplit:
    """
    Split data chronologically into train/validation/test sets.
    
    Example for 5 years (2020-2024):
        Train: 2020-2022 (60% = 3 years)
        Val:   2023      (20% = 1 year)
        Test:  2024      (20% = 1 year)
    
    Args:
        data: DataFrame with datetime index
        train_pct: Fraction for training (default 0.6)
        val_pct: Fraction for validation (default 0.2)
        test_pct: Fraction for testing (default 0.2)
    
    Returns:
        DataSplit object with train, validation, test DataFrames
    """
    assert abs(train_pct + val_pct + test_pct - 1.0) < 0.001, "Percentages must sum to 1.0"
    
    n = len(data)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))
    
    train = data.iloc[:train_end].copy()
    validation = data.iloc[train_end:val_end].copy()
    test = data.iloc[val_end:].copy()
    
    return DataSplit(train=train, validation=validation, test=test)


def time_series_cv_splits(data: pd.DataFrame, 
                          n_splits: int = 5,
                          test_size: int = 126) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Time-series cross-validation with expanding window.
    
    Example with 5 splits:
        Split 1: Train [████████████----] Test [--]
        Split 2: Train [██████████████--] Test [--]
        Split 3: Train [████████████████] Test [--]
        Split 4: Train [██████████████████--] Test [--]
        Split 5: Train [████████████████████] Test [--]
    
    Args:
        data: DataFrame with datetime index
        n_splits: Number of splits (default 5)
        test_size: Size of test set in days (default 126 = ~6 months)
    
    Returns:
        List of (train_data, test_data) tuples
    """
    n = len(data)
    min_train_size = n - (n_splits * test_size)
    
    if min_train_size < 252:  # Need at least 1 year for training
        raise ValueError(f"Not enough data for {n_splits} splits. Need at least {252 + n_splits * test_size} days")
    
    splits = []
    
    for i in range(n_splits):
        test_end = n - (i * test_size)
        test_start = test_end - test_size
        train_end = test_start
        
        if train_end < 252:  # Stop if not enough training data
            break
            
        train = data.iloc[:train_end].copy()
        test = data.iloc[test_start:test_end].copy()
        
        splits.append((train, test))
    
    # Return in chronological order
    return list(reversed(splits))


def validate_no_leakage(train: pd.DataFrame, test: pd.DataFrame) -> bool:
    """
    Verify no data leakage between train and test sets.
    
    Checks:
        1. No overlapping dates
        2. Train ends before test begins
        3. No future data in train set
    
    Returns:
        True if validation passes
    """
    # Check 1: No overlapping dates
    train_dates = set(train.index)
    test_dates = set(test.index)
    overlap = train_dates & test_dates
    
    if overlap:
        print(f"❌ Data leakage detected! {len(overlap)} overlapping dates")
        return False
    
    # Check 2: Train ends before test begins
    if train.index[-1] >= test.index[0]:
        print(f"❌ Data leakage! Train ends ({train.index[-1]}) after test begins ({test.index[0]})")
        return False
    
    print(f"✓ No data leakage detected")
    print(f"  Train: {train.index[0]} to {train.index[-1]}")
    print(f"  Test:  {test.index[0]} to {test.index[-1]}")
    return True


def print_split_summary(split: DataSplit):
    """Print summary statistics for data split"""
    print("=" * 60)
    print("DATA SPLIT SUMMARY")
    print("=" * 60)
    print(f"\nTRAIN SET")
    print(f"  Period:  {split.train.index[0]} to {split.train.index[-1]}")
    print(f"  Days:    {len(split.train)}")
    print(f"  Returns: {split.train['close'].pct_change().mean():.4f} daily avg")
    
    print(f"\nVALIDATION SET")
    print(f"  Period:  {split.validation.index[0]} to {split.validation.index[-1]}")
    print(f"  Days:    {len(split.validation)}")
    print(f"  Returns: {split.validation['close'].pct_change().mean():.4f} daily avg")
    
    print(f"\nTEST SET")
    print(f"  Period:  {split.test.index[0]} to {split.test.index[-1]}")
    print(f"  Days:    {len(split.test)}")
    print(f"  Returns: {split.test['close'].pct_change().mean():.4f} daily avg")
    print("=" * 60)