"""Entry point: per-month winter climatology maps of CaSR air temperature or surface wind."""
import argparse

import xarray as xr

from src import access, climatology, config, plotting


def _tas(ds):
    daily = access.timed_load(ds["tas"], "tas · daily")
    season = climatology.select_season(climatology.monthly_means(daily))
    mean, trend = climatology.per_month(season)

    plotting.save(plotting.facet(mean, "Mean monthly surface air temperature (°C)"), "tas_mean")
    plotting.save(plotting.facet(trend.slope,
                                 f"Trend (°C / decade), dotted: p ≥ {config.SIGNIFICANT_P_VALUE}",
                                 overlays=[(plotting.hatch, trend.p >= config.SIGNIFICANT_P_VALUE)]),
                  "tas_trend")


def _wind(ds):
    daily = [access.timed_load(ds[var], f"{var} · daily") for var in ("uas", "vas")]
    uas, vas = (climatology.climatological_mean(climatology.select_season(monthly))
                for monthly in climatology.monthly_wind_means(*daily))

    plotting.save(plotting.facet(climatology.wind_norm(uas, vas),
                                 "Norm of the mean 10 m wind vector (m s⁻¹)",
                                 overlays=[(plotting.quiver, xr.Dataset({"uas": uas, "vas": vas}))],
                                 cmap="viridis", center=False, vmin=0),
                  "wind_mean")


ANALYSES = {"tas": _tas, "wind": _wind}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", choices=ANALYSES)
    ANALYSES[parser.parse_args().analysis](access.open_cache())


if __name__ == "__main__":
    main()
