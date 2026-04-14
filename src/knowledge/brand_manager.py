import os
from typing import List
from pydantic import BaseModel
from convex import ConvexClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np

class BrandGuideline(BaseModel):
    id: str
    content: str
    category: str  # e.g., 'tone', 'visuals', 'terminology'

class BrandManager:
    def __init__(self, persist_directory: str = "./data/brand_db"):
        self.provider = os.getenv("VECTOR_DB_PROVIDER", "convex")
        
        if self.provider == "convex":
            self.convex_url = os.getenv("CONVEX_URL")
            self.client = ConvexClient(self.convex_url)
            # Using the fully qualified model name for better toolchain compatibility
            self.embedder = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        else:
            raise NotImplementedError("Local ChromaDB has been removed to reduce bundle size. Please use Convex DB.")

    def add_guideline(self, guideline: BrandGuideline):
        """Adds a specific brand guideline to the vector store."""
        if self.provider == "convex":
            try:
                embedding = self.embedder.embed_query(guideline.content)
                self.client.mutation("guidelines:add", {
                    "id": guideline.id,
                    "content": guideline.content,
                    "category": guideline.category,
                    "embedding": embedding
                })
            except Exception as e:
                print(f"BrandManager Storage Failed: {e}")
        else:
            pass

    def get_guidelines(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieves relevant guidelines for a given query (e.g., a draft snippet)."""
        if self.provider == "convex":
            try:
                embedding = self.embedder.embed_query(query)
                results = self.client.action("actions:vectorSearch", {
                    "embedding": embedding,
                    "limit": n_results
                })
                return [r["content"] for r in results]
            except Exception as e:
                print(f"BrandManager Retrieval Failed: {e}")
                return []
        else:
            return []

    def clear_brand_data(self):
        """Resets the collection for a fresh start."""
        if self.provider == "convex":
            self.client.mutation("guidelines:clearAll")
        else:
            pass

    def get_count(self) -> int:
        """Returns the number of guidelines in the store."""
        if self.provider == "convex":
            return self.client.query("guidelines:count")
        else:
            return 0

    def get_knowledge_stats(self) -> dict:
        """Returns detailed statistics about learned knowledge."""
        if self.provider == "convex":
            counts = self.client.query("guidelines:getCategoryCounts") or {}
            total = sum(counts.values())
            return {
                "total": total,
                "categories": counts
            }
        return {"total": 0, "categories": {}}

    def get_visuals(self) -> dict:
        """Retrieves visual brand identity from Convex."""
        if self.provider == "convex":
            try:
                return self.client.query("visuals:get") or {}
            except:
                return {}
        return {}

    def update_visuals(self, visuals: dict):
        """Updates visual brand identity in Convex."""
        if self.provider == "convex":
            self.client.mutation("visuals:update", visuals)

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
