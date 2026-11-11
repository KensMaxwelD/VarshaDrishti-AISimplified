
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score
)

# Load enhanced dataset
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

# Spatial groups
grid_size = 0.02

groups = (
    (df["longitude"] / grid_size).astype(int).astype(str)
    + "_"
    + (df["latitude"] / grid_size).astype(int).astype(str)
)

# Spatial train/test split
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Train model
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=20,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Predictions
y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

# Evaluation
print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print(
    "\nROC-AUC:",
    roc_auc_score(y_test, y_prob)
)

print(
    "PR-AUC:",
    average_precision_score(y_test, y_prob)
)

# Feature importance
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFeature Importance:")
print(importance)

# Save model
os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/random_forest_enhanced.pkl"
)

print("\nEnhanced model saved successfully.")