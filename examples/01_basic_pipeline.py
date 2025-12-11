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