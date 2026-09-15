"""
=============================================================================
README & SETUP GUIDE: Ethio-Jazz GUI Mixer & YouTube Master
=============================================================================

1. Fix the "tkinter" Error (System Prerequisite):
   Ubuntu does not include the visual GUI library by default. You MUST run 
   this in your standard terminal to install it:
       sudo apt update && sudo apt install -y python3-tk

2. Activate your Virtual Environment:
   Ensure your terminal is in the 'utube' folder and run:
       source audio_env/bin/activate
   (Your prompt should show '(audio_env)'.)

3. Install Required Dependencies:
   If you haven't already, install the modern media libraries:
       pip install "moviepy>=2.0" pyloudnorm soundfile numpy

4. Run the GUI Application:
       python app_gui.py

5. How to Use the App:
   - Click 'Add Track(s)' to select your raw .wav files.
   - Use 'Move Up' / 'Move Down' to set which song plays first.
   - Set your crossfade time (e.g., 3.0 seconds blends them smoothly).
   - Select your cover art image.
   - Click Render!
=============================================================================
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from moviepy import ImageClip, AudioFileClip
import os
import threading

class EthioJazzApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ethio-Jazz YouTube Generator")
        self.root.geometry("550x500")
        
        # 1. Audio Track List
        tk.Label(root, text="1. Select & Order Audio Tracks:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=65, height=8)
        self.listbox.pack(pady=5)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Add Track(s)", command=self.add_track).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_track).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Move Up", command=self.move_up).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Move Down", command=self.move_down).grid(row=0, column=3, padx=5)

        # 2. Crossfade Settings
        xfade_frame = tk.Frame(root)
        xfade_frame.pack(pady=15)
        tk.Label(xfade_frame, text="2. Smooth Crossfade Transition (Seconds): ", font=("Arial", 10, "bold")).grid(row=0, column=0)
        self.xfade_entry = tk.Entry(xfade_frame, width=5)
        self.xfade_entry.insert(0, "3.0")  # Default 3 second crossfade
        self.xfade_entry.grid(row=0, column=1)

        # 3. Cover Art
        tk.Label(root, text="3. Select Cover Art Image:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.lbl_art = tk.Label(root, text="No cover art selected", fg="red")
        self.lbl_art.pack()
        tk.Button(root, text="Browse Image", command=self.select_art).pack(pady=5)
        self.cover_path = None

        # 4. Render Button
        self.btn_render = tk.Button(root, text="Master Audio & Render MP4", bg="darkgreen", fg="white", font=("Arial", 12, "bold"), command=self.start_render_thread)
        self.btn_render.pack(pady=20)

        self.lbl_status = tk.Label(root, text="Ready.", fg="blue")
        self.lbl_status.pack()

    # --- GUI INTERACTION LOGIC ---
    def add_track(self):
        files = filedialog.askopenfilenames(filetypes=[("WAV Audio", "*.wav")])
        for f in files:
            self.listbox.insert(tk.END, f)

    def remove_track(self):
        selection = self.listbox.curselection()
        if selection:
            self.listbox.delete(selection[0])

    def move_up(self):
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0: return
        idx = selection[0]
        val = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, val)
        self.listbox.selection_set(idx - 1)

    def move_down(self):
        selection = self.listbox.curselection()
        if not selection or selection[0] == self.listbox.size() - 1: return
        idx = selection[0]
        val = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, val)
        self.listbox.selection_set(idx + 1)

    def select_art(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file:
            self.cover_path = file
            self.lbl_art.config(text=os.path.basename(file), fg="green")

    # --- PROCESSING LOGIC ---
    def start_render_thread(self):
        if self.listbox.size() == 0:
            messagebox.showerror("Error", "Please add at least one audio track.")
            return
        if not self.cover_path:
            messagebox.showerror("Error", "Please select cover art.")
            return

        self.btn_render.config(state=tk.DISABLED, text="Processing... Please wait")
        self.lbl_status.config(text="Processing audio and video... (Check terminal for progress bar)")
        
        # Run processing in background so GUI doesn't freeze
        threading.Thread(target=self.process_pipeline, daemon=True).start()

    def process_pipeline(self):
        try:
            tracks = self.listbox.get(0, tk.END)
            xfade_sec = float(self.xfade_entry.get())
            output_mp4 = "youtube_upload_combined.mp4"
            mastered_temp = "mastered_temp_gui.wav"

            combined_audio = None
            sample_rate = 44100

            # 1. MERGE WITH CROSSFADE
            for idx, track_path in enumerate(tracks):
                data, rate = sf.read(track_path)
                sample_rate = rate # Update to actual rate
                
                # Force mono to stereo to prevent shape crashes
                if data.ndim == 1:
                    data = np.column_stack((data, data))

                if combined_audio is None:
                    combined_audio = data
                else:
                    xfade_samples = int(xfade_sec * sample_rate)
                    if xfade_samples > 0 and len(combined_audio) > xfade_samples and len(data) > xfade_samples:
                        # Mathematical Crossfade overlapping
                        fade_out = np.linspace(1, 0, xfade_samples).reshape(-1, 1)
                        fade_in = np.linspace(0, 1, xfade_samples).reshape(-1, 1)
                        
                        overlap = combined_audio[-xfade_samples:] * fade_out + data[:xfade_samples] * fade_in
                        combined_audio = np.vstack((combined_audio[:-xfade_samples], overlap, data[xfade_samples:]))
                    else:
                        # Just stick them together if crossfade is 0
                        combined_audio = np.vstack((combined_audio, data))

            # 2. MASTER TO -14 LUFS
            meter = pyln.Meter(sample_rate)
            loudness = meter.integrated_loudness(combined_audio)
            final_audio = pyln.normalize.loudness(combined_audio, loudness, -14.0)
            sf.write(mastered_temp, final_audio, sample_rate)

            # 3. RENDER VIDEO (MoviePy 2.0 Syntax)
            audio_clip = AudioFileClip(mastered_temp)
            final_video = ImageClip(self.cover_path).with_duration(audio_clip.duration).with_audio(audio_clip)
            
            final_video.write_videofile(output_mp4, fps=2, codec="libx264", audio_codec="aac")

            # Cleanup
            if os.path.exists(mastered_temp):
                os.remove(mastered_temp)

            self.lbl_status.config(text=f"Success! Saved as: {output_mp4}")
            messagebox.showinfo("Done", f"Successfully generated {output_mp4}!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.lbl_status.config(text="Render failed.")
        finally:
            self.btn_render.config(state=tk.NORMAL, text="Master Audio & Render MP4")

if __name__ == "__main__":
    root = tk.Tk()
    app = EthioJazzApp(root)
    root.mainloop()
