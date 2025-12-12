"""
Options pricing and analysis module

Implements:
    - Black-Scholes model (closed-form solution)
    - Implied volatility solver
    - Binomial tree (American options)
    - Monte Carlo simulation (path-dependent options)
    - Option strategies (multi-leg positions)
"""

from src.options.black_scholes import BlackScholes, OptionPrice
from src.options.implied_volatility import ImpliedVolatilitySolver
from src.options.binomial_tree import BinomialTree
from src.options.monte_carlo import MonteCarlo
from src.options.strategies import (
    OptionStrategy,
    OptionLeg,
    bull_call_spread,
    bear_put_spread,
    long_straddle,
    long_strangle,
    iron_condor,
    butterfly_spread
)

__all__ = [
    'BlackScholes',
    'OptionPrice',
    'ImpliedVolatilitySolver',
    'BinomialTree',
    'MonteCarlo',
    'OptionStrategy',
    'OptionLeg',
    'bull_call_spread',
    'bear_put_spread',
    'long_straddle',
    'long_strangle',
    'iron_condor',
    'butterfly_spread',
]