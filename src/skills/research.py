import os
from typing import List
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def research_skill(query: str, depth: int = 1) -> List[str]:
    """
    Real-world research skill using Tavily.
    """
    print(f"--- [Skill: Researching '{query}' via Tavily (Depth: {depth})] ---")
    
    try:
        # Perform search
        search_result = tavily.search(query=query, search_depth="advanced" if depth > 1 else "basic")
        
        # Extract snippets
        facts = [
            f"Source: {res['url']} - {res['content'][:500]}"
            for res in search_result['results']
        ]
        
        return facts
    except Exception as e:
        print(f"Research failed: {e}")
        return [f"Failed to conduct research on {query}."]
