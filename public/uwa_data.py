from netCDF4 import Dataset
import numpy as np
from typing import List
from datetime import datetime, timezone, timedelta
from weather_data import RainDay, WindDay

_URL = "http://130.95.29.59:8080/thredds/dodsC/WRF/wrf_roms_d02_{}.nc"


class UwaData(RainDay, WindDay):
    def __init__(self, year: int, month: int, day: int):
        date = "{:04d}-{:02d}-{:02d}".format(year, month, day)
        try:
            self._nc = Dataset(_URL.format(date.replace("-", "")), "r", format="NETCDF4")
        except OSError:
            raise LookupError("Can't find data for date {}".format(date))

        self.model_date = self._nc.date
        self.latitude = self._nc["LAT"][:, 0]
        self.lat_bounds = (self.latitude[0], self.latitude[-1])
        self.longitude = self._nc["LON"][0]
        self.lon_bounds = (self.longitude[0], self.longitude[-1])

    @property
    def time_updated(self) -> datetime:
        return datetime.strptime(self._nc.date, "%Y-%m-%d %H:%M:%S.%f")

    def get_rain_at(self, lat: float, lon: float) -> (List[int], List[float]):
        return self._get_rain(*self._coor_to_idx(lat, lon))

    def get_bounds(self):
        return self.lat_bounds, self.lon_bounds

    def get_wind_at(self, lat: float, lon: float):
        pass

    def _get_rain(self, lat_idx: int, lon_idx) -> (List[int], List[float]):
        if lat_idx > 164 or lat_idx < 0:
            raise IndexError("lat_idx {} must be between 0 and 164".format(lat_idx))
        if lon_idx > 89 or lon_idx < 0:
            raise IndexError("lon_idx {} must be between 0 and 89".format(lon_idx))

        utc_time = UwaData._convert_time(self._nc["rain_time"])
        return utc_time, (self._nc["rain"][:, lat_idx, lon_idx]*3600).round(1)  # [time][lat_idx = 0..164][lon_idx = 0..89]

    # convert from days since 2000-01-01 (utc) to unix time
    @staticmethod
    def _convert_time(days_since_20000101: float) -> int:
        base = datetime(2000, 1, 1, tzinfo=timezone.utc)
        return [(base + timedelta(days=d)).timestamp() for d in days_since_20000101]

    def _coor_to_idx(self, lat: float, lon: float) -> (int, int):
        if lat < self.lat_bounds[0] or lat > self.lat_bounds[1]:
            raise IndexError("Latitude {} out of bounds {}".format(lat, self.lat_bounds))
        if lon < self.lon_bounds[0] or lat > self.lon_bounds[1]:
            raise IndexError("Longitude {} out of bounds {}".format(lon, self.lon_bounds))

        i = np.searchsorted(self.latitude, lat)
        j = np.searchsorted(self.longitude, lon)
        return i, j
