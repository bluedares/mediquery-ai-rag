#!/usr/bin/env python3
"""
Script to convert absolute imports to relative imports in backend/app/
This fixes Railway deployment issues with module resolution.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Convert absolute imports (from app.X) to relative imports (from .X or ..X)"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Determine the depth of the file relative to backend/app/
    relative_path = filepath.relative_to(Path('backend/app'))
    depth = len(relative_path.parts) - 1  # -1 because the file itself doesn't count
    
    # Pattern to match: from app.something import ...
    # We'll replace with relative imports based on file location
    
    if depth == 0:
        # File is directly in backend/app/ (like main.py, config.py)
        # from app.models.X -> from .models.X
        # from app.config -> from .config
        content = re.sub(r'\bfrom app\.', 'from .', content)
    elif depth == 1:
        # File is in backend/app/subdir/ (like api/, agents/, services/)
        # from app.models.X -> from ..models.X
        # from app.config -> from ..config
        # from app.agents.X -> from .X (if in agents/)
        
        # Get the subdirectory name
        subdir = relative_path.parts[0]
        
        # Replace imports from the same subdirectory with relative imports
        content = re.sub(rf'\bfrom app\.{subdir}\.', 'from .', content)
        
        # Replace imports from other app modules with parent relative imports
        content = re.sub(r'\bfrom app\.', 'from ..', content)
    elif depth == 2:
        # File is in backend/app/subdir/subsubdir/
        # from app.X -> from ...X
        content = re.sub(r'\bfrom app\.', 'from ...', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in backend/app/"""
    backend_app = Path('backend/app')
    
    if not backend_app.exists():
        print(f"Error: {backend_app} not found")
        return
    
    fixed_files = []
    
    # Find all Python files
    for py_file in backend_app.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue  # Skip __init__ files
        
        try:
            if fix_imports_in_file(py_file):
                fixed_files.append(py_file)
                print(f"✓ Fixed: {py_file}")
        except Exception as e:
            print(f"✗ Error fixing {py_file}: {e}")
    
    print(f"\n✅ Fixed {len(fixed_files)} files")
    
    if fixed_files:
        print("\nFixed files:")
        for f in fixed_files:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
