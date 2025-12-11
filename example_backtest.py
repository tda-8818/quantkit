"""
Example: Backtest a momentum strategy on AAPL
"""

from src.data_pipeline import MarketDataPipeline
from src.backtester import Backtester, MomentumStrategy, SimpleMovingAverageCrossover

# Get data
pipeline = MarketDataPipeline()
data = pipeline.get_data('VOO', start_date='2020-01-01', end_date='2024-12-01')

print(data.columns)
print(data.head())

# Test Strategy 1: Momentum
print("\n" + "="*60)
print("Testing: 12-Month Momentum Strategy")
print("="*60)

momentum_strategy = MomentumStrategy(data, lookback=252)
backtester = Backtester(momentum_strategy, initial_capital=100000)
results = backtester.run()
results.summary()
results.plot()

# Test Strategy 2: Moving Average Crossover
print("\n" + "="*60)
print("Testing: Moving Average Crossover (50/200)")
print("="*60)

ma_strategy = SimpleMovingAverageCrossover(data, fast_period=50, slow_period=200)
backtester = Backtester(ma_strategy, initial_capital=100000)
results = backtester.run()
results.summary()
results.plot()