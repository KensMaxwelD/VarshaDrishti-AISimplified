
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


INPUT_DIR = Path("data/processed/masked")
OUTPUT_DIR = Path("data/processed")
OUTPUT_PATH = OUTPUT_DIR / "features.csv"

FILES = {
    "elevation": INPUT_DIR / "elevation_masked.tif",
    "slope": INPUT_DIR / "slope_masked.tif",
    "rainfall": INPUT_DIR / "rainfall_masked.tif",
}

SAMPLE_STEP = 10


def main():
    with rasterio.open(FILES["elevation"]) as src:
        elevation = src.read(1)
        transform = src.transform
        height, width = elevation.shape

    with rasterio.open(FILES["slope"]) as src:
        slope = src.read(1)

    with rasterio.open(FILES["rainfall"]) as src:
        rainfall = src.read(1)

    rows, cols = np.indices((height, width))

    # Sample every 10th pixel.
    rows = rows[::SAMPLE_STEP, ::SAMPLE_STEP]
    cols = cols[::SAMPLE_STEP, ::SAMPLE_STEP]

    elevation = elevation[::SAMPLE_STEP, ::SAMPLE_STEP]
    slope = slope[::SAMPLE_STEP, ::SAMPLE_STEP]
    rainfall = rainfall[::SAMPLE_STEP, ::SAMPLE_STEP]

    valid = (
        np.isfinite(elevation)
        & np.isfinite(slope)
        & np.isfinite(rainfall)
    )

    rows = rows[valid]
    cols = cols[valid]

    xs, ys = rasterio.transform.xy(
        transform,
        rows,
        cols,
    )

    df = pd.DataFrame({
        "longitude": xs,
        "latitude": ys,
        "elevation_m": elevation[valid],
        "slope_degrees": slope[valid],
        "rainfall_mm": rainfall[valid],
    })

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Feature dataset saved: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()