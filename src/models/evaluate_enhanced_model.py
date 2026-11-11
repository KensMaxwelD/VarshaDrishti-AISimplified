
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
    f1_score,
    precision_score,
    recall_score
)

# Load data
df = pd.read_csv(
    "data/processed/features_enhanced.csv"
)

features = [
    "elevation_m",
    "slope_degrees",
    "rainfall_mm",
    "distance_to_coast_m",
    "distance_to_drainage_m"
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
# 1. Train / validation / test split
# --------------------------------------------------

splitter_1 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.40,
    random_state=42
)

train_idx, temp_idx = next(
    splitter_1.split(X, y, groups=groups)
)

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

X_train = X.iloc[train_idx]
y_train = y.iloc[train_idx]

X_val = X.iloc[val_idx]
y_val = y.iloc[val_idx]

X_test = X.iloc[test_idx]
y_test = y.iloc[test_idx]

print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))
print("Testing samples:", len(X_test))

# --------------------------------------------------
# 2. Train model
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
# 3. Select threshold using validation set
# --------------------------------------------------

val_prob = model.predict_proba(X_val)[:, 1]

thresholds = np.arange(0.05, 0.91, 0.05)

best_threshold = 0.50
best_f1 = -1

print("\nValidation threshold results:")

for threshold in thresholds:
    val_pred = (
        val_prob >= threshold
    ).astype(int)

    precision = precision_score(
        y_val,
        val_pred,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        val_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        val_pred,
        zero_division=0
    )

    print(
        f"Threshold: {threshold:.2f} | "
        f"Precision: {precision:.3f} | "
        f"Recall: {recall:.3f} | "
        f"F1: {f1:.3f}"
    )

    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

print("\nSelected threshold:", best_threshold)
print("Validation F1-score:", best_f1)

# --------------------------------------------------
# 4. Evaluate on test set
# --------------------------------------------------

test_prob = model.predict_proba(X_test)[:, 1]

test_pred = (
    test_prob >= best_threshold
).astype(int)

print("\nTest Classification Report:")
print(classification_report(
    y_test,
    test_pred,
    zero_division=0
))

print("Test Confusion Matrix:")
print(confusion_matrix(y_test, test_pred))

print(
    "\nTest ROC-AUC:",
    roc_auc_score(y_test, test_prob)
)

print(
    "Test PR-AUC:",
    average_precision_score(y_test, test_prob)
)

# --------------------------------------------------
# 5. Feature importance
# --------------------------------------------------

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFeature Importance:")
print(importance)

# --------------------------------------------------
# 6. Save model and threshold
# --------------------------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/random_forest_enhanced_three_way.pkl"
)

with open(
    "models/enhanced_model_threshold.json",
    "w"
) as file:
    json.dump(
        {"threshold": float(best_threshold)},
        file,
        indent=4
    )

print("\nModel and threshold saved successfully.")