"""
Backtest factor model against S&P 500 benchmark
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.data.pipeline import MarketDataPipeline
from src.factors.calculator import FactorCalculator
from src.portfolio.constructor import PortfolioConstructor


class FactorBacktester:
    """
    Backtest factor-based portfolio with monthly rebalancing
    """
    
    def __init__(self, 
                 universe: list,
                 factor_weights: dict,
                 n_stocks: int = 20,
                 initial_capital: float = 100000,
                 rebalance_frequency: str = 'M'):  # Monthly
        
        self.universe = universe
        self.factor_weights = factor_weights
        self.n_stocks = n_stocks
        self.initial_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        
        self.pipeline = MarketDataPipeline()
        self.calculator = FactorCalculator(self.pipeline)
        self.constructor = PortfolioConstructor(n_stocks=n_stocks)
        
    def run(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Run backtest with monthly rebalancing
        
        Returns:
            DataFrame with columns: date, portfolio_value, holdings
        """
        print("=" * 70)
        print("FACTOR MODEL BACKTEST")
        print("=" * 70)
        print(f"Universe:          {len(self.universe)} stocks")
        print(f"Portfolio Size:    {self.n_stocks} stocks")
        print(f"Factor Weights:    {self.factor_weights}")
        print(f"Period:            {start_date} to {end_date}")
        print(f"Initial Capital:   ${self.initial_capital:,.0f}")
        print(f"Rebalance:         Monthly")
        print("=" * 70)
        
        # Generate monthly rebalance dates
        rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        
        print(f"\nNumber of rebalance periods: {len(rebalance_dates)}")
        
        portfolio_values = []
        current_holdings = {}
        portfolio_value = self.initial_capital
        
        for i, date in enumerate(rebalance_dates):
            print(f"\n[{i+1}/{len(rebalance_dates)}] Rebalancing on {date.date()}...")
            
            # Calculate factor scores
            try:
                rankings = self.calculator.calculate_all_factors(
                    tickers=self.universe,
                    date=date,
                    weights=self.factor_weights
                )
                
                if rankings.empty:
                    print("  ⚠ No rankings available, keeping previous holdings")
                    continue
                
                # Construct new portfolio
                portfolio = self.constructor.construct_equal_weight(rankings)
                
                # Calculate portfolio value if we have previous holdings
                if current_holdings:
                    # Get returns since last rebalance
                    if i > 0:
                        prev_date = rebalance_dates[i-1]
                        portfolio_value = self._calculate_portfolio_value(
                            current_holdings, prev_date, date
                        )
                
                # Update holdings
                current_holdings = portfolio.holdings
                
                # Store result
                portfolio_values.append({
                    'date': date,
                    'portfolio_value': portfolio_value,
                    'holdings': len(current_holdings)
                })
                
                print(f"  Portfolio value: ${portfolio_value:,.0f}")
                print(f"  Holdings: {len(current_holdings)}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        # Convert to DataFrame
        results = pd.DataFrame(portfolio_values)
        results.set_index('date', inplace=True)
        
        return results
    
    def _calculate_portfolio_value(self, 
                                   holdings: dict, 
                                   start_date: pd.Timestamp,
                                   end_date: pd.Timestamp) -> float:
        """
        Calculate portfolio value based on holdings and price changes
        """
        total_return = 0
        
        for ticker, weight in holdings.items():
            try:
                # Get price data for this period
                data = self.pipeline.get_data(ticker, start_date=start_date, end_date=end_date)
                
                if len(data) < 2:
                    continue
                
                # Calculate return
                start_price = data['close'].iloc[0]
                end_price = data['close'].iloc[-1]
                ticker_return = (end_price / start_price) - 1
                
                # Weighted return
                total_return += weight * ticker_return
                
            except Exception as e:
                print(f"  ⚠ Error calculating return for {ticker}: {e}")
                continue
        
        return self.initial_capital * (1 + total_return)
    
    def calculate_metrics(self, results: pd.DataFrame, benchmark_ticker: str = 'SPY') -> dict:
        """Calculate performance metrics"""
        
        # Portfolio returns
        portfolio_returns = results['portfolio_value'].pct_change().dropna()
        
        # Benchmark returns
        benchmark_data = self.pipeline.get_data(
            benchmark_ticker,
            start_date=results.index[0],
            end_date=results.index[-1]
        )
        
        # FIX: Convert index to datetime if needed
        if not isinstance(benchmark_data.index, pd.DatetimeIndex):
            benchmark_data.index = pd.to_datetime(benchmark_data.index)
        
        # Resample to monthly
        benchmark_monthly = benchmark_data['close'].resample('MS').first()
        benchmark_returns = benchmark_monthly.pct_change().dropna()
        
        # Align dates
        aligned_returns = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_returns) == 0:
            print("⚠ Warning: No overlapping dates between portfolio and benchmark")
            return {
                'total_return': 0,
                'annual_return': 0,
                'sharpe_ratio': 0,
                'volatility': 0,
                'max_drawdown': 0,
                'benchmark_return': 0,
                'alpha': 0,
                'n_periods': 0
            }
        
        # Calculate metrics
        total_return = (results['portfolio_value'].iloc[-1] / results['portfolio_value'].iloc[0]) - 1
        benchmark_total = (benchmark_monthly.iloc[-1] / benchmark_monthly.iloc[0]) - 1
        
        portfolio_vol = aligned_returns['portfolio'].std() * np.sqrt(12)
        benchmark_vol = aligned_returns['benchmark'].std() * np.sqrt(12)
        
        sharpe = (aligned_returns['portfolio'].mean() * 12) / portfolio_vol if portfolio_vol > 0 else 0
        
        # Max drawdown
        cumulative = (1 + aligned_returns['portfolio']).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        
        return {
            'total_return': total_return,
            'annual_return': (1 + total_return) ** (12 / len(aligned_returns)) - 1,
            'sharpe_ratio': sharpe,
            'volatility': portfolio_vol,
            'max_drawdown': max_dd,
            'benchmark_return': benchmark_total,
            'alpha': total_return - benchmark_total,
            'n_periods': len(results)
        }
        
    def plot_results(self, results: pd.DataFrame, benchmark_ticker: str = 'SPY'):
        """Plot backtest results"""
        
        # Get benchmark data
        benchmark_data = self.pipeline.get_data(
            benchmark_ticker,
            start_date=results.index[0],
            end_date=results.index[-1]
        )
        
        # FIX: Convert index to datetime
        if not isinstance(benchmark_data.index, pd.DatetimeIndex):
            benchmark_data.index = pd.to_datetime(benchmark_data.index)
        
        benchmark_monthly = benchmark_data['close'].resample('MS').first()
        benchmark_normalised = (benchmark_monthly / benchmark_monthly.iloc[0]) * self.initial_capital
        
        # Create figure
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Portfolio value vs benchmark
        axes[0].plot(results.index, results['portfolio_value'], 
                    label='Factor Portfolio', linewidth=2)
        axes[0].plot(benchmark_normalised.index, benchmark_normalised.values,
                    label=f'{benchmark_ticker} Benchmark', linewidth=2, alpha=0.7)
        axes[0].set_ylabel('Portfolio Value ($)')
        axes[0].set_title('Factor Portfolio vs Benchmark')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Plot 2: Rolling Sharpe ratio
        portfolio_returns = results['portfolio_value'].pct_change().dropna()
        
        if len(portfolio_returns) >= 12:
            rolling_sharpe = (portfolio_returns.rolling(window=12).mean() / 
                            portfolio_returns.rolling(window=12).std()) * np.sqrt(12)
            
            axes[1].plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2)
            axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.3)
            axes[1].axhline(y=1, color='g', linestyle='--', alpha=0.3, label='Sharpe = 1.0')
            axes[1].set_ylabel('Rolling Sharpe Ratio (12-month)')
            axes[1].set_xlabel('Date')
            axes[1].set_title('Rolling 12-Month Sharpe Ratio')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        else:
            axes[1].text(0.5, 0.5, 'Insufficient data for rolling Sharpe', 
                        ha='center', va='center', transform=axes[1].transAxes)
        
        plt.tight_layout()
        plt.savefig('data/results/factor_backtest.png', dpi=150, bbox_inches='tight')
        print("\n✓ Chart saved to data/results/factor_backtest.png")
        plt.show()


