import os
import tempfile
from PIL import ImageGrab
import tkinter as tk

def capture_fullscreen(save_dir=None) -> str:
    """Captures the entire screen and saves it as a temporary file."""
    img = ImageGrab.grab()
    
    if save_dir is None:
        save_dir = tempfile.gettempdir()
        
    filepath = os.path.join(save_dir, "jarvis_screen_capture.jpg")
    
    # Optimize for Vision Models (NIM Llama 3.2 Sweet Spot: 1344px)
    MAX_DIM = 1344
    if img.width > MAX_DIM or img.height > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM))
        
    # Convert to RGB before saving as JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.save(filepath, "JPEG", quality=90)
    return filepath

def capture_region(save_dir=None) -> str:
    """Provides a basic UI to capture a region of the screen."""
    root = tk.Tk()
    root.attributes("-alpha", 0.3) # Make window transparent
    root.attributes("-fullscreen", True)
    root.config(cursor="crosshair")
    
    start_x = None
    start_y = None
    rect = None
    
    canvas = tk.Canvas(root, cursor="cross", bg="gray")
    canvas.pack(fill="both", expand=True)
    
    coords = {}

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        start_x = event.x
        start_y = event.y
        rect = canvas.create_rectangle(start_x, start_y, 1, 1, outline='red', width=2, fill="white")

    def on_move_press(event):
        nonlocal start_x, start_y, rect
        cur_x, cur_y = (event.x, event.y)
        canvas.coords(rect, start_x, start_y, cur_x, cur_y)

    def on_button_release(event):
        nonlocal start_x, start_y
        end_x, end_y = (event.x, event.y)
        
        # Ensure correct ordering of coordinates
        x1 = min(start_x, end_x)
        y1 = min(start_y, end_y)
        x2 = max(start_x, end_x)
        y2 = max(start_y, end_y)
        
        coords['box'] = (x1, y1, x2, y2)
        root.quit()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)
    
    # Press Escape to cancel
    root.bind("<Escape>", lambda e: root.quit())
    
    root.mainloop()
    root.destroy()
    
    if 'box' not in coords or coords['box'][2] - coords['box'][0] < 5:
        # If user just clicked without dragging or cancelled, do fullscreen
        return capture_fullscreen(save_dir)
        
    img = ImageGrab.grab(bbox=coords['box'])
    
    if save_dir is None:
        save_dir = tempfile.gettempdir()
        
    filepath = os.path.join(save_dir, "jarvis_region_capture.jpg")

    # Optimize for Vision Models (NIM Llama 3.2 Sweet Spot: 1344px)
    MAX_DIM = 1344
    if img.width > MAX_DIM or img.height > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM))

    # Convert to RGB before saving as JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(filepath, "JPEG", quality=90)
    return filepath

if __name__ == "__main__":
    # Test capture
    print("Capturing fullscreen...")
    path = capture_fullscreen()
    print(f"Saved to {path}")
