
from pathlib import Path

import numpy as np
import rasterio


INPUT_DIR = Path("data/processed/aligned")
OUTPUT_DIR = Path("data/processed/masked")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "elevation": INPUT_DIR / "elevation_aligned.tif",
    "slope": INPUT_DIR / "slope_aligned.tif",
    "rainfall": INPUT_DIR / "rainfall_aligned.tif",
}


def main():
    with rasterio.open(FILES["elevation"]) as elevation_src:
        elevation = elevation_src.read(1)
        profile = elevation_src.profile.copy()

        valid_mask = np.isfinite(elevation)

        for name in ["slope", "rainfall"]:
            with rasterio.open(FILES[name]) as src:
                data = src.read(1)
                valid_mask &= np.isfinite(data)

        # Save a binary land/valid-data mask.
        mask_profile = profile.copy()
        mask_profile.update(
            dtype="uint8",
            nodata=0,
            count=1,
            compress="lzw",
        )

        with rasterio.open(
            OUTPUT_DIR / "land_mask.tif",
            "w",
            **mask_profile,
        ) as dst:
            dst.write(valid_mask.astype("uint8"), 1)

        # Save masked versions of each raster.
        for name, path in FILES.items():
            with rasterio.open(path) as src:
                data = src.read(1).astype("float32")
                data[~valid_mask] = np.nan

                output_profile = src.profile.copy()
                output_profile.update(
                    dtype="float32",
                    nodata=np.nan,
                    compress="lzw",
                )

                with rasterio.open(
                    OUTPUT_DIR / f"{name}_masked.tif",
                    "w",
                    **output_profile,
                ) as dst:
                    dst.write(data, 1)

    print("Land mask created successfully.")
    print("Valid pixels:", int(valid_mask.sum()))
    print("Missing pixels:", int((~valid_mask).sum()))


if __name__ == "__main__":
    main()