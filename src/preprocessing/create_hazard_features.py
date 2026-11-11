
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from shapely.ops import transform


# -----------------------------
# File paths
# -----------------------------
KML_PATH = Path(
    "data/raw/chennai_flood_hazard_zones.kml"
)

MASKED_DIR = Path("data/processed/masked")
OUTPUT_DIR = Path("data/processed")

ELEVATION_PATH = MASKED_DIR / "elevation_masked.tif"
SLOPE_PATH = MASKED_DIR / "slope_masked.tif"
RAINFALL_PATH = MASKED_DIR / "rainfall_masked.tif"

HAZARD_RASTER_PATH = OUTPUT_DIR / "hazard_category.tif"
FEATURES_PATH = OUTPUT_DIR / "features.csv"


# -----------------------------
# Hazard category mapping
# -----------------------------
CATEGORY_CODES = {
    "Very Low": 1,
    "Low": 2,
    "Moderate": 3,
    "High": 4,
    "Very High": 5,
}

HIGH_HAZARD_CATEGORIES = {"High", "Very High"}


# -----------------------------
# Load reference raster
# -----------------------------
with rasterio.open(ELEVATION_PATH) as src:
    elevation = src.read(1)
    profile = src.profile.copy()
    transform_ref = src.transform
    crs_ref = src.crs
    height = src.height
    width = src.width


# -----------------------------
# Load slope and rainfall
# -----------------------------
with rasterio.open(SLOPE_PATH) as src:
    slope = src.read(1)

with rasterio.open(RAINFALL_PATH) as src:
    rainfall = src.read(1)


# -----------------------------
# Validate raster dimensions
# -----------------------------
if elevation.shape != slope.shape:
    raise ValueError("Elevation and slope dimensions differ.")

if elevation.shape != rainfall.shape:
    raise ValueError("Elevation and rainfall dimensions differ.")


# -----------------------------
# Read KML
# -----------------------------
gdf = gpd.read_file(KML_PATH, driver="KML")

if gdf.crs is None:
    raise ValueError("KML has no CRS.")

gdf = gdf.to_crs(crs_ref)

gdf = gdf[gdf.geometry.notna()].copy()
gdf = gdf[gdf["CATEGORY"].notna()].copy()


# -----------------------------
# Remove Z coordinates
# -----------------------------
def remove_z(geometry):
    return transform(
        lambda x, y, z=None: (x, y),
        geometry
    )


gdf["geometry"] = gdf.geometry.apply(remove_z)


# -----------------------------
# Convert categories to codes
# -----------------------------
gdf["category_code"] = gdf["CATEGORY"].map(CATEGORY_CODES)

gdf = gdf[gdf["category_code"].notna()].copy()


# -----------------------------
# Rasterize hazard categories
# -----------------------------
shapes = [
    (geometry, int(code))
    for geometry, code in zip(
        gdf.geometry,
        gdf.category_code
    )
]

hazard_array = rasterize(
    shapes=shapes,
    out_shape=(height, width),
    transform=transform_ref,
    fill=0,
    dtype="uint8",
    all_touched=False,
)


# -----------------------------
# Save hazard raster
# -----------------------------
hazard_profile = profile.copy()

hazard_profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="lzw"
)

with rasterio.open(
    HAZARD_RASTER_PATH,
    "w",
    **hazard_profile
) as dst:
    dst.write(hazard_array, 1)


# -----------------------------
# Create valid feature mask
# -----------------------------
valid_mask = (
    np.isfinite(elevation)
    & np.isfinite(slope)
    & np.isfinite(rainfall)
    & (hazard_array > 0)
)


# -----------------------------
# Extract pixel coordinates
# -----------------------------
rows, cols = np.where(valid_mask)

xs, ys = rasterio.transform.xy(
    transform_ref,
    rows,
    cols
)

xs = np.asarray(xs)
ys = np.asarray(ys)


# -----------------------------
# Create dataframe
# -----------------------------
category_names = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}

hazard_codes = hazard_array[rows, cols]

hazard_categories = [
    category_names[int(code)]
    for code in hazard_codes
]

hazard_labels = [
    1 if category in HIGH_HAZARD_CATEGORIES else 0
    for category in hazard_categories
]


df = pd.DataFrame({
    "longitude": xs,
    "latitude": ys,
    "elevation_m": elevation[rows, cols],
    "slope_degrees": slope[rows, cols],
    "rainfall_mm": rainfall[rows, cols],
    "hazard_category": hazard_categories,
    "hazard_label": hazard_labels,
})


# -----------------------------
# Save features
# -----------------------------
df.to_csv(FEATURES_PATH, index=False)

print("Hazard raster saved:", HAZARD_RASTER_PATH)
print("Features saved:", FEATURES_PATH)
print("Number of rows:", len(df))

print("\nHazard categories:")
print(df["hazard_category"].value_counts())

print("\nBinary label distribution:")
print(df["hazard_label"].value_counts())