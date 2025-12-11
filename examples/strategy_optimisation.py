import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.pipeline import MarketDataPipeline
from src.backtesting.backtester import Backtester
from src.backtesting.optimiser import StrategyOptimiser, StrategyConfig
from src.strategies.momentum import MomentumStrategy
from src.strategies.mean_reversion import MeanReversionStrategy

# Initialize
pipeline = MarketDataPipeline()
optimiser = StrategyOptimiser(pipeline)

# Download data for multiple tickers
tickers = ['VOO', 'QQQ', 'DIA', 'IWM', 'SPY']
print("Downloading data...")
pipeline.update(tickers, '2020-01-01', '2024-12-01')

# Define strategies to test
strategies = [
    # Momentum with different lookbacks
    StrategyConfig('Momentum_3m', MomentumStrategy, {'lookback': 63}),
    StrategyConfig('Momentum_6m', MomentumStrategy, {'lookback': 126}),
    StrategyConfig('Momentum_9m', MomentumStrategy, {'lookback': 189}),
    StrategyConfig('Momentum_12m', MomentumStrategy, {'lookback': 252}),
    
    # Mean Reversion with different lookbacks
    StrategyConfig('MeanRev_20d', MeanReversionStrategy, {'lookback': 20}),
    StrategyConfig('MeanRev_50d', MeanReversionStrategy, {'lookback': 50}),
    StrategyConfig('MeanRev_100d', MeanReversionStrategy, {'lookback': 100}),
    StrategyConfig('MeanRev_200d', MeanReversionStrategy, {'lookback': 200}),
]

# Run grid search
results = optimiser.grid_search(
    tickers=tickers,
    strategies=strategies,
    start_date='2020-01-01',
    end_date='2024-12-01'
)

# Print top 10 strategies
optimiser.print_top_strategies(results, n=10)

# Compare strategy types
optimiser.compare_strategies(results, metric='sharpe')

# Export results
results.to_csv('data/results/strategy_results.csv', index=False)
print("\n✓ Results saved to data/results/strategy_results.csv")

# Plot best strategy
print("\nPlotting best strategy...")
best = results.iloc[0]
best['results_obj'].plot()