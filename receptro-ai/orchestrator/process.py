#!/usr/bin/env python3
"""
Orchestrator Module - Main Pipeline Controller
Routes files to appropriate processing modules and coordinates the full pipeline
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcribe.transcribe import AudioTranscriber
from interpret.interpret import IntentParser
from synthesize.synthesize import TextToSpeech
from extract.extract import DocumentExtractor


class MediaProcessor:
    def __init__(self, output_dir="outputs"):
        """
        Initialize the media processor
        
        Args:
            output_dir: Directory to save all outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize all processing modules
        print("Initializing processing modules...")
        self.transcriber = None
        self.intent_parser = IntentParser()
        self.tts_engine = None
        self.document_extractor = DocumentExtractor()
        
        # Supported file types
        self.audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    
    def _init_transcriber(self):
        """Lazy initialization of transcriber"""
        if self.transcriber is None:
            print("Loading speech-to-text model...")
            self.transcriber = AudioTranscriber()
    
    def _init_tts(self):
        """Lazy initialization of TTS engine"""
        if self.tts_engine is None:
            print("Loading text-to-speech model...")
            self.tts_engine = TextToSpeech()
    
    def detect_file_type(self, file_path):
        """
        Detect file type based on extension
        
        Args:
            file_path: Path to input file
            
        Returns:
            str: File type ('audio', 'image', 'unknown')
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension in self.audio_extensions:
            return 'audio'
        elif extension in self.image_extensions:
            return 'image'
        else:
            return 'unknown'
    
    def process_audio_pipeline(self, audio_path):
        """
        Process audio through the full speech pipeline
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict: Processing results with file paths
        """
        print(f"\n Processing audio pipeline for: {audio_path}")
        results = {
            "input_file": str(audio_path),
            "file_type": "audio",
            "timestamp": datetime.now().isoformat(),
            "outputs": {}
        }
        
        try:
            # Step 1: Speech to Text
            print("\n Step 1: Transcribing audio...")
            self._init_transcriber()
            transcript_path = self.output_dir / "transcript.txt"
            transcript_text = self.transcriber.transcribe_audio(str(audio_path), str(transcript_path))
            
            if not transcript_text:
                results["error"] = "Failed to transcribe audio"
                return results
            
            results["outputs"]["transcript"] = str(transcript_path)
            results["transcript_text"] = transcript_text
            
            # Step 2: Intent Recognition
            print("\n Step 2: Analyzing intent...")
            intent_path = self.output_dir / "intent.json"
            intent_result = self.intent_parser.process_transcript(transcript_path, intent_path)
            
            if not intent_result:
                results["error"] = "Failed to analyze intent"
                return results
            
            results["outputs"]["intent"] = str(intent_path)
            results["intent"] = intent_result["intent"]
            results["confidence"] = intent_result["confidence"]
            results["parameters"] = intent_result["parameters"]
            
            # Step 3: Generate Response and Synthesize
            print("\n  Step 3: Generating speech response...")
            self._init_tts()
            reply_path = self.output_dir / "reply.wav"
            
            # Generate response text
            response_text = self.intent_parser.generate_response(intent_result)
            results["response_text"] = response_text
            
            # Synthesize response
            synthesis_success = self.tts_engine.synthesize_text(response_text, reply_path)
            
            if synthesis_success:
                results["outputs"]["reply_audio"] = str(reply_path)
            else:
                print("  Speech synthesis failed, but pipeline completed")
            
            print("\n Audio pipeline completed successfully!")
            
        except Exception as e:
            results["error"] = f"Pipeline error: {str(e)}"
            print(f" Audio pipeline failed: {e}")
        
        return results
    
    def process_image_pipeline(self, image_path):
        """
        Process image through OCR extraction pipeline
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Processing results with file paths
        """
        print(f"\n Processing image pipeline for: {image_path}")
        results = {
            "input_file": str(image_path),
            "file_type": "image",
            "timestamp": datetime.now().isoformat(),
            "outputs": {}
        }
        
        try:
            # OCR and Field Extraction
            print("\n Extracting document fields...")
            fields_path = self.output_dir / "fields.json"
            extraction_result = self.document_extractor.process_document(image_path, fields_path)
            
            if not extraction_result:
                results["error"] = "Failed to extract document fields"
                return results
            
            results["outputs"]["fields"] = str(fields_path)
            results["extracted_fields"] = extraction_result["extracted_fields"]
            results["field_count"] = extraction_result["field_count"]
            results["raw_text"] = extraction_result["raw_text"]
            
            print("\n Image pipeline completed successfully!")
            
        except Exception as e:
            results["error"] = f"Pipeline error: {str(e)}"
            print(f" Image pipeline failed: {e}")
        
        return results
    
    def process_file(self, file_path):
        """
        Main processing function - routes file to appropriate pipeline
        
        Args:
            file_path: Path to input file
            
        Returns:
            dict: Processing results
        """
        file_path = Path(file_path)
        
        # Validate input file
        if not file_path.exists():
            return {
                "error": f"File not found: {file_path}",
                "input_file": str(file_path)
            }
        
        # Detect file type and route to appropriate pipeline
        file_type = self.detect_file_type(file_path)
        
        if file_type == 'audio':
            return self.process_audio_pipeline(file_path)
        elif file_type == 'image':
            return self.process_image_pipeline(file_path)
        else:
            return {
                "error": f"Unsupported file type: {file_path.suffix}",
                "input_file": str(file_path),
                "supported_types": {
                    "audio": list(self.audio_extensions),
                    "image": list(self.image_extensions)
                }
            }
    
    def print_results_summary(self, results):
        """Print a formatted summary of processing results"""
        print("\n" + "="*60)
        print(" PROCESSING RESULTS SUMMARY")
        print("="*60)
        
        print(f" Input: {results.get('input_file', 'Unknown')}")
        print(f" Type: {results.get('file_type', 'Unknown')}")
        
        if 'error' in results:
            print(f" Error: {results['error']}")
            return
        
        if results.get('file_type') == 'audio':
            print(f"\n Transcript: {results.get('transcript_text', 'N/A')}")
            print(f" Intent: {results.get('intent', 'Unknown')} (confidence: {results.get('confidence', 0)})")
            if results.get('parameters'):
                print(f"⚙️  Parameters: {results['parameters']}")
            print(f" Response: {results.get('response_text', 'N/A')}")
            
        elif results.get('file_type') == 'image':
            print(f"\n Fields extracted: {results.get('field_count', 0)}")
            if results.get('extracted_fields'):
                for key, value in results['extracted_fields'].items():
                    print(f"   • {key}: {value}")
        
        print(f"\n Output files:")
        for output_type, path in results.get('outputs', {}).items():
            print(f"   • {output_type}: {path}")
        
        print("\nProcessing completed!")


def main():
    """CLI interface for the orchestrator"""
    parser = argparse.ArgumentParser(
        description="Receptro.AI Media Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator/process.py sample.wav     # Process audio file
  python orchestrator/process.py doc.png       # Process document image
  python orchestrator/process.py --batch *.wav # Process multiple files
        """
    )
    
    parser.add_argument("files", nargs="+", help="Input file(s) to process")
    parser.add_argument("--output-dir", "-o", default="outputs", 
                       help="Output directory (default: outputs)")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Suppress verbose output")
    parser.add_argument("--json", "-j", action="store_true", 
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = MediaProcessor(output_dir=args.output_dir)
    
    # Process each file
    all_results = []
    
    for file_path in args.files:
        if not args.quiet:
            print(f"\n🚀 Starting processing: {file_path}")
        
        results = processor.process_file(file_path)
        all_results.append(results)
        
        if args.json:
            print(json.dumps(results, indent=2))
        elif not args.quiet:
            processor.print_results_summary(results)
    
    # Save combined results
    if len(all_results) > 1:
        combined_results = {
            "total_files": len(all_results),
            "timestamp": datetime.now().isoformat(),
            "results": all_results
        }
        
        results_path = Path(args.output_dir) / "processing_results.json"
        with open(results_path, 'w') as f:
            json.dump(combined_results, f, indent=2)
        
        if not args.quiet:
            print(f"\n Combined results saved to: {results_path}")


if __name__ == "__main__":
    main()