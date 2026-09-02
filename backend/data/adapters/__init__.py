"""
Data Adapters Package for Real External Ocean & Weather Feeds
"""
from backend.data.adapters.base import BaseDataServiceAdapter
from backend.data.adapters.open_meteo_marine import OpenMeteoMarineAdapter
from backend.data.adapters.open_meteo_weather import OpenMeteoWeatherAdapter
from backend.data.adapters.incois_adapter import INCOISDataServiceAdapter
from backend.data.adapters.cyclone_adapter import TropicalCycloneAdapter

__all__ = [
    "BaseDataServiceAdapter",
    "OpenMeteoMarineAdapter",
    "OpenMeteoWeatherAdapter",
    "INCOISDataServiceAdapter",
    "TropicalCycloneAdapter"
]
