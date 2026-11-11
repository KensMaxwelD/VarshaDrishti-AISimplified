
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report
)

df = pd.read_csv("data/processed/features.csv")

features = [
    "elevation_m",
    "slope_degrees",
    "rainfall_mm"
]

X = df[features]
y = df["hazard_label"]

# Random stratified split - diagnostic only
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=20,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTest ROC-AUC:", roc_auc_score(y_test, y_prob))
print("Test PR-AUC:", average_precision_score(y_test, y_prob))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))