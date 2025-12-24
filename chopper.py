# import os, sys, io
# import numpy as np
# from PIL import Image
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM

# TILE_SIZE = 256
# SKIP_EXISTING = "-d" in sys.argv

# def batch_chop(clean_dir="input_cleaned", raw_dir="input_raw", output_base="training_tiles"):
#     for filename in os.listdir(clean_dir):
#         design_name = os.path.splitext(filename)[0]
#         design_out_folder = os.path.join(output_base, design_name)
        
#         if SKIP_EXISTING and os.path.exists(design_out_folder):
#             print(f"Skipping {design_name} tiles (Exists)")
#             continue
            
#         # Open the Clean Master Map (always a PNG)
#         img_clean = Image.open(os.path.join(clean_dir, filename)).convert("RGB")
        
#         # 1. Find the matching Raw file
#         raw_path = None
#         for f in os.listdir(raw_dir):
#             if os.path.splitext(f)[0] == design_name:
#                 raw_path = os.path.join(raw_dir, f)
#                 break
        
#         if not raw_path: 
#             print(f"No raw pair found for {design_name}")
#             continue

#         # 2. Handle Raw file loading (Check for SVG)
#         if raw_path.lower().endswith('.svg'):
#             print(f"Rasterizing SVG for chopper: {raw_path}")
#             drawing = svg2rlg(raw_path)
#             png_data = io.BytesIO()
#             renderPM.drawToFile(drawing, png_data, fmt="PNG")
#             png_data.seek(0)
#             img_raw = Image.open(png_data).convert("RGB")
#         else:
#             img_raw = Image.open(raw_path).convert("RGB")

#         # 3. Sync sizes and Chop
#         img_raw = img_raw.resize(img_clean.size, Image.Resampling.LANCZOS)
#         os.makedirs(design_out_folder, exist_ok=True)
        
#         count = 0
#         for y in range(0, img_clean.size[1] - TILE_SIZE, TILE_SIZE):
#             for x in range(0, img_clean.size[0] - TILE_SIZE, TILE_SIZE):
#                 box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
#                 t_clean = img_clean.crop(box)
#                 t_raw = img_raw.crop(box)
                
#                 # Filter blank tiles
#                 if np.mean(np.array(t_clean.convert("L"))) > 250: continue

#                 combined = Image.new("RGB", (512, 256))
#                 combined.paste(t_clean, (0,0))
#                 combined.paste(t_raw, (256,0))
#                 combined.save(os.path.join(design_out_folder, f"tile_{count}.png"))
#                 count += 1
#         print(f"Chopped {design_name}: {count} tiles.")

# if __name__ == "__main__":
#     batch_chop()

# import os, sys, io
# import numpy as np
# from PIL import Image

# TILE_SIZE = 256
# SKIP_EXISTING = "-d" in sys.argv

# def batch_chop(clean_dir="input_cleaned", raw_dir="input_raw", output_base="training_tiles"):
#     # Ensure the output directory exists
#     os.makedirs(output_base, exist_ok=True)
    
#     # Iterate through the Cleaned Master Maps (the "Answers")
#     for filename in os.listdir(clean_dir):
#         if not filename.endswith('.png'): continue
        
#         design_name = os.path.splitext(filename)[0]
#         design_out_folder = os.path.join(output_base, design_name)
        
#         if SKIP_EXISTING and os.path.exists(design_out_folder):
#             print(f"Skipping {design_name} tiles (Exists)")
#             continue
            
#         # 1. Open the Clean Master Map
#         clean_path = os.path.join(clean_dir, filename)
#         img_clean = Image.open(clean_path).convert("RGB")
        
#         # 2. Find the matching Raw Artwork PNG in input_raw
#         # Based on your new structure, the PNG is named after the folder
#         raw_path = os.path.join(raw_dir, f"{design_name}.png")
        
#         if not os.path.exists(raw_path):
#             print(f"No raw artwork PNG found for {design_name} at {raw_path}")
#             continue

#         img_raw = Image.open(raw_path).convert("RGB")

#         # 3. Sync sizes (Raw must match Clean exactly for pixel-perfect training)
#         if img_raw.size != img_clean.size:
#             img_raw = img_raw.resize(img_clean.size, Image.Resampling.LANCZOS)
        
#         os.makedirs(design_out_folder, exist_ok=True)
        
#         print(f"Chopping {design_name}...")
        
#         count = 0
#         width, height = img_clean.size
        
