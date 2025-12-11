"""
Walk-forward optimisation for robust strategy validation
Prevents overfitting by testing on unseen future data
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Type, Tuple
from dataclasses import dataclass
import itertools
from src.backtesting.backtester import Backtester, BacktestResults
from src.strategies.base import Strategy


@dataclass
class WalkForwardResult:
    """Results from a single walk-forward window"""
    window_id: int
    train_period: Tuple[str, str]
    test_period: Tuple[str, str]
    best_params: Dict
    train_sharpe: float
    test_sharpe: float
    test_results: BacktestResults


@dataclass
class WalkForwardSummary:
    """Summary of all walk-forward windows"""
    strategy_name: str
    n_windows: int
    avg_train_sharpe: float
    avg_test_sharpe: float
    sharpe_degradation: float  # How much Sharpe drops from train to test
    best_params_stability: float  # How consistent are best params across windows
    all_windows: List[WalkForwardResult]
    
    def print_summary(self):
        """Print walk-forward summary"""
        print("\n" + "=" * 70)
        print(f"WALK-FORWARD optimisation SUMMARY: {self.strategy_name}")
        print("=" * 70)
        
        print(f"\nOVERALL PERFORMANCE")
        print(f"  Number of Windows:        {self.n_windows}")
        print(f"  Avg Train Sharpe:         {self.avg_train_sharpe:.3f}")
        print(f"  Avg Test Sharpe:          {self.avg_test_sharpe:.3f}")
        print(f"  Sharpe Degradation:       {self.sharpe_degradation:.3f} ({self.sharpe_degradation/self.avg_train_sharpe*100:.1f}%)")
        print(f"  Parameter Stability:      {self.best_params_stability:.1%}")
        
        # Interpret results
        print(f"\nINTERPRETATION")
        if self.sharpe_degradation < 0.2:
            print("  ✓ ROBUST - Strategy performs consistently out-of-sample")
        elif self.sharpe_degradation < 0.5:
            print("  ⚠ MODERATE - Some overfitting, but strategy has merit")
        else:
            print("  ✗ OVERFIT - Strategy likely curve-fit to training data")
            
        if self.best_params_stability > 0.7:
            print("  ✓ STABLE - Parameters consistent across time periods")
        elif self.best_params_stability > 0.4:
            print("  ⚠ VARIABLE - Parameters change across time periods")
        else:
            print("  ✗ UNSTABLE - Different parameters work in different periods")
        
        # Window-by-window breakdown
        print(f"\nWINDOW-BY-WINDOW BREAKDOWN")
        print("-" * 70)
        for window in self.all_windows:
            train_start, train_end = window.train_period
            test_start, test_end = window.test_period
            
            print(f"\nWindow {window.window_id}:")
            print(f"  Train: {train_start} to {train_end}")
            print(f"  Test:  {test_start} to {test_end}")
            print(f"  Best Params: {window.best_params}")
            print(f"  Train Sharpe: {window.train_sharpe:.3f}")
            print(f"  Test Sharpe:  {window.test_sharpe:.3f}")
            print(f"  Degradation:  {window.train_sharpe - window.test_sharpe:.3f}")


class WalkForwardOptimiser:
    """
    Walk-forward optimisation:
    1. Split data into windows (train + test)
    2. For each window:
       - Optimise parameters on training data
       - Validate on test data (future, unseen)
    3. Compare in-sample vs out-of-sample performance
    """
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        
    def Optimise(self,
                 strategy_class: Type[Strategy],
                 data: pd.DataFrame,
                 param_grid: Dict[str, List],
                 train_window: int = 504,  # 2 years
                 test_window: int = 126,   # 6 months
                 step_size: int = 126) -> WalkForwardSummary:
        """
        Run walk-forward optimisation.
        
        Args:
            strategy_class: Strategy class to Optimise
            data: Full dataset
            param_grid: Dictionary of parameters to test
                Example: {'lookback': [63, 126, 189, 252]}
            train_window: Training window size in days (default 504 = 2 years)
            test_window: Test window size in days (default 126 = 6 months)
            step_size: How far to step forward each window (default 126 = 6 months)
        
        Returns:
            WalkForwardSummary with results from all windows
        """
        print("=" * 70)
        print("WALK-FORWARD optimisation")
        print("=" * 70)
        print(f"Strategy:      {strategy_class.__name__}")
        print(f"Train Window:  {train_window} days (~{train_window/252:.1f} years)")
        print(f"Test Window:   {test_window} days (~{test_window/252:.1f} years)")
        print(f"Step Size:     {step_size} days (~{step_size/252:.1f} years)")
        print(f"Parameters:    {param_grid}")
        
        # Generate parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        print(f"Total param combinations: {len(param_combinations)}")
        
        # Calculate number of windows
        n_windows = (len(data) - train_window - test_window) // step_size + 1
        print(f"Number of walk-forward windows: {n_windows}")
        print("=" * 70)
        
        # Run walk-forward
        all_results = []
        
        for window_id in range(n_windows):
            start_idx = window_id * step_size
            train_end_idx = start_idx + train_window
            test_end_idx = train_end_idx + test_window
            
            if test_end_idx > len(data):
                break
                
            # Split data
            train_data = data.iloc[start_idx:train_end_idx].copy()
            test_data = data.iloc[train_end_idx:test_end_idx].copy()
            
            train_period = (train_data.index[0].strftime('%Y-%m-%d'), 
                          train_data.index[-1].strftime('%Y-%m-%d'))
            test_period = (test_data.index[0].strftime('%Y-%m-%d'),
                         test_data.index[-1].strftime('%Y-%m-%d'))
            
            print(f"\n[Window {window_id + 1}/{n_windows}]")
            print(f"Train: {train_period[0]} to {train_period[1]}")
            print(f"Test:  {test_period[0]} to {test_period[1]}")
            
            # Optimise on training data
            best_params, best_train_sharpe = self._Optimise_on_window(
                strategy_class, train_data, param_combinations, param_names
            )
            
            print(f"  Best params: {best_params}")
            print(f"  Train Sharpe: {best_train_sharpe:.3f}")
            
            # Test on unseen data
            strategy = strategy_class(test_data, **best_params)
            backtester = Backtester(strategy, self.initial_capital)
            test_results = backtester.run()
            test_sharpe = test_results.sharpe_ratio
            
            print(f"  Test Sharpe:  {test_sharpe:.3f}")
            print(f"  Degradation:  {best_train_sharpe - test_sharpe:.3f}")
            
            # Store results
            all_results.append(WalkForwardResult(
                window_id=window_id + 1,
                train_period=train_period,
                test_period=test_period,
                best_params=best_params,
                train_sharpe=best_train_sharpe,
                test_sharpe=test_sharpe,
                test_results=test_results
            ))
        
        # Calculate summary statistics
        avg_train_sharpe = np.mean([r.train_sharpe for r in all_results])
        avg_test_sharpe = np.mean([r.test_sharpe for r in all_results])
        sharpe_degradation = avg_train_sharpe - avg_test_sharpe
        
        # Calculate parameter stability (how often same params are chosen)
        param_stability = self._calculate_param_stability(all_results, param_names)
        
        summary = WalkForwardSummary(
            strategy_name=strategy_class.__name__,
            n_windows=len(all_results),
            avg_train_sharpe=avg_train_sharpe,
            avg_test_sharpe=avg_test_sharpe,
            sharpe_degradation=sharpe_degradation,
            best_params_stability=param_stability,
            all_windows=all_results
        )
        
        return summary
    
    def _Optimise_on_window(self, 
                           strategy_class: Type[Strategy],
                           data: pd.DataFrame,
                           param_combinations: List[Tuple],
                           param_names: List[str]) -> Tuple[Dict, float]:
        """Find best parameters for a single training window"""
        best_sharpe = -np.inf
        best_params = None
        
        for param_combo in param_combinations:
            params = dict(zip(param_names, param_combo))
            
            try:
                strategy = strategy_class(data, **params)
                backtester = Backtester(strategy, self.initial_capital)
                results = backtester.run()
                
                if results.sharpe_ratio > best_sharpe:
                    best_sharpe = results.sharpe_ratio
                    best_params = params
            except:
                continue
        
        return best_params, best_sharpe
    
    def _calculate_param_stability(self, 
                                   results: List[WalkForwardResult],
                                   param_names: List[str]) -> float:
        """
        Calculate how stable parameters are across windows.
        Returns value between 0 (completely unstable) and 1 (perfectly stable)
        """
        if len(results) < 2:
            return 1.0
        
        # For each parameter, check how often the most common value appears
        stabilities = []
        
        for param_name in param_names:
            values = [r.best_params[param_name] for r in results]
            most_common_count = max([values.count(v) for v in set(values)])
            stability = most_common_count / len(values)
            stabilities.append(stability)
        
        return np.mean(stabilities)