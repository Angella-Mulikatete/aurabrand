import os
import json
import time
import math
import csv
from datetime import datetime
from typing import List, Dict

# Ensure local imports work
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import create_brand_graph
from src.state import BrandContext, AgentState
from src.knowledge.brand_manager import BrandManager
from src.factory import get_model_with_fallback
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from scipy.spatial.distance import cosine

BENCHMARKS_DIR = "docs/benchmarks"
REPORT_FILE = "benchmark_report.tsv"

def load_benchmarks() -> List[Dict]:
    benchmarks = []
    if not os.path.exists(BENCHMARKS_DIR):
        print(f"Error: {BENCHMARKS_DIR} not found.")
        return []
    
    for filename in os.listdir(BENCHMARKS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(BENCHMARKS_DIR, filename), "r") as f:
                benchmarks.append(json.load(f))
    return benchmarks

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates similarity between two texts. Falls back to word overlap if embeddings fail."""
    print("Calculating similarity...")
    try:
        # Try Google Embeddings
        embedder = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
        v1 = embedder.embed_query(text1)
        v2 = embedder.embed_query(text2)
        return 1.0 - cosine(v1, v2)
    except Exception as e:
        print(f"Embedding failed ({e}). Falling back to word overlap.")
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        return len(intersection) / max(len(words1), len(words2))

def run_benchmark(benchmark: Dict):
    print(f"--- Running Benchmark: {benchmark['name']} ---")
    
    print("Compiling brand graph...")
    brand_graph = create_brand_graph()
    
    # Initialize brand context based on benchmark
    print("Preparing context...")
    context = BrandContext(
        name="BenchmarkBrand",
        tone=benchmark.get("target_tone", "professional"),
        guidelines="Follow the provided gold standard style.",
        forbidden_terms=benchmark.get("forbidden_terms", [])
    )
    
    initial_state: AgentState = {
        "user_request": benchmark["request"],
        "brand_context": context,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 2, # Keep it low for benchmarks
        "final_document": None,
        "output_files": []
    }
    
    print("Invoking graph...")
    t0 = time.time()
    final_state = brand_graph.invoke(initial_state)
    t1 = time.time()
    print(f"Graph execution took {t1 - t0:.1f}s")
    
    final_text = final_state.get("final_document", "")
    feedbacks = final_state.get("feedback_history", [])
    
    # Primary Metric: Brand Guardian Score
    guardian_score = feedbacks[-1].score if feedbacks else 0.0
    
    # Secondary Metric: Semantic Similarity to Gold Standard
    similarity = calculate_similarity(final_text, benchmark["gold_standard"])
    
    # Knowledge stats
    bm = BrandManager()
    knowledge_count = bm.get_count()
    
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark_name": benchmark["name"],
        "guardian_score": f"{guardian_score:.4f}",
        "similarity": f"{similarity:.4f}",
        "knowledge_count": knowledge_count,
        "duration_sec": f"{t1 - t0:.1f}",
        "status": "PASS" if guardian_score > 0.8 else "FAIL"
    }
    
    return result

def main():
    print("AuraBrand Benchmark Suite Starting...")
    benchmarks = load_benchmarks()
    
    if not benchmarks:
        print("No benchmarks found. Exiting.")
        return
    
    results = []
    for bm in benchmarks:
        try:
            res = run_benchmark(bm)
            results.append(res)
        except Exception as e:
            print(f"Benchmark {bm['name']} failed with error: {e}")
    
    # Write to TSV
    if not results:
        print("No results to log. Benchmarks might have failed.")
        return

    file_exists = os.path.isfile(REPORT_FILE)
    with open(REPORT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter="\t")
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)
    
    print(f"\nBenchmarking complete. Results logged to {REPORT_FILE}")

if __name__ == "__main__":
    main()
