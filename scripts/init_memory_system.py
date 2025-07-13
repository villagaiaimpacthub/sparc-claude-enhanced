#!/usr/bin/env python3
"""
Real Memory System Initialization Script
Sets up Qdrant collections and prepares the SPARC memory system for actual use
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add lib to path
lib_path = Path(__file__).parent.parent / "lib"
sys.path.insert(0, str(lib_path))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams
    from dotenv import load_dotenv
    from rich.console import Console
    from rich.progress import Progress, TaskID
    import requests
    import httpx
    from mistral_embeddings import MistralEmbeddings
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install: pip install qdrant-client python-dotenv rich requests httpx")
    sys.exit(1)

console = Console()

# Load environment
load_dotenv()

class MemorySystemInitializer:
    """Initialize the real SPARC memory system"""
    
    def __init__(self):
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6338'))
        self.qdrant_client = None
        self.mistral_embeddings = None
        
    async def initialize(self):
        """Initialize the complete memory system"""
        console.print("🚀 [bold blue]Initializing SPARC Memory System[/bold blue]")
        
        # Step 1: Connect to Qdrant
        await self._connect_to_qdrant()
        
        # Step 2: Initialize Mistral embeddings
        await self._initialize_mistral_embeddings()
        
        # Step 3: Create Qdrant collections
        await self._create_qdrant_collections()
        
        # Step 4: Create test project namespace
        await self._create_test_project()
        
        console.print("✅ [bold green]Memory system initialization complete![/bold green]")
        
    async def _connect_to_qdrant(self):
        """Connect to Qdrant vector database"""
        console.print(f"🔗 Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        
        try:
            self.qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port,
                timeout=30
            )
            
            # Test connection
            info = self.qdrant_client.get_collections()
            console.print(f"✅ Connected to Qdrant. Collections: {len(info.collections)}")
            
        except Exception as e:
            console.print(f"❌ Failed to connect to Qdrant: {e}")
            raise
    
    async def _initialize_mistral_embeddings(self):
        """Initialize Mistral API for embeddings"""
        console.print("🧠 Initializing Mistral embeddings...")
        
        try:
            self.mistral_embeddings = MistralEmbeddings()
            
            # Test connection
            if await self.mistral_embeddings.test_connection():
                console.print(f"✅ Mistral API connected. Embedding dimension: {self.mistral_embeddings.get_embedding_dimension()}")
            else:
                raise Exception("Failed to connect to Mistral API")
            
        except Exception as e:
            console.print(f"❌ Failed to initialize Mistral embeddings: {e}")
            raise
    
    async def _create_qdrant_collections(self):
        """Create all required Qdrant collections for memory system"""
        console.print("📁 Creating Qdrant collections...")
        
        # Get embedding dimension from Mistral
        vector_size = self.mistral_embeddings.get_embedding_dimension()
        console.print(f"📏 Mistral embedding dimension: {vector_size}")
        
        collections = [
            {
                "name": "agent_memories",
                "description": "Stores agent execution memories and learned patterns"
            },
            {
                "name": "project_patterns", 
                "description": "Stores successful project implementation patterns"
            },
            {
                "name": "verification_outcomes",
                "description": "Stores BMO verification results and triangulation patterns"
            },
            {
                "name": "code_snippets",
                "description": "Stores reusable code patterns and implementations"
            },
            {
                "name": "test_patterns",
                "description": "Stores effective testing strategies and patterns"
            },
            {
                "name": "architecture_patterns",
                "description": "Stores successful architectural decisions and patterns"
            },
            {
                "name": "user_interactions",
                "description": "Stores user preference patterns and successful interaction outcomes"
            },
            {
                "name": "cross_project_insights",
                "description": "Stores insights that apply across multiple projects"
            }
        ]
        
        with Progress() as progress:
            task = progress.add_task("Creating collections...", total=len(collections))
            
            for collection_info in collections:
                collection_name = collection_info["name"]
                
                try:
                    # Check if collection exists
                    existing_collections = self.qdrant_client.get_collections()
                    collection_exists = any(c.name == collection_name for c in existing_collections.collections)
                    
                    if collection_exists:
                        console.print(f"📁 Collection '{collection_name}' already exists")
                    else:
                        # Create collection
                        self.qdrant_client.create_collection(
                            collection_name=collection_name,
                            vectors_config=VectorParams(
                                size=vector_size,
                                distance=Distance.COSINE
                            )
                        )
                        console.print(f"✅ Created collection: {collection_name}")
                    
                    progress.advance(task)
                    
                except Exception as e:
                    console.print(f"❌ Failed to create collection {collection_name}: {e}")
                    raise
    
    async def _create_test_project(self):
        """Create test project namespace for flight simulator"""
        console.print("🛫 Creating test project: Flight Simulator")
        
        project_data = {
            "project_id": "flight_sim_001",
            "namespace": "flight_simulator_test",
            "goal": "Build a simple flight simulator that works in the browser",
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "memory_enhancement_enabled": True
        }
        
        try:
            # Create project embedding using Mistral
            project_text = f"Project: {project_data['goal']} - Browser-based flight simulator with realistic physics"
            embedding = await self.mistral_embeddings.get_embedding(project_text)
            
            # Store in cross_project_insights collection
            self.qdrant_client.upsert(
                collection_name="cross_project_insights",
                points=[
                    models.PointStruct(
                        id=1,
                        vector=embedding,
                        payload=project_data
                    )
                ]
            )
            
            console.print("✅ Test project created in memory system")
            
        except Exception as e:
            console.print(f"❌ Failed to create test project: {e}")
            raise
    
    async def verify_system(self):
        """Verify the memory system is working correctly"""
        console.print("🔍 Verifying memory system...")
        
        try:
            # Test embedding creation with Mistral
            test_text = "This is a test memory for verification"
            embedding = await self.mistral_embeddings.get_embedding(test_text)
            
            # Test storage
            self.qdrant_client.upsert(
                collection_name="agent_memories",
                points=[
                    models.PointStruct(
                        id=999999,  # Test ID
                        vector=embedding,
                        payload={
                            "content": test_text,
                            "type": "system_test",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                ]
            )
            
            # Test retrieval
            search_results = self.qdrant_client.search(
                collection_name="agent_memories",
                query_vector=embedding,
                limit=1
            )
            
            if search_results and len(search_results) > 0:
                console.print("✅ Memory system verification successful")
                
                # Clean up test data
                self.qdrant_client.delete(
                    collection_name="agent_memories",
                    points_selector=models.PointIdsList(points=[999999])
                )
                
                return True
            else:
                console.print("❌ Memory system verification failed")
                return False
                
        except Exception as e:
            console.print(f"❌ Memory system verification error: {e}")
            return False

async def main():
    """Main initialization function"""
    initializer = MemorySystemInitializer()
    
    try:
        await initializer.initialize()
        success = await initializer.verify_system()
        
        if success:
            console.print("\n🎉 [bold green]SPARC Memory System Ready![/bold green]")
            console.print("You can now run the full SPARC workflow with memory enhancement.")
            return True
        else:
            console.print("\n❌ [bold red]Memory system setup failed[/bold red]")
            return False
            
    except Exception as e:
        console.print(f"\n💥 [bold red]Initialization failed: {e}[/bold red]")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)