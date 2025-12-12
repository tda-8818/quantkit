"""
Binomial Tree Options Pricing Model

Academic Reference:
    Cox, J. C., Ross, S. A., & Rubinstein, M. (1979). 
    "Option Pricing: A Simplified Approach"
    Journal of Financial Economics, 7(3), 229-263.

Key Advantages Over Black-Scholes:
    1. Can price American options (early exercise allowed)
    2. Can handle dividends easily
    3. More intuitive (visualise price tree)
    4. No closed-form formula needed
    
How It Works:
    - Divide time to expiration into N steps
    - At each step, stock can go up or down
    - Build tree of all possible prices
    - Work backwards from expiration, calculating option value at each node
    - At expiration: option value = intrinsic value
    - Before expiration: option value = max(intrinsic value, continuation value)
    
Visual Example (3 steps):
                    S*u³
                   /
              S*u² 
             /    \
        S*u         S*u²*d
       /   \       /
      S      S*u*d
       \   /       \
        S*d         S*u*d²
             \     /
              S*d²
                   \
                    S*d³
                    
Where u = up factor, d = down factor
"""

import numpy as np
from typing import Literal


class BinomialTree:
    """
    Binomial tree model for European and American options
    
    The binomial model discretises time and builds a tree of possible stock prices.
    More steps = more accurate (converges to Black-Scholes as N → ∞)
    
    Typical usage:
        - N = 50-100 steps for decent accuracy
        - N = 200+ for high precision
        - N = 10-20 for quick estimates
    """
    
    def __init__(self, S: float, K: float, T: float, r: float, sigma: float, N: int = 100):
        """
        Initialise binomial tree model
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate (annual)
            sigma: Volatility (annual)
            N: Number of time steps (more steps = more accurate, but slower)
               50-100 is usually good balance between speed and accuracy
               
        Note: Tree grows exponentially! N=100 creates ~10,000 nodes
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N = N
        
        # Calculate time step (Δt)
        # Example: T=1 year, N=100 → Δt = 0.01 years (3.65 days)
        self.dt = T / N
        
        # Calculate up and down factors using Cox-Ross-Rubinstein parameterisation
        # This ensures the tree matches the volatility of the underlying
        
        # Up factor: stock multiplies by u if it goes up
        # u = e^(σ√Δt)
        # Example: σ=30%, Δt=0.01 → u = 1.0305 (3.05% up move)
        self.u = np.exp(sigma * np.sqrt(self.dt))
        
        # Down factor: stock multiplies by d if it goes down
        # d = 1/u (ensures recombining tree)
        # Example: d = 1/1.0305 = 0.9704 (2.96% down move)
        self.d = 1 / self.u
        
        # Risk-neutral probability of up move
        # This is NOT the real-world probability!
        # It's the probability in a risk-neutral world where all assets earn risk-free rate
        # Formula: p = (e^(rΔt) - d) / (u - d)
        # Typically p ≈ 0.5 for at-the-money options
        self.p = (np.exp(r * self.dt) - self.d) / (self.u - self.d)
        
        # Risk-neutral probability of down move
        self.q = 1 - self.p
        
        # Validate probabilities (must be between 0 and 1)
        if not 0 <= self.p <= 1:
            raise ValueError(
                f"Invalid probability p={self.p}. "
                f"This usually means parameters are unrealistic."
            )
    
    def price_european_call(self) -> float:
        """
        Price European call option using binomial tree
        
        European = Can only exercise at expiration
        
        Algorithm:
            1. Build price tree (all possible stock prices at each step)
            2. Calculate payoff at expiration: max(S - K, 0) at each terminal node
            3. Work backwards: discount expected value using risk-neutral probabilities
            4. Value at t=0 is the option price
            
        Returns:
            float: Call option price
            
        Note: For European options, this converges to Black-Scholes as N → ∞
        """
        # Step 1: Build stock price tree
        # stock_tree[i][j] = stock price at step i, node j
        # At step i, there are i+1 possible nodes (0 to i)
        stock_tree = self._build_stock_tree()
        
        # Step 2: Initialise option values at expiration (step N)
        # At expiration, option value = intrinsic value = max(S - K, 0)
        option_tree = np.zeros((self.N + 1, self.N + 1))
        
        for j in range(self.N + 1):
            # Terminal stock price: S * u^j * d^(N-j)
            terminal_price = stock_tree[self.N][j]
            
            # Call payoff: max(stock price - strike, 0)
            option_tree[self.N][j] = max(terminal_price - self.K, 0)
        
        # Step 3: Work backwards through tree
        # At each node, option value = discounted expected value of next step
        discount_factor = np.exp(-self.r * self.dt)
        
        for i in range(self.N - 1, -1, -1):  # From step N-1 down to 0
            for j in range(i + 1):  # At step i, there are i+1 nodes
                # Expected value = p * (value if up) + q * (value if down)
                up_value = option_tree[i + 1][j + 1]  # If stock goes up
                down_value = option_tree[i + 1][j]    # If stock goes down
                
                expected_value = self.p * up_value + self.q * down_value
                
                # Discount back one period
                option_tree[i][j] = discount_factor * expected_value
        
        # Value at root (t=0) is the option price
        return option_tree[0][0]
    
    def price_european_put(self) -> float:
        """
        Price European put option using binomial tree
        
        Same algorithm as call, but payoff = max(K - S, 0)
        
        Returns:
            float: Put option price
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros((self.N + 1, self.N + 1))
        
        # Terminal payoffs: max(strike - stock, 0)
        for j in range(self.N + 1):
            terminal_price = stock_tree[self.N][j]
            option_tree[self.N][j] = max(self.K - terminal_price, 0)
        
        # Work backwards
        discount_factor = np.exp(-self.r * self.dt)
        
        for i in range(self.N - 1, -1, -1):
            for j in range(i + 1):
                up_value = option_tree[i + 1][j + 1]
                down_value = option_tree[i + 1][j]
                expected_value = self.p * up_value + self.q * down_value
                option_tree[i][j] = discount_factor * expected_value
        
        return option_tree[0][0]
    
    def price_american_call(self) -> float:
        """
        Price American call option using binomial tree
        
        American = Can exercise at ANY time before expiration
        
        Key difference from European:
            At each node, compare:
                1. Continuation value (hold option, get expected value)
                2. Exercise value (exercise now, get intrinsic value)
            Option value = max(continuation, exercise)
            
        For calls on non-dividend stocks:
            - Early exercise is NEVER optimal (proven mathematically)
            - American call = European call
            - But we implement early exercise check anyway for completeness
            
        Returns:
            float: American call option price
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros((self.N + 1, self.N + 1))
        
        # Terminal payoffs
        for j in range(self.N + 1):
            terminal_price = stock_tree[self.N][j]
            option_tree[self.N][j] = max(terminal_price - self.K, 0)
        
        discount_factor = np.exp(-self.r * self.dt)
        
        # Work backwards with early exercise check
        for i in range(self.N - 1, -1, -1):
            for j in range(i + 1):
                # Continuation value: expected value if we hold
                up_value = option_tree[i + 1][j + 1]
                down_value = option_tree[i + 1][j]
                continuation_value = discount_factor * (self.p * up_value + self.q * down_value)
                
                # Exercise value: what we get if we exercise now
                current_stock_price = stock_tree[i][j]
                exercise_value = max(current_stock_price - self.K, 0)
                
                # American option: take maximum of continue or exercise
                # This is the KEY difference from European
                option_tree[i][j] = max(continuation_value, exercise_value)
        
        return option_tree[0][0]
    
    def price_american_put(self) -> float:
        """
        Price American put option using binomial tree
        
        For puts, early exercise CAN be optimal:
            - If stock crashes, intrinsic value (K - S) might be worth more than
              waiting for potential further decline
            - Deep in-the-money puts should be exercised early
            - Time value < intrinsic value → exercise now
            
        This is why American puts trade at premium to European puts
        
        Returns:
            float: American put option price (always >= European put)
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros((self.N + 1, self.N + 1))
        
        # Terminal payoffs
        for j in range(self.N + 1):
            terminal_price = stock_tree[self.N][j]
            option_tree[self.N][j] = max(self.K - terminal_price, 0)
        
        discount_factor = np.exp(-self.r * self.dt)
        
        # Work backwards with early exercise check
        for i in range(self.N - 1, -1, -1):
            for j in range(i + 1):
                # Continuation value
                up_value = option_tree[i + 1][j + 1]
                down_value = option_tree[i + 1][j]
                continuation_value = discount_factor * (self.p * up_value + self.q * down_value)
                
                # Exercise value
                current_stock_price = stock_tree[i][j]
                exercise_value = max(self.K - current_stock_price, 0)
                
                # American put: exercise if intrinsic > continuation
                option_tree[i][j] = max(continuation_value, exercise_value)
        
        return option_tree[0][0]
    
    def _build_stock_tree(self) -> np.ndarray:
        """
        Build tree of all possible stock prices
        
        Tree structure:
            stock_tree[i][j] = S * u^j * d^(i-j)
            
            Where:
            - i = time step (0 to N)
            - j = number of up moves (0 to i)
            - Number of down moves = i - j
            
        Example at step 2:
            j=2: S*u²     (2 ups, 0 downs)
            j=1: S*u*d    (1 up, 1 down)
            j=0: S*d²     (0 ups, 2 downs)
            
        Returns:
            numpy array of shape (N+1, N+1) with stock prices
        """
        stock_tree = np.zeros((self.N + 1, self.N + 1))
        
        for i in range(self.N + 1):
            for j in range(i + 1):
                # Number of up moves: j
                # Number of down moves: i - j
                stock_tree[i][j] = self.S * (self.u ** j) * (self.d ** (i - j))
        
        return stock_tree
    
    def get_early_exercise_boundary(self, option_type: Literal['call', 'put']) -> dict:
        """
        Calculate early exercise boundary for American options
        
        The early exercise boundary tells you: "At each point in time, 
        at what stock price should I exercise early?"
        
        This is useful for:
            - Understanding optimal exercise strategy
            - Visualising American vs European difference
            - Risk management (know when counterparty might exercise)
            
        Args:
            option_type: 'call' or 'put'
            
        Returns:
            dict: {time_step: critical_stock_price}
            
        Example output:
            {
                0: None,      # Never exercise at t=0 (not optimal)
                1: 140.5,     # At step 1, exercise if S > 140.5
                2: 138.2,     # At step 2, exercise if S > 138.2
                ...
            }
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros((self.N + 1, self.N + 1))
        
        # Calculate option values (American)
        if option_type == 'call':
            for j in range(self.N + 1):
                option_tree[self.N][j] = max(stock_tree[self.N][j] - self.K, 0)
        else:  # put
            for j in range(self.N + 1):
                option_tree[self.N][j] = max(self.K - stock_tree[self.N][j], 0)
        
        discount_factor = np.exp(-self.r * self.dt)
        boundary = {}
        
        for i in range(self.N - 1, -1, -1):
            exercise_optimal = []
            
            for j in range(i + 1):
                # Calculate continuation and exercise values
                up_value = option_tree[i + 1][j + 1]
                down_value = option_tree[i + 1][j]
                continuation_value = discount_factor * (self.p * up_value + self.q * down_value)
                
                current_stock_price = stock_tree[i][j]
                
                if option_type == 'call':
                    exercise_value = max(current_stock_price - self.K, 0)
                else:  # put
                    exercise_value = max(self.K - current_stock_price, 0)
                
                option_tree[i][j] = max(continuation_value, exercise_value)
                
                # Check if early exercise is optimal at this node
                if exercise_value > continuation_value and exercise_value > 0:
                    exercise_optimal.append(current_stock_price)
            
            # Critical price is the boundary between exercise/hold
            if exercise_optimal:
                boundary[i] = min(exercise_optimal) if option_type == 'call' else max(exercise_optimal)
            else:
                boundary[i] = None
        
        return boundary