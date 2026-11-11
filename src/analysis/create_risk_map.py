
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import rowcol
from rasterio.warp import transform
from matplotlib.colors import ListedColormap


FEATURES_PATH = "data/processed/features_enhanced.csv"
MODEL_PATH = "models/random_forest_enhanced_three_way.pkl"
THRESHOLD_PATH = "models/enhanced_model_threshold.json"
REFERENCE_RASTER = "data/processed/hazard_category.tif"

OUTPUT_CSV = "data/processed/risk_predictions.csv"
OUTPUT_PNG = "data/processed/three_level_risk_map.png"
OUTPUT_TIF = "data/processed/three_level_risk.tif"


print("Loading data and model...")

df = pd.read_csv(FEATURES_PATH)
model = joblib.load(MODEL_PATH)

with open(THRESHOLD_PATH, "r") as file:
    threshold_data = json.load(file)

threshold = threshold_data["threshold"]

feature_columns = [
    "elevation_m",
    "slope_degrees",
    "rainfall_mm",
    "distance_to_coast_m",
    "distance_to_drainage_m",
]

probabilities = model.predict_proba(
    df[feature_columns]
)[:, 1]

df["hazard_probability"] = probabilities


# Risk categories:
# 0 = Low
# 1 = Moderate
# 2 = High

risk_classes = np.select(
    [
        probabilities < 0.10,
        probabilities <= 0.30,
        probabilities > 0.30,
    ],
    [
        0,
        1,
        2,
    ],
    default=0,
)

df["risk_class"] = risk_classes

df["risk_category"] = df["risk_class"].map({
    0: "Low",
    1: "Moderate",
    2: "High",
})

df.to_csv(OUTPUT_CSV, index=False)

print("\nRisk category counts:")
print(df["risk_category"].value_counts())

print(f"\nCSV saved to: {OUTPUT_CSV}")


# Create PNG map
print("Creating PNG map...")

plt.figure(figsize=(10, 8))

cmap = ListedColormap([
    "green",
    "yellow",
    "red",
])

scatter = plt.scatter(
    df["longitude"],
    df["latitude"],
    c=df["risk_class"],
    cmap=cmap,
    vmin=0,
    vmax=2,
    s=0.3,
)

colorbar = plt.colorbar(
    scatter,
    ticks=[0, 1, 2],
)

colorbar.ax.set_yticklabels([
    "Low",
    "Moderate",
    "High",
])

colorbar.set_label("Risk Category")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Three-Level Predicted Hazard Risk Map")
plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=300)
plt.close()

print(f"PNG saved to: {OUTPUT_PNG}")


# Create GeoTIFF
print("Creating GeoTIFF...")

with rasterio.open(REFERENCE_RASTER) as reference:

    profile = reference.profile.copy()
    height = reference.height
    width = reference.width
    reference_transform = reference.transform
    reference_crs = reference.crs

    risk_array = np.full(
        (height, width),
        255,
        dtype=np.uint8,
    )

    xs = df["longitude"].to_numpy()
    ys = df["latitude"].to_numpy()

    if reference_crs.to_string() != "EPSG:4326":
        xs, ys = transform(
            "EPSG:4326",
            reference_crs,
            xs,
            ys,
        )

    rows, cols = rowcol(
        reference_transform,
        xs,
        ys,
    )

    rows = np.asarray(rows)
    cols = np.asarray(cols)

    valid = (
        (rows >= 0)
        & (rows < height)
        & (cols >= 0)
        & (cols < width)
    )

    risk_array[
        rows[valid],
        cols[valid]
    ] = risk_classes[valid]

    profile.update(
        dtype="uint8",
        count=1,
        nodata=255,
        compress="lzw",
    )

    with rasterio.open(
        OUTPUT_TIF,
        "w",
        **profile,
    ) as destination:
        destination.write(risk_array, 1)

print(f"GeoTIFF saved to: {OUTPUT_TIF}")
print("\nFinished successfully!")