
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

df = pd.read_csv("data/processed/features.csv")

grid_size = 0.02

groups = (
    (df["longitude"] / grid_size).astype(int).astype(str)
    + "_"
    + (df["latitude"] / grid_size).astype(int).astype(str)
)

X = df[["elevation_m", "slope_degrees", "rainfall_mm"]]
y = df["hazard_label"]

# First split
splitter_1 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.40,
    random_state=42
)

train_idx, temp_idx = next(
    splitter_1.split(X, y, groups=groups)
)

# Second split
splitter_2 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.50,
    random_state=42
)

val_relative_idx, test_relative_idx = next(
    splitter_2.split(
        X.iloc[temp_idx],
        y.iloc[temp_idx],
        groups=groups.iloc[temp_idx]
    )
)

val_idx = temp_idx[val_relative_idx]
test_idx = temp_idx[test_relative_idx]

# Compare label distributions
splits = {
    "Train": train_idx,
    "Validation": val_idx,
    "Test": test_idx
}

for name, indices in splits.items():
    subset = df.iloc[indices]

    print(f"\n{name}")
    print("Samples:", len(subset))
    print("Positive labels:", int(subset["hazard_label"].sum()))
    print(
        "Positive percentage:",
        round(subset["hazard_label"].mean() * 100, 2),
        "%"
    )

    print("Longitude range:")
    print(
        round(subset["longitude"].min(), 4),
        "to",
        round(subset["longitude"].max(), 4)
    )

    print("Latitude range:")
    print(
        round(subset["latitude"].min(), 4),
        "to",
        round(subset["latitude"].max(), 4)
    )