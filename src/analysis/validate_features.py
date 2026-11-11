import pandas as pd

path = "data/processed/features.csv"

df = pd.read_csv(path)

print("Shape:", df.shape)
print("\nMissing values:")
print(df.isna().sum())

print("\nData types:")
print(df.dtypes)

print("\nLabel distribution:")
print(df["hazard_label"].value_counts(normalize=True))

print("\nCoordinates:")
print("Longitude:", df["longitude"].min(), "to", df["longitude"].max())
print("Latitude:", df["latitude"].min(), "to", df["latitude"].max())

print("\nFeature statistics:")
print(df.describe())