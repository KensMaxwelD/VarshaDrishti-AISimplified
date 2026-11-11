"""Basic validation utilities for geospatial rasters.

This module deliberately does not claim that layers are aligned yet. It reports
metadata so the next step can implement reprojection and common-grid resampling.
"""
from pathlib import Path
import json

try:
    import rasterio
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies from requirements.txt first") from exc


def inspect_raster(path: str | Path) -> dict:
    path = Path(path)
    with rasterio.open(path) as src:
        return {
            "path": str(path),
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "crs": str(src.crs),
            "transform": tuple(src.transform),
            "bounds": tuple(src.bounds),
            "nodata": src.nodata,
            "dtype": src.dtypes[0],
        }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("rasters", nargs="+", help="Raster paths to inspect")
    args = parser.parse_args()
    report = [inspect_raster(p) for p in args.rasters]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
