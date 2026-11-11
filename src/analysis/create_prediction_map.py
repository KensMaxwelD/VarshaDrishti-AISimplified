
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import rowcol
from rasterio.warp import transform


# Paths
FEATURES_PATH = "data/processed/features_enhanced.csv"
MODEL_PATH = "models/random_forest_enhanced_three_way.pkl"
THRESHOLD_PATH = "models/enhanced_model_threshold.json"
REFERENCE_RASTER = "data/processed/hazard_category.tif"

OUTPUT_CSV = "data/processed/hazard_predictions.csv"
OUTPUT_PROBABILITY_TIF = "data/processed/hazard_probability.tif"
OUTPUT_LABEL_TIF = "data/processed/hazard_prediction.tif"

OUTPUT_PROBABILITY_PNG = "data/processed/hazard_probability_map.png"
OUTPUT_LABEL_PNG = "data/processed/hazard_prediction_map.png"


# Load data and model
print("Loading feature data...")
df = pd.read_csv(FEATURES_PATH)

print("Loading model...")
model = joblib.load(MODEL_PATH)

import json

with open(THRESHOLD_PATH, "r") as f:
    threshold_data = json.load(f)

threshold = threshold_data["threshold"]

print(f"Using prediction threshold: {threshold}")


# Prepare features
feature_columns = [
    "elevation_m",
    "slope_degrees",
    "rainfall_mm",
    "distance_to_coast_m",
    "distance_to_drainage_m",
]

X = df[feature_columns]


# Generate predictions
print("Generating predictions...")

probabilities = model.predict_proba(X)[:, 1]
predictions = (probabilities >= threshold).astype(np.uint8)

df["hazard_probability"] = probabilities
df["predicted_hazard"] = predictions

df.to_csv(OUTPUT_CSV, index=False)

print(f"Predictions saved to: {OUTPUT_CSV}")
print("\nPrediction counts:")
print(df["predicted_hazard"].value_counts())


# Create prediction maps as PNG files
print("Creating visual maps...")

plt.figure(figsize=(10, 8))
plt.scatter(
    df["longitude"],
    df["latitude"],
    c=df["hazard_probability"],
    s=0.3,
)
plt.colorbar(label="Hazard Probability")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Predicted Hazard Probability")
plt.tight_layout()
plt.savefig(OUTPUT_PROBABILITY_PNG, dpi=300)
plt.close()


plt.figure(figsize=(10, 8))
plt.scatter(
    df["longitude"],
    df["latitude"],
    c=df["predicted_hazard"],
    s=0.3,
)
plt.colorbar(label="Predicted Hazard Class")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Predicted Hazard Map")
plt.tight_layout()
plt.savefig(OUTPUT_LABEL_PNG, dpi=300)
plt.close()

print(f"Probability map saved to: {OUTPUT_PROBABILITY_PNG}")
print(f"Prediction map saved to: {OUTPUT_LABEL_PNG}")


# Create GeoTIFF prediction maps
print("Creating GeoTIFF files...")

with rasterio.open(REFERENCE_RASTER) as reference:

    profile = reference.profile.copy()
    width = reference.width
    height = reference.height
    transform_ref = reference.transform
    reference_crs = reference.crs

    probability_array = np.full(
        (height, width),
        -9999,
        dtype=np.float32,
    )

    label_array = np.full(
        (height, width),
        255,
        dtype=np.uint8,
    )

    # Transform CSV coordinates into reference CRS
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
        transform_ref,
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

    probability_array[rows[valid], cols[valid]] = (
        probabilities[valid]
    )

    label_array[rows[valid], cols[valid]] = (
        predictions[valid]
    )

    # Probability GeoTIFF
    probability_profile = profile.copy()
    probability_profile.update(
        dtype="float32",
        count=1,
        nodata=-9999,
        compress="lzw",
    )

    with rasterio.open(
        OUTPUT_PROBABILITY_TIF,
        "w",
        **probability_profile,
    ) as destination:
        destination.write(probability_array, 1)

    # Binary prediction GeoTIFF
    label_profile = profile.copy()
    label_profile.update(
        dtype="uint8",
        count=1,
        nodata=255,
        compress="lzw",
    )

    with rasterio.open(
        OUTPUT_LABEL_TIF,
        "w",
        **label_profile,
    ) as destination:
        destination.write(label_array, 1)


print(f"Probability GeoTIFF saved to: {OUTPUT_PROBABILITY_TIF}")
print(f"Prediction GeoTIFF saved to: {OUTPUT_LABEL_TIF}")

print("\nFinished successfully!")