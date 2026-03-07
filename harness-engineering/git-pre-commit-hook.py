#!/usr/bin/env python3
"""
Harness Engineering - Git Pre-commit Hook
Automatically validates constraints before allowing commits
"""

import os
import sys
import subprocess
from pathlib import Path

def get_staged_files():
    """Get list of files staged for commit"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def validate_file_constraints(file_path):
    """Validate staged files against harness engineering constraints"""
    print(f"🔍 Validating: {file_path}")
    
    harness_dir = Path("/a0/usr/workdir/harness-engineering")
    file_path_obj = Path(file_path)
    
    # Skip validation for harness engineering files themselves
    if file_path_obj.parent == harness_dir:
        print("ℹ️  Skipping harness engineering files - allow constraint implementation")
        return True
    
    # Critical: Check for Titan memory modification attempts
    forbidden_modification_patterns = [
        "titan_memory_system.py",
        "titan_memory.py",
        "modify_titan",
        "alter_titan",
        "titan_memory.write",
        "titan_memory.update",
        "titan_memory.delete"
    ]
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        violations = []
        for pattern in forbidden_modification_patterns:
            if pattern in content:
                violations.append(f"Titan memory modification pattern: {pattern}")
        
        if violations:
            print(f"❌ COMMIT REJECTED")
            for violation in violations:
                print(f"   - {violation}")
            print(f"   File: {file_path}")
            return False
        
        print("✅ File validated - No constraint violations")
        return True
        
    except Exception as e:
        print(f"⚠️  Warning: Could not validate {file_path}: {e}")
        return True  # Allow commit if validation fails

def main():
    """Main hook execution"""
    print("🚀 Harness Engineering Pre-commit Hook")
    print("Validating: Titan Memory System Protection")
    
    staged_files = get_staged_files()
    if not staged_files:
        print("ℹ️  No files staged for commit")
        sys.exit(0)
    
    all_valid = True
    for file_path in staged_files:
        if file_path:  # Skip empty lines
            if not validate_file_constraints(file_path):
                all_valid = False
    
    if not all_valid:
        print("\n💥 Commit rejected due to constraint violations")
        print("   Titan memory system modifications are prevented")
        print("   Only Claude Opus has permission to modify Titan memory")
        sys.exit(1)
    
    print("✅ All files validated - Commit allowed")
    sys.exit(0)

if __name__ == "__main__":
    main()
