
import pandas as pd

path = "data/processed/features_enhanced.csv"

df = pd.read_csv(path)

print("Shape:", df.shape)

print("\nMissing values:")
print(df.isna().sum())

print("\nInfinite values:")
print(
    df.select_dtypes(include="number")
    .isin([float("inf"), float("-inf")])
    .sum()
)

new_features = [
    "distance_to_coast_m",
    "distance_to_drainage_m"
]

print("\nNew feature statistics:")
print(df[new_features].describe())

print("\nLabel distribution:")
print(df["hazard_label"].value_counts(normalize=True))

print("\nData types:")
print(df.dtypes)