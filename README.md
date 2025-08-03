# Receptro.AI - Modular Media & Data Processing Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI Whisper](https://img.shields.io/badge/AI-OpenAI%20Whisper-green.svg)](https://github.com/openai/whisper)
[![Flask](https://img.shields.io/badge/Web-Flask-red.svg)](https://flask.palletsprojects.com/)

> **Assessment Project**: Complete end-to-end solution that seamlessly processes speech, text, and document images using state-of-the-art AI models with multiple interactive interfaces.

##  Overview

Receptro.AI is a comprehensive, modular pipeline that demonstrates advanced AI integration across multiple domains:

- ** Speech-to-Text**: High-accuracy transcription using OpenAI Whisper
- ** Intent Recognition**: Natural language understanding with parameter extraction
- ** Text-to-Speech**: Natural audio response generation
- ** Document OCR**: Intelligent field extraction from photographed documents
- ** Unified Orchestration**: Single interface with intelligent file-type routing

##  Key Features

### Core Pipeline
- **Modular Architecture**: Each component independently swappable
- **Auto-Routing**: Detects file type and routes to appropriate pipeline
- **Local Processing**: No API dependencies for core functionality
- **High Accuracy**: State-of-the-art AI models (Whisper, Tesseract)
- **Multiple Formats**: Supports various audio and image file types

Bonus Features 

 Automated End-to-End Demo: Complete pipeline demonstration in one command
 Interactive Web Interface: Professional drag-and-drop file processing
 Docker Support: Containerized deployment with Docker Compose
 Comprehensive Reporting: Detailed analysis and metrics
 Engine Swapping: Easy replacement of any processing component
 
##  Quick Start

### Prerequisites

**System Dependencies:**
```bash
# macOS
brew install tesseract ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-eng ffmpeg

# Windows
# Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Download FFmpeg from: https://ffmpeg.org/download.html
```

**Python Dependencies:**
```bash
pip install -r requirements-simple.txt
```

### Basic Usage

```bash
# Process audio file (complete speech pipeline)
python main.py sample.wav

# Process document image (OCR extraction)
python main.py document.png

# Auto-detect file type and route appropriately
python main.py your-file.mp3
python main.py your-image.jpg
```

##  Demo Options

### 1. Automated End-to-End Demo 
```bash
python run_full_demo.py
```
**The main showcase feature!** Automatically:
- Discovers available input files
- Processes through complete pipeline
- Demonstrates all 5 core capabilities
- Generates comprehensive reports
- Shows engine swapping options

### 2. Interactive Web Interface 
```bash
python web_server.py
# Open http://localhost:5000
```
**Professional web interface featuring:**
- Real-time file upload and processing
- Live progress tracking with status updates
- Drag-and-drop functionality
- Download generated results
- Beautiful, responsive design

### 3. Individual Module Testing 
```bash
# Test each component independently
python transcribe/transcribe.py sample.wav
python interpret/interpret.py outputs/transcript.txt
python synthesize/synthesize.py --text "Hello world"
python extract/extract.py document.png
```

### 4. Docker Deployment 
```bash
# Complete containerized deployment
docker-compose up

# Or build and run manually
docker build -t receptro-ai .
docker run -v $(pwd)/inputs:/app/inputs -v $(pwd)/outputs:/app/outputs receptro-ai
```

##  Project Structure

```
receptro-ai/
├──  main.py                    # Main CLI entry point
├──  run_full_demo.py          # Automated end-to-end demo
├──  web_server.py             # Interactive web interface
├──  requirements-simple.txt    # Python dependencies
├──  README.md                  # This file
├── 
├──  transcribe/
│   └── transcribe.py            # Speech-to-text (OpenAI Whisper)
├──  interpret/
│   └── interpret.py             # Intent recognition (NLU)
├──  synthesize/
│   └── synthesize.py            # Text-to-speech (Google TTS)
├──  extract/
│   └── extract.py               # Document OCR (Tesseract)
├──  orchestrator/
│   └── process.py               # Main pipeline controller
├── 
├──  outputs/                   # Generated results
├──  demo_outputs/              # Automated demo results
├──  web_outputs/               # Web interface results
├── 
├──  docker-compose.yml         # Docker deployment
├──  Dockerfile                 # Container configuration
└──  web_ui.html               # Static web demo
```

##  Pipeline Flow

### Audio Processing Pipeline
```
 Input: sample.wav
    ↓
 Speech-to-Text (Whisper)
    ↓ 
 outputs/transcript.txt
    ↓
 Intent Recognition (NLU)
    ↓
 outputs/intent.json
    ↓
 Text-to-Speech (gTTS)
    ↓
 outputs/reply.mp3
```

### Document Processing Pipeline
```
 Input: document.png
    ↓
 OCR Processing (Tesseract)
    ↓
 Field Extraction (Regex)
    ↓
 outputs/fields.json
```

##  Sample Outputs

### Audio Pipeline Results
```json
{
  "input_file": "sample.wav",
  "transcript_text": "I would like to book an appointment for Monday at 2 PM",
  "intent": "book_appointment",
  "confidence": 0.85,
  "parameters": {
    "date": "Monday",
    "time": "2 PM"
  },
  "response_text": "Okay, I've booked your appointment for Monday at 2 PM.",
  "outputs": {
    "transcript": "outputs/transcript.txt",
    "intent": "outputs/intent.json",
    "reply_audio": "outputs/reply.mp3"
  }
}
```

### Document Pipeline Results
```json
{
  "input_file": "license.png",
  "extracted_fields": {
    "name": "John Doe",
    "date_of_birth": "05/21/1990",
    "id_number": "ABC123456",
    "address": "123 Main Street",
    "expiry_date": "12/31/2025"
  },
  "field_count": 5,
  "outputs": {
    "fields": "outputs/fields.json"
  }
}
```

## Engine Swapping

The modular design allows easy replacement of any processing component:

### Speech-to-Text Alternatives
```python
# Current: OpenAI Whisper (local)
# Alternatives: Google Speech API, Azure Speech, AWS Transcribe

# In transcribe/transcribe.py:
class AudioTranscriber:
    def __init__(self, engine="whisper"):
        if engine == "google":
            self.model = GoogleSpeechClient()
        elif engine == "azure":
            self.model = AzureSpeechClient()
        # ... easy swapping
```

### Intent Recognition Alternatives
```python
# Current: Rule-based patterns
# Alternatives: spaCy NER, Hugging Face Transformers, OpenAI GPT

# In interpret/interpret.py:
class IntentParser:
    def __init__(self, engine="rule_based"):
        if engine == "spacy":
            self.nlp = spacy.load("en_core_web_sm")
        elif engine == "transformers":
            self.classifier = pipeline("text-classification")
        # ... easy swapping
```

### Text-to-Speech Alternatives
```python
# Current: Google TTS (gTTS)
# Alternatives: pyttsx3 (offline), Coqui TTS, Azure Cognitive Services

# In synthesize/synthesize.py:
class TextToSpeech:
    def __init__(self, engine="gtts"):
        if engine == "pyttsx3":
            self.tts = pyttsx3.init()
        elif engine == "azure":
            self.tts = AzureTTSClient()
        # ... easy swapping
```

### OCR Alternatives
```python
# Current: Tesseract (local)
# Alternatives: Google Vision API, Azure Computer Vision, AWS Textract

# In extract/extract.py:
class DocumentExtractor:
    def __init__(self, engine="tesseract"):
        if engine == "google_vision":
            self.client = vision.ImageAnnotatorClient()
        elif engine == "azure":
            self.client = ComputerVisionClient()
        # ... easy swapping
```

## 🛠️ Development

### Running Tests
```bash
# Test individual modules
python test_pipeline.py

# Test complete pipeline
python run_full_demo.py

# Test web interface
python web_server.py
```

### Adding New Engines
1. **Create new engine class** in the appropriate module
2. **Update the factory method** to include new option
3. **Add configuration** in the module's `__init__` method
4. **Update documentation** with usage examples

### Performance Optimization
- **Lazy Loading**: Models load only when needed
- **Caching**: Processed results cached for repeated use
- **Asynchronous Processing**: Web interface uses background processing
- **Memory Management**: Efficient handling of large audio/image files

## 📋 Assessment Requirements

| Requirement | Implementation | Status |
|-------------|----------------|---------|
| **Turn speech into text** | OpenAI Whisper integration |  |
| **Infer intent and parameters** | Rule-based NLU with regex patterns | |
| **Convert text back into audio** | Google TTS (gTTS) synthesis |  |
| **Extract fields from documents** | Tesseract OCR with smart parsing |  |
| **Single, easy-to-use interface** | CLI with auto file-type routing |  |
| **Clean, well-organized code** | Modular structure with clear separation |  |
| **Swappable engine design** | Factory pattern with documented alternatives |  |
| ** Automated end-to-end runner** | Multiple demo scripts and interfaces |  |

## 🎬 Demo Instructions

### For Quick Evaluation (2 minutes)
```bash
# Complete automated demonstration
python run_full_demo.py
```

### For Interactive Testing (5 minutes)
```bash
# Start web interface
python web_server.py
# Visit http://localhost:5000
# Upload audio/image files for real-time processing
```

### For Individual Component Testing
```bash
# Process specific files
python main.py your-audio-file.wav
python main.py your-document-image.png
```

##  Configuration

### Environment Variables
```bash
# Optional: Set custom model paths
export WHISPER_MODEL_SIZE=base  # tiny, base, small, medium, large
export TTS_ENGINE=gtts          # gtts, pyttsx3
export OCR_ENGINE=tesseract     # tesseract, google_vision
```

### Custom Configuration
```python
# config.py (optional)
PROCESSING_CONFIG = {
    "whisper": {"model_size": "base"},
    "tts": {"engine": "gtts", "lang": "en"},
    "ocr": {"engine": "tesseract", "lang": "eng"},
    "intent": {"confidence_threshold": 0.5}
}
```

##  Troubleshooting

### Common Issues

**Whisper model download fails:**
```bash
# Pre-download the model
python -c "import whisper; whisper.load_model('base')"
```

**Tesseract not found:**
```bash
# Verify installation
tesseract --version

# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-eng

# macOS  
brew install tesseract
```

**Audio synthesis fails:**
```bash
# Install alternative TTS
pip install pyttsx3

# Test synthesis
python synthesize/synthesize.py --text "Hello world" --engine pyttsx3
```

**Web interface not loading:**
```bash
# Check Flask installation
pip install Flask Werkzeug

# Verify port is available
lsof -i :5000
```



### Development Setup
```bash
# Clone the repository
git clone https://github.com/your-username/receptro-ai.git
cd receptro-ai

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run demo
python run_full_demo.py
```



## Acknowledgments

- **OpenAI Whisper** - State-of-the-art speech recognition
- **Tesseract OCR** - Reliable text extraction
- **Google Text-to-Speech** - High-quality voice synthesis
- **Flask** - Lightweight web framework
- **Docker** - Containerization platform



---

** Assessment Note**: This project demonstrates all required functionality plus bonus automation features. The `run_full_demo.py` script provides a complete automated demonstration of all five pipeline steps in one seamless execution.

