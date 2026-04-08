"""
Vercel Serverless Function Entry Point
Imports the Flask app from app.py
"""
import sys
import os

# Add project root to Python path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from app import app
