"""
Trading strategies module
"""
from src.strategies.base import Strategy
from src.strategies.momentum import MomentumStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.moving_average import SimpleMovingAverageCrossover

__all__ = [
    'Strategy',
    'MomentumStrategy', 
    'MeanReversionStrategy',
    'SimpleMovingAverageCrossover',
]