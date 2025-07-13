#!/usr/bin/env python3
"""
Research utilities for SPARC agents
Provides AI-powered research capabilities via Perplexity AI
"""

import os
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from rich.console import Console
from .security import get_security_manager

console = Console()

class PerplexityResearcher:
    """Perplexity AI research interface for SPARC agents"""
    
    def __init__(self):
        self.security = get_security_manager()
        self.api_key = self.security.get_api_key("perplexity")
        self.base_url = "https://api.perplexity.ai"
        
        if not self.api_key:
            console.print("⚠️  [yellow]PERPLEXITY_API_KEY not configured. Research features will be limited.[/yellow]")
            console.print("   Add your API key to .env file: PERPLEXITY_API_KEY=sk-or-v1-...")
    
    async def search(self, query: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Perform AI-powered research search via Perplexity"""
        if not self.api_key:
            return {
                "success": False,
                "error": "PERPLEXITY_API_KEY not configured",
                "content": "Research search unavailable - API key required"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Provide comprehensive, well-sourced information with citations. Focus on accuracy and depth."
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1,
                "top_p": 0.9,
                "search_domain_filter": ["perplexity.ai"],
                "return_citations": True,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Extract citations if available
                    citations = self._extract_citations(result)
                    
                    return {
                        "success": True,
                        "content": content,
                        "citations": citations,
                        "usage": result.get("usage", {}),
                        "model": result.get("model", "unknown")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed: {response.status_code}",
                        "content": f"Error: {response.text}"
                    }
                    
        except Exception as e:
            console.print(f"❌ [red]Research search failed: {str(e)}[/red]")
            return {
                "success": False,
                "error": str(e),
                "content": "Research search failed due to technical error"
            }
    
    def _extract_citations(self, api_response: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract citations from Perplexity API response"""
        citations = []
        
        # Perplexity includes citations in the response
        if "citations" in api_response:
            citations = api_response["citations"]
        
        # Also check for inline citations in content
        content = api_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract [1], [2], etc. style citations
        import re
        citation_pattern = r'\[(\d+)\]'
        citation_nums = re.findall(citation_pattern, content)
        
        # Return structured citations
        return citations
    
    async def multi_perspective_research(self, topic: str, perspectives: List[str]) -> Dict[str, Any]:
        """Research a topic from multiple perspectives"""
        results = {}
        
        console.print(f"🔍 [cyan]Researching '{topic}' from {len(perspectives)} perspectives...[/cyan]")
        
        for perspective in perspectives:
            query = f"Research {topic} from the perspective of {perspective}. Provide detailed analysis, key insights, and current trends."
            
            console.print(f"   📋 [dim]Perspective: {perspective}[/dim]")
            result = await self.search(query)
            
            results[perspective] = result
            
            # Brief pause between requests
            await asyncio.sleep(1)
        
        return {
            "topic": topic,
            "perspectives": results,
            "summary": self._synthesize_perspectives(results)
        }
    
    def _synthesize_perspectives(self, perspective_results: Dict[str, Any]) -> str:
        """Synthesize insights from multiple perspectives"""
        synthesis = "## Multi-Perspective Research Synthesis\n\n"
        
        for perspective, result in perspective_results.items():
            if result.get("success"):
                synthesis += f"### {perspective} Perspective\n"
                synthesis += f"{result['content'][:500]}...\n\n"
            else:
                synthesis += f"### {perspective} Perspective\n"
                synthesis += f"Research failed: {result.get('error', 'Unknown error')}\n\n"
        
        return synthesis
    
    async def validate_information(self, claim: str) -> Dict[str, Any]:
        """Validate a specific claim or piece of information"""
        query = f"Fact-check and validate this claim with recent sources: {claim}"
        
        result = await self.search(query)
        
        if result.get("success"):
            # Add validation metadata
            result["validation_type"] = "fact_check"
            result["original_claim"] = claim
        
        return result

# Global researcher instance
_researcher_instance = None

def get_researcher() -> PerplexityResearcher:
    """Get singleton researcher instance"""
    global _researcher_instance
    if _researcher_instance is None:
        _researcher_instance = PerplexityResearcher()
    return _researcher_instance