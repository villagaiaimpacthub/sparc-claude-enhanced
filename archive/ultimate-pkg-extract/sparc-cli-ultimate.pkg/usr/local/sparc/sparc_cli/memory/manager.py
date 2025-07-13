#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "qdrant-client",
#   "mistralai",
#   "python-dotenv",
#   "pydantic",
# ]
# ///

"""Enhanced memory manager for SPARC agents"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from supabase import create_client, Client
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from mistralai import Mistral
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TaskPayload(BaseModel):
    """Standard task structure for agent communication"""
    task_id: str
    description: str
    context: Dict[str, Any]
    requirements: List[str]
    ai_verifiable_outcomes: List[str]
    phase: str
    priority: int = 5

class MemoryManager:
    """Handles all memory operations for SPARC agents"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        
        # Initialize Supabase client
        self.supabase: Client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"]
        )
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(
            host=os.environ.get("QDRANT_HOST", "localhost"),
            port=int(os.environ.get("QDRANT_PORT", 6333))
        )
        
        # Initialize Mistral client
        self.mistral = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        
        # Initialize collections
        self._setup_collections()
    
    def _setup_collections(self):
        """Set up Qdrant collections for the project namespace"""
        collections = [
            f"{self.namespace}_files",
            f"{self.namespace}_chunks", 
            f"{self.namespace}_docs",
            f"{self.namespace}_decisions"
        ]
        
        for collection_name in collections:
            try:
                self.qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # Mistral embedding size
                        distance=Distance.COSINE
                    )
                )
            except Exception:
                # Collection already exists
                pass
    
    async def save_to_project_memorys(self, file_info: Dict[str, Any]) -> None:
        """Save file information to project_memorys table (State Scribe only)"""
        try:
            # Check if record exists
            existing = self.supabase.table("project_memorys").select("*").eq(
                "namespace", self.namespace
            ).eq(
                "file_path", file_info["file_path"]
            ).execute()
            
            if existing.data:
                # Update existing record
                self.supabase.table("project_memorys").update({
                    "memory_type": file_info.get("memory_type"),
                    "brief_description": file_info.get("brief_description"),
                    "elements_description": file_info.get("elements_description"),
                    "rationale": file_info.get("rationale"),
                    "version": existing.data[0]["version"] + 1,
                    "last_updated_timestamp": datetime.now().isoformat()
                }).eq(
                    "namespace", self.namespace
                ).eq(
                    "file_path", file_info["file_path"]
                ).execute()
            else:
                # Insert new record
                self.supabase.table("project_memorys").insert({
                    "namespace": self.namespace,
                    "file_path": file_info["file_path"],
                    "memory_type": file_info.get("memory_type"),
                    "brief_description": file_info.get("brief_description"),
                    "elements_description": file_info.get("elements_description"),
                    "rationale": file_info.get("rationale"),
                    "version": 1
                }).execute()
        except Exception as e:
            print(f"Error saving to project_memorys: {str(e)}")
    
    async def get_project_state(self) -> Dict[str, Any]:
        """Get complete project state"""
        try:
            result = self.supabase.table("project_memorys").select("*").eq(
                "namespace", self.namespace
            ).execute()
            
            return {
                "files": {item["file_path"]: item for item in result.data},
                "total_files": len(result.data),
                "last_updated": max(
                    (item["last_updated_timestamp"] for item in result.data),
                    default=datetime.now().isoformat()
                )
            }
        except Exception as e:
            print(f"Error getting project state: {str(e)}")
            return {"files": {}, "total_files": 0}
    
    async def search_code(self, query: str, limit: int = 20) -> List[Dict]:
        """Semantic search in codebase"""
        try:
            # Get embedding from Mistral
            embedding_response = self.mistral.embeddings.create(
                model="mistral-embed",
                inputs=[query]
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Search in Qdrant
            search_result = self.qdrant.search(
                collection_name=f"{self.namespace}_files",
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "file_path": hit.payload.get("file_path"),
                    "content": hit.payload.get("content"),
                    "score": hit.score,
                    "file_type": hit.payload.get("file_type")
                }
                for hit in search_result
            ]
        except Exception as e:
            print(f"Error searching code: {str(e)}")
            return []
    
    async def index_file(self, file_path: str, content: str = None) -> None:
        """Index a file in Qdrant"""
        try:
            if content is None:
                if not Path(file_path).exists():
                    return
                content = Path(file_path).read_text(encoding='utf-8')
            
            # Get embedding from Mistral
            embedding_response = self.mistral.embeddings.create(
                model="mistral-embed",
                inputs=[content[:8000]]  # Mistral token limit
            )
            embedding = embedding_response.data[0].embedding
            
            # Create point ID
            point_id = int(hashlib.md5(file_path.encode()).hexdigest()[:8], 16)
            
            # Store in Qdrant
            self.qdrant.upsert(
                collection_name=f"{self.namespace}_files",
                points=[PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "file_path": file_path,
                        "content": content,
                        "file_type": Path(file_path).suffix,
                        "indexed_at": datetime.now().isoformat()
                    }
                )]
            )
        except Exception as e:
            print(f"Error indexing file {file_path}: {str(e)}")
    
    async def save_context(self, agent_name: str, phase: str, context: Dict[str, Any]) -> None:
        """Save agent context to Supabase"""
        try:
            self.supabase.table("sparc_contexts").insert({
                "namespace": self.namespace,
                "context_type": "agent_output",
                "context_key": f"{agent_name}_{datetime.now().isoformat()}",
                "agent_name": agent_name,
                "phase": phase,
                "content": context,
                "token_count": self._estimate_tokens(context)
            }).execute()
        except Exception as e:
            print(f"Error saving context: {str(e)}")
    
    async def get_agent_history(self, agent_name: str, limit: int = 10) -> List[Dict]:
        """Get agent's previous outputs"""
        try:
            result = self.supabase.table("sparc_contexts").select("*").eq(
                "namespace", self.namespace
            ).eq(
                "agent_name", agent_name
            ).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            return result.data
        except Exception as e:
            print(f"Error getting agent history: {str(e)}")
            return []
    
    async def create_task(self, from_agent: str, to_agent: str, task_type: str, 
                         task_payload: Dict[str, Any]) -> str:
        """Create a new task in the queue"""
        try:
            result = self.supabase.table("agent_tasks").insert({
                "namespace": self.namespace,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "task_type": task_type,
                "task_payload": task_payload,
                "priority": task_payload.get("priority", 5)
            }).execute()
            
            return result.data[0]["id"]
        except Exception as e:
            print(f"Error creating task: {str(e)}")
            return None
    
    async def get_pending_tasks(self, agent_name: str) -> List[Dict]:
        """Get pending tasks for an agent"""
        try:
            result = self.supabase.table("agent_tasks").select("*").eq(
                "namespace", self.namespace
            ).eq(
                "to_agent", agent_name
            ).eq(
                "status", "pending"
            ).order(
                "priority", desc=True
            ).order(
                "created_at", asc=True
            ).execute()
            
            return result.data
        except Exception as e:
            print(f"Error getting pending tasks: {str(e)}")
            return []
    
    async def request_approval(self, phase: str, agent_name: str, artifacts: Dict[str, Any], 
                              summary: str) -> str:
        """Request human approval"""
        try:
            result = self.supabase.table("approval_queue").insert({
                "namespace": self.namespace,
                "phase": phase,
                "requesting_agent": agent_name,
                "approval_type": "phase_completion",
                "artifacts": artifacts,
                "summary": summary
            }).execute()
            
            return result.data[0]["id"]
        except Exception as e:
            print(f"Error requesting approval: {str(e)}")
            return None
    
    async def check_pending_approvals(self) -> List[Dict]:
        """Check for pending approvals"""
        try:
            result = self.supabase.table("approval_queue").select("*").eq(
                "namespace", self.namespace
            ).eq(
                "status", "pending"
            ).execute()
            
            return result.data
        except Exception as e:
            print(f"Error checking approvals: {str(e)}")
            return []
    
    def _estimate_tokens(self, obj: Any) -> int:
        """Estimate token count for an object"""
        return len(json.dumps(obj)) // 4  # Rough estimate
    
    def _load_namespace(self) -> str:
        """Load namespace from project configuration"""
        # Try to load from project config first
        project_config_path = Path(".sparc/project.json")
        if project_config_path.exists():
            try:
                with open(project_config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('namespace', 'default')
            except Exception:
                pass
        
        # Fallback to CLAUDE.md for backward compatibility
        claude_md = Path("CLAUDE.md")
        if claude_md.exists():
            content = claude_md.read_text()
            for line in content.split('\n'):
                if line.startswith('namespace:'):
                    return line.split(':', 1)[1].strip()
                # Legacy support for project_id
                if line.startswith('project_id:'):
                    return line.split(':', 1)[1].strip()
        return "default"