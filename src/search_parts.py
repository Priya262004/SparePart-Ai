import pandas as pd

df = pd.read_csv("data/spare_parts.csv")

print("=== SparePart AI Search ===")

query = input("Enter part name or machine model: ").strip().lower()

results = df[
    df["part_name"].str.lower().str.contains(query, na=False)
    | df["machine_model"].str.lower().str.contains(query, na=False)
]

if results.empty:
    print("No matching spare parts found.")
else:
    print("\nMatching spare parts:")
    print(results[[
        "part_id",
        "part_name",
        "machine_model",
        "stock",
        "location"
    ]].to_string(index=False))