#         # Slide the window across the image
#         for y in range(0, height - TILE_SIZE, TILE_SIZE):
#             for x in range(0, width - TILE_SIZE, TILE_SIZE):
#                 box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
                
#                 t_clean = img_clean.crop(box)
#                 t_raw = img_raw.crop(box)
                
#                 # FILTER BLANK TILES
#                 # Convert to grayscale and check mean brightness.
#                 # If mean is < 2 (mostly black), it means there is no ink/design here.
#                 if np.mean(np.array(t_clean.convert("L"))) < 2: 
#                     continue

#                 # Create the side-by-side training pair (512x256)
#                 # Left side: Clean Map (Target) | Right side: Raw Image (Input)
#                 combined = Image.new("RGB", (512, 256))
#                 combined.paste(t_clean, (0, 0))
#                 combined.paste(t_raw, (256, 0))
                
#                 combined.save(os.path.join(design_out_folder, f"tile_{count}.png"))
#                 count += 1
                
#         print(f"  [DONE] Created {count} tiles in {design_out_folder}")

# if __name__ == "__main__":
#     batch_chop()

# import os
# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk
# import numpy as np
# import threading

# # --- CONFIGURATION ---
# TILE_SIZE = 256
# PAD_COLOR = (255, 0, 255) # Magenta
# CLEAN_DIR = "input_cleaned"
# RAW_DIR = "input_raw"
# OUTPUT_BASE = "training_tiles"

# class AlignmentGUI:
#     def __init__(self, root, file_list):
#         self.root = root
#         self.file_list = file_list
#         self.current_idx = 0
#         self.off_x, self.off_y = 0, 0
#         self.is_processing = False
        
#         self.root.title("AI Training Data Aligner")
#         self.root.geometry("1100x900")

#         # Left Side: Image Canvas
#         self.canvas = tk.Canvas(root, width=800, height=800, bg="#222")
#         self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

#         # Right Side: Controls Panel
#         self.panel = tk.Frame(root, width=250)
#         self.panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

#         self.info_label = tk.Label(self.panel, text="Alignment Controls", font=("Arial", 14, "bold"))
#         self.info_label.pack(pady=10)

#         # Directional Buttons
#         btn_frame = tk.Frame(self.panel)
#         btn_frame.pack(pady=10)
#         tk.Button(btn_frame, text="▲", width=5, command=lambda: self.nudge(0, -1)).grid(row=0, column=1)
#         tk.Button(btn_frame, text="◀", width=5, command=lambda: self.nudge(-1, 0)).grid(row=1, column=0)
#         tk.Button(btn_frame, text="▶", width=5, command=lambda: self.nudge(1, 0)).grid(row=1, column=2)
#         tk.Button(btn_frame, text="▼", width=5, command=lambda: self.nudge(0, 1)).grid(row=2, column=1)

#         self.offset_label = tk.Label(self.panel, text="Offset: X=0, Y=0", font=("Courier", 10))
#         self.offset_label.pack()

#         tk.Button(self.panel, text="Reset (R)", bg="#ff9999", command=self.reset_offset).pack(pady=5)

#         # Progress Section
#         tk.Label(self.panel, text="Processing Progress:").pack(pady=(20, 0))
#         self.progress = ttk.Progressbar(self.panel, orient=tk.HORIZONTAL, length=200, mode='determinate')
#         self.progress.pack(pady=5)

#         self.btn_save = tk.Button(self.panel, text="SAVE & CHOP (Enter)", bg="#99ff99", font=("Arial", 12, "bold"), 
#                                   height=2, command=self.process_current)
#         self.btn_save.pack(pady=20, fill=tk.X)

#         # Log Window
#         tk.Label(self.panel, text="System Log:").pack()
#         self.log = tk.Text(self.panel, height=15, width=30, font=("Courier", 8), bg="#eee")
#         self.log.pack()

#         # Key Bindings
#         self.root.bind("<Up>", lambda e: self.nudge(0, -1))
#         self.root.bind("<Down>", lambda e: self.nudge(0, 1))
#         self.root.bind("<Left>", lambda e: self.nudge(-1, 0))
#         self.root.bind("<Right>", lambda e: self.nudge(1, 0))
#         self.root.bind("<Shift-Up>", lambda e: self.nudge(0, -10))
#         self.root.bind("<Shift-Down>", lambda e: self.nudge(0, 10))
#         self.root.bind("<Return>", lambda e: self.process_current())
#         self.root.bind("r", lambda e: self.reset_offset())

