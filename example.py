from src.data_pipeline import MarketDataPipeline

pipeline = MarketDataPipeline()

# Download any stocks
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
pipeline.update(tickers, '2020-01-01', '2024-12-01')

# Get data anytime
aapl = pipeline.get_data('AAPL')
print(f"\n{aapl.head()}\n")
print(f"Available: {pipeline.list_tickers()}") # Check what's stored

