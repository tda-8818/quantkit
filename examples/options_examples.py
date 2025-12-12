"""
Comprehensive options pricing examples
Demonstrates all pricing models and strategies
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from src.options.black_scholes import BlackScholes
from src.options.implied_volatility import ImpliedVolatilitySolver
from src.options.binomial_tree import BinomialTree
from src.options.monte_carlo import MonteCarlo
from src.options.strategies import (
    bull_call_spread,
    long_straddle,
    iron_condor
)


def example_1_black_scholes():
    """Example 1: Basic Black-Scholes pricing"""
    print("\n" + "="*70)
    print("EXAMPLE 1: BLACK-SCHOLES PRICING")
    print("="*70)
    
    # Scenario: Price AAPL options
    # AAPL currently at $150
    # Strike $155, 3 months to expiration
    # 5% risk-free rate, 30% volatility
    
    bs = BlackScholes(
        S=150,      # Current price
        K=155,      # Strike
        T=0.25,     # 3 months
        r=0.05,     # 5% rate
        sigma=0.30  # 30% vol
    )
    
    # Price options
    call_price = bs.call_price()
    put_price = bs.put_price()
    
    print(f"\nStock Price: $150")
    print(f"Strike Price: $155")
    print(f"Time to Expiration: 3 months")
    print(f"Volatility: 30%")
    print(f"\nCall Price: ${call_price:.2f}")
    print(f"Put Price: ${put_price:.2f}")
    
    # Calculate Greeks
    call_greeks = bs.greeks_call()
    put_greeks = bs.greeks_put()
    
    print(f"\nCALL GREEKS:")
    print(f"  Delta: {call_greeks.delta:.4f}  (Call gains $0.{int(call_greeks.delta*100)} per $1 stock increase)")
    print(f"  Gamma: {call_greeks.gamma:.4f}  (Delta changes by {call_greeks.gamma:.4f} per $1 stock move)")
    print(f"  Theta: {call_greeks.theta:.4f}  (Loses ${abs(call_greeks.theta):.2f} per day)")
    print(f"  Vega:  {call_greeks.vega:.4f}  (Gains ${call_greeks.vega:.2f} per 1% vol increase)")
    
    print(f"\nPUT GREEKS:")
    print(f"  Delta: {put_greeks.delta:.4f}  (Put gains $0.{int(abs(put_greeks.delta)*100)} per $1 stock decrease)")
    print(f"  Theta: {put_greeks.theta:.4f}  (Loses ${abs(put_greeks.theta):.2f} per day)")


def example_2_implied_volatility():
    """Example 2: Solve for implied volatility"""
    print("\n" + "="*70)
    print("EXAMPLE 2: IMPLIED VOLATILITY")
    print("="*70)
    
    # Scenario: AAPL call trading at $8.50 in market
    # What volatility is implied by this price?
    
    solver = ImpliedVolatilitySolver(
        S=150,
        K=155,
        T=0.25,
        r=0.05
    )
    
    market_price = 8.50
    
    # Solve using both methods
    iv_brent = solver.solve_iv_call(market_price, method='brent')
    iv_newton = solver.solve_iv_call(market_price, method='newton')
    
    print(f"\nMarket Data:")
    print(f"  Call Price: ${market_price:.2f}")
    print(f"  Stock: $150, Strike: $155")
    
    print(f"\nImplied Volatility:")
    print(f"  Brent method:  {iv_brent:.2%}")
    print(f"  Newton method: {iv_newton:.2%}")
    
    # Verify by pricing with implied vol
    bs_verify = BlackScholes(150, 155, 0.25, 0.05, iv_brent)
    price_verify = bs_verify.call_price()
    
    print(f"\nVerification:")
    print(f"  Re-priced with IV {iv_brent:.2%}: ${price_verify:.2f}")
    print(f"  Market price: ${market_price:.2f}")
    print(f"  Error: ${abs(price_verify - market_price):.4f}")


def example_3_american_options():
    """Example 3: American vs European options"""
    print("\n" + "="*70)
    print("EXAMPLE 3: AMERICAN VS EUROPEAN OPTIONS")
    print("="*70)
    
    # Compare American and European pricing
    # American options worth more (early exercise right)
    
    tree = BinomialTree(
        S=100,
        K=105,
        T=1.0,
        r=0.05,
        sigma=0.25,
        N=100  # 100 steps
    )
    
    european_call = tree.price_european_call()
    american_call = tree.price_american_call()
    european_put = tree.price_european_put()
    american_put = tree.price_american_put()
    
    print(f"\nStock: $100, Strike: $105, 1 year")
    print(f"\nCALLS:")
    print(f"  European: ${european_call:.2f}")
    print(f"  American: ${american_call:.2f}")
    print(f"  Premium:  ${american_call - european_call:.2f} ({(american_call - european_call)/european_call*100:.1f}%)")
    
    print(f"\nPUTS:")
    print(f"  European: ${european_put:.2f}")
    print(f"  American: ${american_put:.2f}")
    print(f"  Premium:  ${american_put - european_put:.2f} ({(american_put - european_put)/european_put*100:.1f}%)")
    
    print(f"\nNote: American call = European call (no early exercise benefit)")
    print(f"      American put > European put (early exercise can be optimal)")


def example_4_monte_carlo():
    """Example 4: Monte Carlo simulation with confidence intervals"""
    print("\n" + "="*70)
    print("EXAMPLE 4: MONTE CARLO SIMULATION")
    print("="*70)
    
    mc = MonteCarlo(
        S=100,
        K=105,
        T=1.0,
        r=0.05,
        sigma=0.25
    )
    
    # Price with increasing number of simulations
    simulations = [1000, 10000, 50000]
    
    print(f"\nEuropean Call (Stock $100, Strike $105, 1 year):\n")
    
    for n_sims in simulations:
        price, se = mc.price_european_call(n_simulations=n_sims)
        lower, upper = mc.get_confidence_interval(price, se, 0.95)
        
        print(f"{n_sims:>6,} simulations:")
        print(f"  Price: ${price:.3f}")
        print(f"  95% CI: [${lower:.3f}, ${upper:.3f}]")
        print(f"  Width: ${upper - lower:.3f}\n")
    
    # Compare to Black-Scholes (exact)
    bs = BlackScholes(100, 105, 1.0, 0.05, 0.25)
    exact_price = bs.call_price()
    
    print(f"Black-Scholes (exact): ${exact_price:.3f}")
    print(f"\nNote: More simulations → narrower confidence interval")


def example_5_exotic_options():
    """Example 5: Exotic options (Asian, Barrier)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: EXOTIC OPTIONS")
    print("="*70)
    
    mc = MonteCarlo(
        S=100,
        K=100,
        T=1.0,
        r=0.05,
        sigma=0.25
    )
    
    # Price different option types
    european_call, _ = mc.price_european_call(n_simulations=20000)
    asian_call, _ = mc.price_asian_option('call', 'arithmetic', n_simulations=20000)
    barrier_call, _ = mc.price_barrier_option('call', 'up-and-out', barrier_level=115, n_simulations=20000)
    
    print(f"\nAll options: Stock $100, Strike $100, 1 year\n")
    print(f"European Call:            ${european_call:.2f}")
    print(f"Asian Call (arithmetic):  ${asian_call:.2f}  (cheaper - based on average)")
    print(f"Barrier Call (out @ 115): ${barrier_call:.2f}  (cheaper - can knock out)")
    
    print(f"\nRelative prices:")
    print(f"  Asian   = {asian_call/european_call:.1%} of European")
    print(f"  Barrier = {barrier_call/european_call:.1%} of European")


