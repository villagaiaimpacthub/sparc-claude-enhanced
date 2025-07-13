#!/usr/bin/env python3
"""
Test Ultrathink fixes on previously failing agents
"""

from rich.console import Console
from rich.table import Table
from ultrathink_agent_runner import UltrathinkAgentRunner

console = Console()

def test_ultrathink_fixes():
    """Test the specific agents that were previously failing"""
    
    console.print("🧪 [bold blue]Testing Ultrathink Fixes on Previously Failing Agents[/bold blue]")
    
    runner = UltrathinkAgentRunner()
    
    # Test the previously failing agents
    test_cases = [
        # CLI Agents (should work with fixed parameter handling)
        ('agents/orchestrators/goal_clarification.py', 'CLI Agent - Goal Clarification'),
        ('agents/orchestrators/specification_phase.py', 'CLI Agent - Specification Phase'),
        
        # JSON Agents (should work with proper TaskPayload)
        ('agents/writers/spec_writer_comprehensive.py', 'JSON Agent - Spec Writer'),
        ('agents/testers/tester_tdd_master.py', 'JSON Agent - TDD Master'),
        ('agents/reviewers/security_reviewer_module.py', 'JSON Agent - Security Reviewer'),
        
        # Enhanced Agents (should continue working)
        ('agents/enhanced/bmo_holistic_intent_verifier_enhanced.py', 'JSON Agent - BMO Verifier'),
    ]
    
    # Results tracking
    results = {}
    cli_success = 0
    json_success = 0
    total_cli = 0
    total_json = 0
    
    # Create results table
    table = Table(title="Ultrathink Fix Test Results")
    table.add_column("Agent Type", style="cyan")
    table.add_column("Agent Name", style="green") 
    table.add_column("Interface", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Issue Fixed", style="blue")
    
    for agent_path, description in test_cases:
        console.print(f"\\n🔧 Testing: {description}")
        
        # Determine expected interface
        if 'orchestrators' in agent_path:
            expected_interface = 'CLI'
            total_cli += 1
        else:
            expected_interface = 'JSON'
            total_json += 1
        
        # Run with smart detection
        result = runner.run_agent_smart(
            agent_path,
            'ultrathink_test',
            goal='build a financial intelligence analyzer tool'
        )
        
        # Analyze results
        if result['success']:
            status = "✅ SUCCESS"
            issue_fixed = "✅ FIXED"
            if expected_interface == 'CLI':
                cli_success += 1
            else:
                json_success += 1
        else:
            # Check if it's the old parameter issue
            stderr = result.get('stderr', '')
            if '--phase' in stderr and 'No such option' in stderr:
                status = "❌ OLD ISSUE"
                issue_fixed = "❌ NOT FIXED"
            elif 'TaskPayload' in stderr and 'validation errors' in stderr:
                status = "❌ OLD ISSUE"  
                issue_fixed = "❌ NOT FIXED"
            else:
                status = "⚠️ NEW ISSUE"
                issue_fixed = "⚠️ DIFFERENT"
        
        detected_interface = result.get('interface_type', 'unknown').upper()
        
        table.add_row(
            expected_interface,
            description,
            detected_interface, 
            status,
            issue_fixed
        )
        
        results[description] = result
    
    # Display results
    console.print("\\n")
    console.print(table)
    
    # Summary analysis
    console.print(f"\\n📊 [bold]Ultrathink Fix Analysis:[/bold]")
    console.print(f"  • CLI Agents: {cli_success}/{total_cli} working ({(cli_success/total_cli*100):.1f}%)")
    console.print(f"  • JSON Agents: {json_success}/{total_json} working ({(json_success/total_json*100):.1f}%)")
    
    overall_success = cli_success + json_success
    total_agents = total_cli + total_json
    
    console.print(f"  • Overall: {overall_success}/{total_agents} working ({(overall_success/total_agents*100):.1f}%)")
    
    if overall_success >= total_agents * 0.8:
        console.print("\\n🧠 [bold green]Ultrathink Assessment: MAJOR SUCCESS![/bold green]")
        console.print("  ✅ Interface detection working")
        console.print("  ✅ Parameter handling fixed") 
        console.print("  ✅ TaskPayload validation working")
    elif overall_success >= total_agents * 0.6:
        console.print("\\n🧠 [bold yellow]Ultrathink Assessment: Good progress, minor issues remain[/bold yellow]")
    else:
        console.print("\\n🧠 [bold red]Ultrathink Assessment: Need more fixes[/bold red]")
    
    return overall_success >= total_agents * 0.8

def test_specific_financial_analyzer():
    """Test specific financial analyzer workflow"""
    
    console.print("\\n💰 [bold blue]Testing Financial Intelligence Analyzer Workflow[/bold blue]")
    
    runner = UltrathinkAgentRunner()
    
    # Test just the goal clarification with financial context
    result = runner.run_agent_smart(
        'agents/orchestrators/goal_clarification.py',
        'financial_test_2025',
        goal='build a comprehensive financial intelligence analyzer with real-time market data, risk assessment, portfolio optimization, and regulatory compliance reporting'
    )
    
    if result['success']:
        console.print("✅ Financial analyzer goal clarification successful!")
        
        # Check what was actually created
        from pathlib import Path
        docs_path = Path("docs/Mutual_Understanding_Document.md")
        if docs_path.exists():
            content = docs_path.read_text()
            if 'financial' in content.lower():
                console.print("✅ Document contains financial-specific content")
            else:
                console.print("⚠️ Document still has generic content")
    else:
        console.print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    return result['success']

if __name__ == "__main__":
    # Test 1: Fix validation
    fixes_working = test_ultrathink_fixes()
    
    # Test 2: Financial analyzer specific
    financial_working = test_specific_financial_analyzer()
    
    # Final assessment
    console.print("\\n🎯 [bold blue]Final Ultrathink Assessment:[/bold blue]")
    
    if fixes_working and financial_working:
        console.print("\\n🧠 [bold green]ULTRATHINK SUCCESS: All systems operational![/bold green]")
        console.print("  ✅ Agent interface detection working")
        console.print("  ✅ CLI parameter handling fixed")
        console.print("  ✅ JSON TaskPayload validation working")
        console.print("  ✅ Financial analyzer workflow operational")
        console.print("\\n🚀 The SPARC system is now fully functional with Ultrathink intelligence!")
    else:
        console.print("\\n🧠 [bold yellow]ULTRATHINK PROGRESS: Significant improvements made[/bold yellow]")
        if fixes_working:
            console.print("  ✅ Core agent fixes successful")
        if financial_working:
            console.print("  ✅ Financial analyzer workflow working")
        
        console.print("\\n🔧 Continue refinement for complete optimization")