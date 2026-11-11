
"""Align rainfall and slope rasters to the elevation grid."""

from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling


PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = PROCESSED_DIR / "aligned"

ELEVATION_PATH = PROCESSED_DIR / "chennai_elevation.tif"
SLOPE_PATH = PROCESSED_DIR / "chennai_slope.tif"
RAINFALL_PATH = PROCESSED_DIR / "chennai_20231204_daily_rainfall.tif"



def align_raster(source_path, reference_dataset, output_path):
    """Resample a raster to match the reference raster grid."""

    with rasterio.open(source_path) as source:
        source_data = source.read(1).astype("float32")

        # IMERG daily total accumulation uses a scale factor of 10.
        if source_path == RAINFALL_PATH:
            source_data = source_data / 10.0

        destination = np.full(
            (reference_dataset.height, reference_dataset.width),
            np.nan,
            dtype="float32",
        )

        reproject(
            source=source_data,
            destination=destination,
            src_transform=source.transform,
            src_crs=source.crs,
            dst_transform=reference_dataset.transform,
            dst_crs=reference_dataset.crs,
            resampling=Resampling.bilinear,
            src_nodata=source.nodata,
            dst_nodata=np.nan,
        )

        profile = reference_dataset.profile.copy()
        profile.update(
            dtype="float32",
            count=1,
            nodata=np.nan,
            compress="lzw",
        )

        with rasterio.open(output_path, "w", **profile) as output:
            output.write(destination, 1)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with rasterio.open(ELEVATION_PATH) as elevation:
        # Copy elevation to the aligned directory.
        elevation_profile = elevation.profile.copy()
        elevation_profile.update(compress="lzw")

        with rasterio.open(
            OUTPUT_DIR / "elevation_aligned.tif",
            "w",
            **elevation_profile,
        ) as output:
            output.write(elevation.read())

        align_raster(
            SLOPE_PATH,
            elevation,
            OUTPUT_DIR / "slope_aligned.tif",
        )

        align_raster(
            RAINFALL_PATH,
            elevation,
            OUTPUT_DIR / "rainfall_aligned.tif",
        )

    print("Raster alignment completed successfully.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()