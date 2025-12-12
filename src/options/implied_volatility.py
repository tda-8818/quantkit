"""
Implied Volatility Solver

Implied volatility (IV) is the market's forecast of future volatility, backed out
from actual option prices. It represents the volatility input that makes the
Black-Scholes price match the observed market price.

Key Concepts:
    - Historical volatility: Calculated from past price data
    - Implied volatility: Derived from current option prices
    - IV > HV: Market expects more volatility than history suggests
    - IV < HV: Market expects less volatility than history suggests
    
Uses:
    - Trading: Compare IV across strikes (volatility smile/skew)
    - Risk management: Gauge market fear (VIX is average IV of S&P 500 options)
    - Strategy selection: Sell options when IV is high, buy when low
"""

import numpy as np
from scipy.optimize import brentq, newton
from src.options.black_scholes import BlackScholes


class ImpliedVolatilitySolver:
    """
    Solve for implied volatility using numerical methods
    
    Problem: We observe market price, want to find volatility σ such that:
        Black-Scholes(S, K, T, r, σ) = Market Price
        
    This is a root-finding problem (find σ where error = 0)
    
    Methods available:
        1. Brent's method: Robust, guaranteed convergence, slower
        2. Newton-Raphson: Fast, uses vega, can fail if bad initial guess
    """
    
    def __init__(self, S: float, K: float, T: float, r: float):
        """
        Initialise solver with known option parameters
        
        Args:
            S: Current stock price
            K: Strike price  
            T: Time to expiration (years)
            r: Risk-free rate (annual)
            
        Note: We don't specify volatility because that's what we're solving for!
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
    
    def solve_iv_call(self, market_price: float, method: str = 'brent') -> float:
        """
        Solve for implied volatility of a call option
        
        Args:
            market_price: Observed market price of the call option
            method: 'brent' (robust) or 'newton' (fast)
            
        Returns:
            float: Implied volatility (annual, as decimal)
                   Example: 0.25 means 25% implied volatility
                   
        Example:
            # Market data: AAPL call trading at $8.50
            solver = ImpliedVolatilitySolver(S=150, K=155, T=0.25, r=0.05)
            iv = solver.solve_iv_call(market_price=8.50)
            print(f"Implied vol: {iv:.2%}")  # Might print: "Implied vol: 28.5%"
            
        Raises:
            ValueError: If no solution exists (e.g., price violates arbitrage bounds)
        """
        # Intrinsic value: What option is worth if exercised today
        # Call intrinsic value = max(S - K, 0)
        intrinsic_value = max(self.S - self.K, 0)
        
        # Option price must be at least intrinsic value (arbitrage bound)
        if market_price < intrinsic_value:
            raise ValueError(
                f"Market price {market_price} below intrinsic value {intrinsic_value}. "
                "This violates no-arbitrage condition!"
            )
        
        # Maximum theoretical price: stock price itself (S)
        # Can't be worth more than owning the stock outright
        if market_price > self.S:
            raise ValueError(
                f"Market price {market_price} exceeds stock price {self.S}. "
                "Call can't be worth more than stock!"
            )
        
        if method == 'brent':
            return self._solve_brent_call(market_price)
        elif method == 'newton':
            return self._solve_newton_call(market_price)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'brent' or 'newton'")
    
    def solve_iv_put(self, market_price: float, method: str = 'brent') -> float:
        """
        Solve for implied volatility of a put option
        
        Args:
            market_price: Observed market price of the put option
            method: 'brent' (robust) or 'newton' (fast)
            
        Returns:
            float: Implied volatility (annual, as decimal)
            
        Example:
            # Market data: AAPL put trading at $5.25
            solver = ImpliedVolatilitySolver(S=150, K=155, T=0.25, r=0.05)
            iv = solver.solve_iv_put(market_price=5.25)
            print(f"Implied vol: {iv:.2%}")
        """
        # Intrinsic value for put: max(K - S, 0)
        intrinsic_value = max(self.K - self.S, 0)
        
        if market_price < intrinsic_value:
            raise ValueError(
                f"Market price {market_price} below intrinsic value {intrinsic_value}"
            )
        
        # Maximum put value: present value of strike (can't get more than K)
        max_value = self.K * np.exp(-self.r * self.T)
        if market_price > max_value:
            raise ValueError(
                f"Market price {market_price} exceeds theoretical maximum {max_value}"
            )
        
        if method == 'brent':
            return self._solve_brent_put(market_price)
        elif method == 'newton':
            return self._solve_newton_put(market_price)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _solve_brent_call(self, market_price: float) -> float:
        """
        Solve using Brent's method (combination of bisection, secant, inverse quadratic)
        
        Brent's method:
            - Guaranteed to converge (robust)
            - Requires bracketing interval [a, b] where f(a) and f(b) have opposite signs
            - Slower than Newton but can't fail
            
        We search for σ in range [0.01, 5.0] (1% to 500% volatility)
        This covers all realistic scenarios (even meme stocks)
        
        How it works:
            1. Start with σ_low = 0.01, σ_high = 5.0
            2. Calculate BS_price(σ_low) and BS_price(σ_high)
            3. Since price increases with vol, one will be below market, one above
            4. Iteratively narrow the bracket until σ found
        """
        def objective(sigma):
            """
            Objective function: difference between model and market price
            We want to find σ where this equals zero
            """
            bs = BlackScholes(self.S, self.K, self.T, self.r, sigma)
            return bs.call_price() - market_price
        
        try:
            # Search volatility range: 1% to 500% (covers all realistic scenarios)
            # brentq finds root where objective(σ) = 0
            iv = brentq(objective, 0.01, 5.0, xtol=1e-6, maxiter=100)
            return iv
        except ValueError as e:
            raise ValueError(
                f"Could not find implied volatility. "
                f"Market price {market_price} may be invalid. Error: {e}"
            )
    
    def _solve_brent_put(self, market_price: float) -> float:
        """Solve put IV using Brent's method"""
        def objective(sigma):
            bs = BlackScholes(self.S, self.K, self.T, self.r, sigma)
            return bs.put_price() - market_price
        
        try:
            iv = brentq(objective, 0.01, 5.0, xtol=1e-6, maxiter=100)
            return iv
        except ValueError as e:
            raise ValueError(f"Could not find implied volatility: {e}")
    
    def _solve_newton_call(self, market_price: float, initial_guess: float = 0.3) -> float:
        """
        Solve using Newton-Raphson method (uses derivative for faster convergence)
        
        Newton-Raphson:
            - Very fast convergence (quadratic)
            - Uses derivative (vega) to guide search
            - Can fail if initial guess is bad
            
        Formula:
            σ_new = σ_old - f(σ) / f'(σ)
            
            Where:
            - f(σ) = BS_price(σ) - market_price (error)
            - f'(σ) = vega (how much price changes with σ)
            
        Intuition:
            If BS price is too high, decrease σ by (error / vega)
            If BS price is too low, increase σ by (error / vega)
        """
        def objective_and_derivative(sigma):
            """
            Returns both objective value and its derivative (vega)
            Newton method needs both for: x_new = x - f(x)/f'(x)
            """
            bs = BlackScholes(self.S, self.K, self.T, self.r, sigma)
            price_error = bs.call_price() - market_price
            vega = bs.greeks_call().vega
            return price_error, vega
        
        try:
            # Newton method: Start at 30% vol (typical for stocks)
            # Converges in 3-5 iterations usually
            iv = newton(
                func=lambda sigma: objective_and_derivative(sigma)[0],
                x0=initial_guess,
                fprime=lambda sigma: objective_and_derivative(sigma)[1],
                tol=1e-6,
                maxiter=50
            )
            
            # Validate result is in reasonable range
            if iv < 0.01 or iv > 5.0:
                raise ValueError(f"Implausible IV: {iv}")
                
            return iv
            
        except (ValueError, RuntimeError) as e:
            # Newton method failed, fall back to robust Brent method
            print(f"Newton method failed ({e}), falling back to Brent")
            return self._solve_brent_call(market_price)
    
    def _solve_newton_put(self, market_price: float, initial_guess: float = 0.3) -> float:
        """Solve put IV using Newton-Raphson method"""
        def objective_and_derivative(sigma):
            bs = BlackScholes(self.S, self.K, self.T, self.r, sigma)
            price_error = bs.put_price() - market_price
            vega = bs.greeks_put().vega
            return price_error, vega
        
        try:
            iv = newton(
                func=lambda sigma: objective_and_derivative(sigma)[0],
                x0=initial_guess,
                fprime=lambda sigma: objective_and_derivative(sigma)[1],
                tol=1e-6,
                maxiter=50
            )
            
            if iv < 0.01 or iv > 5.0:
                raise ValueError(f"Implausible IV: {iv}")
                
            return iv
            
        except (ValueError, RuntimeError) as e:
            print(f"Newton method failed ({e}), falling back to Brent")
            return self._solve_brent_put(market_price)