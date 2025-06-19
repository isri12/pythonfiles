#!/usr/bin/env python3
"""
Image to PDF Converter
Supports both Tkinter desktop GUI and Flask web GUI

Features:
Desktop GUI (Tkinter):

File selection dialog for multiple images
Preview list of selected images
Clear selection option
Save dialog for output PDF
Error handling with message boxes

Web GUI (Flask):

Drag-and-drop style file upload interface
Multiple file selection
Real-time file list preview
Automatic PDF download
Responsive design with modern styling

Core Functionality:

Supports multiple image formats (JPG, PNG, BMP, TIFF, WebP)
Converts images to RGB format if needed
Combines multiple images into a single PDF
Proper error handling and cleanup

Usage:
Install required dependencies:
bash  
$ sudo apt-get install python3-tk
pip install Pillow flask
Run with Tkinter GUI (default):
bashpython script.py
# or
python script.py --mode tkinter
Run with Flask web GUI:
bashpython script.py --mode flask
Flask with custom host/port:
bashpython script.py --mode flask --host 0.0.0.0 --port 8080 --debug

"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from flask import Flask, render_template_string, request, send_file, flash, redirect, url_for
import tempfile
import shutil
from werkzeug.utils import secure_filename

class ImageToPDFConverter:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    def convert_images_to_pdf(self, image_paths, output_path):
        """Convert multiple images to a single PDF"""
        if not image_paths:
            raise ValueError("No images provided")
        
        images = []
        try:
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    continue
                
                img = Image.open(img_path)
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            if not images:
                raise ValueError("No valid images found")
            
            # Save as PDF
            images[0].save(output_path, save_all=True, append_images=images[1:])
            return True
            
        except Exception as e:
            raise Exception(f"Error converting images to PDF: {str(e)}")
        finally:
            # Clean up image objects
            for img in images:
                img.close()

class TkinterGUI:
    def __init__(self):
        self.converter = ImageToPDFConverter()
        self.image_paths = []
        
        self.root = tk.Tk()
        self.root.title("Image to PDF Converter")
        self.root.geometry("600x500")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Image to PDF Converter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Select images button
        select_btn = ttk.Button(main_frame, text="Select Images", command=self.select_images)
        select_btn.grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        # Clear selection button
        clear_btn = ttk.Button(main_frame, text="Clear Selection", command=self.clear_selection)
        clear_btn.grid(row=1, column=1, sticky=tk.W)
        
        # Selected images listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.images_listbox = tk.Listbox(list_frame, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.images_listbox.yview)
        self.images_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.images_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Convert button
        convert_btn = ttk.Button(main_frame, text="Convert to PDF", command=self.convert_to_pdf)
        convert_btn.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Configure main frame grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def select_images(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=filetypes
        )
        
        if files:
            self.image_paths.extend(files)
            self.update_listbox()
    
    def clear_selection(self):
        self.image_paths.clear()
        self.update_listbox()
    
    def update_listbox(self):
        self.images_listbox.delete(0, tk.END)
        for path in self.image_paths:
            self.images_listbox.insert(tk.END, os.path.basename(path))
    
    def convert_to_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("Warning", "Please select at least one image")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save PDF as...",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if output_file:
            try:
                self.converter.convert_images_to_pdf(self.image_paths, output_file)
                messagebox.showinfo("Success", f"PDF created successfully!\nSaved as: {output_file}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def run(self):
        self.root.mainloop()

# Flask Web GUI
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

converter = ImageToPDFConverter()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image to PDF Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background: #fafafa;
        }
        .upload-area:hover {
            border-color: #007bff;
            background: #f0f8ff;
        }
        input[type="file"] {
            margin: 10px 0;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
        }
        button:hover {
            background: #0056b3;
        }
        .file-list {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .alert {
            padding: 12px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .alert-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .alert-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .progress {
            display: none;
            margin: 20px 0;
        }
        #fileList {
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖼️ Image to PDF Converter</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-area">
                <h3>📁 Select Images</h3>
                <p>Choose multiple image files (JPG, PNG, BMP, TIFF, WebP)</p>
                <input type="file" name="images" multiple accept="image/*" id="imageInput" required>
                <div id="fileList" class="file-list" style="display: none;"></div>
            </div>
            
            <div style="text-align: center;">
                <button type="submit" id="convertBtn">🔄 Convert to PDF</button>
                <button type="button" onclick="clearFiles()">🗑️ Clear Selection</button>
            </div>
            
            <div class="progress" id="progress">
                <p>Converting images to PDF... Please wait.</p>
            </div>
        </form>
        
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p><strong>Instructions:</strong></p>
            <p>1. Select multiple image files using the file picker</p>
            <p>2. Click "Convert to PDF" to create your PDF</p>
            <p>3. The PDF will be automatically downloaded</p>
        </div>
    </div>
    
    <script>
        document.getElementById('imageInput').addEventListener('change', function() {
            const fileList = document.getElementById('fileList');
            const files = this.files;
            
            if (files.length > 0) {
                fileList.style.display = 'block';
                fileList.innerHTML = '<h4>Selected Files:</h4>';
                for (let i = 0; i < files.length; i++) {
                    fileList.innerHTML += '<p>📄 ' + files[i].name + '</p>';
                }
            } else {
                fileList.style.display = 'none';
            }
        });
        
        document.getElementById('uploadForm').addEventListener('submit', function() {
            document.getElementById('convertBtn').disabled = true;
            document.getElementById('progress').style.display = 'block';
        });
        
        function clearFiles() {
            document.getElementById('imageInput').value = '';
            document.getElementById('fileList').style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('No files selected', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('images')
        if not files or all(f.filename == '' for f in files):
            flash('No files selected', 'error')
            return redirect(request.url)
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        
        try:
            # Save uploaded files
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    if any(filename.lower().endswith(ext) for ext in converter.supported_formats):
                        filepath = os.path.join(temp_dir, filename)
                        file.save(filepath)
                        image_paths.append(filepath)
            
            if not image_paths:
                flash('No valid image files found', 'error')
                return redirect(request.url)
            
            # Create PDF
            pdf_path = os.path.join(temp_dir, 'converted_images.pdf')
            converter.convert_images_to_pdf(image_paths, pdf_path)
            
            # Send file and clean up
            def remove_temp_dir():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return send_file(pdf_path, as_attachment=True, 
                           download_name='converted_images.pdf',
                           mimetype='application/pdf')
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            flash(f'Error converting images: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template_string(HTML_TEMPLATE)

def main():
    parser = argparse.ArgumentParser(description='Image to PDF Converter')
    parser.add_argument('--mode', choices=['tkinter', 'flask'], default='tkinter',
                       help='GUI mode: tkinter for desktop, flask for web')
    parser.add_argument('--host', default='127.0.0.1', help='Flask host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Flask port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run Flask in debug mode')
    
    args = parser.parse_args()
    
    if args.mode == 'tkinter':
        print("Starting Tkinter GUI...")
        gui = TkinterGUI()
        gui.run()
    elif args.mode == 'flask':
        print(f"Starting Flask web server at http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
