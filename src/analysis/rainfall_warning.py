
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


RAINFALL_PATH = "data/processed/chennai_20231204_daily_rainfall.tif"

OUTPUT_MAP = "data/processed/rainfall_warning_map.png"


# Load rainfall raster
with rasterio.open(RAINFALL_PATH) as src:
    rainfall = src.read(1).astype(float)
    nodata = src.nodata

    if nodata is not None:
        rainfall[rainfall == nodata] = np.nan

    profile = src.profile

valid_values = rainfall[np.isfinite(rainfall)]

print("Rainfall statistics")
print("-------------------")
print(f"Minimum: {np.min(valid_values):.2f}")
print(f"Maximum: {np.max(valid_values):.2f}")
print(f"Mean: {np.mean(valid_values):.2f}")
print(f"75th percentile: {np.percentile(valid_values, 75):.2f}")
print(f"90th percentile: {np.percentile(valid_values, 90):.2f}")


# Prototype thresholds based on local raster distribution
moderate_threshold = np.percentile(valid_values, 75)
high_threshold = np.percentile(valid_values, 90)


# Warning classes
# 0 = Normal
# 1 = Moderate
# 2 = High

warning = np.full(rainfall.shape, 255, dtype=np.uint8)

valid = np.isfinite(rainfall)

warning[valid & (rainfall < moderate_threshold)] = 0

warning[
    valid
    & (rainfall >= moderate_threshold)
    & (rainfall < high_threshold)
] = 1

warning[
    valid
    & (rainfall >= high_threshold)
] = 2


print("\nWarning thresholds")
print("------------------")
print(f"Moderate threshold: {moderate_threshold:.2f}")
print(f"High threshold: {high_threshold:.2f}")


# Display map
cmap = ListedColormap([
    "green",
    "yellow",
    "red",
])

plt.figure(figsize=(10, 8))

image = np.ma.masked_where(warning == 255, warning)

plt.imshow(
    image,
    cmap=cmap,
    vmin=0,
    vmax=2,
)

colorbar = plt.colorbar(
    ticks=[0, 1, 2]
)

colorbar.ax.set_yticklabels([
    "Normal",
    "Moderate",
    "High",
])

colorbar.set_label("Prototype Rainfall Warning")

plt.title("Prototype Heavy Rainfall Warning Map")
plt.axis("off")
plt.tight_layout()

plt.savefig(
    OUTPUT_MAP,
    dpi=300,
)

plt.close()

print(f"\nMap saved to: {OUTPUT_MAP}")
print("Finished successfully!")