"""
Factor investing module
"""
from src.factors.calculator import FactorCalculator
from src.factors.value import ValueFactor
from src.factors.momentum import MomentumFactor
from src.factors.quality import QualityFactor
from src.factors.volatility import VolatilityFactor

__all__ = [
    'FactorCalculator',
    'ValueFactor',
    'MomentumFactor',
    'QualityFactor',
    'VolatilityFactor',
]