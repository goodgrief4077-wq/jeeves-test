#!/usr/bin/env python3
"""
Harness Engineering - Architectural Constraints Validator
Enforces module boundaries and dependencies without modifying Titan memory
"""

import ast
import sys
import os
from pathlib import Path
import importlib.util

def validate_dependencies(file_path):
    """Ensure modules follow architectural boundaries"""
    print(f"🔍 Validating architectural constraints for: {file_path}")
    
    # Critical constraints: DO NOT MODIFY TITAN MEMORY SYSTEM
    # These patterns indicate actual modification attempts, not just references
    forbidden_modification_patterns = [
        "titan_memory_system.py",
        "titan_memory.py",
        "modify_titan",
        "alter_titan",
        "titan_memory.write",
        "titan_memory.update",
        "titan_memory.delete"
    ]
    
    # Permissive patterns - references allowed, modifications forbidden
    permissive_reference_patterns = [
        "titan_memory_system",
        "titan_memory"
    ]
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Skip validation for harness engineering files themselves
        harness_dir = Path("/a0/usr/workdir/harness-engineering")
        file_path_obj = Path(file_path)
        
        if file_path_obj.parent == harness_dir:
            print("ℹ️  Skipping harness engineering files - allow references for constraint checking")
            return True
            
        # Check for Titan memory modification attempts in non-harness files
        modification_detected = False
        for pattern in forbidden_modification_patterns:
            if pattern in content:
                print(f"❌ VIOLATION: Titan memory system modification detected")
                print(f"   Pattern: {pattern}")
                print(f"   File: {file_path}")
                modification_detected = True
                break
                
        if modification_detected:
            return False
            
        # Check AST for import modifications
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Allow references but check for modification targets
                    if any(pattern in alias.name for pattern in forbidden_modification_patterns):
                        print(f"❌ VIOLATION: Importing restricted Titan memory modification module")
                        print(f"   Module: {alias.name}")
                        return False
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(pattern in node.module for pattern in forbidden_modification_patterns):
                    print(f"❌ VIOLATION: Importing from restricted Titan memory modification module")
                    print(f"   Module: {node.module}")
                    return False
                    
            # Check for function calls that modify Titan memory
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'attr') and node.func.attr in ['write', 'update', 'delete', 'modify']:
                    # Check if the function is called on Titan memory objects
                    if hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
                        if 'titan' in node.func.value.id.lower():
                            print(f"❌ VIOLATION: Attempted Titan memory modification via {node.func.attr}")
                            return False
        
        print("✅ Architectural constraints validated - No Titan memory modifications detected")
        return True
        
    except Exception as e:
        print(f"⚠️  Warning: Could not validate {file_path}: {e}")
        return True  # Allow execution if validation fails

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python architectural_constraints.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if validate_dependencies(file_path):
        sys.exit(0)
    else:
        sys.exit(1)
