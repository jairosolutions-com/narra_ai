import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Initialize the sentence-transformers model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define the index name and dimension
index_name = "narra"
dimension = 384  # Make sure this matches the embedding model's output dimension

# Only create the index if it doesn't already exist
if index_name not in pc.list_indexes().names():
    # Create the index with the correct dimension and supported region (AWS us-east-1)
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",  # Choose a suitable metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",  # AWS us-east-1 region as per free plan support
        ),
    )
    print(f"Created index '{index_name}' with dimension {dimension}")

# Connect to the index
index = pc.Index(index_name)


# Function to generate embeddings
def get_embedding(text):
    embedding = embedding_model.encode(text)
    return embedding.tolist()  # Convert to list for JSON serialization


# Example data to upsert
responses = [
    {"id": "1", "text": "Hello! How can I assist you today?"},
    {"id": "2", "text": "Goodbye! Have a wonderful day!"},
    {"id": "3", "text": "I'm here to help you with any questions you may have."},
]

# Upsert data into the index
for item in responses:
    embedding = get_embedding(item["text"])
    index.upsert([(item["id"], embedding, {"text": item["text"]})])
    print(f"Upserted item with ID {item['id']}")


# Define a function to store embeddings in the Pinecone index
def store_embedding(item_id, embedding):
    # Upsert the embedding to the index with the given ID
    index.upsert([(item_id, embedding)])


# Function to query Pinecone for the most similar response
def get_similar_response(query_text):
    # Generate embedding for the query text
    query_embedding = get_embedding(query_text)

    # Query Pinecone for the closest match
    result = index.query(vector=query_embedding, top_k=1, include_metadata=True)

    # Check if any matches were found and return the best match's response
    if result["matches"]:
        best_match = result["matches"][0]
        return best_match["metadata"].get("text", "No suitable response found.")
    else:
        return "I'm not sure how to respond to that."
