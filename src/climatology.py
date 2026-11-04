"""Climatological reductions: monthly indicators, season selection, per-month mean and trend."""
import operator
from dataclasses import dataclass

import numpy as np
import xarray as xr
import xclim
from scipy import stats
from xclim.core.units import convert_units_to
from xclim.indicators import atmos, convert, generic

from src import config

MONTH_START = "MS"
YEARS_PER_DECADE = 10


@dataclass(frozen=True)
class MonthlyMean:
    """How a variable's monthly mean is reduced: output units and, for irregular series, a coverage gate."""
    units: str | None = None            # None keeps the source units
    min_coverage: float | None = None   # None leaves the missing check to xclim


MONTHLY_MEANS = {"tas": MonthlyMean(units="degC"),
                 "uas": MonthlyMean(),
                 "vas": MonthlyMean(),
                 "ct": MonthlyMean(units="%", min_coverage=config.MIN_MONTH_COVERAGE)}


def monthly_means(da: xr.DataArray) -> xr.DataArray:
    """Monthly mean of a variable, reduced as its MONTHLY_MEANS row specifies."""
    spec = MONTHLY_MEANS[da.name]
    mean = (generic.stats(da, op="mean", freq=MONTH_START) if spec.min_coverage is None
            else _gated_mean(da, spec.min_coverage))
    return mean if spec.units is None else convert_units_to(mean, spec.units)


def _gated_mean(da: xr.DataArray, min_coverage: float) -> xr.DataArray:
    """Monthly mean of an irregular series, NaN where under min_coverage of its timesteps are present."""
    # counts the timesteps actually present: xclim's missing check needs a regular timestep, cis sgrdr charts do not
    covered = da.notnull().resample(time=MONTH_START).mean() >= min_coverage
    with xclim.set_options(check_missing="skip"):
        return generic.stats(da, op="mean", freq=MONTH_START).where(covered)


def wind_norm(uas: xr.DataArray, vas: xr.DataArray) -> xr.DataArray:
    """Norm of the wind vector from its eastward and northward components."""
    return convert.wind_speed_from_vector(uas=uas, vas=vas)[0]


def days_above_freezing(tas: xr.DataArray) -> xr.DataArray:
    """Monthly count of days with daily mean temperature above FREEZING_THRESHOLD."""
    return atmos.tg_days_above(tas=tas, thresh=config.FREEZING_THRESHOLD, op=">", freq=MONTH_START)


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
