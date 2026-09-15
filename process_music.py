"""
=============================================================================
README & SETUP GUIDE: Modern Python Mastering & YouTube Pipeline
=============================================================================

1. System Prerequisites:
   Ubuntu 24.04 enforces PEP 668 (externally managed environments). You must 
   use a virtual environment and have the system FFmpeg installed.
   
   Run in your terminal:
       sudo apt update && sudo apt install -y python3-venv ffmpeg
       sudo apt update && sudo apt install -y python3-tk

2. Set Up the Virtual Environment (venv):
   Navigate to the folder containing this script:
       python3 -m venv audio_env

3. Activate the venv:
       source audio_env/bin/activate
   (Your terminal prompt will now show '(audio_env)' at the front.)

4. Install Required Dependencies:
   This modern script requires MoviePy, PyLoudNorm, and SoundFile.
   Run this exact command while your venv is active:
       pip install "moviepy>=2.0" pyloudnorm soundfile
       

5. Prepare Input Files:
   Make sure you have your files in the same directory as this script.
   The script will automatically find them!
       - One Audio file: Any .wav file (e.g., ethio_jazz_raw.wav)
       - One Cover image: Any .jpg, .jpeg, or .png file (1920x1080 recommended)

6. Run the Script:
       python process_music.py

7. Exit the venv (when you are completely finished):
       deactivate
=============================================================================
"""

import os
import sys
import glob
import soundfile as sf
import pyloudnorm as pyln
from moviepy import ImageClip, AudioFileClip

def find_input_files():
    """Automatically finds any audio and image file in the folder."""
    # Find audio
    audio_files = glob.glob("*.wav")
    if not audio_files:
        print("Error: No .wav file found in this directory.")
        sys.exit(1)
        
    # Find image (checks multiple extensions)
    image_exts = ["*.jpg", "*.jpeg", "*.png"]
    image_files = []
    for ext in image_exts:
        image_files.extend(glob.glob(ext))
        
    if not image_files:
        print("Error: No .jpg, .jpeg, or .png file found in this directory.")
        sys.exit(1)
        
    # Returns the first audio and image file it finds
    return audio_files[0], image_files[0]

def build_youtube_release(raw_audio, cover_image, output_video):
    print(f"[*] Step 1: Mastering '{raw_audio}' natively with PyLoudNorm...")
    
    # Read raw audio
    data, rate = sf.read(raw_audio)
    
    # Measure and normalize to exactly -14 LUFS for YouTube/Spotify
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    normalized_audio = pyln.normalize.loudness(data, loudness, -14.0)
    
    # Save mastered audio to temporary file
    mastered_audio = "mastered_temp.wav"
    sf.write(mastered_audio, normalized_audio, rate)
    
    print(f"[*] Step 2: Compositing video with MoviePy using '{cover_image}'...")
    
    # Load audio into MoviePy
    audio_clip = AudioFileClip(mastered_audio)
    
    # Load image, set it to last exactly as long as the audio, and attach audio
    # (Using the modern MoviePy v2.0 'with_' syntax)
    final_video = ImageClip(cover_image).with_duration(audio_clip.duration).with_audio(audio_clip)
    
    print("[*] Rendering final MP4 (Watch the progress bar!)...")
    # THE SPEED HACK: Because there is no moving waveform, we can render 
    # the video at a very low frame rate. This renders in seconds, not minutes.
    final_video.write_videofile(
        output_video, 
        fps=2, 
        codec="libx264", 
        audio_codec="aac"
    )
    
    # Cleanup temp audio
    if os.path.exists(mastered_audio):
        os.remove(mastered_audio)
    print(f"\n[+] Success! Final video saved as: {output_video}")

if __name__ == "__main__":
    audio_path, image_path = find_input_files()
    build_youtube_release(audio_path, image_path, "youtube_upload.mp4")
