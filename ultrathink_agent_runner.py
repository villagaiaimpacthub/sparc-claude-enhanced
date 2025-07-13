#!/usr/bin/env python3
"""
Ultrathink Agent Runner - Comprehensive solution for all SPARC agent interfaces
Detects and adapts to both CLI and JSON agent interfaces automatically
"""

import os
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from datetime import datetime

console = Console()

class UltrathinkAgentRunner:
    """Intelligent agent runner that adapts to all agent interface types"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.agents_dir = self.base_path / "agents"
        
        # Agent interface detection patterns
        self.cli_patterns = [
            '@click.command()',
            'click.option',
            'argparse',
            '--namespace'
        ]
        
        self.json_patterns = [
            'json.loads(task_json)',
            'sys.argv[1]',
            'task_json = sys.argv[1]',
            'TaskPayload('
        ]
    
    def detect_agent_interface(self, agent_path: Path) -> str:
        """Detect whether agent uses CLI or JSON interface"""
        
        if not agent_path.exists():
            return 'unknown'
        
        try:
            content = agent_path.read_text()
            
            cli_score = sum(1 for pattern in self.cli_patterns if pattern in content)
            json_score = sum(1 for pattern in self.json_patterns if pattern in content)
            
            if cli_score > json_score:
                return 'cli'
            elif json_score > cli_score:
                return 'json'
            else:
                # Default heuristic: orchestrators are CLI, others are JSON
                if 'orchestrators' in str(agent_path):
                    return 'cli'
                else:
                    return 'json'
                    
        except Exception as e:
            console.print(f"⚠️ Could not analyze {agent_path}: {e}")
            return 'unknown'
    
    def run_cli_agent(self, agent_path: Path, namespace: str, **kwargs) -> Dict[str, Any]:
        """Run CLI-interface agent with proper arguments"""
        
        cmd = ['uv', 'run', str(agent_path), '--namespace', namespace]
        
        # Add only supported CLI arguments (avoid --phase which isn't supported)
        supported_args = ['goal', 'task-id', 'task_id']
        for key, value in kwargs.items():
            if value is not None and key.replace('_', '-') in supported_args:
                cmd.extend([f'--{key.replace("_", "-")}', str(value)])
        
        return self._execute_command(cmd, agent_path)
    
    def run_json_agent(self, agent_path: Path, namespace: str, **kwargs) -> Dict[str, Any]:
        """Run JSON-interface agent with proper task payload"""
        
        # Create proper task payload for JSON agents with ALL required fields
        task_payload = {
            "task_id": f"task_{datetime.now().isoformat()}",
            "description": kwargs.get('goal', 'Execute specialized task'),
            "context": {
                "namespace": namespace,
                "project_goal": kwargs.get('goal', ''),
                "timestamp": datetime.now().isoformat(),
                **kwargs
            },
            "requirements": [
                "Generate high-quality output",
                "Follow SPARC methodology",
                "Include proper documentation"
            ],
            "ai_verifiable_outcomes": [
                "Task completed successfully",
                "Output meets quality standards",
                "Documentation is comprehensive"
            ],
            "phase": kwargs.get('phase', 'execution'),
            "priority": kwargs.get('priority', 5)
        }
        
        # Convert to JSON string
        task_json = json.dumps(task_payload)
        
        cmd = ['uv', 'run', str(agent_path), task_json]
        
        return self._execute_command(cmd, agent_path)
    
    def _execute_command(self, cmd: List[str], agent_path: Path) -> Dict[str, Any]:
        """Execute command and return structured result"""
        
        console.print(f"🤖 Running: {agent_path.name}")
        console.print(f"📋 Command: {' '.join(cmd[:4])}{'...' if len(cmd) > 4 else ''}")
        
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
                console.print(f"✅ {agent_path.name} completed successfully")
            else:
                console.print(f"❌ {agent_path.name} failed with code {result.returncode}")
                if result.stderr:
                    console.print(f"  Error: {result.stderr[:200]}...")
            
            return {
                'success': success,
                'returncode': result.returncode,
                'output': result.stdout,
                'stderr': result.stderr,
                'agent_path': str(agent_path),
                'interface_type': 'detected'
            }
            
        except subprocess.TimeoutExpired:
            console.print(f"⏰ {agent_path.name} timed out")
            return {
                'success': False,
                'error': 'Timeout',
                'output': '',
                'stderr': 'Agent execution timed out after 5 minutes'
            }
        except Exception as e:
            console.print(f"💥 Error running {agent_path.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'stderr': str(e)
            }
    
    def run_agent_smart(self, agent_path: str, namespace: str, **kwargs) -> Dict[str, Any]:
        """Smart agent runner that auto-detects interface type"""
        
        # Convert to Path object
        if not agent_path.startswith('/'):
            full_path = self.base_path / agent_path
        else:
            full_path = Path(agent_path)
        
        if not full_path.exists():
            return {
                'success': False,
                'error': f"Agent not found: {full_path}",
                'interface_type': 'unknown'
            }
        
        # Detect interface type
        interface_type = self.detect_agent_interface(full_path)
        console.print(f"🔍 Detected interface: {interface_type}")
        
        # Call appropriate runner
        if interface_type == 'cli':
            result = self.run_cli_agent(full_path, namespace, **kwargs)
        elif interface_type == 'json':
            result = self.run_json_agent(full_path, namespace, **kwargs)
        else:
            # Try CLI first, then JSON if it fails
            console.print("🔄 Unknown interface, trying CLI first...")
            result = self.run_cli_agent(full_path, namespace, **kwargs)
            
            if not result['success'] and 'unrecognized arguments' in result.get('stderr', ''):
                console.print("🔄 CLI failed, trying JSON interface...")
                result = self.run_json_agent(full_path, namespace, **kwargs)
        
        result['interface_type'] = interface_type
        return result
    
    def fix_prerequisite_checking(self, namespace: str) -> Dict[str, Any]:
        """Fix prerequisite checking by ensuring files are properly registered"""
        
        console.print("🔧 [bold blue]Fixing Prerequisite Checking System[/bold blue]")
        
        # Check what files actually exist
        docs_dir = self.base_path / "docs"
        existing_files = []
        
        if docs_dir.exists():
            for file_path in docs_dir.rglob("*.md"):
                existing_files.append(str(file_path.relative_to(self.base_path)))
        
        console.print(f"📁 Found {len(existing_files)} documentation files:")
        for file_path in existing_files[:5]:  # Show first 5
            console.print(f"  ✅ {file_path}")
        
        # Create file registry for agents to use
        file_registry = {
            'project_files': {file_path: True for file_path in existing_files},
            'namespace': namespace,
            'last_updated': datetime.now().isoformat()
        }
        
        # Save registry
        registry_path = self.base_path / f".sparc_file_registry_{namespace}.json"
        with open(registry_path, 'w') as f:
            json.dump(file_registry, f, indent=2)
        
        console.print(f"📝 Created file registry: {registry_path}")
        
        return {
            'success': True,
            'files_found': len(existing_files),
            'registry_path': str(registry_path)
        }
    
    def run_complete_workflow_ultrathink(self, namespace: str, goal: str) -> Dict[str, Any]:
        """Run complete workflow with Ultrathink intelligence"""
        
        console.print("🧠 [bold blue]Ultrathink Complete Workflow Execution[/bold blue]")
        console.print(f"🎯 Goal: {goal}")
        console.print(f"🏷️ Namespace: {namespace}")
        
        # Phase 1: Fix prerequisite system
        prereq_result = self.fix_prerequisite_checking(namespace)
        
        # Phase 2: Execute workflow with smart agent detection
        phases = [
            ('agents/orchestrators/goal_clarification.py', 'Goal Clarification'),
            ('agents/orchestrators/specification_phase.py', 'Specification'),
            ('agents/enhanced/bmo_holistic_intent_verifier_enhanced.py', 'BMO Verification'),
            ('agents/writers/spec_writer_comprehensive.py', 'Specification Writing'),
            ('agents/orchestrators/architecture_phase.py', 'Architecture Design'),
        ]
        
        results = {}
        successful_phases = 0
        
        for agent_path, phase_name in phases:
            console.print(f"\\n🚀 [bold]Phase: {phase_name}[/bold]")
            
            result = self.run_agent_smart(
                agent_path, 
                namespace, 
                goal=goal,
                phase=phase_name.lower().replace(' ', '_')
            )
            
            results[phase_name] = result
            
            if result['success']:
                successful_phases += 1
                console.print(f"✅ {phase_name} completed successfully")
            else:
                console.print(f"❌ {phase_name} failed: {result.get('error', 'Unknown error')}")
                
                # Show some output for debugging
                if result.get('stderr'):
                    error_lines = result['stderr'].split('\\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            console.print(f"  📄 {line}")
            
            time.sleep(1)  # Brief pause between phases
        
        # Phase 3: Summary
        console.print(f"\\n🎉 [bold]Ultrathink Workflow Complete![/bold]")
        console.print(f"  ✅ Successful phases: {successful_phases}/{len(phases)}")
        console.print(f"  📊 Success rate: {(successful_phases/len(phases)*100):.1f}%")
        
        if successful_phases >= len(phases) * 0.8:
            console.print("\\n🧠 [bold green]Ultrathink Analysis: SYSTEM HIGHLY FUNCTIONAL![/bold green]")
        else:
            console.print("\\n🧠 [bold yellow]Ultrathink Analysis: System needs targeted fixes[/bold yellow]")
        
        return {
            'success': successful_phases >= len(phases) * 0.8,
            'successful_phases': successful_phases,
            'total_phases': len(phases),
            'phase_results': results,
            'prerequisite_fix': prereq_result
        }

def main():
    """CLI interface for Ultrathink Agent Runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultrathink SPARC Agent Runner")
    parser.add_argument('--namespace', required=True, help='Project namespace')
    parser.add_argument('--goal', required=True, help='Project goal')
    parser.add_argument('--agent', help='Specific agent to run')
    parser.add_argument('--workflow', action='store_true', help='Run complete workflow')
    parser.add_argument('--fix-prereqs', action='store_true', help='Fix prerequisite checking')
    
    args = parser.parse_args()
    
    runner = UltrathinkAgentRunner()
    
    if args.fix_prereqs:
        result = runner.fix_prerequisite_checking(args.namespace)
        sys.exit(0 if result['success'] else 1)
    
    if args.workflow:
        result = runner.run_complete_workflow_ultrathink(args.namespace, args.goal)
        sys.exit(0 if result['success'] else 1)
    
    if args.agent:
        result = runner.run_agent_smart(args.agent, args.namespace, goal=args.goal)
        sys.exit(0 if result['success'] else 1)
    
    parser.print_help()

if __name__ == "__main__":
    main()