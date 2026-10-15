import pandas as pd

df = pd.read_csv("data/spare_parts.csv")

print("SparePart AI Dataset")
print(df)

print("\nTotal parts:", len(df))

print("\nOut-of-stock parts:")
print(df[df["stock"] == 0][["part_id", "part_name"]])