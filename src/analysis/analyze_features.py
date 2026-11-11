
import pandas as pd

INPUT_PATH = "data/processed/features.csv"

df = pd.read_csv(INPUT_PATH)

print("\n--- Dataset Information ---")
print(df.info())

print("\n--- Statistical Summary ---")
print(df.describe())

print("\n--- Missing Values ---")
print(df.isnull().sum())

print("\n--- Correlations ---")
print(df.corr(numeric_only=True).round(3))