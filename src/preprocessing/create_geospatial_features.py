
import os
import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point

# --------------------------------------------------
# Paths
# --------------------------------------------------

FEATURES_PATH = "data/processed/features.csv"

COASTLINE_PATH = (
    "data/raw/geospatial/coastline.geojson"
)

DRAINAGE_PATH = (
    "data/raw/geospatial/drainage.geojson"
)

STORMWATER_PATH = (
    "data/raw/geospatial/stormwater_drain_streets.geojson"
)

OUTPUT_PATH = (
    "data/processed/features_enhanced.csv"
)
# --------------------------------------------------
# Load feature dataset
# --------------------------------------------------

df = pd.read_csv(FEATURES_PATH)

geometry = [
    Point(lon, lat)
    for lon, lat in zip(df["longitude"], df["latitude"])
]

points = gpd.GeoDataFrame(
    df,
    geometry=geometry,
    crs="EPSG:4326"
)

# Project to metric CRS
points = points.to_crs("EPSG:32644")

# --------------------------------------------------
# Load coastline and drainage data
# --------------------------------------------------


# Load all geographic layers
coastline = gpd.read_file(COASTLINE_PATH)
drainage = gpd.read_file(DRAINAGE_PATH)
stormwater = gpd.read_file(STORMWATER_PATH)

# Reproject to metric CRS
coastline = coastline.to_crs("EPSG:32644")
drainage = drainage.to_crs("EPSG:32644")
stormwater = stormwater.to_crs("EPSG:32644")

# Remove empty geometries
def clean_geometries(gdf):
    return gdf[
        gdf.geometry.notna()
        & ~gdf.geometry.is_empty
    ]

coastline = clean_geometries(coastline)
drainage = clean_geometries(drainage)
stormwater = clean_geometries(stormwater)

# Combine drainage layers
drainage_combined = pd.concat(
    [
        drainage[["geometry"]],
        stormwater[["geometry"]]
    ],
    ignore_index=True
)

# Combine geometries
coast_geometry = coastline.geometry.union_all()
drainage_geometry = drainage_combined.geometry.union_all()

# Calculate distances
print("Calculating coastline distances...")

points["distance_to_coast_m"] = (
    points.geometry.distance(coast_geometry)
)

print("Calculating drainage distances...")

points["distance_to_drainage_m"] = (
    points.geometry.distance(drainage_geometry)
)


# Remove geometry before saving CSV
points = points.drop(columns=["geometry"])

# --------------------------------------------------
# Save enhanced dataset
# --------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

points.to_csv(OUTPUT_PATH, index=False)

print("\nEnhanced features saved:")
print(OUTPUT_PATH)

print("\nNew feature statistics:")
print(
    points[
        [
            "distance_to_coast_m",
            "distance_to_drainage_m"
        ]
    ].describe()
)