"""Project configuration: cache location, output, season, significance threshold."""
from pathlib import Path

CACHE_PATH = Path.home() / "data" / "ECCC" / "casr_v32_day_gulf_19900901-20200901.nc"
OUTPUT_DIR = Path(__file__).parents[1] / "output"
SEASON_MONTHS = (12, 1, 2, 3)   # display order: winter runs Dec → Mar
SIGNIFICANT_P_VALUE = 0.05