def main():
    """Run factor backtest"""
    
    # Define universe (same as example)
    universe = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        'JPM', 'BAC', 'WFC', 'GS',
        'JNJ', 'UNH', 'PFE', 'ABBV',
        'WMT', 'HD', 'NKE', 'MCD',
        'XOM'
    ]
    
    # Factor weights (emphasise momentum + quality)
    factor_weights = {
        'value': 0.20,
        'momentum': 0.35,
        'quality': 0.30,
        'volatility': 0.15
    }
    
    # Create backtester
    backtester = FactorBacktester(
        universe=universe,
        factor_weights=factor_weights,
        n_stocks=10,
        initial_capital=100000
    )
    
    # Run backtest
    results = backtester.run(start_date='2021-01-01', end_date='2024-12-01')
    
    # Show first portfolio composition
    print("\n" + "="*70)
    print("FIRST PORTFOLIO COMPOSITION (2021-01-01)")
    print("="*70)

    first_date = pd.Timestamp('2021-01-01')
    rankings = backtester.calculator.calculate_all_factors(
        tickers=universe,
        date=first_date,
        weights=factor_weights
    )
    print(rankings.head(10)[['ticker', 'combined_score', 'value_rank', 'momentum_rank', 'quality_rank']])
    
    # Calculate metrics
    metrics = backtester.calculate_metrics(results, benchmark_ticker='SPY')
    
    # Print results
    print("\n" + "=" * 70)
    print("BACKTEST RESULTS")
    print("=" * 70)
    print(f"Total Return:          {metrics['total_return']:>8.2%}")
    print(f"Annual Return:         {metrics['annual_return']:>8.2%}")
    print(f"Sharpe Ratio:          {metrics['sharpe_ratio']:>8.2f}")
    print(f"Volatility:            {metrics['volatility']:>8.2%}")
    print(f"Max Drawdown:          {metrics['max_drawdown']:>8.2%}")
    print(f"\nBenchmark (SPY):       {metrics['benchmark_return']:>8.2%}")
    print(f"Alpha:                 {metrics['alpha']:>8.2%}")
    print(f"\nRebalance Periods:     {metrics['n_periods']:>8.0f}")
    
    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    
    if metrics['alpha'] > 0:
        print(f"✓ OUTPERFORMED benchmark by {metrics['alpha']:.2%}")
    else:
        print(f"✗ UNDERPERFORMED benchmark by {abs(metrics['alpha']):.2%}")
    
    if metrics['sharpe_ratio'] > 1.0:
        print(f"✓ GOOD risk-adjusted returns (Sharpe {metrics['sharpe_ratio']:.2f})")
    elif metrics['sharpe_ratio'] > 0.5:
        print(f"⚠ MODERATE risk-adjusted returns (Sharpe {metrics['sharpe_ratio']:.2f})")
    else:
        print(f"✗ POOR risk-adjusted returns (Sharpe {metrics['sharpe_ratio']:.2f})")
    
    # Plot results
    backtester.plot_results(results)
    
    # Save results
    results.to_csv('data/results/factor_backtest_results.csv')
    print("\n✓ Results saved to data/results/factor_backtest_results.csv")


if __name__ == '__main__':
    main()