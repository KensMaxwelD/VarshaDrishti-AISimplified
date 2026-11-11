# import os
# import pandas as pd
# import geopandas as gpd
# from fiona.drvsupport import supported_drivers

# # Enable KML driver support in Fiona
# supported_drivers['KML'] = 'rw'

# # Define input directory (update this to match where your raw downloads are)
# input_dir = "data/raw/geospatial" 
# output_dir = "data/raw/geospatial"
# os.makedirs(output_dir, exist_ok=True)

# print("⚡ Starting geospatial data pre-processing for Chennai Flood Inundation System...")

# # ==========================================
# # 1. CLEAN & CLIP THE MASSIVE COASTLINE
# # ==========================================
# print("🌊 Processing coastline data...")
# try:
#     # Load the 32MB state-wide CRZ file
#     state_crz = gpd.read_file(os.path.join(input_dir, "chennai_costal.geojson"))
    
#     # Define a robust bounding box for Chennai & surrounding areas (Tiruvallur to Chengalpattu)
#     # Bounding box covers roughly from Pulicat Lake (North) down to Mahabalipuram (South)
#     min_lon, min_lat = 80.10, 12.50
#     max_lon, max_lat = 80.35, 13.40
    
#     # Clip the dataset to just the Chennai region to strip away the rest of Tamil Nadu
#     chennai_coastline = state_crz.cx[min_lon:max_lon, min_lat:max_lat]
    
#     # Save the lean, optimized coastline file
#     chennai_coastline.to_file(os.path.join(output_dir, "coastline.geojson"), driver="GeoJSON")
#     print(f"✅ Coastline successfully clipped and saved to {output_dir}/coastline.geojson")
# except Exception as e:
#     print(f"❌ Error processing coastline: {e}")


# # ==========================================
# # 2. CONVERT & MERGE THE DRAINAGE LAYERS
# # ==========================================
# print("💧 Processing and merging drainage network...")

# # Define the drainage maps you want to merge into your major/minor systems
# # We exclude micro_drains/stormwater from the major network to avoid memory bloat
# major_kml_files = [
#     "chennai_basin_rivers.kml",
#     "chennai_basin_buckingham.kml",
#     "chennai_macro_drain.kml"
# ]

# gdfs = []
# for file_name in major_kml_files:
#     file_path = os.path.join(input_dir, file_name)
#     if os.path.exists(file_path):
#         try:
#             print(f"-> Reading {file_name}...")
#             gdf = gpd.read_file(file_path, driver='KML')
#             # Retain only standard identifying properties to clean metadata
#             if 'Name' in gdf.columns:
#                 gdf = gdf[['Name', 'geometry']]
#             gdfs.append(gdf)
#         except Exception as e:
#             print(f"⚠️ Could not read {file_name}: {e}")

# if gdfs:
#     # Combine the river channels, canals, and macro infrastructure into a single system
#     combined_drainage = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
#     # Force output system coordinates to standard WGS84 for broad compatibility
#     combined_drainage = combined_drainage.set_crs("EPSG:4326", allow_override=True)
    
#     # Save directly to your target directory
#     combined_drainage.to_file(os.path.join(output_dir, "drainage.geojson"), driver="GeoJSON")
#     print(f"✅ Combined drainage grid saved to {output_dir}/drainage.geojson")
# else:
#     print("❌ No valid drainage KML files were processed.")

# # ==========================================
# # 3. EXTRA: OPTIMIZE STREET STORMWATER DRAINS (Optional separate layer)
# # ==========================================
# # Note: chennai_stormwater_drain.kml is 27MB. Keep it separate so your main map doesn't lag!
# stormwater_path = os.path.join(input_dir, "chennai_stormwater_drain.kml")
# if os.path.exists(stormwater_path):
#     print("🔧 Converting large stormwater street grid to GeoJSON...")
#     try:
#         sw_gdf = gpd.read_file(stormwater_path, driver='KML')
#         sw_gdf.to_file(os.path.join(output_dir, "stormwater_streets.geojson"), driver="GeoJSON")
#         print(f"✅ Street stormwater drains saved to {output_dir}/stormwater_streets.geojson")
#     except Exception as e:
#         print(f"⚠️ Error processing street drains: {e}")

# print("\n🚀 All structural vectors are formatted and stored in data/raw/geospatial/!")


import os
import re
import geopandas as gpd
from shapely.geometry import LineString

input_dir = "data/raw/geospatial"
output_dir = "data/raw/geospatial"
sw_kml_path = os.path.join(input_dir, "chennai_stormwater_drain.kml")
output_geojson_path = os.path.join(output_dir, "stormwater_streets.geojson")

print("⚡ Initializing raw text coordinate harvester for street drains...")

# Compiled regular expression to pull anything inside coordinate text blocks
coord_block_regex = re.compile(r'<coordinates>(.*?)</coordinates>', re.DOTALL)

features = []
line_counter = 0

try:
    with open(sw_kml_path, 'r', encoding='utf-8', errors='ignore') as f:
        kml_content = f.read()
    
    # Extract all text blocks nested inside <coordinates> blocks
    coordinate_blocks = coord_block_regex.findall(kml_content)
    print(f"🔄 Found {len(coordinate_blocks)} raw coordinate arrays. Processing lines...")

    for block in coordinate_blocks:
        # Split text by spaces, tabs, or newlines to find discrete coordinate groups
        points_text = block.strip().split()
        valid_coords = []
        
        for pt in points_text:
            try:
                # KML standard is Longitude,Latitude,Elevation
                parts = [float(x) for x in pt.split(',')]
                if len(parts) >= 2:
                    # Append as (longitude, latitude) tuple
                    valid_coords.append((parts[0], parts[1]))
            except ValueError:
                # Silently drops truncated numbers or malformed strings at the EOF
                continue
        
        # A drainage pipe section needs at least 2 connected points (a start and an end node)
        if len(valid_coords) >= 2:
            line_counter += 1
            features.append({
                'type': 'Feature',
                'geometry': LineString(valid_coords),
                'properties': {
                    'id': f'SWD_{line_counter}',
                    'layer': 'Stormwater_Street_Network'
                }
            })

    # Save to your structured workspace directory
    if features:
        sw_gdf = gpd.GeoDataFrame.from_features(features)
        sw_gdf = sw_gdf.set_crs("EPSG:4326")
        
        os.makedirs(output_dir, exist_ok=True)
        sw_gdf.to_file(output_geojson_path, driver="GeoJSON")
        print(f"✅ Success! Fixed {line_counter} street line segments and saved to:")
        print(f"   {output_geojson_path}")
    else:
        print("❌ Could not harvest any coordinate strings from the text file structure.")

except Exception as e:
    print(f"❌ Error during raw text parsing: {e}")
