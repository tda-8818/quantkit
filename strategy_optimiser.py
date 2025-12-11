from src.data_pipeline import MarketDataPipeline
from src.backtester import Backtester, Strategy, BacktestResults
import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class StrategyConfig:
    """Configuration for a strategy test"""
    name: str
    strategy_class: type
    params: Dict
    
class MeanReversionStrategy(Strategy):
    """
    Buy when price below moving average (oversold)
    Sell when price above moving average (overbought)
    """
    def __init__(self, data: pd.DataFrame, lookback: int = 20):
        super().__init__(data)
        self.lookback = lookback
        
    def generate_signals(self) -> pd.Series:
        """
        Signal logic:
        - Buy (1) when price < MA (expecting reversion up)
        - Sell (-1) when price > MA (expecting reversion down)
        """
        ma = self.data['close'].rolling(window=self.lookback).mean()
        
        signals = pd.Series(0, index=self.data.index)
        signals[self.data['close'] < ma] = 1   # Price below MA = buy
        signals[self.data['close'] > ma] = -1  # Price above MA = sell
        
        return signals

class StrategyOptimiser:
    """
    Systematically test multiple strategies and parameters
    """
    def __init__(self, pipeline: MarketDataPipeline, initial_capital: float = 100000):
        self.pipeline = pipeline
        self.initial_capital = initial_capital
        self.results = []
        
    def test_strategy(self, ticker: str, strategy_config: StrategyConfig, 
                     start_date: str, end_date: str) -> Dict:
        """Test a single strategy configuration"""
        # Get data
        data = self.pipeline.get_data(ticker, start_date, end_date)
        
        if data.empty:
            return None
            
        # Create strategy
        strategy = strategy_config.strategy_class(data, **strategy_config.params)
        
        # Run backtest
        backtester = Backtester(strategy, self.initial_capital)
        results = backtester.run()
        
        # Extract key metrics
        return {
            'ticker': ticker,
            'strategy': strategy_config.name,
            'params': strategy_config.params,
            'total_return': results.total_return,
            'annual_return': results.annual_return,
            'sharpe': results.sharpe_ratio,
            'sortino': results.sortino_ratio,
            'max_drawdown': results.max_drawdown,
            'calmar': results.calmar_ratio,
            'win_rate': results.win_rate,
            'profit_factor': results.profit_factor,
            'total_trades': results.total_trades,
            'results_obj': results  # Store full results for plotting later
        }
        
    def grid_search(self, tickers: List[str], strategies: List[StrategyConfig],
                   start_date: str, end_date: str) -> pd.DataFrame:
        """
        Test all combinations of tickers and strategies
        """
        print("=" * 60)
        print(f"STRATEGY OPTIMISER - Grid Search")
        print("=" * 60)
        print(f"Tickers: {len(tickers)}")
        print(f"Strategies: {len(strategies)}")
        print(f"Total tests: {len(tickers) * len(strategies)}")
        print("=" * 60)
        
        results = []
        total_tests = len(tickers) * len(strategies)
        current = 0
        
        for ticker in tickers:
            for strategy_config in strategies:
                current += 1
                print(f"[{current}/{total_tests}] Testing {ticker} - {strategy_config.name}...", end=" ")
                
                result = self.test_strategy(ticker, strategy_config, start_date, end_date)
                
                if result:
                    results.append(result)
                    print(f"✓ Sharpe: {result['sharpe']:.2f}, Return: {result['total_return']:.1f}%")
                else:
                    print("✗ No data")
                    
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Sort by Sharpe ratio (best risk-adjusted return)
        df = df.sort_values('sharpe', ascending=False)
        
        print("\n" + "=" * 60)
        print("Grid Search Complete!")
        print("=" * 60)
        
        return df
        
    def print_top_strategies(self, results_df: pd.DataFrame, n: int = 10):
        """Print top N strategies by Sharpe ratio"""
        print("\n" + "=" * 60)
        print(f"TOP {n} STRATEGIES (by Sharpe Ratio)")
        print("=" * 60)
        
        top = results_df.head(n)
        
        for idx, row in top.iterrows():
            print(f"\n#{idx+1}")
            print(f"  Ticker:         {row['ticker']}")
            print(f"  Strategy:       {row['strategy']}")
            print(f"  Parameters:     {row['params']}")
            print(f"  Sharpe Ratio:   {row['sharpe']:.2f}")
            print(f"  Annual Return:  {row['annual_return']:.2f}%")
            print(f"  Max Drawdown:   {row['max_drawdown']:.2f}%")
            print(f"  Win Rate:       {row['win_rate']:.2f}%")
            print(f"  Profit Factor:  {row['profit_factor']:.2f}")
            
    def compare_strategies(self, results_df: pd.DataFrame, metric: str = 'sharpe'):
        """Compare strategies across different metrics"""
        print("\n" + "=" * 60)
        print(f"STRATEGY COMPARISON (by {metric})")
        print("=" * 60)
        
        # Group by strategy name and average the metric
        comparison = results_df.groupby('strategy').agg({
            metric: 'mean',
            'total_return': 'mean',
            'annual_return': 'mean',
            'max_drawdown': 'mean',
            'win_rate': 'mean',
            'profit_factor': 'mean'
        }).sort_values(metric, ascending=False)
        
        print(comparison)
        
        return comparison