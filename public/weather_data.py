import abc
from typing import List
from datetime import datetime


class RainDay(abc.ABC):

    @property
    def time_updated(self) -> datetime:
        pass

    @abc.abstractmethod
    def get_rain_at(self, lat: float, lon: float) -> (List[int], List[float]):
        pass

    @abc.abstractmethod
    def get_bounds(self) -> ((float, float), (float, float)):
        pass


class WindDay(abc.ABC):

    @abc.abstractmethod
    def get_wind_at(self, lat: float, lon: float) -> (List[int], List[float]):
        pass
