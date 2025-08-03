#!/usr/bin/env python3
"""
Receptro.AI Web Server
Real interactive web interface that processes files through the actual pipeline
"""

import os
import sys
import json
import uuid
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.process import MediaProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'receptro-ai-demo-key'
app.config['UPLOAD_FOLDER'] = 'web_uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('web_outputs', exist_ok=True)

# Store processing results in memory (in production, use Redis or database)
processing_results = {}
processing_status = {}

# Allowed file extensions
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'audio':
        return ext in ALLOWED_AUDIO_EXTENSIONS
    elif file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    
    return False

def process_file_async(file_id, file_path, file_type):
    """Process file asynchronously"""
    try:
        processing_status[file_id] = {
            'status': 'processing',
            'step': 'Initializing...',
            'progress': 0
        }
        
        # Initialize processor
        output_dir = f"web_outputs/{file_id}"
        os.makedirs(output_dir, exist_ok=True)
        processor = MediaProcessor(output_dir=output_dir)
        
        # Update status
        processing_status[file_id]['step'] = 'Loading models...'
        processing_status[file_id]['progress'] = 20
        
        # Process the file
        processing_status[file_id]['step'] = 'Processing file...'
        processing_status[file_id]['progress'] = 40
        
        result = processor.process_file(file_path)
        
        # Update status
        processing_status[file_id]['step'] = 'Finalizing...'
        processing_status[file_id]['progress'] = 90
        
        # Store result
        processing_results[file_id] = result
        processing_status[file_id] = {
            'status': 'completed',
            'step': 'Complete!',
            'progress': 100
        }
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        processing_status[file_id] = {
            'status': 'error',
            'step': f'Error: {str(e)}',
            'progress': 0
        }
        processing_results[file_id] = {'error': str(e)}

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(WEB_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'auto')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Auto-detect file type if not specified
        if file_type == 'auto':
            if any(file.filename.lower().endswith(ext) for ext in ['.wav', '.mp3', '.m4a', '.flac']):
                file_type = 'audio'
            elif any(file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                file_type = 'image'
            else:
                return jsonify({'error': 'Unsupported file type'}), 400
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': f'File type not supported for {file_type} processing'}), 400
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(file_path)
        
        # Start processing in background
        thread = threading.Thread(
            target=process_file_async,
            args=(file_id, file_path, file_type)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'file_id': file_id,
            'filename': filename,
            'type': file_type,
            'status': 'uploaded'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<file_id>')
def get_status(file_id):
    """Get processing status"""
    if file_id not in processing_status:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify(processing_status[file_id])

@app.route('/result/<file_id>')
def get_result(file_id):
    """Get processing result"""
    if file_id not in processing_results:
        return jsonify({'error': 'Result not found'}), 404
    
    return jsonify(processing_results[file_id])

@app.route('/download/<file_id>/<file_type>')
def download_file(file_id, file_type):
    """Download generated files"""
    try:
        output_dir = Path(f"web_outputs/{file_id}")
        
        file_map = {
            'transcript': 'transcript.txt',
            'intent': 'intent.json',
            'reply': 'reply.mp3',
            'fields': 'fields.json'
        }
        
        if file_type not in file_map:
            return jsonify({'error': 'Invalid file type'}), 400
        
        file_path = output_dir / file_map[file_type]
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Web template with real interactivity
WEB_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Receptro.AI - Interactive Processing Pipeline</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .upload-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }

        .upload-area {
            border: 3px dashed #2196F3;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background: white;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }

        .upload-area:hover {
            background: #f0f8ff;
            border-color: #1976D2;
        }

        .upload-area.dragover {
            background: #e3f2fd;
            border-color: #0d47a1;
        }

        .upload-icon {
            font-size: 3em;
            color: #2196F3;
            margin-bottom: 15px;
        }

        .file-input {
            display: none;
        }

        .btn {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .processing-status {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            transition: width 0.3s ease;
            width: 0%;
        }

        .results-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            display: none;
        }

        .result-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
        }

        .download-links {
            margin: 15px 0;
        }

        .download-link {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            margin: 5px;
            font-size: 0.9em;
        }

        .download-link:hover {
            background: #45a049;
        }

        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f44336;
            margin: 15px 0;
        }

        .success-message {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            margin: 15px 0;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🚀 Receptro.AI</h1>
            <p>Interactive Media Processing Pipeline</p>
            <p><small>✨ Real-time processing with actual AI models</small></p>
        </header>

        <main class="main-content">
            <section class="upload-section">
                <h2>🎮 Process Your Files</h2>
                <p>Upload audio or image files for real-time processing through the AI pipeline!</p>

                <div class="upload-area" id="audioUpload">
                    <div class="upload-icon">🎵</div>
                    <h3>Upload Audio File</h3>
                    <p>Supports: .wav, .mp3, .m4a, .flac files</p>
                    <p><em>Will transcribe → analyze intent → generate speech response</em></p>
                    <input type="file" id="audioFile" class="file-input" accept="audio/*">
                    <button class="btn" onclick="document.getElementById('audioFile').click()">Choose Audio File</button>
                </div>

                <div class="upload-area" id="imageUpload">
                    <div class="upload-icon">📄</div>
                    <h3>Upload Document Image</h3>
                    <p>Supports: .png, .jpg, .jpeg files</p>
                    <p><em>Will extract text → identify fields → structure data</em></p>
                    <input type="file" id="imageFile" class="file-input" accept="image/*">
                    <button class="btn" onclick="document.getElementById('imageFile').click()">Choose Image File</button>
                </div>

                <div class="processing-status" id="processingStatus">
                    <h4><span class="spinner"></span>Processing...</h4>
                    <p id="statusText">Initializing...</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p><small id="progressText">0% complete</small></p>
                </div>

                <div class="results-section" id="resultsSection">
                    <h3> Processing Results</h3>
                    <div id="resultsContent"></div>
                </div>
            </section>
        </main>
    </div>

    <script>
        let currentFileId = null;
        let statusInterval = null;

        // File upload handlers
        document.getElementById('audioFile').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0], 'audio');
            }
        });

        document.getElementById('imageFile').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0], 'image');
            }
        });

        // Drag and drop functionality
        ['audioUpload', 'imageUpload'].forEach(id => {
            const element = document.getElementById(id);
            
            element.addEventListener('dragover', function(e) {
                e.preventDefault();
                element.classList.add('dragover');
            });

            element.addEventListener('dragleave', function(e) {
                e.preventDefault();
                element.classList.remove('dragover');
            });

            element.addEventListener('drop', function(e) {
                e.preventDefault();
                element.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const type = id === 'audioUpload' ? 'audio' : 'image';
                    uploadFile(files[0], type);
                }
            });
        });

        function uploadFile(file, type) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('type', type);

            // Show processing status
            document.getElementById('processingStatus').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
            
            // Reset progress
            updateProgress(0, 'Uploading file...');

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                currentFileId = data.file_id;
                updateProgress(10, 'File uploaded, starting processing...');
                
                // Start polling for status
                statusInterval = setInterval(checkStatus, 1000);
            })
            .catch(error => {
                showError('Upload failed: ' + error.message);
            });
        }

        function checkStatus() {
            if (!currentFileId) return;

            fetch('/status/' + currentFileId)
            .then(response => response.json())
            .then(data => {
                updateProgress(data.progress, data.step);
                
                if (data.status === 'completed') {
                    clearInterval(statusInterval);
                    loadResults();
                } else if (data.status === 'error') {
                    clearInterval(statusInterval);
                    showError(data.step);
                }
            })
            .catch(error => {
                clearInterval(statusInterval);
                showError('Status check failed: ' + error.message);
            });
        }

        function loadResults() {
            fetch('/result/' + currentFileId)
            .then(response => response.json())
            .then(data => {
                document.getElementById('processingStatus').style.display = 'none';
                showResults(data);
            })
            .catch(error => {
                showError('Failed to load results: ' + error.message);
            });
        }

        function showResults(data) {
            const resultsContent = document.getElementById('resultsContent');
            let html = '';

            if (data.error) {
                html = '<div class="error-message">Processing failed: ' + data.error + '</div>';
            } else if (data.file_type === 'audio') {
                html = `
                    <div class="success-message"> Audio processing completed successfully!</div>
                    <div class="result-item">
                        <h4>Transcript</h4>
                        <p>${data.transcript_text || 'N/A'}</p>
                    </div>
                    <div class="result-item">
                        <h4>Intent Analysis</h4>
                        <p><strong>Intent:</strong> ${data.intent || 'N/A'}</p>
                        <p><strong>Confidence:</strong> ${data.confidence || 0}</p>
                        <p><strong>Parameters:</strong> ${JSON.stringify(data.parameters || {})}</p>
                    </div>
                    <div class="result-item">
                        <h4> Generated Response</h4>
                        <p>${data.response_text || 'N/A'}</p>
                    </div>
                    <div class="download-links">
                        <h4>📂 Download Files:</h4>
                        <a href="/download/${currentFileId}/transcript" class="download-link"> Transcript</a>
                        <a href="/download/${currentFileId}/intent" class="download-link"> Intent JSON</a>
                        <a href="/download/${currentFileId}/reply" class="download-link"> Audio Reply</a>
                    </div>
                `;
            } else if (data.file_type === 'image') {
                html = `
                    <div class="success-message"> Document processing completed successfully!</div>
                    <div class="result-item">
                        <h4>🔍 Extracted Fields (${data.field_count || 0} found)</h4>
                `;
                
                for (const [key, value] of Object.entries(data.extracted_fields || {})) {
                    html += `<p><strong>${key}:</strong> ${value}</p>`;
                }
                
                html += `
                    </div>
                    <div class="download-links">
                        <h4>📂 Download Files:</h4>
                        <a href="/download/${currentFileId}/fields" class="download-link">📄 Extracted Data JSON</a>
                    </div>
                `;
            }

            resultsContent.innerHTML = html;
            document.getElementById('resultsSection').style.display = 'block';
        }

        function updateProgress(progress, text) {
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = progress + '% complete';
            document.getElementById('statusText').textContent = text;
        }

        function showError(message) {
            document.getElementById('processingStatus').style.display = 'none';
            document.getElementById('resultsContent').innerHTML = 
                '<div class="error-message"> ' + message + '</div>';
            document.getElementById('resultsSection').style.display = 'block';
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print(" Starting Receptro.AI Web Server...")
    print("Open your browser to: http://localhost:5003")
    print(" Interactive processing with real AI models!")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5003)