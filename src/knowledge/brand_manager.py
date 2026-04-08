import chromadb
from typing import List
from pydantic import BaseModel

class BrandGuideline(BaseModel):
    id: str
    content: str
    category: str  # e.g., 'tone', 'visuals', 'terminology'

class BrandManager:
    def __init__(self, persist_directory: str = "./data/brand_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="brand_guidelines",
            metadata={"hnsw:space": "cosine"}
        )

    def add_guideline(self, guideline: BrandGuideline):
        """Adds a specific brand guideline to the vector store."""
        self.collection.add(
            documents=[guideline.content],
            metadatas=[{"category": guideline.category}],
            ids=[guideline.id]
        )

    def get_guidelines(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieves relevant guidelines for a given query (e.g., a draft snippet)."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def clear_brand_data(self):
        """Resets the collection for a fresh start."""
        self.client.delete_collection("brand_guidelines")
        self.collection = self.client.get_or_create_collection("brand_guidelines")

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
