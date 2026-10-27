"""Data access: open the local NetCDF inputs and load them with telemetry."""
import time

import xarray as xr


def open_cache(path) -> xr.Dataset:
    """Open a local NetCDF input lazily."""
    return xr.open_dataset(path)


def timed_load(obj, label):
    """Load a lazy xarray object and print its size, load time and throughput."""
    t0 = time.perf_counter()
    obj = obj.load()
    elapsed = time.perf_counter() - t0
    print(f"{label:<28} {obj.nbytes/1e9:6.2f} GB  {elapsed:6.1f} s  {obj.nbytes/1e6/elapsed:7.1f} MB/s")
    return obj
