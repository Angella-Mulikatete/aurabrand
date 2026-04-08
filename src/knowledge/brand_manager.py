import chromadb
import os
from typing import List
from pydantic import BaseModel
from convex import ConvexClient
from sentence_transformers import SentenceTransformer
import numpy as np

class BrandGuideline(BaseModel):
    id: str
    content: str
    category: str  # e.g., 'tone', 'visuals', 'terminology'

class BrandManager:
    def __init__(self, persist_directory: str = "./data/brand_db"):
        self.provider = os.getenv("VECTOR_DB_PROVIDER", "chroma")
        
        if self.provider == "convex":
            self.convex_url = os.getenv("CONVEX_URL")
            self.client = ConvexClient(self.convex_url)
            # We use a local embedding model for now to keep it consistent
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.chroma_client.get_or_create_collection(
                name="brand_guidelines",
                metadata={"hnsw:space": "cosine"}
            )

    def add_guideline(self, guideline: BrandGuideline):
        """Adds a specific brand guideline to the vector store."""
        if self.provider == "convex":
            embedding = self.embedder.encode(guideline.content).tolist()
            self.client.mutation("guidelines:add", {
                "id": guideline.id,
                "content": guideline.content,
                "category": guideline.category,
                "embedding": embedding
            })
        else:
            self.collection.add(
                documents=[guideline.content],
                metadatas=[{"category": guideline.category}],
                ids=[guideline.id]
            )

    def get_guidelines(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieves relevant guidelines for a given query (e.g., a draft snippet)."""
        if self.provider == "convex":
            embedding = self.embedder.encode(query).tolist()
            results = self.client.action("actions:vectorSearch", {
                "embedding": embedding,
                "limit": n_results
            })
            return [r["content"] for r in results]
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []

    def clear_brand_data(self):
        """Resets the collection for a fresh start."""
        if self.provider == "convex":
            self.client.mutation("guidelines:clearAll")
        else:
            try:
                self.chroma_client.delete_collection("brand_guidelines")
            except:
                pass
            self.collection = self.chroma_client.get_or_create_collection("brand_guidelines")

    def get_count(self) -> int:
        """Returns the number of guidelines in the store."""
        if self.provider == "convex":
            return self.client.query("guidelines:count")
        else:
            return self.collection.count()

if __name__ == "__main__":
    # Quick test
    bm = BrandManager()
    bm.add_guideline(BrandGuideline(
        id="tone_1", 
        content="Our brand is innovative but avoids jargon and marketing fluff.",
        category="tone"
    ))
    relevant = bm.get_guidelines("How should we explain our new AI feature?")
    print(f"Relevant guidelines: {relevant}")
