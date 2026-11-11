
import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    f1_score
)

# Load dataset
df = pd.read_csv("data/processed/features.csv")

features = [
    "elevation_m",
    "slope_degrees",
    "rainfall_mm"
]

X = df[features]
y = df["hazard_label"]

# Create spatial groups
grid_size = 0.02

groups = (
    (df["longitude"] / grid_size).astype(int).astype(str)
    + "_"
    + (df["latitude"] / grid_size).astype(int).astype(str)
)

# --------------------------------------------------
# 1. Spatial split: 60% train, 40% temporary
# --------------------------------------------------

splitter_1 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.40,
    random_state=42
)

train_idx, temp_idx = next(
    splitter_1.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
y_train = y.iloc[train_idx]

X_temp = X.iloc[temp_idx]
y_temp = y.iloc[temp_idx]
groups_temp = groups.iloc[temp_idx]

# --------------------------------------------------
# 2. Spatial split: 20% validation, 20% test
# --------------------------------------------------

splitter_2 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.50,
    random_state=42
)

val_relative_idx, test_relative_idx = next(
    splitter_2.split(
        X_temp,
        y_temp,
        groups=groups_temp
    )
)

X_val = X_temp.iloc[val_relative_idx]
y_val = y_temp.iloc[val_relative_idx]

X_test = X_temp.iloc[test_relative_idx]
y_test = y_temp.iloc[test_relative_idx]

print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))
print("Testing samples:", len(X_test))

# --------------------------------------------------
# 3. Train Random Forest
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=20,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# --------------------------------------------------
# 4. Select threshold using validation set
# --------------------------------------------------

val_prob = model.predict_proba(X_val)[:, 1]

thresholds = np.arange(0.10, 0.91, 0.05)

best_threshold = 0.50
best_f1 = 0.0

print("\nValidation threshold results:")

for threshold in thresholds:
    val_pred = (val_prob >= threshold).astype(int)
    score = f1_score(y_val, val_pred, zero_division=0)

    print(
        f"Threshold: {threshold:.2f} | "
        f"F1-score: {score:.4f}"
    )

    if score > best_f1:
        best_f1 = score
        best_threshold = threshold

print("\nSelected threshold:", best_threshold)
print("Validation F1-score:", best_f1)

# --------------------------------------------------
# 5. Evaluate on untouched test set
# --------------------------------------------------

test_prob = model.predict_proba(X_test)[:, 1]
test_pred = (test_prob >= best_threshold).astype(int)

print("\nTest Classification Report:")
print(classification_report(
    y_test,
    test_pred,
    zero_division=0
))

print("Test Confusion Matrix:")
print(confusion_matrix(y_test, test_pred))

print(
    "Test ROC-AUC:",
    roc_auc_score(y_test, test_prob)
)

print(
    "Test PR-AUC:",
    average_precision_score(y_test, test_prob)
)

# --------------------------------------------------
# 6. Feature importance
# --------------------------------------------------

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFeature Importance:")
print(importance)

# --------------------------------------------------
# 7. Save model and threshold
# --------------------------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/random_forest_baseline.pkl"
)

with open(
    "models/random_forest_threshold.json",
    "w"
) as file:
    json.dump(
        {"threshold": float(best_threshold)},
        file,
        indent=4
    )

print("\nModel and threshold saved successfully.")