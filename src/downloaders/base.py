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