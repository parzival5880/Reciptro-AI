#!/usr/bin/env python3
"""
Receptro.AI - Main Entry Point
Simple CLI interface for the modular media processing pipeline
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.process import main as orchestrator_main

if __name__ == "__main__":
    # Simply delegate to the orchestrator
    orchestrator_main()