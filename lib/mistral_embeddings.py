#!/usr/bin/env python3
"""
Mistral API Embeddings Integration
Centralized embedding generation using Mistral API for semantic search
"""

import os
import asyncio
from typing import List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

class MistralEmbeddings:
    """Mistral API embeddings client for SPARC memory system"""
    
    def __init__(self):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.base_url = "https://api.mistral.ai/v1"
        self.model = "mistral-embed"
        
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": texts
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Mistral API error: {response.status_code} - {response.text}")
                
                result = response.json()
                return [item["embedding"] for item in result["data"]]
                
            except httpx.TimeoutException:
                raise Exception("Mistral API request timed out")
            except Exception as e:
                raise Exception(f"Failed to get Mistral embeddings: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test connection to Mistral API"""
        try:
            await self.get_embedding("test connection")
            return True
        except Exception:
            return False
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of Mistral embeddings"""
        # Mistral-embed produces 1024-dimensional embeddings
        return 1024

# Global instance for easy access
_mistral_client: Optional[MistralEmbeddings] = None

def get_mistral_client() -> MistralEmbeddings:
    """Get or create global Mistral client"""
    global _mistral_client
    if _mistral_client is None:
        _mistral_client = MistralEmbeddings()
    return _mistral_client

async def get_embedding(text: str) -> List[float]:
    """Convenience function to get embedding"""
    client = get_mistral_client()
    return await client.get_embedding(text)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to get multiple embeddings"""
    client = get_mistral_client()
    return await client.get_embeddings(texts)

# Sync versions for compatibility
def get_embedding_sync(text: str) -> List[float]:
    """Synchronous version of get_embedding"""
    return asyncio.run(get_embedding(text))

def get_embeddings_sync(texts: List[str]) -> List[List[float]]:
    """Synchronous version of get_embeddings"""
    return asyncio.run(get_embeddings(texts))

if __name__ == "__main__":
    # Test the Mistral embeddings
    async def test_embeddings():
        client = MistralEmbeddings()
        
        # Test connection
        if await client.test_connection():
            print("✅ Mistral API connection successful")
        else:
            print("❌ Mistral API connection failed")
            return
        
        # Test embedding generation
        test_texts = [
            "This is a test of Mistral embeddings",
            "SPARC autonomous development system",
            "Vector database semantic search"
        ]
        
        embeddings = await client.get_embeddings(test_texts)
        
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0])}")
        print(f"First embedding preview: {embeddings[0][:5]}...")
    
    asyncio.run(test_embeddings())