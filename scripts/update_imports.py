"""
Update all import statements after restructuring
"""
import os
import re

replacements = {
    'from src.data_pipeline import': 'from src.data.pipeline import',
    'from src.backtester import': 'from src.backtesting.backtester import',
    'from src.downloaders': 'from src.data.downloaders',
    'from src.cleaners': 'from src.data.cleaners',
    'from src.storage': 'from src.data.storage',
}

def update_file(filepath):
    """Update imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Updated {filepath}")

def main():
    # Update all Python files
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                update_file(filepath)
    
    for root, dirs, files in os.walk('examples'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                update_file(filepath)

if __name__ == '__main__':
    main()