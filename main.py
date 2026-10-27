"""Entry point: per-month winter climatology maps of CaSR air temperature, surface wind or CIS sea-ice concentration."""
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

    norm = climatology.wind_norm(uas, vas)
    plotting.save(plotting.facet(norm, "Norm of the mean 10 m wind vector (m s⁻¹)",
                                 overlays=[(plotting.graticule, norm),
                                           (plotting.quiver, xr.Dataset({"uas": uas, "vas": vas}))],
                                 cmap="viridis", center=False, vmin=0),
                  "wind_mean")


def _ice(ds):
    weekly = access.timed_load(ds["ct"], "ct · weekly")
    season = climatology.select_season(climatology.monthly_ct_means(weekly))
    mean, trend = (climatology.gate_period_coverage(stat, season) for stat in climatology.per_month(season))

    plotting.save(plotting.facet(mean, "Mean monthly sea-ice concentration (fraction)",
                                 cmap="viridis", center=False, vmin=0, vmax=1),
                  "ice_mean")
    plotting.save(plotting.facet(trend.slope,
                                 f"Trend (fraction / decade), dotted: p ≥ {config.SIGNIFICANT_P_VALUE}",
                                 overlays=[(plotting.hatch, trend.p >= config.SIGNIFICANT_P_VALUE)]),
                  "ice_trend")


ANALYSES = {"tas": (_tas, config.CASR_PATH),
            "wind": (_wind, config.CASR_PATH),
            "ice": (_ice, config.ICE_PATH)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", choices=ANALYSES)
    run, path = ANALYSES[parser.parse_args().analysis]
    run(access.open_cache(path))


if __name__ == "__main__":
    main()
