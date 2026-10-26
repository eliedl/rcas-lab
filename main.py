"""Entry point: per-month seasonal climatology and trend maps of CaSR air temperature."""
from src import access, climatology, config, plotting


def main():
    daily = access.timed_load(access.open_cache()["tas"], "tas · daily")
    season = climatology.select_season(climatology.monthly_means(daily))
    mean, trend = climatology.per_month(season)

    plotting.save(plotting.facet(mean, "Mean monthly surface air temperature (°C)"), "tas_mean")
    plotting.save(plotting.facet(trend.slope,
                                 f"Trend (°C / decade), dotted: p ≥ {config.SIGNIFICANT_P_VALUE}",
                                 overlays=[(plotting.hatch, trend.p >= config.SIGNIFICANT_P_VALUE)]),
                  "tas_trend")


if __name__ == "__main__":
    main()
