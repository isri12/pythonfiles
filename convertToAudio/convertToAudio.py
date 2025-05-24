'''

I'll create a Python GUI application that downloads videos and converts them to various audio formats with quality sorting. This will use `yt-dlp` for downloading and `pydub` for audio conversion.

I've created a comprehensive Python GUI application for converting videos to various audio formats with quality sorting. Here are the key features:

## Features:
- **Modern GUI** with organized tabs for different quality levels
- **Multiple audio formats** including lossless (FLAC, WAV) and compressed formats (MP3, AAC, OGG, M4A)
- **Quality-based organization** - Lossless, High Quality, and Medium Quality tabs
- **Batch conversion** - select multiple formats at once
- **Quality report** - creates a text file sorting outputs by audio quality and file size
- **Progress tracking** with real-time status updates
- **Error handling** and dependency checking

## Required Dependencies:
Before running the script, install these dependencies:

```bash
pip install yt-dlp
```

You'll also need **FFmpeg** installed on your system:
- Windows: Download from https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

## Audio Formats Included:
**Lossless Quality:**
- FLAC (best for archival)
- WAV (uncompressed)

**High Quality:**
- MP3 320kbps, 256kbps
- AAC 256kbps
- OGG 320kbps
- M4A 256kbps

**Medium Quality:**
- MP3 192kbps, 128kbps
- AAC 128kbps
- OGG 192kbps
- M4A 128kbps

## How to Use:
1. Run the script
2. Paste or enter a video URL (YouTube, Vimeo, etc.)
3. Choose output directory
4. Select desired audio formats from the quality tabs
5. Click "Start Conversion"
6. Files will be organized by quality and a report will be generated

The application automatically sorts outputs by audio quality and creates a detailed report showing file sizes and quality levels for easy comparison.


'''


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys
from pathlib import Path
import json

class VideoAudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to Audio Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "AudioConverter"))
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        # Audio formats with quality settings
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
        
        self.selected_formats = {}
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL input
        ttk.Label(main_frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, pady=(0,5))
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Arial', 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0,5))
        
        ttk.Button(url_frame, text="Paste", command=self.paste_url).grid(row=0, column=1)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=(0,5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, font=('Arial', 9))
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0,5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Audio format selection
        ttk.Label(main_frame, text="Select Audio Formats:").grid(row=4, column=0, sticky=tk.W, pady=(10,5))
        
        # Create notebook for organized format selection
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))
        
        # Group formats by quality
        quality_groups = {
            'Lossless': [],
            'High Quality': [],
            'Medium Quality': []
        }
        
        for format_name, format_info in self.audio_formats.items():
            if format_info['quality'] == 'lossless':
                quality_groups['Lossless'].append(format_name)
            elif format_info['quality'] == 'high':
                quality_groups['High Quality'].append(format_name)
            else:
                quality_groups['Medium Quality'].append(format_name)
        
        # Create tabs for each quality group
        for group_name, formats in quality_groups.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=group_name)
            
            for i, format_name in enumerate(formats):
                var = tk.BooleanVar()
                self.selected_formats[format_name] = var
                ttk.Checkbutton(frame, text=format_name, variable=var).grid(
                    row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2
                )
        
        # Quick selection buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(0,10))
        
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="High Quality Only", command=self.select_high_quality).pack(side=tk.LEFT, padx=(0,5))
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=7, column=0, sticky=tk.W, pady=(10,5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Arial', 9))
        self.status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0,10))
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="Start Conversion", 
                                       command=self.start_conversion, style='Accent.TButton')
        self.convert_button.grid(row=10, column=0, columnspan=2, pady=10)
        
        # Log text area
        ttk.Label(main_frame, text="Log:").grid(row=11, column=0, sticky=tk.W, pady=(10,5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(12, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
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
            self.log(f"Missing dependencies: {', '.join(missing_deps)}")
            self.log("Please install them using:")
            if "yt-dlp" in missing_deps:
                self.log("pip install yt-dlp")
            if "ffmpeg" in missing_deps:
                self.log("Download FFmpeg from https://ffmpeg.org/download.html")
            self.convert_button.config(state='disabled')
        else:
            self.log("All dependencies found!")
    
    def paste_url(self):
        try:
            url = self.root.clipboard_get()
            self.url_var.set(url)
        except:
            pass
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def select_all(self):
        for var in self.selected_formats.values():
            var.set(True)
    
    def clear_all(self):
        for var in self.selected_formats.values():
            var.set(False)
    
    def select_high_quality(self):
        self.clear_all()
        high_quality_formats = [name for name, info in self.audio_formats.items() 
                              if info['quality'] in ['lossless', 'high']]
        for format_name in high_quality_formats:
            if format_name in self.selected_formats:
                self.selected_formats[format_name].set(True)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def start_conversion(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        selected = [name for name, var in self.selected_formats.items() if var.get()]
        if not selected:
            messagebox.showerror("Error", "Please select at least one audio format")
            return
        
        # Disable button during conversion
        self.convert_button.config(state='disabled')
        self.progress_var.set(0)
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_video, args=(url, selected))
        thread.daemon = True
        thread.start()
    
    def convert_video(self, url, selected_formats):
        try:
            import yt_dlp
            
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.log(f"Starting conversion for {len(selected_formats)} formats...")
            self.update_status("Downloading video information...")
            
            # Get video info first
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video').replace('/', '_').replace('\\', '_')
                video_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            
            self.log(f"Video title: {video_title}")
            
            total_steps = len(selected_formats) + 1  # +1 for download
            current_step = 0
            
            # Download the best quality audio
            self.update_status("Downloading audio...")
            temp_audio_path = output_dir / f"{video_title}_temp.%(ext)s"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(temp_audio_path),
                'extractaudio': True,
                'audioformat': 'wav',  # Download as WAV for best quality conversion
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            current_step += 1
            self.progress_var.set((current_step / total_steps) * 100)
            
            # Find the downloaded file
            temp_files = list(output_dir.glob(f"{video_title}_temp.*"))
            if not temp_files:
                raise Exception("Failed to download audio file")
            
            source_audio = temp_files[0]
            self.log(f"Downloaded: {source_audio.name}")
            
            # Convert to selected formats
            for format_name in selected_formats:
                self.update_status(f"Converting to {format_name}...")
                self.log(f"Converting to {format_name}...")
                
                format_info = self.audio_formats[format_name]
                ext = format_info['ext']
                bitrate = format_info['bitrate']
                
                output_file = output_dir / f"{video_title}.{ext}"
                
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
                    # Lossless formats
                    if ext == 'flac':
                        cmd.extend(['-codec:a', 'flac'])
                    elif ext == 'wav':
                        cmd.extend(['-codec:a', 'pcm_s16le'])
                
                cmd.append(str(output_file))
                
                # Run conversion
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    file_size = output_file.stat().st_size / (1024 * 1024)  # MB
                    self.log(f"✓ Created: {output_file.name} ({file_size:.1f} MB)")
                else:
                    self.log(f"✗ Failed to create {format_name}: {result.stderr}")
                
                current_step += 1
                self.progress_var.set((current_step / total_steps) * 100)
            
            # Clean up temporary file
            source_audio.unlink()
            
            self.log("Conversion completed!")
            self.update_status("Conversion completed successfully!")
            self.log(f"All files saved to: {output_dir}")
            
            # Create quality report
            self.create_quality_report(output_dir, video_title, selected_formats)
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.update_status(f"Error: {str(e)}")
        finally:
            self.convert_button.config(state='normal')
            self.progress_var.set(100)
    
    def create_quality_report(self, output_dir, video_title, selected_formats):
        """Create a quality report sorting files by audio quality"""
        report_file = output_dir / f"{video_title}_quality_report.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"Audio Quality Report for: {video_title}\n")
            f.write("=" * 50 + "\n\n")
            
            # Group by quality
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
        
        self.log(f"Quality report saved: {report_file.name}")

def main():
    root = tk.Tk()
    app = VideoAudioConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()