#         self.load_images()

#     def write_log(self, message):
#         self.log.insert(tk.END, message + "\n")
#         self.log.see(tk.END)

#     def reset_offset(self):
#         self.off_x, self.off_y = 0, 0
#         self.update_display()
#         self.write_log("Offsets reset to 0.")

#     def load_images(self):
#         if self.current_idx >= len(self.file_list):
#             self.write_log("--- ALL FILES FINISHED ---")
#             self.btn_save.config(state=tk.DISABLED)
#             return

#         filename = self.file_list[self.current_idx]
#         self.design_name = os.path.splitext(filename)[0]
#         self.write_log(f"Loading: {self.design_name}")

#         self.img_clean = Image.open(os.path.join(CLEAN_DIR, filename)).convert("RGB")
#         self.img_raw = Image.open(os.path.join(RAW_DIR, f"{self.design_name}.png")).convert("RGB")
        
#         self.p_clean = self.img_clean.resize((800, 800), Image.NEAREST)
#         self.p_raw = self.img_raw.resize((800, 800), Image.NEAREST)
#         self.update_display()

#     def nudge(self, dx, dy):
#         if self.is_processing: return
#         self.off_x += dx
#         self.off_y += dy
#         self.update_display()

#     def update_display(self):
#         base = self.p_clean.copy()
#         shifted_raw = Image.new("RGB", (800, 800), (0, 0, 0))
#         shifted_raw.paste(self.p_raw, (self.off_x, self.off_y))
        
#         blended = Image.blend(base, shifted_raw, alpha=0.5)
#         self.tk_img = ImageTk.PhotoImage(blended)
#         self.canvas.create_image(400, 400, image=self.tk_img)
#         self.offset_label.config(text=f"Offset: X={self.off_x}, Y={self.off_y}")

#     def process_current(self):
#         if self.is_processing: return
#         self.is_processing = True
#         self.btn_save.config(state=tk.DISABLED, text="Chipping...")
        
#         # Run chopping in a separate thread so the GUI doesn't freeze
#         scale = self.img_clean.width / 800
#         dx, dy = int(self.off_x * scale), int(self.off_y * scale)
        
#         threading.Thread(target=self.chop_thread, args=(dx, dy), daemon=True).start()

#     def chop_thread(self, dx, dy):
#         folder = os.path.join(OUTPUT_BASE, self.design_name)
#         os.makedirs(folder, exist_ok=True)
#         arr_c, arr_r = np.array(self.img_clean), np.array(self.img_raw)
#         h, w, _ = arr_c.shape
        
#         tiles_y = list(range(0, h, TILE_SIZE))
#         tiles_x = list(range(0, w, TILE_SIZE))
#         total_steps = len(tiles_y) * len(tiles_x)
        
#         count, step = 0, 0
#         for y in tiles_y:
#             for x in tiles_x:
#                 y_end, x_end = y + TILE_SIZE, x + TILE_SIZE
#                 t_clean = arr_c[y:y_end, x:x_end]
                
#                 ry, rx = y - dy, x - dx # Realignment
#                 ry_e, rx_e = ry + TILE_SIZE, rx + TILE_SIZE
                
#                 if ry < 0 or rx < 0 or ry_e > h or rx_e > w:
#                     t_raw = np.full((TILE_SIZE, TILE_SIZE, 3), PAD_COLOR, dtype=np.uint8)
#                 else:
#                     t_raw = arr_r[ry:ry_e, rx:rx_e]

#                 # Logical Edge Padding
#                 if t_clean.shape[0] < TILE_SIZE or t_clean.shape[1] < TILE_SIZE:
#                     pad = np.full((TILE_SIZE, TILE_SIZE, 3), PAD_COLOR, dtype=np.uint8)
#                     pad[:t_clean.shape[0], :t_clean.shape[1]] = t_clean
#                     t_clean = pad

#                 if np.mean(t_clean) > 2:
#                     combined = np.concatenate((t_clean, t_raw), axis=1)
#                     Image.fromarray(combined).save(os.path.join(folder, f"tile_{count}.png"))
#                     count += 1
                
#                 step += 1
#                 if step % 10 == 0:
#                     self.progress['value'] = (step / total_steps) * 100
#                     self.root.update_idletasks()

