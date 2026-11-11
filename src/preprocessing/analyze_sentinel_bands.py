from pathlib import Path
import numpy as np
import rasterio

path = next(Path("data/processed/sentinel1").glob("*.tif"))

with rasterio.open(path) as src:
    for i in range(1, src.count + 1):
        data = src.read(i).astype("float32")

        valid = data[np.isfinite(data) & (data > 0)]

        print(f"\nBand {i}")
        print("Valid nonzero pixels:", len(valid))

        if len(valid) > 0:
            print("Min:", np.min(valid))
            print("Max:", np.max(valid))
            print("Mean:", np.mean(valid))
            print("Median:", np.median(valid))
            print("P1:", np.percentile(valid, 1))
            print("P99:", np.percentile(valid, 99))