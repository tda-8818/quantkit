"""
Complete factor investing example
Demonstrates full workflow from data download to portfolio construction
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.data.pipeline import MarketDataPipeline
from src.data.downloaders.fundamental import FundamentalDownloader
from src.data.storage.database import Database
from src.factors.calculator import FactorCalculator
from src.portfolio.constructor import PortfolioConstructor
from src.portfolio.rebalancer import Rebalancer


def main():
    """Run complete factor model example"""
    
    print("=" * 70)
    print("FACTOR INVESTING MODEL - COMPLETE EXAMPLE")
    print("=" * 70)
    
    # ========================================================================
    # STEP 1: Define Universe
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 1: DEFINE STOCK UNIVERSE")
    print("=" * 70)
    
    # Use liquid large-cap stocks for testing (20 stocks)
    # In production, you'd use full S&P 500 or Russell 1000
    universe = [
        # Tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        # Financial
        'JPM', 'BAC', 'WFC', 'GS',
        # Healthcare
        'JNJ', 'UNH', 'PFE', 'ABBV',
        # Consumer
        'WMT', 'HD', 'NKE', 'MCD',
        # Other
        'XOM'
    ]
    
    print(f"Universe: {len(universe)} stocks")
    print(f"Stocks: {', '.join(universe)}")
    
    # ========================================================================
    # STEP 2: Download Price Data
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: DOWNLOAD PRICE DATA")
    print("=" * 70)
    
    pipeline = MarketDataPipeline()
    
    print("Downloading price data (2020-2024)...")
    pipeline.update(universe, '2020-01-01', '2024-12-01')
    
    # ========================================================================
    # STEP 3: Download Fundamental Data
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: DOWNLOAD FUNDAMENTAL DATA")
    print("=" * 70)
    
    fundamental_downloader = FundamentalDownloader()
    
    print("Downloading fundamentals (P/E, ROE, debt, etc.)...")
    fundamentals_df = fundamental_downloader.get_batch(universe)
    
    print(f"\n✓ Downloaded fundamentals for {len(fundamentals_df)} stocks")
    print("\nSample data:")
    print(fundamentals_df[['ticker', 'pe_ratio', 'pb_ratio', 'roe', 'debt_to_equity']].head())
    
    # Store in database
    db = Database()
    db.store_fundamentals(fundamentals_df)
    
    # ========================================================================
    # STEP 4: Calculate Factor Scores
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 4: CALCULATE FACTOR SCORES")
    print("=" * 70)
    
    calculator = FactorCalculator(pipeline)
    
    # As-of date for ranking (use most recent)
    ranking_date = pd.Timestamp('2024-06-01')
    
    # Calculate with custom factor weights
    # Example: Emphasise momentum and quality over value
    factor_weights = {
        'value': 0.20,
        'momentum': 0.35,
        'quality': 0.30,
        'volatility': 0.15
    }
    
    rankings = calculator.calculate_all_factors(
        tickers=universe,
        date=ranking_date,
        weights=factor_weights
    )
    
    print("\nTop 10 stocks by combined score:")
    print(rankings[['ticker', 'value_rank', 'momentum_rank', 'quality_rank', 
                   'volatility_rank', 'combined_score']].head(10))
    
    # ========================================================================
    # STEP 5: Construct Portfolio
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 5: CONSTRUCT PORTFOLIO")
    print("=" * 70)
    
    constructor = PortfolioConstructor(n_stocks=10)
    
    # Create equal-weighted portfolio
    portfolio = constructor.construct_equal_weight(rankings)
    
    constructor.print_portfolio(portfolio)
    
    # ========================================================================
    # STEP 6: Simulate Rebalancing
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 6: SIMULATE MONTHLY REBALANCING")
    print("=" * 70)
    
    # Simulate: Recalculate factors 1 month later
    next_ranking_date = pd.Timestamp('2024-07-01')
    
    print(f"\nRecalculating factors as of {next_ranking_date.date()}...")
    new_rankings = calculator.calculate_all_factors(
        tickers=universe,
        date=next_ranking_date,
        weights=factor_weights
    )
    
    new_portfolio = constructor.construct_equal_weight(new_rankings)
    
    # Calculate rebalancing actions
    rebalancer = Rebalancer(turnover_constraint=0.5)
    actions = rebalancer.calculate_rebalance(portfolio, new_portfolio)
    
    rebalancer.print_rebalance_actions(actions)
    
    # ========================================================================
    # STEP 7: Compare Factor Strategies
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 7: COMPARE DIFFERENT FACTOR COMBINATIONS")
    print("=" * 70)
    
    strategies = {
        'Pure Value': {'value': 1.0, 'momentum': 0.0, 'quality': 0.0, 'volatility': 0.0},
        'Pure Momentum': {'value': 0.0, 'momentum': 1.0, 'quality': 0.0, 'volatility': 0.0},
        'Pure Quality': {'value': 0.0, 'momentum': 0.0, 'quality': 1.0, 'volatility': 0.0},
        'Equal Weight': {'value': 0.25, 'momentum': 0.25, 'quality': 0.25, 'volatility': 0.25},
        'Momentum + Quality': {'value': 0.0, 'momentum': 0.5, 'quality': 0.5, 'volatility': 0.0},
    }
    
    comparison_results = []
    
    for strategy_name, weights in strategies.items():
        print(f"\n{strategy_name}: {weights}")
        
        rankings = calculator.calculate_all_factors(
            tickers=universe,
            date=ranking_date,
            weights=weights
        )
        
        top_5 = rankings.head(5)['ticker'].tolist()
        avg_score = rankings.head(10)['combined_score'].mean()
        
        print(f"  Top 5: {', '.join(top_5)}")
        print(f"  Avg score (top 10): {avg_score:.3f}")
        
        comparison_results.append({
            'strategy': strategy_name,
            'top_stocks': top_5,
            'avg_score': avg_score
        })
    
    # ========================================================================
    # STEP 8: Export Results
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 8: EXPORT RESULTS")
    print("=" * 70)
    
    # Save rankings
    rankings.to_csv('data/results/factor_rankings.csv', index=False)
    print("✓ Rankings saved to data/results/factor_rankings.csv")
    
    # Save portfolio
    portfolio_df = pd.DataFrame([
        {'ticker': ticker, 'weight': weight}
        for ticker, weight in portfolio.holdings.items()
    ])
    portfolio_df.to_csv('data/results/factor_portfolio.csv', index=False)
    print("✓ Portfolio saved to data/results/factor_portfolio.csv")
    
    # Save comparison
    comparison_df = pd.DataFrame(comparison_results)
    comparison_df.to_csv('data/results/factor_comparison.csv', index=False)
    print("✓ Comparison saved to data/results/factor_comparison.csv")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Processed {len(universe)} stocks")
    print(f"✓ Calculated 4 factors (value, momentum, quality, volatility)")
    print(f"✓ Constructed portfolio with {len(portfolio.holdings)} holdings")
    print(f"✓ Simulated monthly rebalancing")
    print(f"✓ Compared 5 factor strategies")
    print(f"✓ Exported results to data/results/")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Run full backtest: python examples/factor_backtest.py")
    print("2. Compare to S&P 500 benchmark")
    print("3. Test on larger universe (S&P 500)")
    print("4. Implement walk-forward validation")


if __name__ == '__main__':
    main()