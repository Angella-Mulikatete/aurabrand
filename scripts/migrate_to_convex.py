import chromadb
import os
from dotenv import load_dotenv
from convex import ConvexClient
from sentence_transformers import SentenceTransformer
import uuid

load_dotenv()

def migrate():
    print("🚀 Starting Migration from ChromaDB to Convex...")
    
    # 1. Connect to local ChromaDB
    persist_directory = "./data/brand_db"
    if not os.path.exists(persist_directory):
        print(f"❌ No local ChromaDB found at {persist_directory}. Nothing to migrate.")
        return

    chroma_client = chromadb.PersistentClient(path=persist_directory)
    try:
        collection = chroma_client.get_collection("brand_guidelines")
    except:
        print("❌ Collection 'brand_guidelines' not found in ChromaDB.")
        return

    # 2. Connect to Convex
    convex_url = os.getenv("CONVEX_URL")
    if not convex_url or "your-deployment-url" in convex_url:
        print("❌ CONVEX_URL not set in .env. Please provide a valid URL.")
        return
    
    convex_client = ConvexClient(convex_url)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Fetch all data from Chroma
    results = collection.get()
    ids = results['ids']
    documents = results['documents']
    metadatas = results['metadatas']

    if not ids:
        print("ℹ️ ChromaDB is empty. No data to migrate.")
        return

    print(f"📦 Found {len(ids)} guidelines in ChromaDB. Migrating...")

    # 4. Push to Convex
    for i in range(len(ids)):
        content = documents[i]
        category = metadatas[i].get('category', 'general')
        guideline_id = ids[i]
        
        print(f"  -> Migrating: {guideline_id}...")
        
        # Generate embedding locally
        embedding = embedder.encode(content).tolist()
        
        # Push to Convex
        convex_client.mutation("guidelines:add", {
            "id": guideline_id,
            "content": content,
            "category": category,
            "embedding": embedding
        })

    print(f"✅ Successfully migrated {len(ids)} items to Convex!")

if __name__ == "__main__":
    migrate()
