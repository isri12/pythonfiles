'''

To use the web version:

Install dependencies:

bash   pip install flask yt-dlp

Install FFmpeg (same as before):

Windows: Download from https://ffmpeg.org/download.html
macOS: brew install ffmpeg
Linux: sudo apt install ffmpeg


Run the script:

bashpython web_converter.py

Open your browser and go to: http://localhost:5000

Features of the web version:

Modern responsive web interface with tabs and styling
Real-time progress tracking with live updates
Same audio format options organized by quality
Automatic ZIP packaging of all converted files
Quality report generation included in download
Live conversion log showing detailed progress
Quick selection buttons (Select All, High Quality Only, etc.)

Advantages over tkinter version:

✅ No tkinter dependency issues
✅ Works on any OS with a web browser
✅ Better user interface with modern styling
✅ Automatic file packaging for easy download
✅ Real-time updates without freezing
✅ Can be accessed remotely if needed

The web interface is much more user-friendly and eliminates all the tkinter installation headaches. Just run the Python script and use your browser!

'''


from flask import Flask, render_template_string, request, jsonify, send_file
import threading
import os
import subprocess
import json
from pathlib import Path
import zipfile
import tempfile
import shutil

app = Flask(__name__)

class VideoAudioConverter:
    def __init__(self):
        self.audio_formats = {
            'FLAC (Lossless)': {'ext': 'flac', 'quality': 'lossless', 'bitrate': None},
            'WAV (Lossless)': {'ext': 'wav', 'quality': 'lossless', 'bitrate': None},
            'MP3 320kbps': {'ext': 'mp3', 'quality': 'high', 'bitrate': '320k'},
            'MP3 256kbps': {'ext': 'mp3', 'quality': 'high', 'bitrate': '256k'},
            'MP3 192kbps': {'ext': 'mp3', 'quality': 'medium', 'bitrate': '192k'},
            'MP3 128kbps': {'ext': 'mp3', 'quality': 'medium', 'bitrate': '128k'},
            'AAC 256kbps': {'ext': 'aac', 'quality': 'high', 'bitrate': '256k'},
            'AAC 128kbps': {'ext': 'aac', 'quality': 'medium', 'bitrate': '128k'},
            'OGG 320kbps': {'ext': 'ogg', 'quality': 'high', 'bitrate': '320k'},
            'OGG 192kbps': {'ext': 'ogg', 'quality': 'medium', 'bitrate': '192k'},
            'M4A 256kbps': {'ext': 'm4a', 'quality': 'high', 'bitrate': '256k'},
            'M4A 128kbps': {'ext': 'm4a', 'quality': 'medium', 'bitrate': '128k'}
        }
        self.conversion_status = {'progress': 0, 'status': 'Ready', 'log': [], 'completed': False}
        
    def log(self, message):
        self.conversion_status['log'].append(message)
        print(message)  # Also print to console
        
    def convert_video(self, url, selected_formats, output_dir):
        try:
            import yt_dlp
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.conversion_status = {'progress': 0, 'status': 'Starting...', 'log': [], 'completed': False}
            self.log(f"Starting conversion for {len(selected_formats)} formats...")
            
            # Get video info
            self.conversion_status['status'] = 'Getting video information...'
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video').replace('/', '_').replace('\\', '_')
                video_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            
            self.log(f"Video title: {video_title}")
            
            total_steps = len(selected_formats) + 1
            current_step = 0
            
            # Download audio
            self.conversion_status['status'] = 'Downloading audio...'
            temp_audio_path = output_path / f"{video_title}_temp.%(ext)s"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(temp_audio_path),
                'extractaudio': True,
                'audioformat': 'wav',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            current_step += 1
            self.conversion_status['progress'] = int((current_step / total_steps) * 100)
            
            # Find downloaded file
            temp_files = list(output_path.glob(f"{video_title}_temp.*"))
            if not temp_files:
                raise Exception("Failed to download audio file")
            
            source_audio = temp_files[0]
            self.log(f"Downloaded: {source_audio.name}")
            
            # Convert to selected formats
            converted_files = []
            for format_name in selected_formats:
                self.conversion_status['status'] = f'Converting to {format_name}...'
                self.log(f"Converting to {format_name}...")
                
                format_info = self.audio_formats[format_name]
                ext = format_info['ext']
                bitrate = format_info['bitrate']
                
                output_file = output_path / f"{video_title}.{ext}"
                
                # Build FFmpeg command
                cmd = ['ffmpeg', '-y', '-i', str(source_audio)]
                
                if bitrate:
                    if ext == 'mp3':
                        cmd.extend(['-codec:a', 'mp3', '-b:a', bitrate])
                    elif ext == 'aac':
                        cmd.extend(['-codec:a', 'aac', '-b:a', bitrate])
                    elif ext == 'ogg':
                        cmd.extend(['-codec:a', 'libvorbis', '-b:a', bitrate])
                    elif ext == 'm4a':
                        cmd.extend(['-codec:a', 'aac', '-b:a', bitrate])
                else:
                    if ext == 'flac':
                        cmd.extend(['-codec:a', 'flac'])
                    elif ext == 'wav':
                        cmd.extend(['-codec:a', 'pcm_s16le'])
                
                cmd.append(str(output_file))
                
                # Run conversion
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    file_size = output_file.stat().st_size / (1024 * 1024)
                    self.log(f"✓ Created: {output_file.name} ({file_size:.1f} MB)")
                    converted_files.append(output_file)
                else:
                    self.log(f"✗ Failed to create {format_name}: {result.stderr}")
                
                current_step += 1
                self.conversion_status['progress'] = int((current_step / total_steps) * 100)
            
            # Clean up temp file
            source_audio.unlink()
            
            # Create quality report
            self.create_quality_report(output_path, video_title, selected_formats)
            
            # Create ZIP file with all converted audio files
            zip_path = output_path / f"{video_title}_audio_collection.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in converted_files:
                    zipf.write(file_path, file_path.name)
                # Add quality report
                report_file = output_path / f"{video_title}_quality_report.txt"
                if report_file.exists():
                    zipf.write(report_file, report_file.name)
            
            self.conversion_status['status'] = 'Conversion completed!'
            self.conversion_status['completed'] = True
            self.conversion_status['zip_file'] = str(zip_path)
            self.log("Conversion completed successfully!")
            self.log(f"ZIP file created: {zip_path.name}")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.conversion_status['status'] = f'Error: {str(e)}'
    
    def create_quality_report(self, output_dir, video_title, selected_formats):
        report_file = output_dir / f"{video_title}_quality_report.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"Audio Quality Report for: {video_title}\n")
            f.write("=" * 50 + "\n\n")
            
            quality_groups = {'Lossless': [], 'High Quality': [], 'Medium Quality': []}
            
            for format_name in selected_formats:
                format_info = self.audio_formats[format_name]
                quality = format_info['quality']
                ext = format_info['ext']
                
                file_path = output_dir / f"{video_title}.{ext}"
                if file_path.exists():
                    file_size = file_path.stat().st_size / (1024 * 1024)
                    
                    if quality == 'lossless':
                        quality_groups['Lossless'].append((format_name, file_size, ext))
                    elif quality == 'high':
                        quality_groups['High Quality'].append((format_name, file_size, ext))
                    else:
                        quality_groups['Medium Quality'].append((format_name, file_size, ext))
            
            for group_name, files in quality_groups.items():
                if files:
                    f.write(f"{group_name}:\n")
                    f.write("-" * 20 + "\n")
                    for format_name, size, ext in sorted(files, key=lambda x: x[1], reverse=True):
                        f.write(f"  {format_name:<20} | {size:>6.1f} MB | .{ext}\n")
                    f.write("\n")

