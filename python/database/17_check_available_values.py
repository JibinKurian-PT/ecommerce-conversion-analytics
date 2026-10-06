import pandas as pd
from pathlib import Path
PROJECT_DIR = Path(__file__).resolve().parents[2]

file_path = PROJECT_DIR / "data" / "processed" / "final_time_aware_events.csv"

print("Reading available column...")

df = pd.read_csv(
    file_path,
    usecols=["available"]
)

print("\nData type:")
print(df["available"].dtype)

print("\nUnique values:")
print(df["available"].value_counts(dropna=False).to_string())

print("\nMinimum:")
print(df["available"].min())

print("\nMaximum:")
print(df["available"].max())
