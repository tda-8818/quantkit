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