converter = VideoAudioConverter()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video to Audio Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        input[type="text"], input[type="url"] { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px; }
        input[type="text"]:focus, input[type="url"]:focus { outline: none; border-color: #667eea; }
        .format-tabs { margin: 20px 0; }
        .tab-buttons { display: flex; margin-bottom: 15px; }
        .tab-button { flex: 1; padding: 10px; background: #f8f9fa; border: 1px solid #ddd; cursor: pointer; text-align: center; font-weight: 600; }
        .tab-button.active { background: #667eea; color: white; }
        .tab-content { display: none; padding: 15px; border: 1px solid #ddd; border-radius: 0 0 6px 6px; }
        .tab-content.active { display: block; }
        .format-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .format-option { display: flex; align-items: center; padding: 8px; }
        .format-option input { margin-right: 8px; }
        .quick-buttons { margin: 15px 0; text-align: center; }
        .btn { padding: 10px 20px; margin: 0 5px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .progress-container { margin: 20px 0; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s; border-radius: 10px; }
        .status { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; font-weight: 600; }
        .log-container { margin: 20px 0; }
        .log-box { height: 200px; padding: 15px; background: #2d3748; color: #e2e8f0; border-radius: 6px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; }
        .download-section { margin: 20px 0; padding: 20px; background: #d4edda; border-radius: 6px; text-align: center; display: none; }
        .download-section.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Video to Audio Converter</h1>
            <p>Convert videos to high-quality audio in multiple formats</p>
        </div>
        <div class="content">
            <form id="converterForm">
                <div class="form-group">
                    <label for="videoUrl">Video URL:</label>
                    <input type="url" id="videoUrl" placeholder="https://www.youtube.com/watch?v=..." required>
                </div>
                
                <div class="form-group">
                    <label>Select Audio Formats:</label>
                    <div class="format-tabs">
                        <div class="tab-buttons">
                            <div class="tab-button active" onclick="showTab('lossless')">Lossless</div>
                            <div class="tab-button" onclick="showTab('high')">High Quality</div>
                            <div class="tab-button" onclick="showTab('medium')">Medium Quality</div>
                        </div>
                        
                        <div id="lossless" class="tab-content active">
                            <div class="format-grid">
                                <div class="format-option">
                                    <input type="checkbox" id="flac" name="formats" value="FLAC (Lossless)">
                                    <label for="flac">FLAC (Lossless)</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="wav" name="formats" value="WAV (Lossless)">
                                    <label for="wav">WAV (Lossless)</label>
                                </div>
                            </div>
                        </div>
                        
                        <div id="high" class="tab-content">
                            <div class="format-grid">
                                <div class="format-option">
                                    <input type="checkbox" id="mp3-320" name="formats" value="MP3 320kbps">
                                    <label for="mp3-320">MP3 320kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="mp3-256" name="formats" value="MP3 256kbps">
                                    <label for="mp3-256">MP3 256kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="aac-256" name="formats" value="AAC 256kbps">
                                    <label for="aac-256">AAC 256kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="ogg-320" name="formats" value="OGG 320kbps">
                                    <label for="ogg-320">OGG 320kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="m4a-256" name="formats" value="M4A 256kbps">
                                    <label for="m4a-256">M4A 256kbps</label>
                                </div>
                            </div>
                        </div>
                        
                        <div id="medium" class="tab-content">
                            <div class="format-grid">
                                <div class="format-option">
                                    <input type="checkbox" id="mp3-192" name="formats" value="MP3 192kbps">
                                    <label for="mp3-192">MP3 192kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="mp3-128" name="formats" value="MP3 128kbps">
                                    <label for="mp3-128">MP3 128kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="aac-128" name="formats" value="AAC 128kbps">
                                    <label for="aac-128">AAC 128kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="ogg-192" name="formats" value="OGG 192kbps">
                                    <label for="ogg-192">OGG 192kbps</label>
                                </div>
                                <div class="format-option">
                                    <input type="checkbox" id="m4a-128" name="formats" value="M4A 128kbps">
                                    <label for="m4a-128">M4A 128kbps</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quick-buttons">
                        <button type="button" class="btn btn-secondary" onclick="selectAll()">Select All</button>
                        <button type="button" class="btn btn-secondary" onclick="clearAll()">Clear All</button>
                        <button type="button" class="btn btn-secondary" onclick="selectHighQuality()">High Quality Only</button>
                    </div>
                </div>
                
                <button type="submit" id="convertBtn" class="btn btn-primary">🚀 Start Conversion</button>
            </form>
            
            <div class="progress-container" id="progressContainer" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <div class="status" id="statusText">Ready</div>
            </div>
            
            <div class="download-section" id="downloadSection">
                <h3>✅ Conversion Complete!</h3>
                <p>Your audio files have been converted and packaged.</p>
                <button type="button" class="btn btn-success" onclick="downloadFiles()">📥 Download ZIP</button>
            </div>
            
            <div class="log-container">
                <label>Conversion Log:</label>
                <div class="log-box" id="logBox"></div>
            </div>
        </div>
    </div>

    <script>
        let conversionInterval;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function selectAll() {
            document.querySelectorAll('input[name="formats"]').forEach(cb => cb.checked = true);
        }
        
        function clearAll() {
            document.querySelectorAll('input[name="formats"]').forEach(cb => cb.checked = false);
        }
        
        function selectHighQuality() {
            clearAll();
            ['flac', 'wav', 'mp3-320', 'mp3-256', 'aac-256', 'ogg-320', 'm4a-256'].forEach(id => {
                const cb = document.getElementById(id);
                if (cb) cb.checked = true;
            });
        }
        
        document.getElementById('converterForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('videoUrl').value;
            const selectedFormats = Array.from(document.querySelectorAll('input[name="formats"]:checked'))
                                        .map(cb => cb.value);
            
            if (!url) {
                alert('Please enter a video URL');
                return;
            }
            
            if (selectedFormats.length === 0) {
                alert('Please select at least one audio format');
                return;
            }
            
            startConversion(url, selectedFormats);
        });
        
        function startConversion(url, formats) {
            document.getElementById('convertBtn').disabled = true;
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('downloadSection').classList.remove('show');
            
            fetch('/convert', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url, formats: formats})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Start polling for progress
                    conversionInterval = setInterval(checkProgress, 1000);
                } else {
                    alert('Failed to start conversion: ' + data.error);
                    document.getElementById('convertBtn').disabled = false;
                }
            })
            .catch(error => {
                alert('Error: ' + error);
                document.getElementById('convertBtn').disabled = false;
            });
        }
        
        function checkProgress() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('progressFill').style.width = data.progress + '%';
                document.getElementById('statusText').textContent = data.status;
                
                const logBox = document.getElementById('logBox');
                logBox.innerHTML = data.log.map(line => '<div>' + line + '</div>').join('');
                logBox.scrollTop = logBox.scrollHeight;
                
                if (data.completed) {
                    clearInterval(conversionInterval);
                    document.getElementById('convertBtn').disabled = false;
                    document.getElementById('downloadSection').classList.add('show');
                }
            });
        }
        
        function downloadFiles() {
            window.location.href = '/download';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        url = data.get('url')
        formats = data.get('formats', [])
        
        if not url or not formats:
            return jsonify({'success': False, 'error': 'Missing URL or formats'})
        
        # Create temp output directory
        output_dir = tempfile.mkdtemp(prefix='audio_converter_')
        
        # Start conversion in background thread
        thread = threading.Thread(target=converter.convert_video, args=(url, formats, output_dir))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    return jsonify(converter.conversion_status)

@app.route('/download')
def download():
    if 'zip_file' in converter.conversion_status:
        zip_path = converter.conversion_status['zip_file']
        if os.path.exists(zip_path):
            return send_file(zip_path, as_attachment=True)
    return "No files available for download", 404

if __name__ == '__main__':
    # Check dependencies
    missing_deps = []
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("ffmpeg")
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Please install:")
        if "yt-dlp" in missing_deps:
            print("  pip install yt-dlp")
        if "ffmpeg" in missing_deps:
            print("  Install FFmpeg from https://ffmpeg.org/download.html")
        exit(1)
    
    print("Starting Video to Audio Converter...")
    print("Open http://localhost:5000 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)