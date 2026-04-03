from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from flask_cors import CORS
import socket

# Get local IP address
def get_local_ip():
    try:
        # Create a socket connection to an external server (doesn't actually connect)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Google's public DNS server
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Could not determine local IP: {e}")
        return '0.0.0.0'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Get server IP and port
SERVER_IP = get_local_ip()
PORT = 5000

# Allowed file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Mobile Voice Recorder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 24px;
            font-size: 24px;
        }
        .button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            margin: 10px 0;
            width: 200px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .button:active {
            transform: scale(0.95);
        }
        .button.stop {
            background: #f44336;
        }
        .status {
            margin: 20px 0;
            padding: 12px;
            border-radius: 8px;
            background: #f0f0f0;
            color: #555;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #f44336;
            margin-right: 8px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        .server-info {
            margin-top: 20px;
            font-size: 14px;
            color: #666;
            background: #f9f9f9;
            padding: 10px;
            border-radius: 8px;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Voice Recorder</h1>
        <div class="status" id="status">Ready to record</div>
        <button class="button" id="recordButton">Start Recording</button>
        <div class="server-info">
            <div>Server: <span id="serverUrl">Not connected</span></div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        const recordButton = document.getElementById('recordButton');
        const statusElement = document.getElementById('status');
        const serverUrlElement = document.getElementById('serverUrl');
        
        // Get server URL from query parameter or use current host
        const urlParams = new URLSearchParams(window.location.search);
        const serverUrl = urlParams.get('server') || window.location.origin;
        serverUrlElement.textContent = serverUrl;

        // Check for microphone access
        async function initRecorder() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = async () => {
                    if (audioChunks.length === 0) return;
                    
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    await uploadAudio(audioBlob);
                    audioChunks = [];
                };

                return true;
            } catch (error) {
                console.error('Error initializing recorder:', error);
                statusElement.textContent = 'Error: Could not access microphone';
                return false;
            }
        }


        async function uploadAudio(audioBlob) {
            statusElement.innerHTML = '<span class="pulse"></span> Uploading...';
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            
            try {
                const response = await fetch(`${serverUrl}/upload`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    statusElement.textContent = 'Recording uploaded successfully!';
                    setTimeout(() => {
                        statusElement.textContent = 'Ready to record';
                    }, 3000);
                } else {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                statusElement.textContent = 'Error uploading recording';
            }
        }

        // Initialize on page load
        window.onload = async () => {
            const success = await initRecorder();
            if (!success) {
                recordButton.disabled = true;
            }
        };

        // Toggle recording
        recordButton.addEventListener('click', () => {
            if (mediaRecorder.state === 'inactive') {
                audioChunks = [];
                mediaRecorder.start();
                recordButton.textContent = 'Stop Recording';
                recordButton.classList.add('stop');
                statusElement.innerHTML = '<span class="pulse"></span> Recording...';
            } else {
                mediaRecorder.stop();
                recordButton.textContent = 'Start Recording';
                recordButton.classList.remove('stop');
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'wav'
        filename = f"recording_{timestamp}_{unique_id}.{ext}"
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"File saved: {filepath}")
        
        response = jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': os.path.getsize(filepath)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print(f"\nTo access from other devices on the same network:")
    print(f"- Open http://{SERVER_IP}:{PORT} in your mobile browser")
    print("\nMake sure your device is connected to the same network as this computer.")
    print("\nTo connect from mobile, open this URL in your mobile browser:")
    print(f"http://{SERVER_IP}:{PORT}")
    
    # For development, use adhoc SSL (self-signed certificate)
    # In production, you should use proper SSL certificates
    print("\nWARNING: Using self-signed certificate. You may see a security warning in your browser.")
    app.run(host='0.0.0.0', port=PORT, ssl_context='adhoc', debug=True)
