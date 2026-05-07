#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import sys

class FFsubsyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFsubsync GUI")
        self.root.geometry("600x500")
        
        self.video_path = tk.StringVar()
        self.subtitle_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Video selection
        tk.Label(self.root, text="Video File:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.select_video).grid(row=0, column=2, padx=5, pady=5)
        
        # Subtitle selection
        tk.Label(self.root, text="Subtitle File:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.subtitle_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.select_subtitle).grid(row=1, column=2, padx=5, pady=5)
        
        # Output
        tk.Label(self.root, text="Output File:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.select_output).grid(row=2, column=2, padx=5, pady=5)
        
        # Sync button
        sync_btn = tk.Button(self.root, text="🔄 Sync Subtitles", command=self.sync_subtitles, 
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        sync_btn.grid(row=3, column=1, pady=20)
        
        # Log output
        tk.Label(self.root, text="Log Output:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.root, width=70, height=12, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_video(self):
        file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv *.webm"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.video_path.set(file)
            # Auto-suggest output
            if not self.output_path.get():
                base = os.path.splitext(file)[0]
                self.output_path.set(base + "_synced.srt")
            self.log(f"Selected video: {file}")
    
    def select_subtitle(self):
        file = filedialog.askopenfilename(
            title="Select Subtitle File",
            filetypes=[
                ("Subtitle Files", "*.srt *.ass *.ssa *.sub *.vtt"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.subtitle_path.set(file)
            self.log(f"Selected subtitle: {file}")
    
    def select_output(self):
        file = filedialog.asksaveasfilename(
            title="Save Synced Subtitle",
            defaultextension=".srt",
            filetypes=[
                ("Subtitle Files", "*.srt"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.output_path.set(file)
            self.log(f"Output will be: {file}")
    
    def sync_subtitles(self):
        video = self.video_path.get().strip()
        subtitle = self.subtitle_path.get().strip()
        output = self.output_path.get().strip()
        
        if not video:
            messagebox.showerror("Error", "Please select a video file!")
            return
        
        if not subtitle:
            messagebox.showerror("Error", "Please select a subtitle file!")
            return
        
        if not output:
            messagebox.showerror("Error", "Please specify an output file!")
            return
        
        if not os.path.exists(video):
            messagebox.showerror("Error", f"Video file not found: {video}")
            return
        
        if not os.path.exists(subtitle):
            messagebox.showerror("Error", f"Subtitle file not found: {subtitle}")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.log("=" * 60)
        self.log("Starting subtitle synchronization...")
        self.log(f"Video: {video}")
        self.log(f"Subtitle: {subtitle}")
        self.log(f"Output: {output}")
        self.log("=" * 60)
        self.status.config(text="Syncing... Please wait")
        
        try:
            # Run ffsubsync
            cmd = ["ffsubsync", video, "-i", subtitle, "-o", output]
            self.log(f"Running: {' '.join(cmd)}")
            self.log("-" * 60)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Real-time output
            for line in process.stdout:
                self.log(line.rstrip())
            
            returncode = process.wait()
            
            self.log("-" * 60)
            if returncode == 0:
                self.log("✅ Sync completed successfully!")
                self.status.config(text="✓ Sync completed!")
                messagebox.showinfo("Success", f"Subtitles synced successfully!\n\nOutput: {output}")
            else:
                self.log(f"❌ Sync failed with return code: {returncode}")
                self.status.config(text="✗ Sync failed!")
                messagebox.showerror("Error", "Subtitle synchronization failed!\nCheck log for details.")
                
        except FileNotFoundError:
            self.log("❌ ERROR: ffsubsync not found!")
            self.status.config(text="Error: ffsubsync missing")
            messagebox.showerror("Error", "ffsubsync executable not found!\nThis should not happen in a bundled AppImage.")
        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
            self.status.config(text="Error!")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFsubsyncGUI(root)
    root.mainloop()
