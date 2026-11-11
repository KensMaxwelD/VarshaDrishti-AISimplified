from pathlib import Path
import rasterio

folder = Path("data/processed/sentinel1")

for path in folder.glob("*.tif"):
    print(f"\nFile: {path.name}")

    with rasterio.open(path) as src:
        print("Width:", src.width)
        print("Height:", src.height)
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)
        print("Resolution:", src.res)
        print("Bands:", src.count)
        print("Data types:", src.dtypes)