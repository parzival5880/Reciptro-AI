#!/usr/bin/env python3
"""
Interpret Module - Intent Recognition and Parameter Extraction
Uses rule-based pattern matching to identify intents and extract parameters
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path


class IntentParser:
    def __init__(self):
        """Initialize the intent parser with predefined patterns"""
        self.intent_patterns = {
            "book_appointment": {
                "keywords": ["book", "appointment", "schedule", "meeting", "reserve"],
                "params": {
                    "date": r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|\d{1,2}(?:st|nd|rd|th)?)",
                    "time": r"(\d{1,2}(?::\d{2})?\s*(?:am|pm|o'clock))",
                    "service": r"(consultation|checkup|meeting|call|session)"
                }
            },
            "get_weather": {
                "keywords": ["weather", "forecast", "temperature", "rain", "sunny", "cloudy"],
                "params": {
                    "location": r"in\s+([a-zA-Z\s]+)",
                    "time": r"(today|tomorrow|this week|next week)"
                }
            },
            "set_reminder": {
                "keywords": ["remind", "reminder", "alert", "notify"],
                "params": {
                    "task": r"to\s+([^.!?]+)",
                    "time": r"(in\s+\d+\s+(?:minutes?|hours?|days?)|at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm))"
                }
            },
            "play_music": {
                "keywords": ["play", "music", "song", "artist", "album"],
                "params": {
                    "song": r"play\s+([^.!?]+)",
                    "artist": r"by\s+([a-zA-Z\s]+)"
                }
            },
            "get_directions": {
                "keywords": ["directions", "navigate", "route", "way to", "how to get"],
                "params": {
                    "destination": r"to\s+([^.!?]+)",
                    "from": r"from\s+([a-zA-Z\s]+)"
                }
            },
            "general_question": {
                "keywords": ["what", "how", "when", "where", "why", "tell me", "explain"],
                "params": {
                    "topic": r"(?:what|how|when|where|why).*?([^.!?]+)"
                }
            }
        }
    
    def extract_intent(self, text):
        """
        Extract intent and parameters from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict: Intent and parameters
        """
        text_lower = text.lower().strip()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0
            for keyword in intent_data["keywords"]:
                if keyword in text_lower:
                    score += 1
            intent_scores[intent_name] = score
        
        # Get the best matching intent
        best_intent = max(intent_scores, key=intent_scores.get) if max(intent_scores.values()) > 0 else "unknown"
        
        # Extract parameters for the identified intent
        parameters = {}
        if best_intent != "unknown" and best_intent in self.intent_patterns:
            intent_data = self.intent_patterns[best_intent]
            for param_name, pattern in intent_data["params"].items():
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    parameters[param_name] = match.group(1).strip()
        
        # Additional context extraction
        confidence = intent_scores[best_intent] / len(self.intent_patterns[best_intent]["keywords"]) if best_intent != "unknown" else 0
        
        return {
            "intent": best_intent,
            "parameters": parameters,
            "confidence": round(confidence, 2),
            "original_text": text
        }
    
    def process_transcript(self, transcript_path, output_path="outputs/intent.json"):
        """
        Process transcript file and extract intent
        
        Args:
            transcript_path: Path to transcript text file
            output_path: Path to save intent JSON
            
        Returns:
            dict: Intent analysis result
        """
        try:
            # Read transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read().strip()
            
            if not transcript_text:
                print("Warning: Empty transcript file")
                return None
            
            # Extract intent
            print(f"Processing transcript: {transcript_text}")
            intent_result = self.extract_intent(transcript_text)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save result
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(intent_result, f, indent=2, ensure_ascii=False)
            
            print(f"Intent analysis saved to: {output_path}")
            print(f"Detected intent: {intent_result['intent']} (confidence: {intent_result['confidence']})")
            if intent_result['parameters']:
                print(f"Parameters: {intent_result['parameters']}")
            
            return intent_result
            
        except Exception as e:
            print(f"Error processing transcript: {e}")
            return None
    
    def generate_response(self, intent_result):
        """
        Generate appropriate response based on intent
        
        Args:
            intent_result: Intent analysis result
            
        Returns:
            str: Response text
        """
        intent = intent_result.get("intent", "unknown")
        params = intent_result.get("parameters", {})
        
        responses = {
            "book_appointment": f"Okay, I've booked your appointment{' for ' + params.get('date', '') if params.get('date') else ''}{' at ' + params.get('time', '') if params.get('time') else ''}.",
            "get_weather": f"The weather{' in ' + params.get('location', '') if params.get('location') else ''} is looking good today.",
            "set_reminder": f"I'll remind you{' to ' + params.get('task', '') if params.get('task') else ''}{' ' + params.get('time', '') if params.get('time') else ''}.",
            "play_music": f"Playing{' ' + params.get('song', 'music') if params.get('song') else ' music'}{' by ' + params.get('artist', '') if params.get('artist') else ''}.",
            "get_directions": f"Here are directions{' to ' + params.get('destination', '') if params.get('destination') else ''}.",
            "general_question": f"Let me help you with that question.",
            "unknown": "I'm not sure how to help with that, but I'm here to assist you."
        }
        
        return responses.get(intent, responses["unknown"])


def main():
    """CLI interface for intent recognition module"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract intent and parameters from transcript")
    parser.add_argument("transcript_file", help="Path to transcript text file")
    parser.add_argument("--output", "-o", default="outputs/intent.json", 
                       help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.transcript_file):
        print(f"Error: Transcript file not found: {args.transcript_file}")
        exit(1)
    
    # Initialize parser and process
    parser = IntentParser()
    result = parser.process_transcript(args.transcript_file, args.output)
    
    if result:
        print("✅ Intent recognition completed successfully")
        # Generate and print response
        response = parser.generate_response(result)
        print(f"Generated response: {response}")
    else:
        print("❌ Intent recognition failed")
        exit(1)


if __name__ == "__main__":
    main()