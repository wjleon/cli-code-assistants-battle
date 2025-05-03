"""
Helper script to fix Python path for imports.
Run this before importing the deepl package.
"""
import os
import sys

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path) 