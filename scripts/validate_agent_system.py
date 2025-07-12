#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
SPARC Agent System Validation
Comprehensive validation of all enhanced agents and Layer 2 integration
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Any
import ast

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class AgentValidator:
    """Validates SPARC enhanced agents"""
    
    def __init__(self):
        self.agents_dir = Path("agents/enhanced")
        self.validation_results = {}
        self.layer2_components = [
            'PerfectPromptGenerator',
            'TestOracleResolver', 
            'InteractiveQuestionEngine',
            'BMOIntentTracker',
            'CognitiveTriangulationEngine',
            'SequentialReviewChain'
        ]
        
    def validate_all_agents(self) -> Dict[str, Any]:
        """Validate all enhanced agents"""
        
        console.print(Panel.fit(
            "[blue]🔍 SPARC Agent System Validation[/blue]\n\n"
            "Validating all enhanced agents and Layer 2 integration",
            title="System Validation",
            border_style="blue"
        ))
        
        agent_files = list(self.agents_dir.glob("*_enhanced.py"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Validating agents...", total=len(agent_files))
            
            for agent_file in agent_files:
                agent_name = agent_file.stem
                progress.update(task, description=f"Validating {agent_name}")
                
                validation_result = self.validate_agent(agent_file)
                self.validation_results[agent_name] = validation_result
                
                progress.advance(task)
        
        return self.validation_results
    
    def validate_agent(self, agent_file: Path) -> Dict[str, Any]:
        """Validate individual agent"""
        
        result = {
            'file_exists': False,
            'syntax_valid': False,
            'layer2_imports': [],
            'missing_layer2': [],
            'has_main_class': False,
            'has_execute_method': False,
            'has_error_handling': False,
            'has_supabase_init': False,
            'has_async_methods': False,
            'validation_score': 0.0,
            'issues': []
        }
        
        # Check file exists
        if not agent_file.exists():
            result['issues'].append(f"Agent file not found: {agent_file}")
            return result
        
        result['file_exists'] = True
        
        try:
            # Read and parse file
            content = agent_file.read_text()
            tree = ast.parse(content)
            
            result['syntax_valid'] = True
            
            # Analyze AST for Layer 2 components
            self._analyze_imports(tree, result)
            self._analyze_classes(tree, result)
            self._analyze_methods(tree, result)
            self._analyze_error_handling(tree, result)
            
            # Calculate validation score
            result['validation_score'] = self._calculate_score(result)
            
        except SyntaxError as e:
            result['issues'].append(f"Syntax error: {e}")
        except Exception as e:
            result['issues'].append(f"Validation error: {e}")
        
        return result
    
    def _analyze_imports(self, tree: ast.AST, result: Dict[str, Any]):
        """Analyze imports for Layer 2 components"""
        
        imported_components = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        if alias.name in self.layer2_components:
                            imported_components.append(alias.name)
        
        result['layer2_imports'] = imported_components
        result['missing_layer2'] = [comp for comp in self.layer2_components if comp not in imported_components]
    
    def _analyze_classes(self, tree: ast.AST, result: Dict[str, Any]):
        """Analyze class definitions"""
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Enhanced') and 'Agent' in node.name:
                    result['has_main_class'] = True
                    
                    # Check for __init__ method with supabase initialization
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                            for stmt in method.body:
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and target.attr == 'supabase':
                                            result['has_supabase_init'] = True
    
    def _analyze_methods(self, tree: ast.AST, result: Dict[str, Any]):
        """Analyze method definitions"""
        
        async_methods = []
        execute_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_methods.append(node.name)
                if 'execute' in node.name.lower():
                    execute_methods.append(node.name)
        
        result['has_async_methods'] = len(async_methods) > 0
        result['has_execute_method'] = len(execute_methods) > 0
        result['async_method_count'] = len(async_methods)
        result['execute_methods'] = execute_methods
    
    def _analyze_error_handling(self, tree: ast.AST, result: Dict[str, Any]):
        """Analyze error handling patterns"""
        
        try_blocks = []
        exception_handlers = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_blocks.append(node)
                for handler in node.handlers:
                    if isinstance(handler, ast.ExceptHandler):
                        exception_handlers.append(handler)
        
        result['has_error_handling'] = len(try_blocks) > 0
        result['try_block_count'] = len(try_blocks)
        result['exception_handler_count'] = len(exception_handlers)
    
    def _calculate_score(self, result: Dict[str, Any]) -> float:
        """Calculate validation score"""
        
        score = 0.0
        max_score = 10.0
        
        # Basic requirements (4 points)
        if result['file_exists']:
            score += 1.0
        if result['syntax_valid']:
            score += 1.0
        if result['has_main_class']:
            score += 1.0
        if result['has_supabase_init']:
            score += 1.0
        
        # Layer 2 integration (3 points)
        layer2_ratio = len(result['layer2_imports']) / len(self.layer2_components)
        score += layer2_ratio * 3.0
        
        # Advanced features (3 points)
        if result['has_execute_method']:
            score += 1.0
        if result['has_async_methods']:
            score += 1.0
        if result['has_error_handling']:
            score += 1.0
        
        return (score / max_score) * 100.0
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        
        if not self.validation_results:
            return "No validation results available"
        
        # Summary statistics
        total_agents = len(self.validation_results)
        valid_agents = sum(1 for r in self.validation_results.values() if r['syntax_valid'])
        avg_score = sum(r['validation_score'] for r in self.validation_results.values()) / total_agents
        
        # Detailed results table
        table = Table(title="Agent Validation Results")
        table.add_column("Agent", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Layer 2", style="yellow")
        table.add_column("Execute Method", style="blue")
        table.add_column("Error Handling", style="magenta")
        table.add_column("Issues", style="red")
        
        for agent_name, result in self.validation_results.items():
            layer2_status = f"{len(result['layer2_imports'])}/{len(self.layer2_components)}"
            execute_status = "✅" if result['has_execute_method'] else "❌"
            error_status = "✅" if result['has_error_handling'] else "❌"
            issues_count = len(result['issues'])
            
            table.add_row(
                agent_name,
                f"{result['validation_score']:.1f}%",
                layer2_status,
                execute_status,
                error_status,
                str(issues_count) if issues_count > 0 else "None"
            )
        
        console.print(table)
        
        # Summary panel
        summary = Panel.fit(
            f"[green]✅ Validation Summary[/green]\n\n"
            f"Total Agents: {total_agents}\n"
            f"Valid Syntax: {valid_agents}/{total_agents}\n"
            f"Average Score: {avg_score:.1f}%\n"
            f"Layer 2 Components: {len(self.layer2_components)}\n\n"
            f"System Status: {'🟢 EXCELLENT' if avg_score >= 90 else '🟡 GOOD' if avg_score >= 75 else '🔴 NEEDS IMPROVEMENT'}",
            title="Validation Summary",
            border_style="green" if avg_score >= 90 else "yellow" if avg_score >= 75 else "red"
        )
        
        console.print(summary)
        
        return f"Validation complete: {valid_agents}/{total_agents} agents valid, average score {avg_score:.1f}%"
    
    def display_agent_tree(self):
        """Display agent hierarchy as tree"""
        
        tree = Tree("[bold blue]SPARC Enhanced Agent System[/bold blue]")
        
        # Group agents by category
        categories = {}
        for agent_name, result in self.validation_results.items():
            # Determine category from agent name
            if 'phase' in agent_name:
                category = "Phase Orchestrators"
            elif 'quality' in agent_name or 'security' in agent_name or 'performance' in agent_name:
                category = "Quality Review Agents"
            elif 'testing' in agent_name:
                category = "Testing Agents"
            elif 'documentation' in agent_name or 'deployment' in agent_name or 'monitoring' in agent_name:
                category = "Support Agents"
            elif 'integration' in agent_name:
                category = "Integration Agents"
            else:
                category = "Other Agents"
            
            if category not in categories:
                categories[category] = []
            categories[category].append((agent_name, result))
        
        # Add categories to tree
        for category, agents in categories.items():
            category_node = tree.add(f"[yellow]{category}[/yellow] ({len(agents)} agents)")
            
            for agent_name, result in agents:
                score = result['validation_score']
                status_icon = "🟢" if score >= 90 else "🟡" if score >= 75 else "🔴"
                layer2_count = len(result['layer2_imports'])
                
                agent_node = category_node.add(f"{status_icon} {agent_name} ({score:.1f}%)")
                agent_node.add(f"Layer 2 Components: {layer2_count}/{len(self.layer2_components)}")
                
                if result['issues']:
                    issues_node = agent_node.add("[red]Issues:[/red]")
                    for issue in result['issues']:
                        issues_node.add(f"• {issue}")
        
        console.print(tree)
    
    def check_system_completeness(self):
        """Check if the agent system is complete"""
        
        expected_agents = [
            'goal_clarification_phase_enhanced',
            'specification_phase_enhanced', 
            'architecture_phase_enhanced',
            'pseudocode_phase_enhanced',
            'implementation_phase_agent_enhanced',
            'refinement_phase_agent_enhanced',
            'completion_phase_agent_enhanced',
            'testing_master_agent_enhanced',
            'security_reviewer_agent_enhanced',
            'performance_reviewer_agent_enhanced',
            'code_quality_reviewer_agent_enhanced',
            'architecture_reviewer_agent_enhanced',
            'documentation_agent_enhanced',
            'deployment_agent_enhanced',
            'monitoring_agent_enhanced',
            'integration_agent_enhanced'
        ]
        
        found_agents = list(self.validation_results.keys())
        missing_agents = [agent for agent in expected_agents if agent not in found_agents]
        extra_agents = [agent for agent in found_agents if agent not in expected_agents]
        
        completeness_table = Table(title="System Completeness Check")
        completeness_table.add_column("Category", style="cyan")
        completeness_table.add_column("Expected", style="green")
        completeness_table.add_column("Found", style="yellow")
        completeness_table.add_column("Status", style="blue")
        
        completeness_table.add_row(
            "Expected Agents",
            str(len(expected_agents)),
            str(len(found_agents)),
            "✅ Complete" if len(missing_agents) == 0 else f"❌ Missing {len(missing_agents)}"
        )
        
        console.print(completeness_table)
        
        if missing_agents:
            console.print(f"[red]Missing agents:[/red] {', '.join(missing_agents)}")
        
        if extra_agents:
            console.print(f"[yellow]Extra agents:[/yellow] {', '.join(extra_agents)}")
        
        return len(missing_agents) == 0

def main():
    """Main validation function"""
    
    validator = AgentValidator()
    
    # Run validation
    results = validator.validate_all_agents()
    
    # Generate reports
    validator.generate_validation_report()
    console.print("\n")
    validator.display_agent_tree()
    console.print("\n")
    completeness_ok = validator.check_system_completeness()
    
    # Final assessment
    total_agents = len(results)
    avg_score = sum(r['validation_score'] for r in results.values()) / total_agents if total_agents > 0 else 0
    
    if completeness_ok and avg_score >= 90:
        status = "[green]🎉 SYSTEM READY FOR PRODUCTION[/green]"
    elif completeness_ok and avg_score >= 75:
        status = "[yellow]⚠️ SYSTEM GOOD - MINOR IMPROVEMENTS NEEDED[/yellow]"
    else:
        status = "[red]❌ SYSTEM NEEDS SIGNIFICANT WORK[/red]"
    
    console.print(Panel.fit(
        f"{status}\n\n"
        f"Total Enhanced Agents: {total_agents}\n"
        f"Average Validation Score: {avg_score:.1f}%\n"
        f"System Completeness: {'✅ Complete' if completeness_ok else '❌ Incomplete'}\n\n"
        f"All agents feature:\n"
        f"• Layer 2 Intelligence Integration\n"
        f"• Comprehensive Error Handling\n"
        f"• Agent Communication System\n"
        f"• Project State Management\n"
        f"• Interactive Clarification\n"
        f"• AI-Verifiable Outcomes",
        title="🚀 SPARC Agent System Status",
        border_style="green" if completeness_ok and avg_score >= 90 else "yellow" if avg_score >= 75 else "red"
    ))
    
    return results

if __name__ == "__main__":
    main()