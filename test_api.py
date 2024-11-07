import os
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Test the API key by listing existing indexes
try:
    indexes = pc.list_indexes().names()
    print("Your Pinecone API key is working.")
    print("Available indexes:", indexes)
except Exception as e:
    print("Error:", e)
