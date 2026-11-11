
import pandas as pd
import matplotlib.pyplot as plt

# Load features
df = pd.read_csv("data/processed/features.csv")

# Create spatial plot
plt.figure(figsize=(10, 8))

scatter = plt.scatter(
    df["longitude"],
    df["latitude"],
    c=df["hazard_label"],
    cmap="RdYlBu_r",
    s=0.5,
    alpha=0.6
)

plt.colorbar(scatter, label="Hazard Label")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Spatial Distribution of High-Hazard Zones")

plt.tight_layout()

# Save image
plt.savefig(
    "data/processed/hazard_label_map.png",
    dpi=300
)

plt.show()