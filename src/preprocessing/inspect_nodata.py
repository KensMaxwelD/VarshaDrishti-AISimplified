
import rasterio
import numpy as np
import matplotlib.pyplot as plt

path = "data/processed/aligned/elevation_aligned.tif"

with rasterio.open(path) as src:
    elevation = src.read(1)

valid_mask = ~np.isnan(elevation)

plt.figure(figsize=(10, 8))
plt.imshow(valid_mask, cmap="gray")
plt.title("Elevation Valid-Pixel Coverage")
plt.xlabel("Column")
plt.ylabel("Row")
plt.colorbar(label="Valid (1) / Missing (0)")
plt.savefig("data/processed/elevation_valid_mask.png", dpi=150)
plt.close()

print("Saved: data/processed/elevation_valid_mask.png")