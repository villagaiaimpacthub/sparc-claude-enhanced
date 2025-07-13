#!/usr/bin/env python3
"""
Build script for SPARC CLI package
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: str) -> bool:
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """Main build script"""
    print("🚀 Building SPARC CLI package...")
    
    # Ensure we're in the right directory
    package_dir = Path(__file__).parent.parent
    print(f"Package directory: {package_dir}")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    cleanup_commands = [
        "rm -rf build/",
        "rm -rf dist/",
        "rm -rf *.egg-info/",
        "find . -name '*.pyc' -delete",
        "find . -name '__pycache__' -type d -exec rm -rf {} +",
    ]
    
    for cmd in cleanup_commands:
        run_command(cmd)
    
    # Build package
    print("\n📦 Building package...")
    if not run_command("python -m build"):
        print("❌ Build failed!")
        return False
    
    # Check package
    print("\n🔍 Checking package...")
    if not run_command("python -m twine check dist/*"):
        print("❌ Package check failed!")
        return False
    
    print("\n✅ Package built successfully!")
    print("\nBuilt files:")
    dist_dir = package_dir / "dist"
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")
    
    print("\n📝 Next steps:")
    print("1. Test locally: pip install dist/sparc_cli-*.whl")
    print("2. Upload to PyPI: python -m twine upload dist/*")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)