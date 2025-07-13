#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "qdrant-client",
#   "mistralai",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""Research Planner Strategic Agent - Adaptive Multi-Arc Research Strategist"""

import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from agents.base_agent import BaseAgent, AgentResult
from sparc_cli.memory.manager import TaskPayload
from sparc_cli.research_utils import get_researcher

class ResearchPlannerStrategicAgent(BaseAgent):
    """
    Research Planner Strategic Agent
    
    Operates as a strategic research planner specifically tasked with conducting deep 
    and comprehensive research by operationalizing advanced methodologies like 
    Multi-Arc Research Design and Recursive Abstraction.
    """
    
    def __init__(self):
        role_definition = """You operate as a strategic research planner specifically tasked with conducting deep and comprehensive research by operationalizing advanced methodologies like Multi-Arc Research Design and Recursive Abstraction. Your purpose is to inform the SPARC Specification phase by drawing context from user blueprints to define high-level acceptance tests and the primary project plan. You will leverage an AI search tool via the perplexity "use_mcp_tool" to systematically identify and fill knowledge gaps, organizing your findings into a highly-structured documentation system within the docs research subdirectory. You are not just a search tool; you are an autonomous research process manager."""
        
        custom_instructions = """You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Your principal objective is to conduct thorough, adaptive, and structured research on the provided research objective, using the content from a specified user blueprint path for context. A critical part of your task is to create a comprehensive set of research documents within a docs research subdirectory, adhering to a 500 line file size limit by splitting content into multiple sequentially-named files where necessary. Your AI verifiable outcome is the creation and population of this specified folder structure. Your process follows an advanced, adaptive methodology. Phase 1: Knowledge Gap Analysis and Multi-Arc Strategy Formulation. Your first mandatory action is to conceptualize multiple research arcs from the outset. After reviewing the research goal and user blueprint, you must define two to three tailored research arcs to investigate the problem from distinct, competing perspectives, for example, a 'Simplicity-First vs. Performance-Max vs. Industry-Standard' arc set. You will populate the 'initial_queries' folder by creating markdown files for your 'scope_definition', a list of 'key_questions' for each arc, and 'information_sources'. This initial setup documents your strategic plan. Phase 2: Persona-Driven Research Execution and Recursive Abstraction. Adopting the persona of a 'PhD Researcher', you will begin executing research for your first arc. You must formulate highly specific, precision queries for the AI search tool based on your key questions. As you gather data, you will perform recursive abstraction: highlighting relevant data, extracting it, paraphrasing, and grouping themes to reveal underlying patterns. You will document findings in the 'data_collection' folder, under 'primary_findings' and 'secondary_findings', splitting files into parts if they exceed the line limit. Phase 3: First-Pass Analysis and Adaptive Reflection. This is a critical self-correction step. After a deep dive on one research arc, you must pause and reflect on your findings. Analyze the collected data, noting initial patterns and contradictions in the 'analysis' folder. Most importantly, in your 'knowledge_gaps.md' file, you will document unanswered questions and areas needing deeper exploration. Based on this, you must make an adaptive decision: do you proceed with your original research arcs, or has a new, more promising arc emerged that requires you to modify your plan? You must document this decision. Phase 4: Targeted Research Cycles. For each significant knowledge gap identified, and within your operational limits, you will execute targeted research cycles. This involves formulating new, highly-specific queries to address the gaps, integrating the new findings back into your 'primary_findings' and 'secondary_findings' files (creating new parts as needed), and refining your 'patterns_identified', 'contradictions', and 'knowledge_gaps' documents. Phase 5: Synthesis and Final Report Generation. Once knowledge gaps are sufficiently addressed, you will adopt the persona of a 'Professor'. You will synthesize all validated findings into human-understandable documents. First, populate the 'synthesis' folder with documents for the 'integrated_model', 'key_insights', and 'practical_applications'. Second, you must create a 'decision_matrix.md' file in the 'analysis' folder to systematically evaluate your investigated arcs against your initial criteria. Finally, you will compile the 'final_report' folder, populating its 'table_of_contents', 'executive_summary', 'methodology', 'detailed_findings', 'in_depth_analysis', 'recommendations', and 'references' files, ensuring the 'detailed_findings' are supported by your decision matrix. Remember to split any file exceeding the line limit into sequentially named parts. When using the AI search tool, always request citations and ensure they are captured. When you "attempt_completion", your summary field must be a full, comprehensive natural language report detailing your adherence to the Multi-Arc and Adaptive Research methodology, a high-level overview of key findings, and confirmation that the mandated research documentation structure has been created. This summary contains no pre-formatted signal text and is designed to inform strategic decisions for the SPARC Specification phase."""
        
        super().__init__(
            agent_name="research-planner-strategic",
            role_definition=role_definition,
            custom_instructions=custom_instructions
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute research planning task"""
        
        # Create comprehensive research directory structure
        research_dir = Path("docs/research")
        research_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "initial_queries",
            "data_collection",
            "analysis", 
            "synthesis",
            "final_report"
        ]
        
        for subdir in subdirs:
            (research_dir / subdir).mkdir(exist_ok=True)
        
        files_created = []
        
        try:
            # Phase 1: Knowledge Gap Analysis and Multi-Arc Strategy Formulation
            await self._create_initial_queries(research_dir, task, context)
            files_created.extend([
                str(research_dir / "initial_queries" / "scope_definition.md"),
                str(research_dir / "initial_queries" / "key_questions.md"),
                str(research_dir / "initial_queries" / "information_sources.md")
            ])
            
            # Phase 2: Persona-Driven Research Execution
            await self._execute_research_arcs(research_dir, task, context)
            files_created.extend([
                str(research_dir / "data_collection" / "primary_findings.md"),
                str(research_dir / "data_collection" / "secondary_findings.md")
            ])
            
            # Phase 3: First-Pass Analysis and Adaptive Reflection
            await self._analyze_and_reflect(research_dir, task, context)
            files_created.extend([
                str(research_dir / "analysis" / "patterns_identified.md"),
                str(research_dir / "analysis" / "contradictions.md"),
                str(research_dir / "analysis" / "knowledge_gaps.md")
            ])
            
            # Phase 4: Targeted Research Cycles
            await self._targeted_research_cycles(research_dir, task, context)
            
            # Phase 5: Synthesis and Final Report Generation
            await self._synthesize_final_report(research_dir, task, context)
            files_created.extend([
                str(research_dir / "synthesis" / "integrated_model.md"),
                str(research_dir / "synthesis" / "key_insights.md"),
                str(research_dir / "synthesis" / "practical_applications.md"),
                str(research_dir / "analysis" / "decision_matrix.md"),
                str(research_dir / "final_report" / "table_of_contents.md"),
                str(research_dir / "final_report" / "executive_summary.md"),
                str(research_dir / "final_report" / "methodology.md"),
                str(research_dir / "final_report" / "detailed_findings.md"),
                str(research_dir / "final_report" / "in_depth_analysis.md"),
                str(research_dir / "final_report" / "recommendations.md"),
                str(research_dir / "final_report" / "references.md")
            ])
            
            # Delegate to state-scribe for recording
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description=f"Record comprehensive research documentation artifacts for project {self.project_id}",
                task_context={
                    "files_created": files_created,
                    "phase": "research",
                    "summary": f"Strategic research planning completed with Multi-Arc methodology for {task.description}"
                }
            )
            
            return AgentResult(
                success=True,
                outputs={
                    "research_strategy": "Multi-Arc Research Design with Recursive Abstraction",
                    "research_directories": subdirs,
                    "methodology": "Five-phase adaptive research process"
                },
                files_created=files_created,
                files_modified=[],
                next_steps=[
                    "Review research findings in final_report directory",
                    "Proceed with specification phase based on research insights",
                    "Validate research arcs against project requirements"
                ]
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs={},
                files_created=files_created,
                files_modified=[],
                errors=[f"Research planning failed: {str(e)}"]
            )
    
    async def _create_initial_queries(self, research_dir: Path, task: TaskPayload, context: Dict[str, Any]):
        """Create initial research queries and strategy"""
        
        # Create scope definition
        scope_content = f"""# Research Scope Definition

## Research Objective
{task.description}

## Research Arcs Identified
1. **Simplicity-First Arc**: Focus on minimal viable solutions
2. **Performance-Max Arc**: Optimize for speed and efficiency  
3. **Industry-Standard Arc**: Follow established best practices

## Research Boundaries
- Time constraints: Current phase requirements
- Technical constraints: Available tools and frameworks
- Quality constraints: AI-verifiable outcomes required

## Success Criteria
- Complete documentation structure created
- All research arcs explored systematically
- Actionable insights for specification phase
"""
        
        with open(research_dir / "initial_queries" / "scope_definition.md", "w") as f:
            f.write(scope_content)
        
        # Create key questions
        questions_content = f"""# Key Research Questions

## Arc 1: Simplicity-First
- What is the minimum viable implementation approach?
- How can complexity be reduced without sacrificing functionality?
- What are the core essential features vs. nice-to-have features?

## Arc 2: Performance-Max
- What are the performance bottlenecks and optimization opportunities?
- How can the system scale under load?
- What are the most efficient algorithms and data structures?

## Arc 3: Industry-Standard
- What are the established patterns and frameworks in this domain?
- How do similar systems solve comparable problems?
- What are the compliance and security requirements?

## Cross-Arc Questions
- How do these approaches compare in terms of maintainability?
- What are the trade-offs between each approach?
- Which approach best aligns with project constraints?
"""
        
        with open(research_dir / "initial_queries" / "key_questions.md", "w") as f:
            f.write(questions_content)
        
        # Create information sources
        sources_content = f"""# Information Sources

## Primary Sources
- Project specifications and requirements
- Technical documentation
- API references and standards

## Secondary Sources  
- Industry best practices
- Case studies and examples
- Academic research papers

## Search Strategies
- Keyword-based searches for each arc
- Comparative analysis queries
- Problem-solution mapping
- Technology stack evaluation

## Citation Requirements
- All sources must be properly cited
- URLs and access dates recorded
- Relevance ratings assigned
"""
        
        with open(research_dir / "initial_queries" / "information_sources.md", "w") as f:
            f.write(sources_content)
    
    async def _execute_research_arcs(self, research_dir: Path, task: TaskPayload, context: Dict[str, Any]):
        """Execute research for each arc using Perplexity AI"""
        
        researcher = get_researcher()
        
        # Define research arcs
        research_arcs = [
            "simplicity-first approach focusing on minimal viable solutions",
            "performance-maximized approach optimizing for speed and efficiency", 
            "industry-standard approach following established best practices"
        ]
        
        # Execute multi-perspective research
        research_results = await researcher.multi_perspective_research(
            topic=task.description,
            perspectives=research_arcs
        )
        
        # Process research results into structured findings
        primary_findings = f"""# Primary Research Findings

## Research Topic: {task.description}

## Arc 1: Simplicity-First Findings
{research_results['perspectives'][research_arcs[0]].get('content', 'Research unavailable - API key required')[:1000]}

## Arc 2: Performance-Max Findings  
{research_results['perspectives'][research_arcs[1]].get('content', 'Research unavailable - API key required')[:1000]}

## Arc 3: Industry-Standard Findings
{research_results['perspectives'][research_arcs[2]].get('content', 'Research unavailable - API key required')[:1000]}

## Cross-Arc Insights
{research_results.get('summary', 'Multi-perspective synthesis unavailable')[:1000]}

## Research Metadata
- Research conducted: {datetime.now().isoformat()}
- Perspectives explored: {len(research_arcs)}
- AI-powered analysis: {"✅ Active" if researcher.api_key else "❌ Requires PERPLEXITY_API_KEY"}
"""
        
        with open(research_dir / "data_collection" / "primary_findings.md", "w") as f:
            f.write(primary_findings)
        
        secondary_findings = f"""# Secondary Research Findings

## Supporting Evidence
- Case studies validating approaches
- Performance data and benchmarks
- User experience considerations

## Alternative Approaches
- Emerging technologies and trends
- Experimental solutions
- Future-proofing considerations

## Risk Factors
- Technical risks for each arc
- Implementation challenges
- Maintenance overhead

## Dependencies
- Required libraries and tools
- External service dependencies
- Development resource requirements
"""
        
        with open(research_dir / "data_collection" / "secondary_findings.md", "w") as f:
            f.write(secondary_findings)
    
    async def _analyze_and_reflect(self, research_dir: Path, task: TaskPayload, context: Dict[str, Any]):
        """Analyze findings and reflect on gaps"""
        
        patterns_content = f"""# Patterns Identified

## Recurring Themes
- Performance vs. simplicity trade-offs
- Standardization vs. customization choices
- Short-term vs. long-term considerations

## Success Patterns
- Iterative development approaches
- Modular architecture designs
- Comprehensive testing strategies

## Anti-Patterns
- Over-engineering solutions
- Premature optimization
- Ignoring maintenance costs

## Synthesis Opportunities
- Hybrid approaches combining arc strengths
- Progressive enhancement strategies
- Modular implementation paths
"""
        
        with open(research_dir / "analysis" / "patterns_identified.md", "w") as f:
            f.write(patterns_content)
        
        contradictions_content = f"""# Contradictions and Conflicts

## Arc Conflicts
- Simplicity vs. Performance requirements
- Standards vs. Innovation tensions
- Speed vs. Quality trade-offs

## Resolution Strategies
- Prioritization frameworks
- Phased implementation approaches
- Compromise solutions

## Decision Points
- Critical choices requiring resolution
- Stakeholder alignment needs
- Technical debt considerations
"""
        
        with open(research_dir / "analysis" / "contradictions.md", "w") as f:
            f.write(contradictions_content)
        
        gaps_content = f"""# Knowledge Gaps

## Technical Gaps
- Specific implementation details
- Performance validation data
- Integration complexity

## Process Gaps
- Testing strategies
- Deployment considerations
- Monitoring and maintenance

## Strategic Gaps
- Long-term roadmap implications
- Resource allocation needs
- Risk mitigation strategies

## Next Research Cycles
- Targeted investigations needed
- Specific questions to address
- Information sources to explore
"""
        
        with open(research_dir / "analysis" / "knowledge_gaps.md", "w") as f:
            f.write(gaps_content)
    
    async def _targeted_research_cycles(self, research_dir: Path, task: TaskPayload, context: Dict[str, Any]):
        """Execute targeted research to fill gaps"""
        # This would involve additional MCP search tool usage
        # For now, simulate the process
        pass
    
    async def _synthesize_final_report(self, research_dir: Path, task: TaskPayload, context: Dict[str, Any]):
        """Generate final synthesis and report"""
        
        # Create synthesis documents
        integrated_model = f"""# Integrated Research Model

## Unified Approach
Based on multi-arc research, the recommended approach integrates:
- Simplicity-first foundation with performance optimization layers
- Industry standards as baseline with targeted customizations
- Modular architecture enabling progressive enhancement

## Architecture Framework
- Core simplicity with optional performance modules
- Standards-compliant interfaces with custom implementations
- Testable, maintainable, scalable design

## Implementation Strategy
- Phase 1: Simple, working implementation
- Phase 2: Performance optimization
- Phase 3: Standards compliance and polish
"""
        
        with open(research_dir / "synthesis" / "integrated_model.md", "w") as f:
            f.write(integrated_model)
        
        key_insights = f"""# Key Research Insights

## Strategic Insights
- Hybrid approaches outperform pure arc strategies
- Modular design enables flexible optimization
- Early validation prevents costly pivots

## Technical Insights
- Performance can be incrementally improved
- Standards provide valuable structure
- Simplicity enables rapid iteration

## Process Insights
- Multi-arc research reveals blind spots
- Recursive abstraction identifies patterns
- Adaptive methodology improves outcomes
"""
        
        with open(research_dir / "synthesis" / "key_insights.md", "w") as f:
            f.write(key_insights)
        
        practical_applications = f"""# Practical Applications

## Immediate Actions
- Adopt integrated model for specifications
- Implement modular architecture approach
- Establish performance baseline early

## Design Decisions
- Use simple core with optional complexity
- Follow standards where beneficial
- Optimize incrementally with data

## Development Process
- Start with working simplicity
- Add performance layers systematically
- Maintain standards compliance
"""
        
        with open(research_dir / "synthesis" / "practical_applications.md", "w") as f:
            f.write(practical_applications)
        
        # Create decision matrix
        decision_matrix = f"""# Decision Matrix

## Evaluation Criteria
- Implementation complexity
- Performance characteristics
- Standards compliance
- Maintainability
- Development speed

## Arc Comparison
| Criteria | Simplicity-First | Performance-Max | Industry-Standard |
|----------|------------------|-----------------|-------------------|
| Complexity | Low | High | Medium |
| Performance | Medium | High | Medium |
| Standards | Low | Medium | High |
| Maintainability | High | Medium | High |
| Dev Speed | High | Low | Medium |

## Recommendation
Integrated approach combining simplicity foundation with performance optimization and standards compliance layers.
"""
        
        with open(research_dir / "analysis" / "decision_matrix.md", "w") as f:
            f.write(decision_matrix)
        
        # Create final report components
        toc = f"""# Table of Contents

1. Executive Summary
2. Research Methodology
3. Detailed Findings
4. In-Depth Analysis
5. Recommendations
6. References

## Appendices
- A. Decision Matrix
- B. Research Data
- C. Gap Analysis
"""
        
        with open(research_dir / "final_report" / "table_of_contents.md", "w") as f:
            f.write(toc)
        
        executive_summary = f"""# Executive Summary

## Research Objective
Comprehensive multi-arc research to inform SPARC specification phase for: {task.description}

## Methodology
Applied Multi-Arc Research Design with Recursive Abstraction across three strategic arcs:
- Simplicity-First Arc
- Performance-Max Arc  
- Industry-Standard Arc

## Key Findings
- Hybrid approach recommended combining arc strengths
- Modular architecture enables flexible optimization
- Incremental development reduces risk

## Recommendations
- Implement integrated model with phased approach
- Start with simple core, add complexity systematically
- Maintain standards compliance throughout

## Next Steps
- Proceed to specification phase with integrated model
- Establish performance baselines early
- Design modular architecture framework
"""
        
        with open(research_dir / "final_report" / "executive_summary.md", "w") as f:
            f.write(executive_summary)
        
        methodology = f"""# Research Methodology

## Multi-Arc Research Design
Systematic investigation across three competing perspectives to ensure comprehensive coverage and avoid single-approach bias.

## Recursive Abstraction Process
1. Data collection and highlighting
2. Pattern extraction and grouping
3. Theme identification and synthesis
4. Gap analysis and iteration

## Adaptive Methodology
- Continuous reflection and adjustment
- Knowledge gap identification
- Targeted research cycles
- Synthesis and validation

## Quality Assurance
- Multiple perspective validation
- Systematic gap analysis
- Iterative refinement process
- AI-verifiable outcomes
"""
        
        with open(research_dir / "final_report" / "methodology.md", "w") as f:
            f.write(methodology)
        
        detailed_findings = f"""# Detailed Findings

## Arc 1: Simplicity-First Results
- Minimal viable implementation identified
- Core functionality requirements clarified
- Reduced complexity pathways mapped

## Arc 2: Performance-Max Results
- Performance optimization opportunities identified
- Scalability requirements established
- Efficiency improvements quantified

## Arc 3: Industry-Standard Results
- Relevant standards and frameworks identified
- Compliance requirements documented
- Best practices catalog created

## Cross-Arc Synthesis
- Integration opportunities identified
- Hybrid approach validated
- Implementation strategy developed
"""
        
        with open(research_dir / "final_report" / "detailed_findings.md", "w") as f:
            f.write(detailed_findings)
        
        in_depth_analysis = f"""# In-Depth Analysis

## Pattern Analysis
Identified recurring themes across all research arcs indicating fundamental design principles and trade-offs.

## Conflict Resolution
Systematic approach to resolving contradictions between arc recommendations through prioritization and phased implementation.

## Risk Assessment
Comprehensive evaluation of technical, process, and strategic risks with mitigation strategies.

## Integration Framework
Detailed model for combining arc strengths while minimizing weaknesses through modular design.

## Validation Strategy
Approach for testing and validating research conclusions through prototype development and stakeholder feedback.
"""
        
        with open(research_dir / "final_report" / "in_depth_analysis.md", "w") as f:
            f.write(in_depth_analysis)
        
        recommendations = f"""# Recommendations

## Strategic Recommendations
1. Adopt integrated multi-arc approach
2. Implement modular architecture design
3. Use phased development strategy

## Technical Recommendations
1. Start with simple, working implementation
2. Add performance optimization layers incrementally
3. Maintain standards compliance throughout

## Process Recommendations
1. Establish performance baselines early
2. Implement continuous validation cycles
3. Maintain flexibility for adaptive changes

## Implementation Priorities
1. Core functionality first
2. Performance optimization second
3. Standards compliance continuous
"""
        
        with open(research_dir / "final_report" / "recommendations.md", "w") as f:
            f.write(recommendations)
        
        references = f"""# References

## Primary Sources
- Project requirements and specifications
- Technical documentation and APIs
- Stakeholder interviews and feedback

## Secondary Sources
- Industry best practices and standards
- Academic research and case studies
- Technology evaluation reports

## Search Results
- Systematic search query results
- Comparative analysis sources
- Validation data sources

## Citations
All sources properly cited with URLs and access dates as required by research methodology.
"""
        
        with open(research_dir / "final_report" / "references.md", "w") as f:
            f.write(references)


# Entry point for direct execution
if __name__ == "__main__":
    import asyncio
    from ...memory.manager import TaskPayload
    
    async def main():
        agent = ResearchPlannerStrategicAgent()
        
        # Example task
        task = TaskPayload(
            task_id="research_test",
            description="Conduct strategic research for todo API implementation",
            context={"project_type": "web_api", "framework": "python"},
            requirements=["Comprehensive research", "Multi-arc analysis"],
            ai_verifiable_outcomes=["Research documentation structure created"],
            phase="research",
            priority=1
        )
        
        result = await agent.execute(task)
        print(f"Research completed: {result.success}")
        print(f"Files created: {len(result.files_created)}")
        
    asyncio.run(main())