#         self.write_log(f"Success! {count} tiles saved.")
#         self.is_processing = False
#         self.btn_save.config(state=tk.NORMAL, text="SAVE & CHOP (Enter)")
#         self.progress['value'] = 0
#         self.current_idx += 1
#         self.off_x, self.off_y = 0, 0
#         self.root.after(10, self.load_images)

# if __name__ == "__main__":
#     files = [f for f in os.listdir(CLEAN_DIR) if f.endswith('.png')]
#     root = tk.Tk()
#     AlignmentGUI(root, files)
#     root.mainloop()

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import threading

# --- CONFIGURATION ---
TILE_SIZE = 256
CLEAN_DIR = "input_cleaned"
RAW_DIR = "input_raw"
OUTPUT_BASE = "training_tiles"

class AlignmentGUI:
    def __init__(self, root, file_list):
        self.root = root
        self.file_list = file_list
        self.current_idx = 0
        self.off_x, self.off_y = 0, 0
        self.is_processing = False
        
        self.root.title("Pixel-Sync: Standard Dataset Creator")
        self.root.geometry("1100x950")
        self.root.configure(bg="#1e1e1e")

        # Layout
        self.canvas = tk.Canvas(root, width=800, height=800, bg="#000000", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)

        self.sidebar = tk.Frame(root, width=250, bg="#1e1e1e")
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=20)

        # Header
        tk.Label(self.sidebar, text="DATASET BUILDER", font=("Segoe UI", 16, "bold"), fg="#4CAF50", bg="#1e1e1e").pack(pady=20)
        tk.Label(self.sidebar, text="Standard: [RAW | CLEAN]", font=("Segoe UI", 9), fg="#888", bg="#1e1e1e").pack()
        
        # Nudge Controls
        ctrl_frame = tk.Frame(self.sidebar, bg="#1e1e1e")
        ctrl_frame.pack(pady=10)
        
        btn_opts = {"width": 5, "height": 2, "font": ("Arial", 10, "bold"), "bg": "#333", "fg": "white", "activebackground": "#555"}
        tk.Button(ctrl_frame, text="▲", **btn_opts, command=lambda: self.nudge(0, -1)).grid(row=0, column=1, pady=2)
        tk.Button(ctrl_frame, text="◀", **btn_opts, command=lambda: self.nudge(-1, 0)).grid(row=1, column=0, padx=2)
        tk.Button(ctrl_frame, text="▶", **btn_opts, command=lambda: self.nudge(1, 0)).grid(row=1, column=2, padx=2)
        tk.Button(ctrl_frame, text="▼", **btn_opts, command=lambda: self.nudge(0, 1)).grid(row=2, column=1, pady=2)

        self.offset_txt = tk.Label(self.sidebar, text="X: 0 | Y: 0", font=("Consolas", 12), fg="#00ff00", bg="#1e1e1e")
        self.offset_txt.pack(pady=10)

        # Action Buttons
        tk.Button(self.sidebar, text="Reset Alignment (R)", bg="#444", fg="white", command=self.reset_offset).pack(fill=tk.X, pady=5)
        
        self.btn_chop = tk.Button(self.sidebar, text="GENERATE TILES & NEXT", bg="#2e7d32", fg="white", 
                                  font=("Arial", 11, "bold"), height=3, command=self.start_process)
        self.btn_chop.pack(fill=tk.X, pady=20)

        tk.Button(self.sidebar, text="SKIP", bg="#c62828", fg="white", command=self.skip).pack(fill=tk.X)

        # Progress
        tk.Label(self.sidebar, text="Tile Generation:", bg="#1e1e1e", fg="white").pack(pady=(20, 0))
        self.progress = ttk.Progressbar(self.sidebar, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(pady=5, fill=tk.X)

        # Console
        self.log = tk.Text(self.sidebar, height=12, width=30, bg="#000", fg="#00ff00", font=("Consolas", 8))
        self.log.pack(pady=10)

        # Keybinds
        self.root.bind("<Up>", lambda e: self.nudge(0, -1))
        self.root.bind("<Down>", lambda e: self.nudge(0, 1))
        self.root.bind("<Left>", lambda e: self.nudge(-1, 0))
        self.root.bind("<Right>", lambda e: self.nudge(1, 0))
        self.root.bind("<Return>", lambda e: self.start_process())
        self.root.bind("r", lambda e: self.reset_offset())

        self.load_artwork()

    def log_msg(self, msg):
        self.log.insert(tk.END, f"> {msg}\n")
        self.log.see(tk.END)

    def nudge(self, dx, dy):
        if self.is_processing: return
        self.off_x += dx
        self.off_y += dy
        self.update_view()

    def reset_offset(self):
        self.off_x = self.off_y = 0
        self.update_view()

    def load_artwork(self):
        if self.current_idx >= len(self.file_list):
            self.log_msg("QUEUE FINISHED.")
            return

        fname = self.file_list[self.current_idx]
        self.design_name = os.path.splitext(fname)[0]
        self.log_msg(f"Loading: {self.design_name}")

        self.img_clean = Image.open(os.path.join(CLEAN_DIR, fname)).convert("RGB")
        self.img_raw = Image.open(os.path.join(RAW_DIR, f"{self.design_name}.png")).convert("RGB")
        
        self.prev_clean = self.img_clean.resize((800, 800), Image.NEAREST)
        self.prev_raw = self.img_raw.resize((800, 800), Image.NEAREST)
        self.update_view()

    def update_view(self):
        base = self.prev_clean.copy()
        top = Image.new("RGB", (800, 800), (0, 0, 0))
        top.paste(self.prev_raw, (self.off_x, self.off_y))
        
        blended = Image.blend(base, top, alpha=0.5)
        self.tk_img = ImageTk.PhotoImage(blended)
        self.canvas.delete("all")
        self.canvas.create_image(400, 400, image=self.tk_img)
        self.offset_txt.config(text=f"X: {self.off_x} | Y: {self.off_y}")

    def skip(self):
        self.current_idx += 1
        self.reset_offset()
        self.load_artwork()

    def start_process(self):
        if self.is_processing: return
        self.is_processing = True
        self.btn_chop.config(state=tk.DISABLED)
        
        scale = self.img_clean.width / 800
        dx, dy = int(self.off_x * scale), int(self.off_y * scale)
        
        threading.Thread(target=self.run_chop, args=(dx, dy), daemon=True).start()

    def run_chop(self, dx, dy):
        out_dir = os.path.join(OUTPUT_BASE, self.design_name)
        os.makedirs(out_dir, exist_ok=True)
        
        c_arr = np.array(self.img_clean)
        r_arr = np.array(self.img_raw)
        h, w, _ = c_arr.shape

        ox_start, ox_end = max(0, dx), min(w, w + dx)
        oy_start, oy_end = max(0, dy), min(h, h + dy)

        rows = range(oy_start, oy_end - TILE_SIZE + 1, TILE_SIZE)
        cols = range(ox_start, ox_end - TILE_SIZE + 1, TILE_SIZE)
        
        count = 0
        total_steps = len(rows) * len(cols)

        for i, y in enumerate(rows):
            for x in cols:
                # Target (Clean)
                tile_c = c_arr[y : y+TILE_SIZE, x : x+TILE_SIZE]
                # Source (Raw - realigned)
                ry, rx = y - dy, x - dx
                tile_r = r_arr[ry : ry+TILE_SIZE, rx : rx+TILE_SIZE]

                if np.mean(tile_c) > 3:
                    # STANDARD PIX2PIX FORMAT: [ RAW (Input) | CLEAN (Target) ]
                    combined = np.concatenate((tile_r, tile_c), axis=1)
                    
                    base_name = f"tile_{count}"
                    # Save Image
                    Image.fromarray(combined).save(os.path.join(out_dir, f"{base_name}.png"))
                    
                    # Save Caption for Kohya_ss
                    caption = f"a screen printing separation of {self.design_name.replace('_', ' ')} showing raw artwork and halftones"
                    with open(os.path.join(out_dir, f"{base_name}.txt"), "w") as f:
                        f.write(caption)
                        
                    count += 1
            
            self.progress['value'] = ((i + 1) / len(rows)) * 100
            self.root.update_idletasks()

        self.log_msg(f"Finished: {count} pairs saved.")
        self.is_processing = False
        self.btn_chop.config(state=tk.NORMAL)
        self.current_idx += 1
        self.off_x = self.off_y = 0
        self.progress['value'] = 0
        self.root.after(10, self.load_artwork)

if __name__ == "__main__":
    if not os.path.exists(CLEAN_DIR): os.makedirs(CLEAN_DIR)
    if not os.path.exists(RAW_DIR): os.makedirs(RAW_DIR)
    files = [f for f in os.listdir(CLEAN_DIR) if f.lower().endswith('.png')]
    root = tk.Tk()
    app = AlignmentGUI(root, files)
    root.mainloop()