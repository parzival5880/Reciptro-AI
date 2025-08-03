#!/usr/bin/env python3
"""
Setup script for Receptro.AI
Handles initial setup, model downloads, and system checks
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_system_dependencies():
    """Check if required system dependencies are installed"""
    print("🔍 Checking system dependencies...")
    
    # Check Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR found")
        else:
            print("❌ Tesseract OCR not found")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR not found")
        print_tesseract_install_instructions()
        return False
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
        else:
            print("❌ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        print_ffmpeg_install_instructions()
        return False
    
    return True

def print_tesseract_install_instructions():
    """Print Tesseract installation instructions"""
    system = platform.system().lower()
    print("\n📦 Tesseract Installation Instructions:")
    
    if system == "linux":
        print("Ubuntu/Debian: sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-eng")
        print("CentOS/RHEL: sudo yum install tesseract tesseract-langpack-eng")
    elif system == "darwin":
        print("macOS: brew install tesseract")
    elif system == "windows":
        print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    else:
        print("Please install Tesseract OCR for your operating system")

def print_ffmpeg_install_instructions():
    """Print FFmpeg installation instructions"""
    system = platform.system().lower()
    print("\n📦 FFmpeg Installation Instructions:")
    
    if system == "linux":
        print("Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("CentOS/RHEL: sudo yum install ffmpeg")
    elif system == "darwin":
        print("macOS: brew install ffmpeg")
    elif system == "windows":
        print("Windows: Download from https://ffmpeg.org/download.html")
    else:
        print("Please install FFmpeg for your operating system")

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def download_models():
    """Download required AI models"""
    print("\n🤖 Downloading AI models...")
    
    # Download Whisper model
    try:
        print("Downloading Whisper base model...")
        import whisper
        whisper.load_model("base")
        print("✅ Whisper model downloaded")
    except Exception as e:
        print(f"⚠️  Whisper model download failed: {e}")
    
    # Download TTS model
    try:
        print("Downloading TTS model...")
        from TTS.api import TTS
        TTS(model_name="tts_models/en/ljspeech/fast_pitch", progress_bar=False)
        print("✅ TTS model downloaded")
    except Exception as e:
        print(f"⚠️  TTS model download failed: {e}")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "outputs",
        "tests/inputs",
        "tests/outputs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def create_sample_files():
    """Create sample input files if they don't exist"""
    print("\n📄 Creating sample files...")
    
    # Create sample audio file placeholder
    sample_wav = Path("sample.wav")
    if not sample_wav.exists():
        print("⚠️  sample.wav not found. Please provide a 5-10 second audio file.")
        print("   You can record one using your phone or computer and save it as sample.wav")
    
    # Create sample document image placeholder
    sample_doc = Path("doc.png")
    if not sample_doc.exists():
        print("⚠️  doc.png not found. Please provide a document image.")
        print("   Take a photo of an ID card, license, or any document with text fields.")

def run_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    
    # Test individual modules
    modules_to_test = [
        ("transcribe.transcribe", "Transcription module"),
        ("interpret.interpret", "Intent recognition module"),
        ("synthesize.synthesize", "Text-to-speech module"),
        ("extract.extract", "Document extraction module"),
        ("orchestrator.process", "Main orchestrator")
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description} - OK")
        except ImportError as e:
            print(f"❌ {description} - Failed: {e}")

def main():
    """Main setup function"""
    print("🚀 Receptro.AI Setup")
    print("=" * 50)
    
    # Check system dependencies
    if not check_system_dependencies():
        print("\n❌ System dependencies missing. Please install them and run setup again.")
        return
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies.")
        return
    
    # Create directories
    create_directories()
    
    # Download models
    download_models()
    
    # Create sample files
    create_sample_files()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\n🚀 Quick start:")
    print("   python main.py sample.wav    # Process audio")
    print("   python main.py doc.png       # Process document")
    print("\n📖 See README.md for detailed usage instructions.")

if __name__ == "__main__":
    main()