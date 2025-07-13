#!/usr/bin/env python3
"""
Test Mistral-enabled SPARC memory system
"""

import asyncio
import os
from pathlib import Path
import sys

# Add lib to path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

from dotenv import load_dotenv
from rich.console import Console
from mistral_embeddings import MistralEmbeddings

load_dotenv()
console = Console()

async def test_mistral_memory_integration():
    """Test the complete Mistral + Qdrant memory system"""
    
    console.print("🧪 [bold blue]Testing Mistral Memory Integration[/bold blue]")
    
    # Test 1: Mistral embeddings
    console.print("1️⃣ Testing Mistral embeddings...")
    mistral = MistralEmbeddings()
    
    test_texts = [
        "React component with useState hook",
        "FastAPI endpoint with authentication",
        "Database migration script for users table",
        "SPARC autonomous development workflow"
    ]
    
    embeddings = await mistral.get_embeddings(test_texts)
    console.print(f"✅ Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
    
    # Test 2: Semantic similarity
    console.print("2️⃣ Testing semantic similarity...")
    similar_query = "React hook component"
    query_embedding = await mistral.get_embedding(similar_query)
    
    # Calculate cosine similarity with first text
    import numpy as np
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    similarity = cosine_similarity(query_embedding, embeddings[0])
    console.print(f"✅ Similarity between '{similar_query}' and '{test_texts[0]}': {similarity:.3f}")
    
    # Test 3: Qdrant integration
    console.print("3️⃣ Testing Qdrant integration...")
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    
    qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port = int(os.getenv('QDRANT_PORT', '6336'))
    
    qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
    
    # Store test embedding in code_snippets collection
    test_point = models.PointStruct(
        id=999999,  # Test ID
        vector=embeddings[0],
        payload={
            "content": test_texts[0],
            "type": "test_pattern",
            "language": "javascript",
            "framework": "react"
        }
    )
    
    qdrant.upsert(
        collection_name="code_snippets",
        points=[test_point]
    )
    console.print("✅ Stored test embedding in Qdrant")
    
    # Test semantic search
    search_results = qdrant.search(
        collection_name="code_snippets",
        query_vector=query_embedding,
        limit=3
    )
    
    console.print(f"✅ Found {len(search_results)} similar patterns")
    for i, result in enumerate(search_results):
        console.print(f"   {i+1}. Score: {result.score:.3f} - {result.payload.get('content', 'N/A')[:50]}...")
    
    # Cleanup
    qdrant.delete(
        collection_name="code_snippets",
        points_selector=models.PointIdsList(points=[999999])
    )
    
    console.print("🎉 [bold green]Mistral memory integration test successful![/bold green]")

if __name__ == "__main__":
    asyncio.run(test_mistral_memory_integration())