def example_6_option_strategies():
    """Example 6: Multi-leg option strategies"""
    print("\n" + "="*70)
    print("EXAMPLE 6: OPTION STRATEGIES")
    print("="*70)
    
    # Stock at $100
    S, T, r, sigma = 100, 0.25, 0.05, 0.30
    
    print("\n--- BULL CALL SPREAD ---")
    bull_spread = bull_call_spread(S, T, r, sigma, lower_strike=100, upper_strike=110)
    bull_spread.print_summary()
    
    print("\n--- LONG STRADDLE ---")
    straddle = long_straddle(S, T, r, sigma, strike=100)
    straddle.print_summary()
    
    print("\n--- IRON CONDOR ---")
    condor = iron_condor(S, T, r, sigma, 
                        put_lower=85, put_upper=90,
                        call_lower=110, call_upper=115)
    condor.print_summary()


def example_7_visualisations():
    """Example 7: Visualise option payoffs and Greeks"""
    print("\n" + "="*70)
    print("EXAMPLE 7: VISUALISATIONS")
    print("="*70)
    
    # Create visualisations
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Option payoffs
    stock_range = np.linspace(70, 130, 100)
    
    # Bull call spread
    bull_spread = bull_call_spread(100, 0.25, 0.05, 0.30, 100, 110)
    bull_payoffs = bull_spread.calculate_payoff(stock_range)
    
    axes[0, 0].plot(stock_range, bull_payoffs, linewidth=2)
    axes[0, 0].axhline(0, color='black', linestyle='--', alpha=0.3)
    axes[0, 0].axvline(100, color='red', linestyle='--', alpha=0.3, label='Current price')
    axes[0, 0].set_xlabel('Stock Price at Expiration')
    axes[0, 0].set_ylabel('Profit/Loss')
    axes[0, 0].set_title('Bull Call Spread Payoff')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Greeks vs stock price
    stock_prices = np.linspace(80, 120, 50)
    deltas = []
    gammas = []
    
    for price in stock_prices:
        bs = BlackScholes(price, 100, 0.25, 0.05, 0.30)
        greeks = bs.greeks_call()
        deltas.append(greeks.delta)
        gammas.append(greeks.gamma)
    
    axes[0, 1].plot(stock_prices, deltas, label='Delta', linewidth=2)
    axes[0, 1].axvline(100, color='red', linestyle='--', alpha=0.3)
    axes[0, 1].set_xlabel('Stock Price')
    axes[0, 1].set_ylabel('Delta')
    axes[0, 1].set_title('Call Option Delta')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Gamma vs stock price
    axes[1, 0].plot(stock_prices, gammas, label='Gamma', color='orange', linewidth=2)
    axes[1, 0].axvline(100, color='red', linestyle='--', alpha=0.3)
    axes[1, 0].set_xlabel('Stock Price')
    axes[1, 0].set_ylabel('Gamma')
    axes[1, 0].set_title('Call Option Gamma (peaks at-the-money)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Volatility smile
    strikes = np.array([80, 85, 90, 95, 100, 105, 110, 115, 120])
    ivs = []
    
    for strike in strikes:
        bs = BlackScholes(100, strike, 0.25, 0.05, 0.30)
        market_price = bs.call_price()
        
        # Add some artificial skew for visualisation
        # (real market data would show actual smile)
        moneyness = strike / 100
        skew_adjustment = 0.05 * (moneyness - 1)**2
        adjusted_price = market_price * (1 + skew_adjustment)
        
        solver = ImpliedVolatilitySolver(100, strike, 0.25, 0.05)
        try:
            iv = solver.solve_iv_call(adjusted_price)
            ivs.append(iv)
        except:
            ivs.append(np.nan)
    
    axes[1, 1].plot(strikes, np.array(ivs)*100, 'o-', linewidth=2)
    axes[1, 1].axvline(100, color='red', linestyle='--', alpha=0.3, label='ATM')
    axes[1, 1].set_xlabel('Strike Price')
    axes[1, 1].set_ylabel('Implied Volatility (%)')
    axes[1, 1].set_title('Volatility Smile (stylised)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/results/options_visualisations.png', dpi=150, bbox_inches='tight')
    print("\n✓ Visualisations saved to data/results/options_visualisations.png")
    plt.show()


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("OPTIONS PRICING - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    example_1_black_scholes()
    example_2_implied_volatility()
    example_3_american_options()
    example_4_monte_carlo()
    example_5_exotic_options()
    example_6_option_strategies()
    example_7_visualisations()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETE")
    print("="*70)
    print("\nYou now have a complete options pricing library!")
    print("Includes:")
    print("  ✓ Black-Scholes (analytical)")
    print("  ✓ Implied volatility solver")
    print("  ✓ Binomial trees (American options)")
    print("  ✓ Monte Carlo (exotic options)")
    print("  ✓ Option strategies (spreads, straddles, condors)")
    print("  ✓ Greeks calculation")
    print("  ✓ Visualisations")


if __name__ == '__main__':
    main()