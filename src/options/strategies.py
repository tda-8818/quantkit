"""
Common Option Trading Strategies

This module implements popular multi-leg option strategies used by traders.
Each strategy combines multiple options to create specific risk/reward profiles.

Categories:
    - Spreads: Limited risk, limited reward
    - Straddles/Strangles: Bet on volatility
    - Butterflies/Condors: Bet on range-bound movement
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from src.options.black_scholes import BlackScholes


@dataclass
class OptionLeg:
    """
    Single option in a multi-leg strategy
    
    Attributes:
        option_type: 'call' or 'put'
        strike: Strike price
        position: 'long' (buy) or 'short' (sell)
        quantity: Number of contracts
    """
    option_type: str  # 'call' or 'put'
    strike: float
    position: str  # 'long' or 'short'
    quantity: int = 1


class OptionStrategy:
    """
    Multi-leg option strategy analyser
    
    Calculates:
        - Total premium (cost to enter strategy)
        - Payoff at expiration
        - Breakeven points
        - Max profit/loss
        - Greeks (combined position)
    """
    
    def __init__(self, S: float, T: float, r: float, sigma: float):
        """
        Initialise strategy analyser
        
        Args:
            S: Current stock price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
        """
        self.S = S
        self.T = T
        self.r = r
        self.sigma = sigma
        self.legs: List[OptionLeg] = []
        
    def add_leg(self, leg: OptionLeg):
        """Add option leg to strategy"""
        self.legs.append(leg)
    
    def calculate_total_premium(self) -> float:
        """
        Calculate total premium paid/received to enter strategy
        
        Convention:
            - Positive = you pay (debit spread)
            - Negative = you receive (credit spread)
            
        Returns:
            float: Net premium (negative if credit received)
        """
        total_premium = 0
        
        for leg in self.legs:
            # Price the option using Black-Scholes
            bs = BlackScholes(self.S, leg.strike, self.T, self.r, self.sigma)
            
            if leg.option_type == 'call':
                price = bs.call_price()
            else:  # put
                price = bs.put_price()
            
            # Long position = pay premium (positive cost)
            # Short position = receive premium (negative cost)
            if leg.position == 'long':
                total_premium += price * leg.quantity
            else:  # short
                total_premium -= price * leg.quantity
        
        return total_premium
    
    def calculate_payoff(self, stock_prices: np.ndarray) -> np.ndarray:
        """
        Calculate strategy payoff at expiration for range of stock prices
        
        This shows the P&L diagram (hockey stick charts traders love)
        
        Args:
            stock_prices: Array of stock prices to evaluate
            
        Returns:
            Array of payoffs corresponding to each stock price
            
        Example:
            stock_range = np.linspace(80, 120, 100)
            payoffs = strategy.calculate_payoff(stock_range)
            plt.plot(stock_range, payoffs)
            plt.axhline(0, color='black', linestyle='--')
            plt.xlabel('Stock Price at Expiration')
            plt.ylabel('Profit/Loss')
        """
        payoffs = np.zeros_like(stock_prices, dtype=float)
        
        for leg in self.legs:
            if leg.option_type == 'call':
                # Call payoff: max(S - K, 0)
                leg_payoff = np.maximum(stock_prices - leg.strike, 0)
            else:  # put
                # Put payoff: max(K - S, 0)
                leg_payoff = np.maximum(leg.strike - stock_prices, 0)
            
            # Long position = receive payoff
            # Short position = pay out payoff (negative)
            if leg.position == 'long':
                payoffs += leg_payoff * leg.quantity
            else:  # short
                payoffs -= leg_payoff * leg.quantity
        
        # Subtract initial premium paid
        initial_cost = self.calculate_total_premium()
        payoffs -= initial_cost
        
        return payoffs
    
    def calculate_breakeven_points(self) -> List[float]:
        """
        Find stock prices where strategy breaks even (P&L = 0)
        
        Returns:
            List of breakeven stock prices
        """
        # Search range: ±50% of current price
        stock_range = np.linspace(self.S * 0.5, self.S * 1.5, 1000)
        payoffs = self.calculate_payoff(stock_range)
        
        # Find where payoff crosses zero
        breakevens = []
        for i in range(len(payoffs) - 1):
            # Check if sign changes (crosses zero)
            if payoffs[i] * payoffs[i + 1] < 0:
                # Linear interpolation to find exact crossover
                breakeven = stock_range[i] + (0 - payoffs[i]) * (stock_range[i + 1] - stock_range[i]) / (payoffs[i + 1] - payoffs[i])
                breakevens.append(breakeven)
        
        return breakevens
    
    def calculate_max_profit_loss(self) -> Tuple[float, float]:
        """
        Calculate maximum profit and maximum loss
        
        Returns:
            tuple: (max_profit, max_loss)
                  None if unlimited
        """
        # Evaluate payoffs over wide range
        stock_range = np.linspace(self.S * 0.1, self.S * 3, 1000)
        payoffs = self.calculate_payoff(stock_range)
        
        max_profit = np.max(payoffs)
        max_loss = np.min(payoffs)
        
        # Check if unbounded
        # If payoffs still increasing at edges, it's unlimited
        if payoffs[-1] > payoffs[-2]:
            max_profit = np.inf
        
        if payoffs[0] < payoffs[1]:
            max_loss = -np.inf
        
        return max_profit, max_loss
    
    def calculate_total_greeks(self) -> dict:
        """
        Calculate combined Greeks for entire strategy
        
        Portfolio Greeks = sum of individual option Greeks
        
        Returns:
            dict: Combined delta, gamma, theta, vega, rho
        """
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        total_rho = 0
        
        for leg in self.legs:
            bs = BlackScholes(self.S, leg.strike, self.T, self.r, self.sigma)
            
            if leg.option_type == 'call':
                greeks = bs.greeks_call()
            else:
                greeks = bs.greeks_put()
            
            # Long position = positive Greeks
            # Short position = negative Greeks
            multiplier = leg.quantity if leg.position == 'long' else -leg.quantity
            
            total_delta += greeks.delta * multiplier
            total_gamma += greeks.gamma * multiplier
            total_theta += greeks.theta * multiplier
            total_vega += greeks.vega * multiplier
            total_rho += greeks.rho * multiplier
        
        return {
            'delta': total_delta,
            'gamma': total_gamma,
            'theta': total_theta,
            'vega': total_vega,
            'rho': total_rho
        }
    
    def print_summary(self):
        """Print comprehensive strategy summary"""
        print("=" * 70)
        print("OPTION STRATEGY SUMMARY")
        print("=" * 70)
        
        print("\nLEGS:")
        for i, leg in enumerate(self.legs, 1):
            bs = BlackScholes(self.S, leg.strike, self.T, self.r, self.sigma)
            price = bs.call_price() if leg.option_type == 'call' else bs.put_price()
            
            print(f"  {i}. {leg.position.upper()} {leg.quantity}x {leg.option_type.upper()} @ ${leg.strike:.2f}")
            print(f"     Premium: ${price:.2f} per contract")
        
        total_premium = self.calculate_total_premium()
        print(f"\nNET PREMIUM: ${abs(total_premium):.2f} {'(DEBIT)' if total_premium > 0 else '(CREDIT)'}")
        
        breakevens = self.calculate_breakeven_points()
        print(f"\nBREAKEVEN POINTS: {', '.join([f'${be:.2f}' for be in breakevens])}")
        
        max_profit, max_loss = self.calculate_max_profit_loss()
        print(f"\nMAX PROFIT: ${max_profit:.2f}" if max_profit != np.inf else "\nMAX PROFIT: UNLIMITED")
        print(f"MAX LOSS: ${abs(max_loss):.2f}" if max_loss != -np.inf else "MAX LOSS: UNLIMITED")
        
        greeks = self.calculate_total_greeks()
        print(f"\nPORTFOLIO GREEKS:")
        print(f"  Delta:  {greeks['delta']:>8.3f}")
        print(f"  Gamma:  {greeks['gamma']:>8.4f}")
        print(f"  Theta:  {greeks['theta']:>8.3f} (per day)")
        print(f"  Vega:   {greeks['vega']:>8.3f} (per 1% vol)")
        print(f"  Rho:    {greeks['rho']:>8.3f} (per 1% rate)")


# ============================================================================
# Pre-Built Common Strategies
# ============================================================================

def bull_call_spread(S: float, T: float, r: float, sigma: float, 
                     lower_strike: float, upper_strike: float) -> OptionStrategy:
    """
    Bull Call Spread: Bullish strategy with limited risk and reward
    
    Construction:
        - Buy call at lower strike (ITM or ATM)
        - Sell call at higher strike (OTM)
        
    Characteristics:
        - Net debit (pay premium)
        - Max profit: (upper strike - lower strike) - net premium
        - Max loss: net premium paid
        - Breakeven: lower strike + net premium
        
    Use when:
        - Moderately bullish
        - Want to reduce cost vs buying call outright
        - Willing to cap upside for lower cost
        
    Example:
        Stock at $100
        Buy $100 call for $5
        Sell $110 call for $2
        Net cost: $3
        Max profit: $10 - $3 = $7 (at $110+)
        Max loss: $3 (below $100)
        Breakeven: $103
    """
    strategy = OptionStrategy(S, T, r, sigma)
    strategy.add_leg(OptionLeg('call', lower_strike, 'long', 1))
    strategy.add_leg(OptionLeg('call', upper_strike, 'short', 1))
    return strategy


def bear_put_spread(S: float, T: float, r: float, sigma: float,
                    lower_strike: float, upper_strike: float) -> OptionStrategy:
    """
    Bear Put Spread: Bearish strategy with limited risk and reward
    
    Construction:
        - Buy put at higher strike (ITM or ATM)
        - Sell put at lower strike (OTM)
        
    Characteristics:
        - Net debit
        - Max profit: (upper strike - lower strike) - net premium
        - Max loss: net premium paid
        
    Use when:
        - Moderately bearish
        - Want to reduce cost vs buying put outright
    """
    strategy = OptionStrategy(S, T, r, sigma)
    strategy.add_leg(OptionLeg('put', upper_strike, 'long', 1))
    strategy.add_leg(OptionLeg('put', lower_strike, 'short', 1))
    return strategy


def long_straddle(S: float, T: float, r: float, sigma: float, strike: float) -> OptionStrategy:
    """
    Long Straddle: Bet on big move in either direction
    
    Construction:
        - Buy call at strike
        - Buy put at same strike
        
    Characteristics:
        - Net debit (expensive)
        - Profits from large moves in EITHER direction
        - Max loss: total premium paid (if stock stays at strike)
        - Two breakevens: strike ± total premium
        
    Use when:
        - Expecting big volatility (earnings, FDA approval, etc.)
        - Don't know direction
        - Implied vol is low relative to expected move
        
    Example:
        Stock at $100, straddle at $100 strike
        Buy $100 call for $6
        Buy $100 put for $6
        Total cost: $12
        Need stock to move >$12 to profit
        Breakevens: $88 and $112
    """
    strategy = OptionStrategy(S, T, r, sigma)
    strategy.add_leg(OptionLeg('call', strike, 'long', 1))
    strategy.add_leg(OptionLeg('put', strike, 'long', 1))
    return strategy


def long_strangle(S: float, T: float, r: float, sigma: float,
                  put_strike: float, call_strike: float) -> OptionStrategy:
    """
    Long Strangle: Cheaper straddle with wider breakevens
    
    Construction:
        - Buy OTM put (lower strike)
        - Buy OTM call (higher strike)
        
    Characteristics:
        - Cheaper than straddle (buying OTM options)
        - Need bigger move to profit
        - Wider breakevens
        
    Use when:
        - Same as straddle but want lower cost
        - Willing to accept wider breakevens
    """
    strategy = OptionStrategy(S, T, r, sigma)
    strategy.add_leg(OptionLeg('put', put_strike, 'long', 1))
    strategy.add_leg(OptionLeg('call', call_strike, 'long', 1))
    return strategy


def iron_condor(S: float, T: float, r: float, sigma: float,
                put_lower: float, put_upper: float,
                call_lower: float, call_upper: float) -> OptionStrategy:
    """
    Iron Condor: Bet on low volatility (range-bound)
    
    Construction:
        - Sell OTM put at put_upper
        - Buy OTM put at put_lower (protection)
        - Sell OTM call at call_lower
        - Buy OTM call at call_upper (protection)
        
    Characteristics:
        - Net credit (receive premium)
        - Profits if stock stays between short strikes
        - Max profit: net premium received
        - Max loss: width of spread - net premium
        
    Use when:
        - Expecting low volatility
        - Stock to stay range-bound
        - Implied vol is high
        
    Example:
        Stock at $100
        Sell $90 put, buy $85 put (collect $1)
        Sell $110 call, buy $115 call (collect $1)
        Total credit: $2
        Max profit: $2 (if stock stays $90-$110)
        Max loss: $5 - $2 = $3 (if stock moves beyond $85 or $115)
    """
    strategy = OptionStrategy(S, T, r, sigma)
    # Put spread (lower)
    strategy.add_leg(OptionLeg('put', put_lower, 'long', 1))
    strategy.add_leg(OptionLeg('put', put_upper, 'short', 1))
    # Call spread (upper)
    strategy.add_leg(OptionLeg('call', call_lower, 'short', 1))
    strategy.add_leg(OptionLeg('call', call_upper, 'long', 1))
    return strategy


def butterfly_spread(S: float, T: float, r: float, sigma: float,
                     lower_strike: float, middle_strike: float, upper_strike: float) -> OptionStrategy:
    """
    Butterfly Spread: Bet on minimal movement
    
    Construction (using calls):
        - Buy 1 call at lower strike
        - Sell 2 calls at middle strike
        - Buy 1 call at upper strike
        
    Characteristics:
        - Low cost (almost neutral)
        - Max profit at middle strike
        - Limited loss
        - Three breakevens
        
    Use when:
        - Stock will stay near middle strike
        - Low volatility expected
    """
    strategy = OptionStrategy(S, T, r, sigma)
    strategy.add_leg(OptionLeg('call', lower_strike, 'long', 1))
    strategy.add_leg(OptionLeg('call', middle_strike, 'short', 2))
    strategy.add_leg(OptionLeg('call', upper_strike, 'long', 1))
    return strategy