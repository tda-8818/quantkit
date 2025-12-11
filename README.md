# QuantKit: Institutional-Grade Quantitative Trading Research Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A complete quantitative finance research platform for systematic trading strategy development, backtesting, and deployment. Built from first principles to mirror institutional quant desk infrastructure.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Project Roadmap](#project-roadmap)
- [Implementation Guide](#implementation-guide)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [Performance Benchmarks](#performance-benchmarks)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

---

## 🎯 Overview

**QuantKit** is a professional-grade quantitative trading research platform that provides end-to-end infrastructure for systematic trading strategy development. It implements the four fundamental pillars used by top quantitative hedge funds:

1. **Market Data Pipeline** - Industrial-strength data acquisition, cleaning, and storage
2. **Vectorized Backtester** - High-performance strategy testing engine
3. **Factor Investing Model** - Academic factor research and portfolio construction
4. **Options Pricing Engine** - Derivatives valuation and risk management

### What Makes This Different?

Unlike hobbyist trading bots or commercial black-boxes, QuantKit is:

- ✅ **Educational First** - Every design decision is explained
- ✅ **Production Ready** - Built with institutional standards
- ✅ **Research Focused** - Emphasis on statistical rigor over quick profits
- ✅ **Transparent** - Full visibility into methodology and assumptions
- ✅ **Extensible** - Modular architecture for easy customization

---

## 🏗️ System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     QUANTKIT PLATFORM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐     ┌──────────────┐     ┌────────────────┐ │
│  │  Data Layer   │────▶│ Research Lab │────▶│ Execution Layer│ │
│  └───────────────┘     └──────────────┘     └────────────────┘ │
│         │                     │                      │          │
│         ▼                     ▼                      ▼          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Storage & Monitoring                         │  │
│  │  • PostgreSQL/SQLite  • Redis Cache  • Prometheus        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Market Data Sources (Yahoo, Alpaca, Polygon)
          │
          ▼
    Data Pipeline ─────┐
    • Download        │
    • Clean           │
    • Validate        │
    • Store           │
          │           │
          ▼           │
    Database          │
    • Prices          │
    • Fundamentals    │
    • Alt Data        │
          │           │
          ▼           │
    Factor Model ◀────┘
    • Calculate factors
    • Rank securities
    • Generate signals
          │
          ▼
    Backtester
    • Simulate trades
    • Calculate metrics
    • Assess risk
          │
          ▼
    Options Engine
    • Price derivatives
    • Calculate Greeks
    • Hedge portfolio
          │
          ▼
    Execution (Alpaca API)
    • Paper trading
    • Live trading
    • Order management
```

---

## 🔧 Core Components

### Component 1: Market Data Pipeline

**Purpose:** Acquire, clean, validate, and store market data from multiple sources.

**What It Does:**
- Downloads historical and real-time price data
- Handles corporate actions (splits, dividends, symbol changes)
- Validates data quality (missing values, outliers, anomalies)
- Stores in optimized database with proper indexing
- Provides unified API for data retrieval

**Key Features:**
- Multi-source support (Yahoo Finance, Alpaca, Polygon.io)
- Automatic data cleaning and normalization
- Corporate action adjustments
- Data quality monitoring dashboard
- Efficient storage with SQLAlchemy ORM
- Rate limit handling and caching

**Technologies:**
```python
- yfinance          # Free Yahoo Finance data
- alpaca-trade-api  # Professional market data
- pandas            # Data manipulation
- sqlalchemy        # Database ORM
- redis             # Caching layer (optional)
```

**Data Schema:**
```sql
CREATE TABLE daily_prices (
    id INTEGER PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    adj_close FLOAT,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

CREATE INDEX idx_ticker_date ON daily_prices(ticker, date);
CREATE INDEX idx_date ON daily_prices(date);
```

### Component 2: Vectorized Backtester

**Purpose:** Test trading strategies on historical data with institutional-grade performance measurement.

**What It Does:**
- Simulates trading strategies on historical price data
- Calculates comprehensive performance metrics
- Models realistic transaction costs (commission + slippage)
- Implements walk-forward optimization to prevent overfitting
- Generates detailed performance reports and visualizations

**Key Features:**
- **Vectorized Operations:** Process years of data in seconds using NumPy
- **Transaction Cost Modeling:** Realistic commission (0.1%) and slippage (0.05%)
- **Walk-Forward Analysis:** Train on past data, test on future data
- **Performance Metrics:** Sharpe, Sortino, Calmar, Max Drawdown, Win Rate
- **Benchmark Comparison:** Compare against S&P 500, risk-free rate
- **Monte Carlo Simulation:** Assess strategy robustness

**Performance Metrics Explained:**

| Metric | Formula | What It Means | Good Value |
|--------|---------|---------------|------------|
| **Sharpe Ratio** | `(Return - RiskFree) / StdDev` | Risk-adjusted return | > 1.0 |
| **Sortino Ratio** | `(Return - RiskFree) / DownsideStdDev` | Downside risk-adjusted return | > 1.5 |
| **Max Drawdown** | `max(peak - trough) / peak` | Worst peak-to-trough decline | < -20% |
| **Calmar Ratio** | `AnnualReturn / abs(MaxDrawdown)` | Return per unit of downside risk | > 0.5 |
| **Win Rate** | `WinningTrades / TotalTrades` | % of profitable trades | > 50% |

**Technologies:**
```python
- numpy             # Vectorized operations
- pandas            # Time series analysis
- matplotlib/plotly # Visualization
- scipy             # Statistical functions
```

**Example Output:**
```
═══════════════════════════════════════════════════════════
                  BACKTEST RESULTS                          
═══════════════════════════════════════════════════════════
Strategy: Momentum Factor (12-month)
Period: 2020-01-01 to 2024-12-01
Initial Capital: $100,000
───────────────────────────────────────────────────────────
RETURNS
  Total Return:              47.32%
  Annualized Return:         15.24%
  Benchmark Return (SPY):    52.18%
  Alpha:                     -4.86%
───────────────────────────────────────────────────────────
RISK METRICS
  Sharpe Ratio:              1.34
  Sortino Ratio:             1.89
  Max Drawdown:             -18.23%
  Calmar Ratio:              0.84
  Volatility (Annual):       11.37%
───────────────────────────────────────────────────────────
TRADE STATISTICS
  Total Trades:              147
  Win Rate:                  52.38%
  Average Win:               +2.14%
  Average Loss:              -1.87%
  Profit Factor:             1.42
  Best Trade:                +8.91%
  Worst Trade:              -6.23%
───────────────────────────────────────────────────────────
COSTS
  Total Commission:          $1,470.00
  Estimated Slippage:        $735.00
  Total Transaction Costs:   $2,205.00
═══════════════════════════════════════════════════════════
```

### Component 3: Factor Investing Model

**Purpose:** Implement academic factor research to identify securities with expected outperformance.

**What It Does:**
- Calculates quantitative factors (momentum, value, quality, size, volatility)
- Ranks securities based on factor exposures
- Constructs long/short portfolios
- Tests factor performance and statistical significance
- Combines multiple factors optimally

**Academic Background:**

Factor investing is based on decades of financial research showing that certain characteristics ("factors") predict future returns:

| Factor | Description | Academic Paper | Typical Return |
|--------|-------------|----------------|----------------|
| **Value** | Low P/E, P/B stocks outperform | Fama & French (1992) | 4-5% annually |
| **Momentum** | 12-month winners keep winning | Jegadeesh & Titman (1993) | 8-10% annually |
| **Quality** | High ROE, margins outperform | Novy-Marx (2013) | 3-4% annually |
| **Low Volatility** | Low beta stocks outperform | Ang et al. (2006) | 3-5% annually |
| **Size** | Small caps outperform (debated) | Fama & French (1992) | 1-2% annually |

**Implementation:**

```python
# Value Factor Example
def calculate_value_factor(data):
    """
    Value factor: Stocks with low P/E ratios tend to outperform
    
    Returns:
        Series: Value scores for each stock (higher = more value)
    """
    pe_ratios = data['price'] / data['earnings_per_share']
    
    # Invert so higher score = more value
    value_scores = 1 / pe_ratios
    
    # Winsorize outliers (cap at 1st/99th percentile)
    value_scores = value_scores.clip(
        lower=value_scores.quantile(0.01),
        upper=value_scores.quantile(0.99)
    )
    
    # Z-score normalization (mean=0, std=1)
    value_scores = (value_scores - value_scores.mean()) / value_scores.std()
    
    return value_scores

# Momentum Factor Example
def calculate_momentum_factor(data, period=252):
    """
    Momentum factor: 12-month returns (skip most recent month)
    
    Research shows skipping the most recent month improves performance
    due to short-term mean reversion.
    """
    # 12-month return
    returns_12m = data['close'].pct_change(period)
    
    # Skip most recent month (21 trading days)
    returns_12m_skip1m = data['close'].pct_change(period).shift(21)
    
    # Z-score normalization
    momentum_scores = (returns_12m_skip1m - returns_12m_skip1m.mean()) / returns_12m_skip1m.std()
    
    return momentum_scores
```

**Portfolio Construction:**

```python
# Long/Short Portfolio
def construct_portfolio(factor_scores, n_stocks=50):
    """
    Creates long/short portfolio based on factor scores
    
    Args:
        factor_scores: DataFrame with factor scores for each stock
        n_stocks: Number of stocks in each leg (long and short)
    
    Returns:
        dict: Portfolio weights
    """
    # Rank stocks by factor score
    ranked = factor_scores.rank(ascending=False)
    
    # Long top n_stocks (equal weight)
    long_stocks = ranked.nsmallest(n_stocks).index
    long_weights = {stock: 1/n_stocks for stock in long_stocks}
    
    # Short bottom n_stocks (equal weight)
    short_stocks = ranked.nlargest(n_stocks).index
    short_weights = {stock: -1/n_stocks for stock in short_stocks}
    
    # Combine (dollar-neutral portfolio)
    portfolio = {**long_weights, **short_weights}
    
    return portfolio
```

**Technologies:**
```python
- numpy             # Numerical operations
- pandas            # Factor calculation
- scipy.stats       # Statistical tests (t-stats, p-values)
- statsmodels       # Regression analysis
- scikit-learn      # Factor combination (PCA, ridge regression)
```

### Component 4: Options Pricing Engine

**Purpose:** Price derivatives, calculate risk metrics (Greeks), and manage portfolio hedging.

**What It Does:**
- Prices European and American options
- Calculates option Greeks (Delta, Gamma, Vega, Theta, Rho)
- Solves for implied volatility
- Constructs volatility surfaces
- Generates hedging strategies

**Pricing Methods:**

1. **Black-Scholes Model** (Analytical)
```python
def black_scholes_call(S, K, T, r, sigma):
    """
    Black-Scholes formula for European call option
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate
        sigma: Volatility (annualized)
    
    Returns:
        float: Option price
    """
    from scipy.stats import norm
    import numpy as np
    
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    
    return call_price
```

2. **Binomial Tree** (Discrete)
```python
def binomial_tree_american(S, K, T, r, sigma, N=100, option_type='call'):
    """
    Binomial tree for American options (can exercise early)
    
    Args:
        N: Number of time steps
        option_type: 'call' or 'put'
    
    Returns:
        float: Option price
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u                          # Down factor
    p = (np.exp(r*dt) - d) / (u - d)  # Risk-neutral probability
    
    # Build price tree
    stock_tree = np.zeros((N+1, N+1))
    stock_tree[0, 0] = S
    
    for i in range(1, N+1):
        stock_tree[i, 0] = stock_tree[i-1, 0] * u
        for j in range(1, i+1):
            stock_tree[i, j] = stock_tree[i-1, j-1] * d
    
    # Calculate option values at expiration
    option_tree = np.zeros((N+1, N+1))
    for j in range(N+1):
        if option_type == 'call':
            option_tree[N, j] = max(0, stock_tree[N, j] - K)
        else:
            option_tree[N, j] = max(0, K - stock_tree[N, j])
    
    # Work backwards (dynamic programming)
    for i in range(N-1, -1, -1):
        for j in range(i+1):
            # Expected value (hold option)
            hold_value = np.exp(-r*dt) * (p * option_tree[i+1, j] + 
                                          (1-p) * option_tree[i+1, j+1])
            
            # Exercise value (American feature)
            if option_type == 'call':
                exercise_value = max(0, stock_tree[i, j] - K)
            else:
                exercise_value = max(0, K - stock_tree[i, j])
            
            # Take maximum (optimal decision)
            option_tree[i, j] = max(hold_value, exercise_value)
    
    return option_tree[0, 0]
```

3. **Monte Carlo Simulation** (Path-Dependent)
```python
def monte_carlo_option(S, K, T, r, sigma, n_simulations=10000):
    """
    Monte Carlo simulation for option pricing
    
    Useful for exotic options (Asian, barrier, lookback)
    """
    dt = T / 252  # Daily steps
    n_steps = 252
    
    # Simulate price paths
    paths = np.zeros((n_simulations, n_steps))
    paths[:, 0] = S
    
    for t in range(1, n_steps):
        z = np.random.standard_normal(n_simulations)
        paths[:, t] = paths[:, t-1] * np.exp(
            (r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z
        )
    
    # Calculate payoffs
    payoffs = np.maximum(paths[:, -1] - K, 0)
    
    # Discount to present value
    option_price = np.exp(-r*T) * np.mean(payoffs)
    
    return option_price
```

**Greeks Calculation:**

```python
def calculate_greeks(S, K, T, r, sigma):
    """
    Calculate option Greeks using finite differences
    
    Returns:
        dict: Delta, Gamma, Vega, Theta, Rho
    """
    # Base price
    V = black_scholes_call(S, K, T, r, sigma)
    
    # Delta: ∂V/∂S (sensitivity to stock price)
    dS = 0.01 * S
    delta = (black_scholes_call(S + dS, K, T, r, sigma) - V) / dS
    
    # Gamma: ∂²V/∂S² (delta sensitivity)
    V_up = black_scholes_call(S + dS, K, T, r, sigma)
    V_down = black_scholes_call(S - dS, K, T, r, sigma)
    gamma = (V_up - 2*V + V_down) / (dS**2)
    
    # Vega: ∂V/∂σ (sensitivity to volatility)
    dsigma = 0.01
    vega = (black_scholes_call(S, K, T, r, sigma + dsigma) - V) / dsigma
    
    # Theta: ∂V/∂T (time decay)
    dT = 1/365  # 1 day
    theta = (black_scholes_call(S, K, T - dT, r, sigma) - V) / dT
    
    # Rho: ∂V/∂r (sensitivity to interest rates)
    dr = 0.01
    rho = (black_scholes_call(S, K, T, r + dr, sigma) - V) / dr
    
    return {
        'delta': delta,
        'gamma': gamma,
        'vega': vega,
        'theta': theta,
        'rho': rho
    }
```

**Technologies:**
```python
- numpy             # Numerical computation
- scipy             # Statistical distributions, optimization
- matplotlib        # Volatility surface visualization
- py_vollib         # Advanced volatility calculations (optional)
```

---

## 🗺️ Project Roadmap

### Phase 1: Foundation (Weeks 1-3)
**Goal:** Build production-grade data infrastructure

- ✅ Market Data Pipeline
  - [x] Basic data downloader (yfinance)
  - [x] Data cleaning functions
  - [x] SQLite database schema
  - [ ] Multi-source support (Alpaca, Polygon)
  - [ ] Corporate actions handling
  - [ ] Data quality dashboard
  - [ ] Automated update scheduler

**Deliverable:** `MarketDataPipeline` class that downloads, cleans, and stores data for any ticker.

### Phase 2: Backtesting (Weeks 4-7)
**Goal:** Build institutional-grade strategy testing engine

- ✅ Vectorized Backtester
  - [x] Simple buy-and-hold backtest
  - [x] Transaction cost modeling
  - [x] Performance metrics calculation
  - [ ] Walk-forward optimization
  - [ ] Monte Carlo simulation
  - [x] Strategy comparison framework
  - [x] Detailed reporting system

**Deliverable:** Working backtester with realistic costs and professional metrics.

### Phase 3: Factor Research (Weeks 8-12)
**Goal:** Implement academic factor investing

- ✅ Factor Investing Model
  - [ ] 5 core factors (Value, Momentum, Quality, Size, Low Vol)
  - [ ] Factor backtesting framework
  - [ ] Statistical significance testing
  - [ ] Multi-factor portfolio optimization
  - [ ] Factor decay monitoring
  - [ ] Research notebook templates

**Deliverable:** Factor research system with publishable results.

### Phase 4: Advanced Topics (Weeks 13-18)
**Goal:** Add derivatives and risk management

- ✅ Options Pricing Engine
  - [ ] Black-Scholes implementation
  - [ ] Binomial trees
  - [ ] Monte Carlo simulation
  - [ ] Greeks calculation
  - [ ] Implied volatility solver
  - [ ] Volatility surface construction
  - [ ] Portfolio hedging strategies

**Deliverable:** Complete options pricing library.

### Phase 5: Live Trading (Weeks 19-22)
**Goal:** Deploy to paper/live trading

- ✅ Execution Layer
  - [ ] Alpaca API integration
  - [ ] Order management system
  - [ ] Position tracking
  - [ ] Paper trading mode
  - [ ] Risk management checks
  - [ ] Performance monitoring
  - [ ] Alert system (Telegram/email)

**Deliverable:** Live trading capability with full monitoring.

### Phase 6: Polish & Deploy (Weeks 23-24)
**Goal:** Make production-ready

- ✅ Documentation & Testing
  - [ ] Comprehensive README
  - [ ] API documentation
  - [ ] Unit tests (>80% coverage)
  - [ ] Integration tests
  - [ ] Example notebooks
  - [ ] Video walkthrough
  - [ ] Blog post series

**Deliverable:** Portfolio-ready project with full documentation.

---

## 📖 Implementation Guide

### Week 1-3: Market Data Pipeline

#### Day 1-2: Project Setup

1. **Initialize Repository**
```bash
# Create project structure
mkdir quantkit && cd quantkit
git init

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install yfinance pandas numpy sqlalchemy python-dotenv pytest black
pip freeze > requirements.txt
```

2. **Create Project Structure**
```bash
quantkit/
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   ├── downloaders/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── yahoo.py
│   ├── cleaners/
│   │   ├── __init__.py
│   │   └── price_cleaner.py
│   └── storage/
│       ├── __init__.py
│       └── database.py
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py
├── notebooks/
│   └── 01_data_exploration.ipynb
├── data/
│   ├── raw/
│   └── cleaned/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

3. **Configuration File**
```python
# .env
DATA_DIR=./data
DB_PATH=./data/quantkit.db
ALPACA_API_KEY=your_key_here  # Get from alpaca.markets
ALPACA_SECRET_KEY=your_secret_here
```

4. **.gitignore**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Data
data/
*.db
*.csv
*.parquet

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# Jupyter
.ipynb_checkpoints/
```

#### Day 3-4: Basic Data Downloader

**File: `src/downloaders/base.py`**
```python
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

class BaseDownloader(ABC):
    """Abstract base class for data downloaders"""
    
    @abstractmethod
    def download(self, 
                 tickers: List[str], 
                 start_date: str, 
                 end_date: str) -> pd.DataFrame:
        """Download market data for given tickers"""
        pass
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate downloaded data"""
        pass
```

**File: `src/downloaders/yahoo.py`**
```python
import yfinance as yf
import pandas as pd
from typing import List
from .base import BaseDownloader

class YahooDownloader(BaseDownloader):
    """Download data from Yahoo Finance"""
    
    def __init__(self):
        self.source = 'yahoo'
    
    def download(self, 
                 tickers: List[str], 
                 start_date: str, 
                 end_date: str) -> dict:
        """
        Download OHLCV data from Yahoo Finance
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            dict: {ticker: DataFrame} with OHLCV data
        """
        data = {}
        
        for ticker in tickers:
            try:
                df = yf.download(ticker, 
                               start=start_date, 
                               end=end_date,
                               auto_adjust=True,  # Adjust for splits/dividends
                               progress=False)
                
                if not df.empty:
                    data[ticker] = df
                    print(f"✓ Downloaded {ticker}: {len(df)} days")
                else:
                    print(f"✗ No data for {ticker}")
                    
            except Exception as e:
                print(f"✗ Error downloading {ticker}: {str(e)}")
        
        return data
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate data has required columns"""
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        return required_columns.issubset(data.columns)
```

#### Day 5-7: Data Cleaning

**File: `src/cleaners/price_cleaner.py`**
```python
import pandas as pd
import numpy as np

class PriceCleaner:
    """Clean and validate price data"""
    
    def __init__(self):
        self.cleaning_log = []
    
    def clean(self, df: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
        """
        Apply all cleaning steps
        
        Steps:
        1. Remove zero-volume days
        2. Forward fill missing values
        3. Detect outliers
        4. Validate OHLC relationships
        """
        df = df.copy()
        original_len = len(df)
        
        # 1. Remove zero volume
        df = self._remove_zero_volume(df)
        
        # 2. Handle missing values
        df = self._handle_missing(df)
        
        # 3. Detect outliers
        outliers = self._detect_outliers(df)
        if outliers.any():
            self.cleaning_log.append(f"{ticker}: {outliers.sum()} outliers detected")
        
        # 4. Validate OHLC
        invalid = self._validate_ohlc(df)
        if invalid.any():
            self.cleaning_log.append(f"{ticker}: {invalid.sum()} invalid OHLC bars")
            df = df[~invalid]
        
        cleaned_len = len(df)
        removed = original_len - cleaned_len
        
        if removed > 0:
            self.cleaning_log.append(f"{ticker}: Removed {removed} rows")
        
        return df
    
    def _remove_zero_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove days with zero volume (weekends/holidays)"""
        return df[df['Volume'] > 0]
    
    def _handle_missing(self, df: pd.DataFrame, max_gap: int = 5) -> pd.DataFrame:
        """
        Forward fill missing values (max 5 days)
        
        Args:
            max_gap: Maximum consecutive days to fill
        """
        # Forward fill with limit
        df = df.fillna(method='ffill', limit=max_gap)
        
        # Drop remaining NaNs
        df = df.dropna()
        
        return df
    
    def _detect_outliers(self, df: pd.DataFrame, threshold: float = 5.0) -> pd.Series:
        """
        Detect outliers using z-score method
        
        Args:
            threshold: Number of standard deviations
        
        Returns:
            Boolean series indicating outliers
        """
        returns = df['Close'].pct_change()
        z_scores = np.abs((returns - returns.mean()) / returns.std())
        
        return z_scores > threshold
    
    def _validate_ohlc(self, df: pd.DataFrame) -> pd.Series:
        """
        Validate OHLC relationships
        
        Valid bar: Low <= Open, Close <= High
        """
        invalid = (
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close'])
        )
        
        return invalid
    
    def get_log(self) -> List[str]:
        """Return cleaning log"""
        return self.cleaning_log
```

#### Day 8-10: Database Storage

**File: `src/storage/database.py`**
```python
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

Base = declarative_base()

class DailyPrice(Base):
    """Daily OHLCV price data"""
    __tablename__ = 'daily_prices'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<DailyPrice(ticker='{self.ticker}', date='{self.date}', close={self.close})>"

class Database:
    """Database interface for market data"""
    
    def __init__(self, db_path: str = 'data/quantkit.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def insert_prices(self, ticker: str, df: pd.DataFrame):
        """
        Insert price data into database
        
        Args:
            ticker: Stock ticker
            df: DataFrame with OHLCV data
        """
        for date, row in df.iterrows():
            # Check if record exists
            exists = self.session.query(DailyPrice).filter_by(
                ticker=ticker,
                date=date.date()
            ).first()
            
            if exists:
                # Update existing
                exists.open = float(row['Open'])
                exists.high = float(row['High'])
                exists.low = float(row['Low'])
                exists.close = float(row['Close'])
                exists.volume = float(row['Volume'])
            else:
                # Insert new
                price = DailyPrice(
                    ticker=ticker,
                    date=date.date(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                self.session.add(price)
        
        self.session.commit()
    
    def get_prices(self, 
                   ticker: str, 
                   start_date: str = None, 
                   end_date: str = None) -> pd.DataFrame:
        """
        Retrieve price data from database
        
        Args:
            ticker: Stock ticker
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            DataFrame with OHLCV data
        """
        query = self.session.query(DailyPrice).filter_by(ticker=ticker)
        
        if start_date:
            query = query.filter(DailyPrice.date >= start_date)
        if end_date:
            query = query.filter(DailyPrice.date <= end_date)
        
        query = query.order_by(DailyPrice.date)
        
        # Convert to DataFrame
        data = [{
            'date': p.date,
            'open': p.open,
            'high': p.high,
            'low': p.low,
            'close': p.close,
            'volume': p.volume
        } for p in query.all()]
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        return df
    
    def get_available_tickers(self) -> list:
        """Get list of all tickers in database"""
        result = self.session.query(DailyPrice.ticker).distinct().all()
        return [r[0] for r in result]
    
    def get_date_range(self, ticker: str) -> tuple:
        """Get first and last available date for ticker"""
        result = self.session.query(
            DailyPrice.date
        ).filter_by(ticker=ticker).order_by(DailyPrice.date).all()
        
        if not result:
            return None, None
        
        return result[0][0], result[-1][0]
```

#### Day 11-14: Complete Pipeline

**File: `src/data_pipeline.py`**
```python
from pathlib import Path
from typing import List, Optional
import pandas as pd

from .downloaders.yahoo import YahooDownloader
from .cleaners.price_cleaner import PriceCleaner
from .storage.database import Database

class MarketDataPipeline:
    """
    Complete market data pipeline
    
    Usage:
        pipeline = MarketDataPipeline()
        pipeline.update(['AAPL', 'GOOGL', 'MSFT'], '2020-01-01', '2024-12-01')
    """
    
    def __init__(self, 
                 data_dir: str = 'data',
                 db_path: str = 'data/quantkit.db'):
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.downloader = YahooDownloader()
        self.cleaner = PriceCleaner()
        self.db = Database(db_path)
    
    def update(self, 
               tickers: List[str], 
               start_date: str, 
               end_date: str,
               force_download: bool = False):
        """
        Download, clean, and store data
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            force_download: Re-download even if data exists
        """
        print(f"\n{'='*60}")
        print(f"Market Data Pipeline - Updating {len(tickers)} tickers")
        print(f"{'='*60}\n")
        
        # Download
        print("Step 1: Downloading data...")
        raw_data = self.downloader.download(tickers, start_date, end_date)
        
        # Clean
        print("\nStep 2: Cleaning data...")
        cleaned_data = {}
        for ticker, df in raw_data.items():
            cleaned_df = self.cleaner.clean(df, ticker)
            cleaned_data[ticker] = cleaned_df
        
        # Store
        print("\nStep 3: Storing to database...")
        for ticker, df in cleaned_data.items():
            self.db.insert_prices(ticker, df)
            print(f"✓ Stored {ticker}: {len(df)} days")
        
        # Summary
        print(f"\n{'='*60}")
        print("Pipeline Complete!")
        print(f"{'='*60}")
        
        # Show cleaning log
        log = self.cleaner.get_log()
        if log:
            print("\nCleaning Log:")
            for entry in log:
                print(f"  - {entry}")
    
    def get_data(self, 
                 ticker: str, 
                 start_date: str = None, 
                 end_date: str = None) -> pd.DataFrame:
        """
        Retrieve data from database
        
        Returns:
            DataFrame with OHLCV data
        """
        return self.db.get_prices(ticker, start_date, end_date)
    
    def list_tickers(self) -> list:
        """Get all available tickers"""
        return self.db.get_available_tickers()
    
    def info(self, ticker: str):
        """Show info about ticker"""
        start, end = self.db.get_date_range(ticker)
        df = self.get_data(ticker)
        
        print(f"\n{'='*60}")
        print(f"Ticker: {ticker}")
        print(f"{'='*60}")
        print(f"Date Range: {start} to {end}")
        print(f"Total Days: {len(df)}")
        print(f"Missing Days: {df.isna().sum().sum()}")
        print(f"\nFirst 5 days:")
        print(df.head())
        print(f"\nLast 5 days:")
        print(df.tail())
        print(f"{'='*60}\n")
```

#### Complete Example Usage

**File: `examples/01_basic_pipeline.py`**
```python
from src.data_pipeline import MarketDataPipeline

# Initialize pipeline
pipeline = MarketDataPipeline()

# Download S&P 500 tech stocks
tech_stocks = [
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'GOOGL', # Alphabet
    'AMZN',  # Amazon
    'NVDA',  # NVIDIA
    'META',  # Meta
    'TSLA',  # Tesla
]

# Update database
pipeline.update(
    tickers=tech_stocks,
    start_date='2020-01-01',
    end_date='2024-12-01'
)

# Retrieve data
aapl = pipeline.get_data('AAPL')
print(aapl.head())

# Show info
pipeline.info('AAPL')

# List all tickers
tickers = pipeline.list_tickers()
print(f"Available tickers: {tickers}")
```

**Expected Output:**
```
============================================================
Market Data Pipeline - Updating 7 tickers
============================================================

Step 1: Downloading data...
✓ Downloaded AAPL: 1258 days
✓ Downloaded MSFT: 1258 days
✓ Downloaded GOOGL: 1258 days
✓ Downloaded AMZN: 1258 days
✓ Downloaded NVDA: 1258 days
✓ Downloaded META: 1258 days
✓ Downloaded TSLA: 1258 days

Step 2: Cleaning data...

Step 3: Storing to database...
✓ Stored AAPL: 1256 days
✓ Stored MSFT: 1257 days
✓ Stored GOOGL: 1255 days
✓ Stored AMZN: 1256 days
✓ Stored NVDA: 1258 days
✓ Stored META: 1253 days
✓ Stored TSLA: 1250 days

============================================================
Pipeline Complete!
============================================================

Cleaning Log:
  - AAPL: Removed 2 rows
  - GOOGL: Removed 3 rows
  - META: Removed 5 rows
  - TSLA: 3 outliers detected
  - TSLA: Removed 8 rows
```

---

### Week 4-7: Vectorized Backtester

*(Similar detailed breakdown for backtester, factor model, and options engine would follow...)*

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/quantkit.git
cd quantkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Example

```python
from quantkit import MarketDataPipeline, Backtester, FactorModel

# Step 1: Get data
pipeline = MarketDataPipeline()
pipeline.update(['AAPL', 'GOOGL', 'MSFT'], '2020-01-01', '2024-12-01')

# Step 2: Calculate factors
factors = FactorModel(pipeline)
factors.add_momentum()
factors.add_value()

# Step 3: Backtest
strategy = factors.create_long_short_strategy(top_n=10, bottom_n=10)
results = Backtester(strategy).run()

print(f"Sharpe Ratio: {results.sharpe:.2f}")
print(f"Annual Return: {results.annual_return:.2%}")
```

### 3. Run Tests

```bash
pytest tests/ -v
```

---

## 📚 Resources

### Books
- **"Quantitative Trading" by Ernest Chan** - Beginner-friendly intro
- **"Algorithmic Trading" by Ernest Chan** - More advanced strategies
- **"Active Portfolio Management" by Grinold & Kahn** - Factor investing bible
- **"Options, Futures, and Other Derivatives" by Hull** - Options theory

### Papers
- **Fama & French (1992)** - "The Cross-Section of Expected Stock Returns"
- **Jegadeesh & Titman (1993)** - "Returns to Buying Winners and Selling Losers"
- **Novy-Marx (2013)** - "The Quality Dimension of Value Investing"

### Online Courses
- **Quantopian Lectures** (free) - Algo trading fundamentals
- **WorldQuant University** (free) - MSc in Financial Engineering
- **Coursera: Machine Learning for Trading** - Georgia Tech

### Communities
- **QuantConnect Forum** - Algo trading discussions
- **r/algotrading** - Reddit community
- **Wilmott Forums** - Quant finance theory

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT:** This project is for educational purposes only.

- Past performance does not guarantee future results
- Trading involves risk of loss
- No strategy is guaranteed profitable
- Always paper trade before risking real capital
- Consult a financial advisor before investing

**Not Investment Advice:** Nothing in this project constitutes investment advice or a recommendation to buy/sell securities.

---

## 📞 Contact

**Project Maintainer:** Your Name
- GitHub: [@tda-8818](https://github.com/tda-8818)
- LinkedIn: [Elsa Tsia](https://linkedin.com/in/elsatsia)

**Found a bug?** [Open an issue](https://github.com/yourusername/quantkit/issues)

**Want to discuss?** [Start a discussion](https://github.com/yourusername/quantkit/discussions)

---

**Built with ❤️ for the quant finance community**

*"In God we trust, all others must bring data." - W. Edwards Deming*
```

---
