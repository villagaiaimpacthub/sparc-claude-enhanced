#!/usr/bin/env python3
"""
Claude Code execution bridge for SPARC agents
Fixes the broken BaseAgent._run_claude() method
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional

class ClaudeRunner:
    """Proper Claude Code execution for agents"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        
    async def run_claude(self, prompt: str, max_tokens: int = 50000) -> str:
        """Execute Claude Code with proper method"""
        
        # Create temporary file with prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(f"""# SPARC Agent Task

{prompt}

Please execute this task and provide a detailed response with specific actions taken.
""")
            temp_file = f.name
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(self.project_path)
            
            # Run Claude Code with the prompt file
            cmd = ["claude", "--file", temp_file]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=600,
                cwd=self.project_path
            )
            
            if result.returncode != 0:
                raise Exception(f"Claude execution failed: {result.stderr}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise Exception("Claude execution timed out")
        except FileNotFoundError:
            raise Exception("Claude Code CLI not found. Please ensure Claude Code is installed and in PATH.")
        except Exception as e:
            raise Exception(f"Claude execution error: {str(e)}")
        finally:
            # Cleanup
            os.chdir(original_cwd)
            try:
                os.unlink(temp_file)
            except:
                pass

# Alternative method using stdin
class ClaudeRunnerStdin:
    """Claude runner using stdin instead of temp files"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        
    async def run_claude(self, prompt: str, max_tokens: int = 50000) -> str:
        """Execute Claude Code via stdin"""
        
        full_prompt = f"""# SPARC Agent Task

{prompt}

Please execute this task and provide detailed response with specific actions taken.
"""
        
        try:
            # Change to project directory  
            original_cwd = os.getcwd()
            os.chdir(self.project_path)
            
            # Run Claude Code with stdin
            cmd = ["claude"]
            
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=self.project_path
            )
            
            if result.returncode != 0:
                raise Exception(f"Claude execution failed: {result.stderr}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise Exception("Claude execution timed out") 
        except FileNotFoundError:
            raise Exception("Claude Code CLI not found. Please ensure Claude Code is installed and in PATH.")
        except Exception as e:
            raise Exception(f"Claude execution error: {str(e)}")
        finally:
            os.chdir(original_cwd)