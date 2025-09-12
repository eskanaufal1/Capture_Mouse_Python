#!/usr/bin/env python3
"""
Simple Mouse Tracking Test
==========================

This script tests basic mouse tracking functionality to verify that
the mouse cursor is being tracked properly.
"""

import tkinter as tk
import time

class SimpleMouseTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Mouse Tracking Test")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        self.canvas = tk.Canvas(
            self.root,
            width=800,
            height=600,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse tracking variables
        self.mouse_x = 400
        self.mouse_y = 300
        self.movement_count = 0
        
        # Bind mouse movement
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Create info label
        self.info_label = tk.Label(
            self.root,
            text="Move your mouse to test tracking",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='white'
        )
        self.info_label.place(x=10, y=10)
        
        # Start animation
        self.animate()
        
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.movement_count += 1
        
    def animate(self):
        """Animation loop"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get actual canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Draw tracking circle
        radius = 20
        self.canvas.create_oval(
            self.mouse_x - radius, self.mouse_y - radius,
            self.mouse_x + radius, self.mouse_y + radius,
            fill='#ff4757', outline='white', width=2
        )
        
        # Draw adaptive crosshair
        self.canvas.create_line(
            0, self.mouse_y, canvas_width, self.mouse_y,
            fill='#ff4757', width=1
        )
        self.canvas.create_line(
            self.mouse_x, 0, self.mouse_x, canvas_height,
            fill='#ff4757', width=1
        )
        
        # Update info
        self.info_label.config(
            text=f"Mouse: ({self.mouse_x}, {self.mouse_y}) | Movements: {self.movement_count} | Press ESC to exit"
        )
        
        # Schedule next frame
        self.root.after(16, self.animate)  # ~60 FPS
        
    def run(self):
        """Start the test"""
        print("🔍 Simple Mouse Tracking Test")
        print("   Move your mouse around the window")
        print("   The red circle should follow your cursor")
        print("   Press ESC to exit")
        self.root.mainloop()

if __name__ == "__main__":
    test = SimpleMouseTest()
    test.run()