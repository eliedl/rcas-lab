"""Climatological reductions: monthly indicators, season selection, per-month mean and trend."""
import operator

import numpy as np
import xarray as xr
import xclim
from scipy import stats
from xclim import atmos
from xclim.core.units import convert_units_to
from xclim.indicators import convert, generic

from src import config

MONTH_START = "MS"
YEARS_PER_DECADE = 10


def monthly_means(tas: xr.DataArray) -> xr.DataArray:
    """Monthly mean air temperature in °C from a continuous daily series."""
    return atmos.tg_mean(tas, freq=MONTH_START).pipe(convert_units_to, "degC")


def monthly_wind_means(uas: xr.DataArray, vas: xr.DataArray) -> tuple[xr.DataArray, xr.DataArray]:
    """Monthly means of the eastward and northward wind components from continuous daily series."""
    # components are averaged before any conversion: the mean of speeds is not the norm of the mean vector
    return tuple(generic.stats(da, op="mean", freq=MONTH_START).rename(da.name) for da in (uas, vas))


def monthly_ct_means(ct: xr.DataArray) -> xr.DataArray:
    """Monthly mean sea-ice concentration from weekly charts; NaN under MIN_MONTH_COVERAGE."""
    # counts the charts actually present: xclim's missing check needs a regular timestep, cis sgrdr chart do not
    covered = ct.notnull().resample(time=MONTH_START).mean() >= config.MIN_MONTH_COVERAGE
    with xclim.set_options(check_missing="skip"):
        return generic.stats(ct, op="mean", freq=MONTH_START).rename(ct.name).where(covered)


def wind_norm(uas: xr.DataArray, vas: xr.DataArray) -> xr.DataArray:
    """Norm of the wind vector from its eastward and northward components."""
    return convert.wind_speed_from_vector(uas=uas, vas=vas)[0]


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


def climatological_mean(season: xr.DataArray) -> xr.DataArray:
    """Per-month climatological mean, keyed by month in groupby order."""
    return season.groupby("time.month").mean()


def per_month(season: xr.DataArray) -> tuple[xr.DataArray, xr.Dataset]:
    """Per-month climatological mean and trend, keyed by month in groupby order."""
    return climatological_mean(season), season.groupby("time.month").map(trend_per_decade)


def gate_period_coverage(stat, season: xr.DataArray):
    """Blank the cell-months of a per-month statistic where under MIN_PERIOD_COVERAGE of the years have a value."""
    # one value per year in each month group: the mean of notnull is the fraction of years covered
    covered = season.notnull().groupby("time.month").mean() >= config.MIN_PERIOD_COVERAGE
    return stat.where(covered)
