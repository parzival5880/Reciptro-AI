#!/usr/bin/env python3
"""
Test script for Receptro.AI pipeline
Tests individual modules and full pipeline functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_intent_recognition():
    """Test intent recognition with sample text"""
    print("\n🧠 Testing Intent Recognition...")
    
    from interpret.interpret import IntentParser
    
    test_cases = [
        "I want to book an appointment for Monday at 2pm",
        "What's the weather like today?",
        "Remind me to call John tomorrow",
        "Play some music by The Beatles",
        "How do I get to the airport?",
        "Tell me about machine learning"
    ]
    
    parser = IntentParser()
    
    for text in test_cases:
        result = parser.extract_intent(text)
        print(f"Input: '{text}'")
        print(f"  Intent: {result['intent']} (confidence: {result['confidence']})")
        if result['parameters']:
            print(f"  Parameters: {result['parameters']}")
        print()

def test_text_to_speech():
    """Test text-to-speech with sample text"""
    print("\n🗣️  Testing Text-to-Speech...")
    
    try:
        from synthesize.synthesize import TextToSpeech
        
        tts = TextToSpeech()
        test_text = "Hello, this is a test of the text to speech system."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            success = tts.synthesize_text(test_text, tmp.name)
            
            if success and os.path.exists(tmp.name):
                print(