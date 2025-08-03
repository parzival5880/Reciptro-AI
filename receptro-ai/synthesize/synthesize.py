#!/usr/bin/env python3
"""
Synthesize Module - Text to Speech (Simplified Version)
Uses gTTS or pyttsx3 for speech synthesis to avoid dependency conflicts
"""

import os
import sys
import json
from pathlib import Path


class TextToSpeech:
    def __init__(self, engine="auto"):
        """
        Initialize TTS engine
        
        Args:
            engine: TTS engine to use ("gtts", "pyttsx3", "auto")
        """
        self.engine_type = engine
        self.engine = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup the best available TTS engine"""
        if self.engine_type == "auto":
            # Try gTTS first, then pyttsx3
            if self._try_gtts():
                self.engine_type = "gtts"
            elif self._try_pyttsx3():
                self.engine_type = "pyttsx3"
            else:
                print("⚠️  No TTS engine available. Will create text files instead.")
                self.engine_type = "none"
        elif self.engine_type == "gtts":
            self._try_gtts()
        elif self.engine_type == "pyttsx3":
            self._try_pyttsx3()
    
    def _try_gtts(self):
        """Try to initialize gTTS"""
        try:
            from gtts import gTTS
            print(" Using Google Text-to-Speech (gTTS)")
            return True
        except ImportError:
            print("⚠️  gTTS not available")
            return False
    
    def _try_pyttsx3(self):
        """Try to initialize pyttsx3"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            print("✅ Using pyttsx3 (offline TTS)")
            return True
        except ImportError:
            print("⚠️  pyttsx3 not available")
            return False
        except Exception as e:
            print(f"⚠️  pyttsx3 initialization failed: {e}")
            return False
    
    def synthesize_text(self, text, output_path="outputs/reply.wav"):
        """
        Convert text to speech and save as audio file
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            
        Returns:
            bool: Success status
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            print(f"Synthesizing text: {text}")
            
            if self.engine_type == "gtts":
                return self._synthesize_gtts(text, output_path)
            elif self.engine_type == "pyttsx3":
                return self._synthesize_pyttsx3(text, output_path)
            else:
                return self._create_text_file(text, output_path)
            
        except Exception as e:
            print(f"Error during synthesis: {e}")
            return False
    
    def _synthesize_gtts(self, text, output_path):
        """Synthesize using gTTS"""
        try:
            from gtts import gTTS
            
            # Convert Path object to string if necessary
            output_path_str = str(output_path)
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Convert .wav to .mp3 for gTTS (it only supports mp3)
            if output_path_str.endswith('.wav'):
                mp3_path = output_path_str.replace('.wav', '.mp3')
            else:
                mp3_path = output_path_str
            
            # Save the audio
            tts.save(mp3_path)
            
            print(f"Audio saved to: {mp3_path}")
            
            # If original path was .wav, mention the actual format
            if output_path_str.endswith('.wav') and mp3_path.endswith('.mp3'):
                print(f"Note: Saved as MP3 format due to gTTS limitations")
            
            return True
            
        except Exception as e:
            print(f"gTTS synthesis failed: {e}")
            return False
    
    def _synthesize_pyttsx3(self, text, output_path):
        """Synthesize using pyttsx3"""
        try:
            if self.engine is None:
                import pyttsx3
                self.engine = pyttsx3.init()
            
            # Configure voice properties
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level
            
            # Save to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            print(f"Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"pyttsx3 synthesis failed: {e}")
            return False
    
    def _create_text_file(self, text, output_path):
        """Create a text file when no TTS is available"""
        try:
            text_path = output_path.replace('.wav', '.txt').replace('.mp3', '.txt')
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"SPEECH OUTPUT: {text}\n")
                f.write(f"(Audio synthesis not available - this is the text that would be spoken)")
            
            print(f"Text output saved to: {text_path}")
            print("💡 Install gTTS or pyttsx3 for actual audio synthesis")
            return True
            
        except Exception as e:
            print(f"Failed to create text file: {e}")
            return False
    
    def synthesize_from_intent(self, intent_path, output_path="outputs/reply.wav"):
        """
        Generate speech from intent JSON file
        
        Args:
            intent_path: Path to intent JSON file
            output_path: Path to save audio file
            
        Returns:
            bool: Success status
        """
        try:
            # Read intent file
            with open(intent_path, 'r', encoding='utf-8') as f:
                intent_data = json.load(f)
            
            # Import IntentParser to generate response
            from interpret.interpret import IntentParser
            parser = IntentParser()
            response_text = parser.generate_response(intent_data)
            
            print(f"Generated response: {response_text}")
            
            # Synthesize the response
            return self.synthesize_text(response_text, output_path)
            
        except Exception as e:
            print(f"Error synthesizing from intent: {e}")
            return False


def main():
    """CLI interface for text-to-speech module"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert text to speech")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", "-t", help="Text to synthesize")
    group.add_argument("--intent", "-i", help="Path to intent JSON file")
    
    parser.add_argument("--output", "-o", default="outputs/reply.wav", 
                       help="Output audio file path")
    parser.add_argument("--engine", "-e", choices=["gtts", "pyttsx3", "auto"], 
                       default="auto", help="TTS engine to use")
    
    args = parser.parse_args()
    
    # Initialize TTS engine
    tts_engine = TextToSpeech(engine=args.engine)
    
    if args.text:
        # Synthesize direct text
        success = tts_engine.synthesize_text(args.text, args.output)
    else:
        # Synthesize from intent file
        if not os.path.exists(args.intent):
            print(f"Error: Intent file not found: {args.intent}")
            sys.exit(1)
        success = tts_engine.synthesize_from_intent(args.intent, args.output)
    
    if success:
        print(" Speech synthesis completed successfully")
    else:
        print("Speech synthesis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()