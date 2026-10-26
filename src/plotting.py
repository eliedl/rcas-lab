"""Plotting: month-faceted maps in season order, hatching and wind overlays, figure output."""
import calendar

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from src import config

NOT_SIGNIFICANT_HATCH = "..."
FIGURE_DPI = 150
QUIVER_STRIDE = 8          # grid cells between arrows, along each axis
ARROW_FILL = 0.8           # arrow length as a fraction of the arrow spacing: arrows never overlap
ARROW_COLOR = "white"


def winter_order(da: xr.DataArray) -> xr.DataArray:
    """Reorder months to the season order and label them (Dec, Jan, …)."""
    return (da.sel(month=list(config.SEASON_MONTHS))
              .assign_coords(month=[calendar.month_abbr[m] for m in config.SEASON_MONTHS]))


def hatch(ax, mask):
    """Overlay: hatch the cells where mask is True."""
    ydim, xdim = mask.dims                      # same (y, x) order xarray uses for the facet
    # the single band [0.5, 1.5] of the 0/1 mask holds exactly the True cells; fill is transparent
    ax.contourf(mask[xdim], mask[ydim], mask.astype(float),
                levels=[0.5, 1.5], colors="none", hatches=[NOT_SIGNIFICANT_HATCH])


def quiver(ax, wind):
    """Overlay: equal-length arrows pointing where the wind blows to, from a (uas, vas) Dataset."""
    ydim, xdim = wind.uas.dims
    sub = wind.isel({ydim: slice(None, None, QUIVER_STRIDE), xdim: slice(None, None, QUIVER_STRIDE)})
    norm = np.hypot(sub.uas, sub.vas)
    spacing = abs(float(sub[xdim][1] - sub[xdim][0]))
    ax.quiver(sub[xdim], sub[ydim], sub.uas / norm, sub.vas / norm, color=ARROW_COLOR,
              angles="xy", scale_units="xy", scale=1 / (ARROW_FILL * spacing), pivot="middle")


def facet(da, label, overlays=(), **plot_kw):
    """One map per month in season order, with (draw, month-keyed data) overlays drawn on each map."""
    kw = dict(cmap="RdBu_r", center=0, robust=True) | plot_kw
    fg = winter_order(da).plot(col="month", col_wrap=2, cbar_kwargs={"label": label}, **kw)
    fg.set_titles("{value}")
    for ax, month in zip(fg.axs.flat, config.SEASON_MONTHS):    # facets are in season order
        ax.set_aspect("equal")
        for draw, data in overlays:
            draw(ax, data.sel(month=month))
    return fg


def save(fg, name):
    """Write a facet figure to the output directory as PNG and release it."""
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    fg.fig.savefig(config.OUTPUT_DIR / f"{name}.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fg.fig)
