import pytest
from src.data_pipeline import MarketDataPipeline

def test_download():
    pipeline = MarketDataPipeline()
    pipeline.update(['AAPL'], '2024-01-01', '2024-01-31')
    data = pipeline.get_data('AAPL')
    assert len(data) > 0
    assert 'close' in data.columns