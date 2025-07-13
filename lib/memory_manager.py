#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "qdrant-client>=1.7.0",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
#   "httpx>=0.24.0",
# ]
# ///

"""
SPARC Memory Manager - Intelligent Memory Architecture
Combines Supabase (structured) + Qdrant (semantic) for exponential intelligence

This transforms SPARC from a stateless system into a continuously learning AI developer
that gets smarter with every project, remembers successful patterns, and applies
learned insights to improve each generation.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel
import numpy as np
from dataclasses import dataclass

try:
    from rich.console import Console
    from supabase import create_client, Client
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from mistral_embeddings import MistralEmbeddings
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

class MemoryType(str):
    """Memory type constants"""
    PROJECT_CONTEXT = "project_context"
    CODE_PATTERN = "code_pattern"
    QUALITY_INSIGHT = "quality_insight"
    USER_PREFERENCE = "user_preference"
    SUCCESSFUL_SOLUTION = "successful_solution"
    FAILED_ATTEMPT = "failed_attempt"
    AGENT_INTERACTION = "agent_interaction"
    CROSS_PROJECT_LEARNING = "cross_project_learning"

class MemoryRecord(BaseModel):
    """Structured memory record for Supabase"""
    memory_id: str
    namespace: str
    memory_type: str
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    usage_count: int
    created_at: datetime
    last_accessed: datetime
    tags: List[str]
    vector_id: Optional[str] = None  # Link to Qdrant vector

class SemanticQuery(BaseModel):
    """Semantic search query structure"""
    query_text: str
    memory_types: List[str] = []
    min_quality_score: float = 0.5
    limit: int = 10
    include_metadata: bool = True

class MemoryInsight(BaseModel):
    """Extracted insight from memory analysis"""
    insight_type: str
    insight_text: str
    confidence: float
    supporting_evidence: List[str]
    applicable_contexts: List[str]

class MemoryManager:
    """
    Intelligent Memory Manager - The Brain of SPARC
    
    Architecture:
    1. Supabase: Structured data, relationships, metadata, usage tracking
    2. Qdrant: Semantic embeddings, similarity search, pattern matching
    3. Embedding Model: Converts text to high-dimensional vectors
    4. Intelligence Layer: Extracts insights, learns patterns, makes recommendations
    
    Capabilities:
    - Stores every interaction, decision, and outcome
    - Finds similar past situations using semantic search
    - Learns from successful patterns and failed attempts  
    - Provides context-aware recommendations to agents
    - Continuously improves system performance through experience
    """
    
    def __init__(self, 
                 supabase_url: str, 
                 supabase_key: str,
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 embedding_provider: str = "mistral"):
        
        # Initialize clients
        self.supabase = create_client(supabase_url, supabase_key)
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.mistral_embeddings = MistralEmbeddings()
        
        # Initialize collections
        asyncio.create_task(self._initialize_collections())
        
        console.print(f"[green]🧠 Memory Manager initialized with semantic intelligence[/green]")
    
    async def _initialize_collections(self):
        """Initialize Qdrant collections for different memory types"""
        
        # Vector dimensions for sentence-transformer model
        vector_size = 384
        
        collections = [
            "sparc_requirements",      # User requirements and goals
            "sparc_code_patterns",     # Code snippets and implementations
            "sparc_architectures",     # System architectures and designs
            "sparc_quality_insights",  # Quality patterns and best practices
            "sparc_user_preferences",  # User preferences and behavior patterns
            "sparc_agent_knowledge",   # Agent conversations and decisions
            "sparc_solutions",         # Complete solution patterns
            "sparc_cross_project"      # Cross-project learnings
        ]
        
        for collection_name in collections:
            try:
                # Check if collection exists
                collections_list = self.qdrant.get_collections()
                existing_names = [c.name for c in collections_list.collections]
                
                if collection_name not in existing_names:
                    # Create collection with optimal settings
                    self.qdrant.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=vector_size,
                            distance=models.Distance.COSINE
                        ),
                        optimizers_config=models.OptimizersConfigDiff(
                            default_segment_number=2
                        ),
                        hnsw_config=models.HnswConfigDiff(
                            payload_m=16,
                            m=0
                        )
                    )
                    console.print(f"[blue]📚 Created collection: {collection_name}[/blue]")
                else:
                    console.print(f"[dim]📚 Collection exists: {collection_name}[/dim]")
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  Collection setup warning for {collection_name}: {e}[/yellow]")
    
    async def store_memory(self, 
                          content: str,
                          memory_type: str,
                          namespace: str,
                          metadata: Dict[str, Any] = None,
                          quality_score: float = 0.5,
                          tags: List[str] = None) -> str:
        """
        Store memory in both structured (Supabase) and semantic (Qdrant) storage
        Returns memory_id for future reference
        """
        
        metadata = metadata or {}
        tags = tags or []
        memory_id = f"{memory_type}_{namespace}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Store in Supabase (structured)
        memory_record = MemoryRecord(
            memory_id=memory_id,
            namespace=namespace,
            memory_type=memory_type,
            content=content,
            metadata=metadata,
            quality_score=quality_score,
            usage_count=0,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            tags=tags
        )
        
        try:
            # Store structured data
            await self._store_structured_memory(memory_record)
            
            # Generate and store semantic embedding
            vector_id = await self._store_semantic_memory(
                content, memory_type, memory_id, metadata, tags
            )
            
            # Update record with vector reference
            memory_record.vector_id = vector_id
            await self._update_structured_memory(memory_record)
            
            console.print(f"[green]💾 Stored memory: {memory_type} [{memory_id[:12]}...]")
            return memory_id
            
        except Exception as e:
            console.print(f"[red]❌ Memory storage failed: {e}[/red]")
            return ""
    
    async def semantic_search(self, 
                            query: str,
                            memory_types: List[str] = None,
                            namespace: str = None,
                            limit: int = 10,
                            min_quality_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Perform semantic search across memory to find similar patterns/solutions
        """
        
        try:
            # Generate query embedding using Mistral
            query_vector = await self.mistral_embeddings.get_embedding(query)
            
            # Determine which collections to search
            if memory_types:
                collections = [self._get_collection_name(mt) for mt in memory_types]
            else:
                collections = [
                    "sparc_requirements", "sparc_code_patterns", "sparc_architectures",
                    "sparc_quality_insights", "sparc_solutions"
                ]
            
            all_results = []
            
            # Search each relevant collection
            for collection_name in collections:
                try:
                    # Build search filter
                    search_filter = models.Filter()
                    conditions = []
                    
                    if namespace:
                        conditions.append(
                            models.FieldCondition(
                                key="namespace", 
                                match=models.MatchValue(value=namespace)
                            )
                        )
                    
                    if min_quality_score > 0:
                        conditions.append(
                            models.FieldCondition(
                                key="quality_score",
                                range=models.Range(gte=min_quality_score)
                            )
                        )
                    
                    if conditions:
                        search_filter = models.Filter(must=conditions)
                    
                    # Perform vector search
                    search_results = self.qdrant.search(
                        collection_name=collection_name,
                        query_vector=query_vector,
                        query_filter=search_filter if conditions else None,
                        limit=limit,
                        with_payload=True,
                        with_vectors=False
                    )
                    
                    # Process results
                    for hit in search_results:
                        result = {
                            'memory_id': hit.payload.get('memory_id'),
                            'content': hit.payload.get('content'),
                            'memory_type': hit.payload.get('memory_type'),
                            'namespace': hit.payload.get('namespace'),
                            'similarity_score': hit.score,
                            'quality_score': hit.payload.get('quality_score', 0.5),
                            'metadata': hit.payload.get('metadata', {}),
                            'tags': hit.payload.get('tags', []),
                            'collection': collection_name
                        }
                        all_results.append(result)
                        
                except Exception as e:
                    console.print(f"[yellow]⚠️  Search warning for {collection_name}: {e}[/yellow]")
                    continue
            
            # Sort by similarity score and return top results
            all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Update usage counts for accessed memories
            for result in all_results[:limit]:
                await self._increment_usage_count(result['memory_id'])
            
            console.print(f"[blue]🔍 Semantic search found {len(all_results[:limit])} similar memories[/blue]")
            return all_results[:limit]
            
        except Exception as e:
            console.print(f"[red]❌ Semantic search failed: {e}[/red]")
            return []
    
    async def get_contextual_insights(self, 
                                    current_context: Dict[str, Any],
                                    memory_types: List[str] = None,
                                    namespace: str = None) -> List[MemoryInsight]:
        """
        Extract contextual insights based on current situation and past experiences
        This is where the AI becomes truly intelligent - applying learned patterns
        """
        
        insights = []
        
        try:
            # Build context query
            context_query = self._build_context_query(current_context)
            
            # Find similar past situations
            similar_memories = await self.semantic_search(
                query=context_query,
                memory_types=memory_types or [
                    MemoryType.SUCCESSFUL_SOLUTION,
                    MemoryType.QUALITY_INSIGHT,
                    MemoryType.CODE_PATTERN
                ],
                namespace=namespace,
                limit=20,
                min_quality_score=0.7
            )
            
            # Extract patterns from high-quality memories
            if similar_memories:
                insights.extend(await self._extract_solution_patterns(similar_memories))
                insights.extend(await self._extract_quality_patterns(similar_memories))
                insights.extend(await self._extract_architectural_insights(similar_memories))
            
            # Get cross-project learnings
            cross_project_insights = await self._get_cross_project_insights(current_context)
            insights.extend(cross_project_insights)
            
            console.print(f"[green]💡 Generated {len(insights)} contextual insights[/green]")
            return insights
            
        except Exception as e:
            console.print(f"[red]❌ Insight generation failed: {e}[/red]")
            return []
    
    async def learn_from_outcome(self,
                               action_taken: str,
                               outcome_quality: float,
                               context: Dict[str, Any],
                               namespace: str,
                               outcome_details: Dict[str, Any] = None) -> None:
        """
        Learn from the outcome of an action to improve future decisions
        This creates the feedback loop that makes the system continuously smarter
        """
        
        outcome_details = outcome_details or {}
        
        try:
            # Determine if this was a success or failure
            memory_type = MemoryType.SUCCESSFUL_SOLUTION if outcome_quality >= 0.7 else MemoryType.FAILED_ATTEMPT
            
            # Create learning record
            learning_content = f"""
            Action: {action_taken}
            Context: {json.dumps(context, indent=2)}
            Outcome Quality: {outcome_quality}
            Details: {json.dumps(outcome_details, indent=2)}
            """
            
            # Store the learning
            await self.store_memory(
                content=learning_content,
                memory_type=memory_type,
                namespace=namespace,
                metadata={
                    'action': action_taken,
                    'outcome_quality': outcome_quality,
                    'context': context,
                    'outcome_details': outcome_details,
                    'learning_timestamp': datetime.now().isoformat()
                },
                quality_score=outcome_quality,
                tags=self._extract_learning_tags(action_taken, context)
            )
            
            # Update cross-project insights if this is a significant learning
            if outcome_quality >= 0.8 or outcome_quality <= 0.3:
                await self._update_cross_project_insights(
                    action_taken, outcome_quality, context, outcome_details
                )
            
            console.print(f"[blue]📈 Learned from {'success' if outcome_quality >= 0.7 else 'failure'}: {action_taken[:50]}...[/blue]")
            
        except Exception as e:
            console.print(f"[red]❌ Learning failed: {e}[/red]")
    
    async def get_agent_context(self, 
                              agent_name: str,
                              phase: str,
                              user_goal: str,
                              namespace: str) -> Dict[str, Any]:
        """
        Provide rich context to agents based on memory and learned patterns
        This is what makes agents exponentially smarter over time
        """
        
        try:
            # Build comprehensive context query
            context_query = f"{user_goal} {phase} {agent_name}"
            
            # Get relevant memories
            relevant_memories = await self.semantic_search(
                query=context_query,
                namespace=namespace,
                limit=15,
                min_quality_score=0.6
            )
            
            # Get contextual insights
            insights = await self.get_contextual_insights(
                current_context={
                    'agent': agent_name,
                    'phase': phase,
                    'goal': user_goal,
                    'namespace': namespace
                },
                namespace=namespace
            )
            
            # Get user preferences from memory
            user_preferences = await self._get_user_preferences(namespace)
            
            # Get successful patterns for this type of task
            successful_patterns = await self._get_successful_patterns(phase, user_goal)
            
            # Build rich context
            agent_context = {
                'relevant_memories': relevant_memories,
                'contextual_insights': [i.dict() for i in insights],
                'user_preferences': user_preferences,
                'successful_patterns': successful_patterns,
                'similar_projects': await self._get_similar_projects(user_goal),
                'quality_benchmarks': await self._get_quality_benchmarks(phase),
                'common_pitfalls': await self._get_common_pitfalls(phase, user_goal),
                'enhancement_suggestions': await self._get_enhancement_suggestions(user_goal)
            }
            
            console.print(f"[green]🎯 Enhanced {agent_name} with {len(relevant_memories)} memories and {len(insights)} insights[/green]")
            return agent_context
            
        except Exception as e:
            console.print(f"[red]❌ Context generation failed: {e}[/red]")
            return {}
    
    # Internal helper methods
    
    def _get_collection_name(self, memory_type: str) -> str:
        """Map memory types to Qdrant collection names"""
        mapping = {
            MemoryType.PROJECT_CONTEXT: "sparc_requirements",
            MemoryType.CODE_PATTERN: "sparc_code_patterns",
            MemoryType.QUALITY_INSIGHT: "sparc_quality_insights",
            MemoryType.USER_PREFERENCE: "sparc_user_preferences",
            MemoryType.SUCCESSFUL_SOLUTION: "sparc_solutions",
            MemoryType.FAILED_ATTEMPT: "sparc_solutions",
            MemoryType.AGENT_INTERACTION: "sparc_agent_knowledge",
            MemoryType.CROSS_PROJECT_LEARNING: "sparc_cross_project"
        }
        return mapping.get(memory_type, "sparc_requirements")
    
    async def _store_structured_memory(self, memory_record: MemoryRecord):
        """Store structured memory in Supabase"""
        try:
            self.supabase.table('sparc_memory').insert(memory_record.model_dump(mode='json')).execute()
        except Exception as e:
            console.print(f"[yellow]⚠️  Structured storage warning: {e}[/yellow]")
    
    async def _store_semantic_memory(self, 
                                   content: str,
                                   memory_type: str,
                                   memory_id: str,
                                   metadata: Dict[str, Any],
                                   tags: List[str]) -> str:
        """Store semantic memory in Qdrant"""
        try:
            # Generate embedding using Mistral
            vector = await self.mistral_embeddings.get_embedding(content)
            
            # Determine collection
            collection_name = self._get_collection_name(memory_type)
            
            # Create payload
            payload = {
                'memory_id': memory_id,
                'content': content,
                'memory_type': memory_type,
                'metadata': metadata,
                'tags': tags,
                'namespace': metadata.get('namespace', ''),
                'quality_score': metadata.get('quality_score', 0.5),
                'created_at': datetime.now().isoformat()
            }
            
            # Store vector
            vector_id = f"{memory_id}_vector"
            self.qdrant.upsert(
                collection_name=collection_name,
                points=[models.PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=payload
                )]
            )
            
            return vector_id
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Semantic storage warning: {e}[/yellow]")
            return ""
    
    async def _update_structured_memory(self, memory_record: MemoryRecord):
        """Update structured memory with vector reference"""
        try:
            self.supabase.table('sparc_memory').update({
                'vector_id': memory_record.vector_id
            }).eq('memory_id', memory_record.memory_id).execute()
        except Exception as e:
            console.print(f"[yellow]⚠️  Memory update warning: {e}[/yellow]")
    
    def _build_context_query(self, context: Dict[str, Any]) -> str:
        """Build semantic search query from context"""
        parts = []
        
        if context.get('goal'):
            parts.append(context['goal'])
        if context.get('phase'):
            parts.append(f"phase: {context['phase']}")
        if context.get('agent'):
            parts.append(f"agent: {context['agent']}")
        if context.get('requirements'):
            parts.extend(context['requirements'])
        
        return ' '.join(parts)
    
    def _extract_learning_tags(self, action: str, context: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from action and context for better memory organization"""
        tags = []
        
        # Extract technology tags
        action_lower = action.lower()
        tech_keywords = ['python', 'javascript', 'react', 'fastapi', 'postgresql', 'docker']
        tags.extend([kw for kw in tech_keywords if kw in action_lower])
        
        # Extract phase tags
        if context.get('phase'):
            tags.append(f"phase_{context['phase']}")
        
        # Extract pattern tags
        pattern_keywords = ['api', 'database', 'auth', 'security', 'performance']
        tags.extend([f"pattern_{kw}" for kw in pattern_keywords if kw in action_lower])
        
        return tags
    
    async def _increment_usage_count(self, memory_id: str):
        """Increment usage count for accessed memory"""
        try:
            # Update both structured and semantic storage
            self.supabase.rpc('increment_memory_usage', {'memory_id_param': memory_id}).execute()
        except Exception as e:
            # Non-critical error
            pass
    
    # Insight extraction methods (abbreviated for space - full implementations would be more sophisticated)
    
    async def _extract_solution_patterns(self, memories: List[Dict[str, Any]]) -> List[MemoryInsight]:
        """Extract solution patterns from similar successful memories"""
        insights = []
        
        # Group by solution approach
        approaches = {}
        for memory in memories:
            if memory['memory_type'] == MemoryType.SUCCESSFUL_SOLUTION:
                approach = memory['metadata'].get('approach', 'general')
                if approach not in approaches:
                    approaches[approach] = []
                approaches[approach].append(memory)
        
        # Generate insights for common approaches
        for approach, approach_memories in approaches.items():
            if len(approach_memories) >= 2:  # Pattern confirmed by multiple examples
                insight = MemoryInsight(
                    insight_type="solution_pattern",
                    insight_text=f"Successful pattern: {approach} approach has {len(approach_memories)} successful implementations",
                    confidence=min(0.9, len(approach_memories) * 0.2),
                    supporting_evidence=[m['memory_id'] for m in approach_memories],
                    applicable_contexts=[approach]
                )
                insights.append(insight)
        
        return insights
    
    async def _extract_quality_patterns(self, memories: List[Dict[str, Any]]) -> List[MemoryInsight]:
        """Extract quality patterns from high-performing solutions"""
        # Implementation would analyze quality metrics across memories
        return []
    
    async def _extract_architectural_insights(self, memories: List[Dict[str, Any]]) -> List[MemoryInsight]:
        """Extract architectural insights from similar projects"""
        # Implementation would analyze architectural decisions and outcomes
        return []
    
    async def _get_cross_project_insights(self, context: Dict[str, Any]) -> List[MemoryInsight]:
        """Get insights that apply across multiple projects"""
        # Implementation would find patterns that work across different projects
        return []
    
    async def _update_cross_project_insights(self, action: str, quality: float, context: Dict[str, Any], details: Dict[str, Any]):
        """Update cross-project learning database"""
        # Implementation would update insights that apply across projects
        pass
    
    async def _get_user_preferences(self, namespace: str) -> Dict[str, Any]:
        """Extract user preferences from memory"""
        try:
            prefs = await self.semantic_search(
                query="user preference technology choice",
                memory_types=[MemoryType.USER_PREFERENCE],
                namespace=namespace,
                limit=10
            )
            return {'preferences': prefs}
        except:
            return {}
    
    async def _get_successful_patterns(self, phase: str, goal: str) -> List[Dict[str, Any]]:
        """Get successful patterns for this phase and goal type"""
        try:
            return await self.semantic_search(
                query=f"{phase} {goal} successful",
                memory_types=[MemoryType.SUCCESSFUL_SOLUTION],
                limit=5,
                min_quality_score=0.8
            )
        except:
            return []
    
    async def _get_similar_projects(self, goal: str) -> List[Dict[str, Any]]:
        """Find similar past projects"""
        try:
            return await self.semantic_search(
                query=goal,
                memory_types=[MemoryType.PROJECT_CONTEXT],
                limit=5,
                min_quality_score=0.6
            )
        except:
            return []
    
    async def _get_quality_benchmarks(self, phase: str) -> Dict[str, float]:
        """Get quality benchmarks for this phase"""
        # Implementation would return typical quality scores for phase
        return {'typical_quality': 0.75, 'excellent_quality': 0.9}
    
    async def _get_common_pitfalls(self, phase: str, goal: str) -> List[str]:
        """Get common pitfalls for this phase and goal type"""
        try:
            failures = await self.semantic_search(
                query=f"{phase} {goal} failed",
                memory_types=[MemoryType.FAILED_ATTEMPT],
                limit=5
            )
            return [f['content'][:100] for f in failures]
        except:
            return []
    
    async def _get_enhancement_suggestions(self, goal: str) -> List[str]:
        """Get suggestions for enhancing the approach"""
        # Implementation would suggest improvements based on memory
        return []

# Convenience function for quick memory manager setup
async def create_memory_manager(supabase_url: str = None, 
                              supabase_key: str = None,
                              qdrant_host: str = "localhost") -> MemoryManager:
    """Create and initialize memory manager with environment defaults"""
    
    import os
    
    supabase_url = supabase_url or os.getenv('SUPABASE_URL')
    supabase_key = supabase_key or os.getenv('SUPABASE_KEY') 
    
    if not supabase_url or not supabase_key:
        console.print("[yellow]⚠️  Supabase credentials not found, using fallback mode[/yellow]")
        # Could implement local fallback here
        return None
    
    memory_manager = MemoryManager(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        qdrant_host=qdrant_host
    )
    
    return memory_manager

if __name__ == "__main__":
    # Test the memory manager
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_memory_manager():
        """Test memory manager functionality"""
        
        memory = await create_memory_manager()
        if not memory:
            print("Could not initialize memory manager")
            return
        
        # Test storing memory
        memory_id = await memory.store_memory(
            content="FastAPI with JWT authentication and PostgreSQL database",
            memory_type=MemoryType.SUCCESSFUL_SOLUTION,
            namespace="test_project",
            metadata={'framework': 'fastapi', 'auth': 'jwt', 'db': 'postgresql'},
            quality_score=0.9,
            tags=['python', 'api', 'auth', 'database']
        )
        
        console.print(f"Stored memory: {memory_id}")
        
        # Test semantic search
        similar = await memory.semantic_search(
            query="Python API with authentication",
            namespace="test_project",
            limit=5
        )
        
        console.print(f"Found {len(similar)} similar memories")
        for mem in similar:
            console.print(f"  - {mem['content'][:50]}... (score: {mem['similarity_score']:.3f})")
        
        # Test contextual insights
        insights = await memory.get_contextual_insights(
            current_context={
                'goal': 'build secure API',
                'phase': 'implementation',
                'requirements': ['authentication', 'database', 'security']
            },
            namespace="test_project"
        )
        
        console.print(f"Generated {len(insights)} insights")
        for insight in insights:
            console.print(f"  - {insight.insight_text}")
    
    # Uncomment to test:
    # asyncio.run(test_memory_manager())