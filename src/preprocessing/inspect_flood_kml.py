from pathlib import Path
import geopandas as gpd

path = Path("data/raw/chennai_flood_hazard_zones.kml")

gdf = gpd.read_file(path, driver="KML")

print("Number of features:", len(gdf))
print("CRS:", gdf.crs)
print("Columns:", list(gdf.columns))
print("\nFirst rows:")
print(gdf.head())

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\nHazard categories:")
print(gdf["CATEGORY"].value_counts(dropna=False))

print("\nKML bounds:")
print(gdf.total_bounds)