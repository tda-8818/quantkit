"""
SQLAlchemy-based database interface for storing market data.

Provides:
- DailyPrice model: OHLCV data schema with ticker/date indexing
- Database class: Insert/retrieve price data with automatic upserts
- SQLite backend: Local file storage (upgradeable to PostgreSQL)

Usage:
    db = Database('data/quantkit.db')
    db.insert_prices('AAPL', dataframe)
    prices = db.get_prices('AAPL', start_date='2024-01-01')
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

Base = declarative_base()

class DailyPrice(Base):
    """
    Daily OHLCV price data model.
    
    Schema:
        ticker: Stock symbol (indexed for fast queries)
        date: Trading date (indexed with ticker as composite key)
        open/high/low/close: Price data
        volume: Trading volume
        created_at: Record insertion timestamp
    """
    
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

class Database:
    """
    Database interface for market data storage and retrieval.
    
    Features:
        - Automatic table creation on init
        - Upsert logic (update if exists, insert if new)
        - Date range filtering
        - Ticker inventory management
    """
    
    def __init__(self, db_path: str = 'data/quantkit.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: SQLite database file path
        """
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine) # Create tables if not exist
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def insert_prices(self, ticker: str, df: pd.DataFrame):
        """
        Insert or update price data (upsert).
        
        Args:
            ticker: Stock symbol
            df: DataFrame with DatetimeIndex and OHLCV columns
            
        Note: Automatically updates existing records or inserts new ones
        """
        
        for date, row in df.iterrows():
            # Check if record already exists
            exists = self.session.query(DailyPrice).filter_by(
                ticker=ticker, date=date.date()).first()
            
            if exists:
                # Update existing record
                exists.open = row['Open']
                exists.high = row['High']
                exists.low = row['Low']
                exists.close = row['Close']
                exists.volume = row['Volume']
            else:
                # Insert new record
                price = DailyPrice(
                    ticker=ticker,
                    date=date.date(),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )
                self.session.add(price)
        self.session.commit() # Save all changes to disk
    
    def get_prices(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Retrieve price data from database.
        
        Args:
            ticker: Stock symbol
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            DataFrame with date index and OHLCV columns
            Empty DataFrame if no data found
        """
        query = self.session.query(DailyPrice).filter_by(ticker=ticker)
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(DailyPrice.date >= start_date)
        if end_date:
            query = query.filter(DailyPrice.date <= end_date)
        query = query.order_by(DailyPrice.date) # Sort chronologically
        
        # Convert SQLAlchemy objects to DataFrame
        data = [{'date': p.date, 'open': p.open, 'high': p.high, 
                 'low': p.low, 'close': p.close, 'volume': p.volume}
                for p in query.all()]
        
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data).set_index('date')
    
    def get_available_tickers(self) -> list:
        """
        Get list of all tickers in database.
        
        Returns:
            List of unique ticker symbols
        """
        result = self.session.query(DailyPrice.ticker).distinct().all()
        return [r[0] for r in result]
