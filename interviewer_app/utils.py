# interviewer_app/utils.py
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from .models import UserProfile
from django.shortcuts import get_object_or_404

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define the index name and dimension
index_name = "narra-intake-questions"
dimension = 384  # Ensure this matches your embedding model's output dimension

# Only create the index if it doesn't already exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  # or "gcp" depending on your Pinecone plan
            region="us-east-1",  # Choose a region supported by your plan
        ),
    )
    print(f"Created index '{index_name}' with dimension {dimension}")

# Connect to the index
index = pc.Index(index_name)

# Initialize the sentence-transformers model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_profile_embedding(user_id):
    """Combine UserProfile data into a single text and generate an embedding."""
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    profile_text = user_profile.get_profile_text()
    embedding = embedding_model.encode(profile_text).tolist()
    return embedding, user_profile.full_name


def upsert_user_profile_to_index(user_id):
    """Upsert the UserProfile embedding into the Pinecone index with all profile fields as metadata."""
    # Retrieve the user profile data
    user_profile = get_object_or_404(UserProfile, user_id=user_id)

    # Combine profile data into a single text
    profile_text = (
        user_profile.get_profile_text()
    )  # Ensure get_profile_text method combines all fields for embedding

    # Generate an embedding for the combined text
    embedding = embedding_model.encode(profile_text).tolist()

    # Prepare metadata with all UserProfile fields
    metadata = {
        "full_name": user_profile.full_name,
        "maiden_name": user_profile.maiden_name,
        "previous_name": user_profile.previous_name,
        "birthday": str(user_profile.birthday) if user_profile.birthday else "",
        "birth_place": user_profile.birth_place,
        "grew_up_in": user_profile.grew_up_in,
    }

    # Upsert the embedding into Pinecone with metadata
    index.upsert([(str(user_id), embedding, metadata)])
    print(f"Upserted profile for user_id {user_id} into Pinecone.")


def store_embedding(item_id, embedding):
    """Store the embedding in the Pinecone index with a specific item ID."""
    index.upsert([(item_id, embedding)])


def get_embedding(text):
    """Generate embedding for a given text using the embedding model."""
    return embedding_model.encode(text).tolist()


def get_similar_response(query_text):
    """Query Pinecone for the most similar response based on query_text."""
    query_embedding = get_embedding(query_text)
    result = index.query(vector=query_embedding, top_k=1, include_metadata=True)

    if result["matches"]:
        best_match = result["matches"][0]
        return best_match["metadata"].get("text", "No suitable response found.")
    else:
        return "I'm not sure how to respond to that."
