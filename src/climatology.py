"""Climatological reductions: monthly indicator, season selection, per-month mean and trend."""
import operator

import numpy as np
import xarray as xr
from scipy import stats
from xclim import atmos
from xclim.core.units import convert_units_to

from src import config

MONTH_START = "MS"
YEARS_PER_DECADE = 10


def monthly_means(tas: xr.DataArray) -> xr.DataArray:
    """Monthly mean air temperature in °C from a continuous daily series."""
    return atmos.tg_mean(tas, freq=MONTH_START).pipe(convert_units_to, "degC")


def select_season(monthly: xr.DataArray) -> xr.DataArray:
    """Keep the season's months only."""
    return monthly.sel(time=monthly.time.dt.month.isin(config.SEASON_MONTHS))


def trend_per_decade(da: xr.DataArray) -> xr.Dataset:
    """Least-squares linear trend along time (one value per year), in input units per decade."""
    by_year = da.assign_coords(year=da.time.dt.year).swap_dims(time="year")
    slope = (by_year.polyfit("year", deg=1)
                .polyfit_coefficients.sel(degree=1, drop=True)
                .pipe(operator.mul, YEARS_PER_DECADE)
                .assign_attrs(units=f"{da.attrs['units']} / decade"))

    r = xr.corr(by_year, by_year.year, dim="year")       # ignores NaN pairs
    n = by_year.count("year")                            # valid years per cell
    t = r * np.sqrt((n - 2) / (1 - r**2))
    p = xr.apply_ufunc(stats.t.sf, abs(t), n - 2) * 2
    return xr.Dataset({"slope": slope, "r2": r**2, "p": p})


def per_month(season: xr.DataArray) -> tuple[xr.DataArray, xr.Dataset]:
    """Per-month climatological mean and trend, keyed by month in groupby order."""
    by_month = season.groupby("time.month")
    return by_month.mean(), by_month.map(trend_per_decade)
