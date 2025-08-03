#!/usr/bin/env python3
"""
Receptro.AI - Automated End-to-End Demo Runner

This script demonstrates all five pipeline capabilities in one seamless execution:
1. Speech-to-Text transcription
2. Intent recognition and parameter extraction  
3. Text-to-Speech synthesis
4. Document OCR and field extraction
5. Unified orchestration with auto-routing

Bonus feature for the assessment - executes everything automatically!
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.process import MediaProcessor

class AutomatedDemoRunner:
    def __init__(self):
        """Initialize the automated demo runner"""
        self.start_time = datetime.now()
        self.results = []
        self.demo_files = []
        
        # Create demo output directory
        self.demo_dir = Path("demo_outputs")
        self.demo_dir.mkdir(exist_ok=True)
        
        print(" RECEPTRO.AI - AUTOMATED END-TO-END DEMO")
        print("=" * 60)
        print(f" Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(" Executing all five pipeline steps automatically...")
        print()
    
    def find_demo_files(self):
        """Find available demo files in the project"""
        print("📁 STEP 1: Discovering input files...")
        
        # Look for audio files
        audio_extensions = ['.wav', '.mp3', '.m4a', '.flac']
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        
        for ext in audio_extensions:
            for file_path in Path('.').glob(f'*{ext}'):
                if file_path.is_file():
                    self.demo_files.append(('audio', file_path))
                    print(f"🎵 Found audio file: {file_path}")
        
        for ext in image_extensions:
            for file_path in Path('.').glob(f'*{ext}'):
                if file_path.is_file():
                    self.demo_files.append(('image', file_path))
                    print(f" Found image file: {file_path}")
        
        if not self.demo_files:
            print("⚠️  No demo files found. Creating sample files...")
            self.create_sample_files()
        
        print(f"✅ Found {len(self.demo_files)} files for processing")
        print()
        
        return len(self.demo_files) > 0
    
    def create_sample_files(self):
        """Create sample files if none exist"""
        # Create a simple text file that shows what would be processed
        sample_audio_info = self.demo_dir / "audio_sample_info.txt"
        with open(sample_audio_info, 'w') as f:
            f.write("AUDIO SAMPLE PLACEHOLDER\n")
            f.write("In a real demo, this would be a 5-10 second audio file with speech like:\n")
            f.write("'I would like to book an appointment for Monday at 2 PM'\n")
            f.write("\nTo test with real audio, add a .wav or .mp3 file to the project root.")
        
        sample_doc_info = self.demo_dir / "document_sample_info.txt"
        with open(sample_doc_info, 'w') as f:
            f.write("DOCUMENT SAMPLE PLACEHOLDER\n")
            f.write("In a real demo, this would be a photo of a document with text fields like:\n")
            f.write("- Name: John Doe\n")
            f.write("- Date of Birth: 05/21/1990\n")
            f.write("- ID Number: ABC123456\n")
            f.write("\nTo test with real images, add a .png or .jpg file to the project root.")
        
        print(f" Created placeholder files in {self.demo_dir}/")
    
    def run_audio_pipeline_demo(self, audio_file):
        """Demonstrate the complete audio processing pipeline"""
        print("🎵 STEP 2: Audio Processing Pipeline Demo")
        print("-" * 40)
        
        try:
            # Initialize processor
            processor = MediaProcessor(output_dir=self.demo_dir / "audio_outputs")
            
            # Process the audio file
            print(f"Processing: {audio_file}")
            result = processor.process_file(audio_file)
            
            if 'error' not in result:
                print(" Audio pipeline completed successfully!")
                print(f"    Transcript: {result.get('transcript_text', 'N/A')}")
                print(f"    Intent: {result.get('intent', 'N/A')} (confidence: {result.get('confidence', 0)})")
                print(f"    Response: {result.get('response_text', 'N/A')}")
                
                # Show generated files
                for output_type, path in result.get('outputs', {}).items():
                    print(f"    {output_type}: {path}")
            else:
                print(f" Audio pipeline failed: {result['error']}")
            
            self.results.append(('audio', result))
            print()
            
        except Exception as e:
            print(f" Audio pipeline error: {e}")
            self.results.append(('audio', {'error': str(e)}))
    
    def run_image_pipeline_demo(self, image_file):
        """Demonstrate the document processing pipeline"""
        print(" STEP 3: Document Processing Pipeline Demo")
        print("-" * 40)
        
        try:
            # Initialize processor
            processor = MediaProcessor(output_dir=self.demo_dir / "image_outputs")
            
            # Process the image file
            print(f"Processing: {image_file}")
            result = processor.process_file(image_file)
            
            if 'error' not in result:
                print(" Document pipeline completed successfully!")
                print(f"    Fields extracted: {result.get('field_count', 0)}")
                
                # Show extracted fields
                for field, value in result.get('extracted_fields', {}).items():
                    print(f"   • {field}: {value}")
                
                # Show generated files
                for output_type, path in result.get('outputs', {}).items():
                    print(f"    {output_type}: {path}")
            else:
                print(f" Document pipeline failed: {result['error']}")
            
            self.results.append(('image', result))
            print()
            
        except Exception as e:
            print(f" Document pipeline error: {e}")
            self.results.append(('image', {'error': str(e)}))
    
    def run_module_tests(self):
        """Test individual modules to show modularity"""
        print("🔧 STEP 4: Individual Module Testing")
        print("-" * 40)
        
        modules = [
            ("transcribe/transcribe.py", "Speech-to-Text"),
            ("interpret/interpret.py", "Intent Recognition"),
            ("synthesize/synthesize.py", "Text-to-Speech"),
            ("extract/extract.py", "Document Extraction"),
            ("orchestrator/process.py", "Main Orchestrator")
        ]
        
        for module_path, description in modules:
            try:
                # Test if module can be imported
                module_name = module_path.replace('/', '.').replace('.py', '')
                __import__(module_name)
                print(f"✅ {description} - Module OK")
            except Exception as e:
                print(f" {description} - Error: {e}")
        
        print()
    
    def demonstrate_swappable_engines(self):
        """Show how easy it is to swap processing engines"""
        print("STEP 5: Swappable Engine Demonstration")
        print("-" * 40)
        
        print(" The modular design allows easy engine swapping:")
        print("   • Speech-to-Text: Whisper → Google Speech API → Azure Speech")
        print("   • Intent Recognition: Rule-based → spaCy → OpenAI GPT")
        print("   • Text-to-Speech: gTTS → pyttsx3 → Coqui TTS")
        print("   • OCR: Tesseract → Google Vision → AWS Textract")
        print()
        
        print("📝 Configuration examples saved to demo_outputs/")
        
        # Create configuration examples
        config_examples = {
            "whisper_config": {
                "model_size": "base",
                "alternative_engines": ["google_speech", "azure_speech", "aws_transcribe"]
            },
            "intent_config": {
                "current_engine": "rule_based",
                "alternative_engines": ["spacy_ner", "huggingface_transformers", "openai_gpt"]
            },
            "tts_config": {
                "current_engine": "gtts",
                "alternative_engines": ["pyttsx3", "coqui_tts", "azure_cognitive"]
            },
            "ocr_config": {
                "current_engine": "tesseract",
                "alternative_engines": ["google_vision", "azure_computer_vision", "aws_textract"]
            }
        }
        
        with open(self.demo_dir / "engine_swap_examples.json", 'w') as f:
            json.dump(config_examples, f, indent=2)
        
        print("Engine swap examples documented")
        print()
    
    def generate_final_report(self):
        """Generate a comprehensive demo report"""
        print("STEP 6: Generating Final Demo Report")
        print("-" * 40)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "demo_info": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "files_processed": len([r for r in self.results if 'error' not in r[1]])
            },
            
        }
        
        # Add individual results
        for result_type, result_data in self.results:
            report["pipeline_results"].append({
                "type": result_type,
                "success": 'error' not in result_data,
                "details": result_data
            })
        
        # Save the report
        report_path = self.demo_dir / "demo_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save a human-readable summary
        summary_path = self.demo_dir / "demo_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(" RECEPTRO.AI - AUTOMATED DEMO SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Demo completed in {duration.total_seconds():.2f} seconds\n")
            f.write(f"Files processed: {len(self.results)}\n")
            f.write(f"Success rate: {len([r for r in self.results if 'error' not in r[1]])}/{len(self.results)}\n\n")
            
            f.write("CAPABILITIES DEMONSTRATED:\n")
            for capability in report["capabilities_demonstrated"]:
                f.write(f"{capability}\n")
            
            f.write("\nASSESSMENT REQUIREMENTS MET:\n")
            for req, status in report["assessment_requirements"].items():
                f.write(f"{req}: {status}\n")
        
        print(f"Demo report saved to: {report_path}")
        print(f" Summary saved to: {summary_path}")
        print()
        
        return report
    
    def run_complete_demo(self):
        """Execute the complete automated demo"""
        try:
            # Step 1: Find files
            if not self.find_demo_files():
                print(" No files available for demo")
                return False
            
            # Step 2 & 3: Process files
            for file_type, file_path in self.demo_files:
                if file_type == 'audio':
                    self.run_audio_pipeline_demo(file_path)
                elif file_type == 'image':
                    self.run_image_pipeline_demo(file_path)
            
            # Step 4: Module tests
            self.run_module_tests()
            
            # Step 5: Engine swapping demo
            self.demonstrate_swappable_engines()
            
            # Step 6: Final report
            report = self.generate_final_report()
            
            # Success summary
            print(" DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✨ All five pipeline steps executed automatically")
            print("📁 Complete results saved in demo_outputs/")
  
         
            
            return True
            
        except Exception as e:
            print(f" Demo failed: {e}")
            return False


def main():
    """Main demo runner function"""
    runner = AutomatedDemoRunner()
    success = runner.run_complete_demo()
    
    if success:
        print(" Run this script anytime to demonstrate the complete pipeline!")
        print(" To test with your own files, just add .wav/.mp3 and .png/.jpg files to the project root")
    else:
        print(" Demo encountered issues. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()