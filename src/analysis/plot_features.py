
import pandas as pd
import matplotlib.pyplot as plt

INPUT_PATH = "data/processed/features.csv"
OUTPUT_PATH = "data/processed/feature_distributions.png"

df = pd.read_csv(INPUT_PATH)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

df["elevation_m"].hist(ax=axes[0], bins=50)
axes[0].set_title("Elevation Distribution")
axes[0].set_xlabel("Elevation (m)")

df["slope_degrees"].hist(ax=axes[1], bins=50)
axes[1].set_title("Slope Distribution")
axes[1].set_xlabel("Slope (degrees)")

df["rainfall_mm"].hist(ax=axes[2], bins=50)
axes[2].set_title("Rainfall Distribution")
axes[2].set_xlabel("Rainfall (mm)")

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150)
plt.close()

print(f"Saved: {OUTPUT_PATH}")