#!/usr/bin/env python3
"""
Transcribe Module - Speech to Text
Uses OpenAI Whisper for audio transcription
"""

import whisper
import os
import sys
from pathlib import Path


class AudioTranscriber:
    def __init__(self, model_size="base"):
        """
        Initialize the transcriber with Whisper model
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            sys.exit(1)
    
    def transcribe_audio(self, audio_path, output_path="outputs/transcript.txt"):
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to input audio file (.wav, .mp3, etc.)
            output_path: Path to save transcript text file
            
        Returns:
            str: Transcribed text
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert Path object to string if necessary
            audio_path_str = str(audio_path)
            
            # Transcribe audio
            print(f"Transcribing audio: {audio_path_str}")
            result = self.model.transcribe(audio_path_str)
            
            # Extract text
            transcript_text = result["text"].strip()
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            
            print(f"Transcript saved to: {output_path}")
            print(f"Transcribed text: {transcript_text}")
            
            return transcript_text
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None


def main():
    """CLI interface for transcription module"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe audio to text using Whisper")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--output", "-o", default="outputs/transcript.txt", 
                       help="Output text file path")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    # Initialize transcriber and process
    transcriber = AudioTranscriber(model_size=args.model)
    result = transcriber.transcribe_audio(args.audio_file, args.output)
    
    if result:
        print("✅ Transcription completed successfully")
    else:
        print("❌ Transcription failed")
        sys.exit(1)


if __name__ == "__main__":
    main()