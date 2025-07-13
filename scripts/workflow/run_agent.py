#!/usr/bin/env python3
"""
Universal agent runner that works with UV for all 36 SPARC agents
Fixes UV execution issues and provides consistent agent interface
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console

console = Console()

class UniversalAgentRunner:
    """Universal runner for all SPARC agents"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.agents_dir = self.base_path / "agents"
        
    def run_agent(self, agent_path: str, namespace: str, **kwargs) -> Dict[str, Any]:
        """Run any SPARC agent with proper UV execution"""
        
        # Convert relative path to absolute
        if not agent_path.startswith('/'):
            full_agent_path = self.base_path / agent_path
        else:
            full_agent_path = Path(agent_path)
        
        if not full_agent_path.exists():
            return {
                'success': False,
                'error': f"Agent not found: {full_agent_path}",
                'output': '',
                'stderr': ''
            }
        
        # Build command
        cmd = ['uv', 'run', str(full_agent_path), '--namespace', namespace]
        
        # Add additional arguments
        for key, value in kwargs.items():
            if key not in ['namespace']:  # Avoid duplicates
                cmd.extend([f'--{key}', str(value)])
        
        console.print(f"🤖 Running agent: {full_agent_path.name}")
        console.print(f"📋 Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.base_path
            )
            
            success = result.returncode == 0
            
            if success:
                console.print(f"✅ Agent {full_agent_path.name} completed successfully")
            else:
                console.print(f"❌ Agent {full_agent_path.name} failed with code {result.returncode}")
                if result.stderr:
                    console.print(f"  Error: {result.stderr[:200]}...")
            
            return {
                'success': success,
                'returncode': result.returncode,
                'output': result.stdout,
                'stderr': result.stderr,
                'agent_path': str(full_agent_path)
            }
            
        except subprocess.TimeoutExpired:
            console.print(f"⏰ Agent {full_agent_path.name} timed out")
            return {
                'success': False,
                'error': 'Timeout',
                'output': '',
                'stderr': 'Agent execution timed out after 5 minutes'
            }
        except Exception as e:
            console.print(f"💥 Error running agent {full_agent_path.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'stderr': str(e)
            }
    
    def run_orchestrator_phase(self, phase: str, namespace: str, **kwargs) -> Dict[str, Any]:
        """Run a specific orchestrator phase"""
        
        orchestrator_map = {
            'goal-clarification': 'agents/orchestrators/goal_clarification.py',
            'specification': 'agents/orchestrators/specification_phase.py',
            'pseudocode': 'agents/orchestrators/pseudocode_phase.py',
            'architecture': 'agents/orchestrators/architecture_phase.py',
            'implementation': 'agents/orchestrators/refinement_implementation.py',
            'testing': 'agents/orchestrators/refinement_testing.py',
            'documentation': 'agents/orchestrators/completion_documentation.py',
            'bmo-completion': 'agents/orchestrators/bmo_completion_phase.py'
        }
        
        agent_path = orchestrator_map.get(phase)
        if not agent_path:
            return {
                'success': False,
                'error': f"Unknown phase: {phase}",
                'available_phases': list(orchestrator_map.keys())
            }
        
        return self.run_agent(agent_path, namespace, **kwargs)
    
    def run_full_workflow(self, namespace: str, goal: str = None) -> Dict[str, Any]:
        """Run complete SPARC workflow through all phases"""
        
        console.print("🚀 [bold blue]Starting Full SPARC Autonomous Workflow[/bold blue]")
        console.print(f"🏷️ Namespace: {namespace}")
        if goal:
            console.print(f"🎯 Goal: {goal}")
        
        phases = [
            'goal-clarification',
            'specification', 
            'pseudocode',
            'architecture',
            'implementation',
            'testing',
            'documentation'
        ]
        
        results = {}
        failed_phase = None
        
        for phase in phases:
            console.print(f"\\n📋 [bold]Phase: {phase}[/bold]")
            
            # Add goal parameter for goal-clarification phase
            kwargs = {}
            if phase == 'goal-clarification' and goal:
                kwargs['goal'] = goal
            
            result = self.run_orchestrator_phase(phase, namespace, **kwargs)
            results[phase] = result
            
            if not result['success']:
                console.print(f"❌ Phase {phase} failed: {result.get('error', 'Unknown error')}")
                failed_phase = phase
                break
            else:
                console.print(f"✅ Phase {phase} completed successfully")
                
                # Show key outputs
                if result.get('output'):
                    lines = result['output'].strip().split('\\n')
                    for line in lines[-3:]:  # Show last 3 lines
                        if line.strip():
                            console.print(f"  📄 {line}")
            
            # Brief pause between phases
            time.sleep(1)
        
        # Summary
        console.print(f"\\n🎉 [bold]Workflow Summary[/bold]")
        
        if failed_phase:
            completed_phases = len([p for p in phases if p in results and results[p]['success']])
            console.print(f"  ⚠️ Completed {completed_phases}/{len(phases)} phases")
            console.print(f"  ❌ Failed at: {failed_phase}")
        else:
            console.print(f"  ✅ All {len(phases)} phases completed successfully!")
        
        return {
            'success': failed_phase is None,
            'completed_phases': len([p for p in phases if p in results and results[p]['success']]),
            'total_phases': len(phases),
            'failed_phase': failed_phase,
            'phase_results': results
        }
    
    def list_available_agents(self) -> Dict[str, List[str]]:
        """List all available agents by category"""
        
        categories = {}
        
        if self.agents_dir.exists():
            for category_dir in self.agents_dir.iterdir():
                if category_dir.is_dir() and not category_dir.name.startswith('.'):
                    agents = []
                    for agent_file in category_dir.glob('*.py'):
                        if agent_file.name != '__init__.py':
                            agents.append(agent_file.name)
                    
                    if agents:
                        categories[category_dir.name] = sorted(agents)
        
        return categories

def main():
    """CLI interface for universal agent runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal SPARC Agent Runner")
    parser.add_argument('--namespace', required=True, help='Project namespace')
    parser.add_argument('--phase', help='Orchestrator phase to run')
    parser.add_argument('--agent', help='Specific agent path to run')
    parser.add_argument('--goal', help='Project goal (for goal-clarification phase)')
    parser.add_argument('--workflow', action='store_true', help='Run full workflow')
    parser.add_argument('--list-agents', action='store_true', help='List available agents')
    
    args = parser.parse_args()
    
    runner = UniversalAgentRunner()
    
    if args.list_agents:
        agents = runner.list_available_agents()
        console.print("🤖 [bold]Available SPARC Agents[/bold]")
        for category, agent_list in agents.items():
            console.print(f"\\n📁 {category}:")
            for agent in agent_list:
                console.print(f"  • {agent}")
        return
    
    if args.workflow:
        result = runner.run_full_workflow(args.namespace, args.goal)
        sys.exit(0 if result['success'] else 1)
    
    if args.phase:
        result = runner.run_orchestrator_phase(args.phase, args.namespace, goal=args.goal)
        sys.exit(0 if result['success'] else 1)
    
    if args.agent:
        result = runner.run_agent(args.agent, args.namespace, goal=args.goal)
        sys.exit(0 if result['success'] else 1)
    
    parser.print_help()

if __name__ == "__main__":
    main()