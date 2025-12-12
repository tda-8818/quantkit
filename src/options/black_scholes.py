"""
Black-Scholes Options Pricing Model

Academic Reference:
    Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
    Journal of Political Economy, 81(3), 637-654.

Key Assumptions:
    1. European options (can only exercise at expiration)
    2. No dividends paid during option life
    3. Markets are efficient (no arbitrage)
    4. No transaction costs or taxes
    5. Risk-free rate and volatility are constant
    6. Returns are log-normally distributed
    
The Black-Scholes formula revolutionised derivatives trading and earned Myron Scholes
and Robert Merton the 1997 Nobel Prize in Economics (Fischer Black had passed away).
"""

import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from typing import Tuple


@dataclass
class OptionPrice:
    """
    Container for option price and Greeks
    
    Attributes:
        price: Option premium (what you pay for the option)
        delta: Rate of change of option price with respect to stock price
               Measures directional risk. Call delta: 0 to 1, Put delta: -1 to 0
        gamma: Rate of change of delta with respect to stock price
               Measures convexity/curvature. Higher gamma = delta changes faster
        theta: Rate of change of option price with respect to time (time decay)
               Usually negative - options lose value as expiration approaches
        vega: Rate of change of option price with respect to volatility
              Higher volatility = higher option prices (more uncertainty)
        rho: Rate of change of option price with respect to interest rate
             Usually small impact compared to other Greeks
    """
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class BlackScholes:
    """
    Black-Scholes options pricing model for European options
    
    The model uses a closed-form solution (exact formula) rather than simulation.
    This makes it extremely fast but requires strict assumptions.
    
    Example:
        # Price a call option on AAPL
        bs = BlackScholes(
            S=150,      # Current AAPL price
            K=155,      # Strike price (right to buy at $155)
            T=0.25,     # 3 months to expiration (0.25 years)
            r=0.05,     # 5% risk-free rate (T-bills)
            sigma=0.30  # 30% annual volatility
        )
        
        call_price = bs.call_price()  # Returns option premium
        greeks = bs.greeks_call()     # Returns all Greeks
    """
    
    def __init__(self, S: float, K: float, T: float, r: float, sigma: float):
        """
        Initialise Black-Scholes model parameters
        
        Args:
            S: Current stock price (spot price)
               Example: If AAPL trades at $150, S=150
               
            K: Strike price (exercise price)
               Example: Right to buy at $155, K=155
               
            T: Time to expiration in years
               Example: 3 months = 0.25, 6 months = 0.5, 1 year = 1.0
               Calculate as: days_to_expiry / 365
               
            r: Risk-free interest rate (annual, as decimal)
               Example: 5% = 0.05
               Use: Current T-bill rate (check FRED website)
               
            sigma: Volatility (annual standard deviation of returns, as decimal)
               Example: 30% vol = 0.30
               Calculate from historical data: std(daily_returns) * sqrt(252)
               Or use implied volatility from market prices
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        
        # Validate inputs
        if S <= 0:
            raise ValueError("Stock price must be positive")
        if K <= 0:
            raise ValueError("Strike price must be positive")
        if T <= 0:
            raise ValueError("Time to expiration must be positive")
        if sigma <= 0:
            raise ValueError("Volatility must be positive")
    
    def call_price(self) -> float:
        """
        Calculate European call option price using Black-Scholes formula
        
        A call option gives you the RIGHT (not obligation) to BUY stock at strike price.
        
        Formula breakdown:
            C = S * N(d1) - K * e^(-rT) * N(d2)
            
            Where:
            - S * N(d1): Expected stock price at expiration, discounted for probability
            - K * e^(-rT) * N(d2): Present value of strike price, discounted for probability
            - N(d1), N(d2): Cumulative normal distribution (probability terms)
        
        Intuition:
            Call value = (What you expect to receive) - (What you have to pay)
        
        Returns:
            float: Call option price (premium) in same currency as stock price
            
        Example:
            If call_price() returns 8.50, you pay $8.50 per share for the option.
            On 100 shares: $8.50 × 100 = $850 total premium
        """
        d1, d2 = self._d1_d2()
        
        # N(d1) and N(d2) are probabilities from standard normal distribution
        # norm.cdf() gives cumulative probability: P(Z <= d)
        call_value = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        
        return call_value
    
    def put_price(self) -> float:
        """
        Calculate European put option price using Black-Scholes formula
        
        A put option gives you the RIGHT (not obligation) to SELL stock at strike price.
        
        Formula:
            P = K * e^(-rT) * N(-d2) - S * N(-d1)
        
        Or using put-call parity:
            P = C - S + K * e^(-rT)
        
        Intuition:
            Put value = (Strike you can sell at) - (Current market value)
        
        Returns:
            float: Put option price (premium)
            
        Example:
            If put_price() returns 5.25, you pay $5.25 per share.
            This gives you the right to sell at strike price, protecting downside.
        """
        d1, d2 = self._d1_d2()
        
        # Note the negative signs: N(-d) represents downside probability
        put_value = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        
        return put_value
    
    def greeks_call(self) -> OptionPrice:
        """
        Calculate all Greeks for a call option
        
        Greeks measure sensitivities (how option price changes with inputs).
        Traders use Greeks for:
            - Risk management (hedge portfolios)
            - Position sizing (control exposure)
            - Market making (delta-neutral strategies)
        
        Returns:
            OptionPrice dataclass with price and all Greeks
            
        Example output:
            OptionPrice(
                price=8.50,    # Option costs $8.50
                delta=0.55,    # $1 stock increase → $0.55 option increase
                gamma=0.02,    # Delta will increase by 0.02 per $1 stock move
                theta=-0.03,   # Loses $0.03 per day (time decay)
                vega=0.25,     # 1% vol increase → $0.25 option increase
                rho=0.10       # 1% rate increase → $0.10 option increase
            )
        """
        price = self.call_price()
        d1, d2 = self._d1_d2()
        
        # DELTA: ∂C/∂S (partial derivative of call price with respect to stock price)
        # Call delta is always between 0 and 1
        # Delta = 0.5 means "50% chance of finishing in-the-money"
        # At-the-money options have delta ≈ 0.5
        # Deep in-the-money calls have delta ≈ 1.0 (move 1:1 with stock)
        # Deep out-of-the-money calls have delta ≈ 0 (worthless)
        delta = norm.cdf(d1)
        
        # GAMMA: ∂²C/∂S² (second derivative - rate of change of delta)
        # Measures convexity (curvature) of option price
        # Highest gamma occurs at-the-money
        # Low gamma for deep ITM/OTM options (delta stable)
        # High gamma = delta changes rapidly = more risk/reward
        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        
        # THETA: ∂C/∂T (time decay - how much value lost per day)
        # Usually negative (options lose value as expiration approaches)
        # Accelerates as expiration nears (non-linear decay)
        # Divided by 365 to get daily theta (traders quote daily)
        # At-the-money options have highest theta (most time value)
        theta = (
            (-self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
            - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        ) / 365
        
        # VEGA: ∂C/∂σ (sensitivity to volatility changes)
        # NOT actually a Greek letter (made up by traders)
        # Divided by 100 so vega represents $change per 1% vol change
        # Long options have positive vega (want volatility to increase)
        # Short options have negative vega (want volatility to decrease)
        # At-the-money options have highest vega
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T) / 100
        
        # RHO: ∂C/∂r (sensitivity to interest rate changes)
        # Usually smallest Greek (rates don't change much day-to-day)
        # Divided by 100 so rho represents $change per 1% rate change
        # Calls have positive rho (benefit from higher rates)
        # Puts have negative rho (hurt by higher rates)
        rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) / 100
        
        return OptionPrice(price, delta, gamma, theta, vega, rho)
    
    def greeks_put(self) -> OptionPrice:
        """
        Calculate all Greeks for a put option
        
        Put Greeks differ from call Greeks in sign:
            - Delta is negative (puts increase when stock falls)
            - Gamma is same (convexity doesn't depend on call/put)
            - Theta usually more negative for puts (time decay)
            - Vega is same (volatility helps both calls and puts)
            - Rho is negative (puts hurt by higher rates)
        
        Returns:
            OptionPrice dataclass with price and all Greeks
        """
        price = self.put_price()
        d1, d2 = self._d1_d2()
        
        # PUT DELTA: N(d1) - 1, ranges from -1 to 0
        # Delta = -0.5 means $1 stock drop → $0.50 put gain
        # Deep in-the-money puts have delta ≈ -1.0
        # Deep out-of-the-money puts have delta ≈ 0
        delta = norm.cdf(d1) - 1
        
        # PUT GAMMA: Same as call gamma
        # Convexity doesn't depend on whether it's call or put
        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        
        # PUT THETA: Usually more negative than call theta
        # Puts decay faster because they also lose "interest benefit"
        theta = (
            (-self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
            + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
        ) / 365
        
        # PUT VEGA: Same as call vega
        # Both calls and puts benefit from higher volatility
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T) / 100
        
        # PUT RHO: Negative (opposite of call)
        # Higher rates hurt puts (reduce present value of strike)
        rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) / 100
        
        return OptionPrice(price, delta, gamma, theta, vega, rho)
    
    def _d1_d2(self) -> Tuple[float, float]:
        """
        Calculate d1 and d2 terms used in Black-Scholes formula
        
        These are standardised variables from the log-normal distribution:
        
        d1 formula breakdown:
            d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
            
            Where:
            - ln(S/K): Moneyness (how far in/out of the money)
              ln(S/K) > 0: In-the-money (S > K)
              ln(S/K) = 0: At-the-money (S = K)
              ln(S/K) < 0: Out-of-the-money (S < K)
              
            - (r + σ²/2)T: Expected drift (growth + volatility adjustment)
              Higher rate → stock expected to grow more
              Higher vol → compensate for log-normal distribution
              
            - σ√T: Total volatility over option life
              Scales volatility by square root of time
              
        d2 formula:
            d2 = d1 - σ√T
            
            Simpler: d2 is just d1 adjusted for volatility drag
        
        Interpretation:
            - d1: Related to probability of stock being above strike (in terms of delta)
            - d2: Related to probability of exercising option profitably
            - N(d1): Delta of call option
            - N(d2): Risk-neutral probability of finishing in-the-money
        
        Returns:
            Tuple of (d1, d2) values
        """
        # Calculate d1
        # Numerator: Log moneyness + drift term
        numerator = np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T
        
        # Denominator: Total volatility (vol × sqrt(time))
        denominator = self.sigma * np.sqrt(self.T)
        
        d1 = numerator / denominator
        
        # d2 is d1 minus one volatility standard deviation
        d2 = d1 - self.sigma * np.sqrt(self.T)
        
        return d1, d2