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