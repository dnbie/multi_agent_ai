"""
Vercel Serverless Function Entry Point
Imports the Flask app from app.py
"""
import sys
import os

# Add project root to Python path so all imports work
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

# Set VERCEL env so config.py uses /tmp for writable dirs
os.environ.setdefault('VERCEL', '1')

from app import app

# Vercel looks for 'app' — it's already imported above
