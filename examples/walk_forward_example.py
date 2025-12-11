import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.pipeline import MarketDataPipeline
from src.backtesting.validation import split_data, validate_no_leakage, print_split_summary
from src.backtesting.walk_forward import WalkForwardOptimiser
from src.backtesting.backtester import Backtester
from src.strategies.momentum import MomentumStrategy

# Initialise
pipeline = MarketDataPipeline()

# Get data
print("Loading data...")
data = pipeline.get_data('VOO', start_date='2020-01-01', end_date='2024-12-01')

print(f"Total data: {len(data)} days from {data.index[0]} to {data.index[-1]}\n")

# ============================================================
# METHOD 1: Simple Train/Val/Test Split
# ============================================================
print("\n" + "="*70)
print("METHOD 1: SIMPLE TRAIN/VAL/TEST SPLIT")
print("="*70)

split = split_data(data, train_pct=0.6, val_pct=0.2, test_pct=0.2)
print_split_summary(split)

# Validate no leakage
validate_no_leakage(split.train, split.test)

# Train on training set
print("\n1. Training on train set...")
strategy_train = MomentumStrategy(split.train, lookback=189)
backtester_train = Backtester(strategy_train)
results_train = backtester_train.run()
print(f"   Train Sharpe: {results_train.sharpe_ratio:.3f}")

# Validate on validation set
print("\n2. Validating on validation set...")
strategy_val = MomentumStrategy(split.validation, lookback=189)
backtester_val = Backtester(strategy_val)
results_val = backtester_val.run()
print(f"   Val Sharpe: {results_val.sharpe_ratio:.3f}")

# Final test on test set
print("\n3. Final test on test set...")
strategy_test = MomentumStrategy(split.test, lookback=189)
backtester_test = Backtester(strategy_test)
results_test = backtester_test.run()
print(f"   Test Sharpe: {results_test.sharpe_ratio:.3f}")

print("\nRESULTS SUMMARY:")
print(f"  Train Sharpe:  {results_train.sharpe_ratio:.3f}")
print(f"  Val Sharpe:    {results_val.sharpe_ratio:.3f}")
print(f"  Test Sharpe:   {results_test.sharpe_ratio:.3f}")
print(f"  Degradation:   {results_train.sharpe_ratio - results_test.sharpe_ratio:.3f}")

if results_train.sharpe_ratio - results_test.sharpe_ratio < 0.2:
    print("  ✓ Strategy is ROBUST (low degradation)")
else:
    print("  ✗ Strategy may be OVERFIT (high degradation)")

# ============================================================
# METHOD 2: Walk-Forward Optimisation
# ============================================================
print("\n\n" + "="*70)
print("METHOD 2: WALK-FORWARD OPTIMISATION")
print("="*70)

optimiser = WalkForwardOptimiser()

# Test multiple lookback periods
param_grid = {
    'lookback': [63, 126, 189, 252]  # 3, 6, 9, 12 months
}

summary = optimiser.Optimise(
    strategy_class=MomentumStrategy,
    data=data,
    param_grid=param_grid,
    train_window=504,  # 2 years training
    test_window=126,   # 6 months testing
    step_size=126      # Step forward 6 months each time
)

# Print comprehensive summary
summary.print_summary()

# Plot results
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Train vs Test Sharpe over time
windows = [w.window_id for w in summary.all_windows]
train_sharpes = [w.train_sharpe for w in summary.all_windows]
test_sharpes = [w.test_sharpe for w in summary.all_windows]

axes[0].plot(windows, train_sharpes, 'o-', label='Train Sharpe', linewidth=2)
axes[0].plot(windows, test_sharpes, 's-', label='Test Sharpe', linewidth=2)
axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.3)
axes[0].set_xlabel('Window')
axes[0].set_ylabel('Sharpe Ratio')
axes[0].set_title('Walk-Forward: Train vs Test Sharpe Ratio')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Sharpe degradation over time
degradation = [w.train_sharpe - w.test_sharpe for w in summary.all_windows]
axes[1].bar(windows, degradation, alpha=0.7)
axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.3)
axes[1].set_xlabel('Window')
axes[1].set_ylabel('Sharpe Degradation')
axes[1].set_title('Walk-Forward: Sharpe Degradation (Train - Test)')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/results/walk_forward_analysis.png', dpi=150, bbox_inches='tight')
print("\n✓ Chart saved to data/results/walk_forward_analysis.png")
plt.show()