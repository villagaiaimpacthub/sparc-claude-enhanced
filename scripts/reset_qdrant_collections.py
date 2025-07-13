#!/usr/bin/env python3
"""
Reset Qdrant Collections for Mistral Embeddings
Recreates all collections with the correct 1024-dimensional vectors for Mistral
"""

import os
import sys
from pathlib import Path

# Add lib to path
lib_path = Path(__file__).parent.parent / "lib"
sys.path.insert(0, str(lib_path))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams
    from dotenv import load_dotenv
    from rich.console import Console
    from rich.progress import Progress
    from mistral_embeddings import MistralEmbeddings
except ImportError as e:
    print(f"Missing required packages: {e}")
    sys.exit(1)

console = Console()
load_dotenv()

async def reset_collections():
    """Reset all Qdrant collections for Mistral embeddings"""
    console.print("🔄 [bold blue]Resetting Qdrant Collections for Mistral[/bold blue]")
    
    # Connect to Qdrant
    qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port = int(os.getenv('QDRANT_PORT', '6336'))
    
    qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=30)
    console.print(f"✅ Connected to Qdrant at {qdrant_host}:{qdrant_port}")
    
    # Get Mistral embedding dimension
    mistral_embeddings = MistralEmbeddings()
    vector_size = mistral_embeddings.get_embedding_dimension()
    console.print(f"📏 Mistral embedding dimension: {vector_size}")
    
    collections = [
        "agent_memories",
        "project_patterns", 
        "verification_outcomes",
        "code_snippets",
        "test_patterns",
        "architecture_patterns",
        "user_interactions",
        "cross_project_insights"
    ]
    
    with Progress() as progress:
        task = progress.add_task("Resetting collections...", total=len(collections))
        
        for collection_name in collections:
            try:
                # Delete existing collection
                try:
                    qdrant_client.delete_collection(collection_name)
                    console.print(f"🗑️ Deleted existing collection: {collection_name}")
                except Exception:
                    console.print(f"ℹ️ Collection {collection_name} didn't exist")
                
                # Create new collection with correct dimensions
                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                console.print(f"✅ Created collection: {collection_name}")
                
                progress.advance(task)
                
            except Exception as e:
                console.print(f"❌ Failed to reset collection {collection_name}: {e}")
                raise
    
    console.print("✅ [bold green]All collections reset for Mistral embeddings![/bold green]")

if __name__ == "__main__":
    import asyncio
    asyncio.run(reset_collections())