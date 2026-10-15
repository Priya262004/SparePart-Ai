import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the spare-parts dataset
df = pd.read_csv("data/spare_parts.csv")

print("Loading AI search model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create descriptions for each spare part
descriptions = (
    "Part name: " + df["part_name"].astype(str)
    + ". Category: " + df["category"].astype(str)
    + ". Machine model: " + df["machine_model"].astype(str)
)

# Convert descriptions into numerical vectors
part_vectors = model.encode(
    descriptions.tolist(),
    normalize_embeddings=True
)

print("\n===== SparePart AI Semantic Search =====")
print("Example: I need a motor for my machine")
print("Type 'exit' to stop.")

while True:
    query = input("\nDescribe the spare part you need: ").strip()

    if query.lower() == "exit":
        print("Thank you for using SparePart AI!")
        break

    if not query:
        print("Please enter a search query.")
        continue

    # Convert the user's query into a vector
    query_vector = model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    # Calculate similarity scores
    scores = part_vectors @ query_vector

    # Find the three most relevant parts
    top_indices = scores.argsort()[::-1][:3]

    results = df.iloc[top_indices].copy()
    results["similarity"] = scores[top_indices].round(3)

    print("\n===== Search Results =====")

    print(
        results[
            [
                "part_id",
                "part_name",
                "machine_model",
                "stock",
                "location",
                "similarity",
            ]
        ].to_string(index=False)
    )

    print(
        "\nNote: Similarity indicates text relevance, "
        "not confirmed machine compatibility."
    )