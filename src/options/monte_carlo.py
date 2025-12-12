"""
Monte Carlo Options Pricing

Monte Carlo simulation prices options by:
    1. Simulating thousands of possible stock price paths
    2. Calculating payoff for each path
    3. Averaging payoffs and discounting to present value

Advantages:
    - Can price complex path-dependent options (Asian, barrier, lookback)
    - Easily handles multiple underlying assets
    - Can incorporate realistic dynamics (jumps, stochastic vol)
    
Disadvantages:
    - Slow (needs many simulations for accuracy)
    - Cannot price American options efficiently (need to check exercise at every point)
    - Statistical error (results vary between runs)

Academic Reference:
    Boyle, P. P. (1977). "Options: A Monte Carlo Approach"
    Journal of Financial Economics, 4(3), 323-338.
"""

import numpy as np
from typing import Literal, Callable


class MonteCarlo:
    """
    Monte Carlo simulation for European options
    
    Uses Geometric Brownian Motion (GBM) to simulate stock prices:
        dS = μ S dt + σ S dW
        
    Where:
        - μ: drift (expected return)
        - σ: volatility
        - dW: Wiener process (random walk)
        
    Discrete approximation:
        S(t+Δt) = S(t) * exp((r - 0.5σ²)Δt + σ√Δt * Z)
        
    Where Z ~ N(0,1) (standard normal random variable)
    """
    
    def __init__(self, S: float, K: float, T: float, r: float, sigma: float):
        """
        Initialise Monte Carlo simulator
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate (annual)
            sigma: Volatility (annual)
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
    
    def price_european_call(self, n_simulations: int = 10000, n_steps: int = 252) -> tuple:
        """
        Price European call using Monte Carlo simulation
        
        Args:
            n_simulations: Number of price paths to simulate
                          More paths = more accurate, but slower
                          10,000 is reasonable for quick estimate
                          100,000+ for production use
                          
            n_steps: Number of time steps per simulation
                    252 = daily steps for 1 year (trading days)
                    More steps = smoother paths, but slower
                    
        Returns:
            tuple: (price, standard_error)
                  price: Estimated option price
                  standard_error: 95% confidence interval = ±2*SE
                  
        Example:
            mc = MonteCarlo(S=100, K=105, T=1, r=0.05, sigma=0.2)
            price, se = mc.price_european_call(n_simulations=50000)
            print(f"Call price: ${price:.2f} ± ${2*se:.2f}")
            # Might print: "Call price: $8.23 ± $0.12"
        """
        # Time step size
        dt = self.T / n_steps
        
        # Drift term: (r - 0.5 * σ²) * dt
        # The -0.5σ² term is Itô's lemma correction for log-normal
        drift = (self.r - 0.5 * self.sigma**2) * dt
        
        # Volatility term: σ * √dt
        vol = self.sigma * np.sqrt(dt)
        
        # Generate all random numbers at once (fast vectorised operation)
        # Shape: (n_simulations, n_steps)
        # Each row is one price path, each column is one time step
        Z = np.random.standard_normal((n_simulations, n_steps))
        
        # Simulate price paths using GBM formula
        # S(t+dt) = S(t) * exp(drift + vol * Z)
        
        # Calculate log returns for all steps
        log_returns = drift + vol * Z
        
        # Cumulative log returns give log(S_T / S_0)
        cumulative_log_returns = np.cumsum(log_returns, axis=1)
        
        # Terminal stock prices: S_T = S_0 * exp(cumulative log returns)
        # We only need final prices for European options
        terminal_prices = self.S * np.exp(cumulative_log_returns[:, -1])
        
        # Payoffs: max(S_T - K, 0) for each simulation
        payoffs = np.maximum(terminal_prices - self.K, 0)
        
        # Discount payoffs to present value
        discount_factor = np.exp(-self.r * self.T)
        discounted_payoffs = discount_factor * payoffs
        
        # Option price = average discounted payoff
        price = np.mean(discounted_payoffs)
        
        # Standard error: measures uncertainty in estimate
        # SE = std(payoffs) / sqrt(n)
        # 95% confidence interval: price ± 2*SE
        standard_error = np.std(discounted_payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    def price_european_put(self, n_simulations: int = 10000, n_steps: int = 252) -> tuple:
        """
        Price European put using Monte Carlo simulation
        
        Same as call, but payoff = max(K - S_T, 0)
        
        Returns:
            tuple: (price, standard_error)
        """
        dt = self.T / n_steps
        drift = (self.r - 0.5 * self.sigma**2) * dt
        vol = self.sigma * np.sqrt(dt)
        
        Z = np.random.standard_normal((n_simulations, n_steps))
        log_returns = drift + vol * Z
        cumulative_log_returns = np.cumsum(log_returns, axis=1)
        terminal_prices = self.S * np.exp(cumulative_log_returns[:, -1])
        
        # Put payoff: max(K - S_T, 0)
        payoffs = np.maximum(self.K - terminal_prices, 0)
        
        discount_factor = np.exp(-self.r * self.T)
        discounted_payoffs = discount_factor * payoffs
        
        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    def price_asian_option(self, 
                          option_type: Literal['call', 'put'],
                          averaging: Literal['arithmetic', 'geometric'] = 'arithmetic',
                          n_simulations: int = 10000,
                          n_steps: int = 252) -> tuple:
        """
        Price Asian option using Monte Carlo
        
        Asian options:
            - Payoff depends on AVERAGE price over option life
            - Not just final price like European options
            
        Types:
            - Arithmetic average: (S_1 + S_2 + ... + S_n) / n
            - Geometric average: (S_1 * S_2 * ... * S_n)^(1/n)
            
        Uses:
            - Reduce manipulation risk (can't pump price at expiration)
            - Common in commodities (oil, gold)
            - Corporate hedging (match average costs)
            
        Args:
            option_type: 'call' or 'put'
            averaging: 'arithmetic' or 'geometric'
            n_simulations: Number of paths
            n_steps: Observation points for averaging
            
        Returns:
            tuple: (price, standard_error)
            
        Example:
            # Asian call with arithmetic average
            mc = MonteCarlo(S=100, K=100, T=1, r=0.05, sigma=0.2)
            price, se = mc.price_asian_option('call', 'arithmetic')
            # Asian options are cheaper than European (less volatile payoff)
        """
        dt = self.T / n_steps
        drift = (self.r - 0.5 * self.sigma**2) * dt
        vol = self.sigma * np.sqrt(dt)
        
        # Simulate full paths (need all prices, not just terminal)
        Z = np.random.standard_normal((n_simulations, n_steps))
        log_returns = drift + vol * Z
        
        # Build full price paths
        # paths[i, j] = stock price at simulation i, time step j
        paths = np.zeros((n_simulations, n_steps + 1))
        paths[:, 0] = self.S  # Start at current price
        
        for t in range(1, n_steps + 1):
            paths[:, t] = paths[:, t-1] * np.exp(log_returns[:, t-1])
        
        # Calculate average price for each path
        if averaging == 'arithmetic':
            # Simple average: (sum of all prices) / n
            average_prices = np.mean(paths, axis=1)
        else:  # geometric
            # Geometric average: (product of all prices)^(1/n)
            # Compute as: exp(mean of log prices) to avoid overflow
            average_prices = np.exp(np.mean(np.log(paths), axis=1))
        
        # Payoff based on average price vs strike
        if option_type == 'call':
            payoffs = np.maximum(average_prices - self.K, 0)
        else:  # put
            payoffs = np.maximum(self.K - average_prices, 0)
        
        # Discount and calculate price
        discount_factor = np.exp(-self.r * self.T)
        discounted_payoffs = discount_factor * payoffs
        
        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    def price_barrier_option(self,
                            option_type: Literal['call', 'put'],
                            barrier_type: Literal['up-and-out', 'down-and-out', 'up-and-in', 'down-and-in'],
                            barrier_level: float,
                            n_simulations: int = 10000,
                            n_steps: int = 252) -> tuple:
        """
        Price barrier option using Monte Carlo
        
        Barrier options:
            - Activated or deactivated when price crosses barrier
            - Cheaper than vanilla options (less likely to pay off)
            
        Types:
            - Knock-out: Option dies if barrier touched
              * Up-and-out: Dies if price goes above barrier
              * Down-and-out: Dies if price goes below barrier
              
            - Knock-in: Option activates if barrier touched
              * Up-and-in: Activates if price goes above barrier
              * Down-and-in: Activates if price goes below barrier
              
        Uses:
            - Reduce hedging costs (accept barrier risk for lower premium)
            - Express directional view (e.g., "stock won't crash below $X")
            - Structured products (embed in notes for retail investors)
            
        Args:
            option_type: 'call' or 'put'
            barrier_type: Type of barrier condition
            barrier_level: Barrier price level
            n_simulations: Number of paths
            n_steps: Monitoring frequency (more steps = continuous monitoring)
            
        Returns:
            tuple: (price, standard_error)
            
        Example:
            # Up-and-out call: Worthless if stock touches $120
            mc = MonteCarlo(S=100, K=105, T=1, r=0.05, sigma=0.2)
            price, se = mc.price_barrier_option(
                'call', 'up-and-out', barrier_level=120
            )
            # Will be cheaper than vanilla call
        """
        dt = self.T / n_steps
        drift = (self.r - 0.5 * self.sigma**2) * dt
        vol = self.sigma * np.sqrt(dt)
        
        # Simulate full paths (need to check barrier at every step)
        Z = np.random.standard_normal((n_simulations, n_steps))
        log_returns = drift + vol * Z
        
        paths = np.zeros((n_simulations, n_steps + 1))
        paths[:, 0] = self.S
        
        for t in range(1, n_steps + 1):
            paths[:, t] = paths[:, t-1] * np.exp(log_returns[:, t-1])
        
        # Check barrier condition for each path
        if barrier_type == 'up-and-out':
            # Option dies if price ever goes above barrier
            barrier_hit = np.any(paths >= barrier_level, axis=1)
            active = ~barrier_hit  # Active if barrier never hit
            
        elif barrier_type == 'down-and-out':
            # Option dies if price ever goes below barrier
            barrier_hit = np.any(paths <= barrier_level, axis=1)
            active = ~barrier_hit
            
        elif barrier_type == 'up-and-in':
            # Option activates only if price goes above barrier
            barrier_hit = np.any(paths >= barrier_level, axis=1)
            active = barrier_hit
            
        else:  # down-and-in
            # Option activates only if price goes below barrier
            barrier_hit = np.any(paths <= barrier_level, axis=1)
            active = barrier_hit
        
        # Calculate payoffs only for active paths
        terminal_prices = paths[:, -1]
        
        if option_type == 'call':
            payoffs = np.where(active, np.maximum(terminal_prices - self.K, 0), 0)
        else:  # put
            payoffs = np.where(active, np.maximum(self.K - terminal_prices, 0), 0)
        
        # Discount and calculate price
        discount_factor = np.exp(-self.r * self.T)
        discounted_payoffs = discount_factor * payoffs
        
        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    def get_confidence_interval(self, price: float, standard_error: float, confidence: float = 0.95) -> tuple:
        """
        Calculate confidence interval for Monte Carlo estimate
        
        Monte Carlo gives statistical estimate with uncertainty.
        Confidence interval tells us: "True price is in this range with X% probability"
        
        Args:
            price: Estimated option price
            standard_error: Standard error from simulation
            confidence: Confidence level (0.95 = 95%)
            
        Returns:
            tuple: (lower_bound, upper_bound)
            
        Example:
            price, se = mc.price_european_call(n_simulations=10000)
            lower, upper = mc.get_confidence_interval(price, se, 0.95)
            print(f"Price: ${price:.2f}, 95% CI: [${lower:.2f}, ${upper:.2f}]")
            # Might print: "Price: $8.23, 95% CI: [$8.11, $8.35]"
        """
        # Z-score for confidence level
        # 95% → 1.96, 99% → 2.576, 90% → 1.645
        from scipy.stats import norm
        z_score = norm.ppf((1 + confidence) / 2)
        
        margin_of_error = z_score * standard_error
        
        lower_bound = price - margin_of_error
        upper_bound = price + margin_of_error
        
        return lower_bound, upper_bound