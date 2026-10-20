"""Plotting: month-faceted maps in season order, significance hatching, figure output."""
import calendar

import matplotlib.pyplot as plt
import xarray as xr

from src import config

NOT_SIGNIFICANT_HATCH = "..."
FIGURE_DPI = 150


def winter_order(da: xr.DataArray) -> xr.DataArray:
    """Reorder months to the season order and label them (Dec, Jan, …)."""
    return (da.sel(month=list(config.SEASON_MONTHS))
              .assign_coords(month=[calendar.month_abbr[m] for m in config.SEASON_MONTHS]))


def _hatch(ax, mask):
    ydim, xdim = mask.dims                      # same (y, x) order xarray uses for the facet
    ax.contourf(mask[xdim], mask[ydim], mask.astype(float),
                levels=[0.5, 1.5], colors="none", hatches=[NOT_SIGNIFICANT_HATCH])


def facet(da, label, hatch_mask=None, **plot_kw):
    """One map per month in season order, optionally hatched where hatch_mask is True."""
    da = winter_order(da)
    if hatch_mask is not None:
        hatch_mask = winter_order(hatch_mask)
    kw = dict(cmap="RdBu_r", center=0, robust=True) | plot_kw
    fg = da.plot(col="month", col_wrap=2, cbar_kwargs={"label": label}, **kw)
    fg.set_titles("{value}")
    for ax, sel in zip(fg.axs.flat, fg.name_dicts.flat):
        ax.set_aspect("equal")
        if hatch_mask is not None and sel is not None:
            _hatch(ax, hatch_mask.sel(sel))
    return fg


def save(fg, name):
    """Write a facet figure to the output directory as PNG and release it."""
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    fg.fig.savefig(config.OUTPUT_DIR / f"{name}.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fg.fig)
