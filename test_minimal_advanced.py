#!/usr/bin/env python3
"""
Minimal Advanced Mouse Tracker Test
===================================

This is a simplified version to test the core mouse tracking functionality
of the advanced tracker without all the complex features.
"""

import tkinter as tk
import time
import math

class MinimalAdvancedTracker:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Minimal Advanced Tracker Test")
        self.root.configure(bg='#2b2b2b')
        self.root.geometry('800x600')
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=800, 
            height=600,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse tracking variables
        self.current_x = 400
        self.current_y = 300
        self.raw_delta_x = 0
        self.raw_delta_y = 0
        self.movement_velocity = 0
        self.movement_count = 0
        
        # Bind events
        self.root.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Info label
        self.info_label = tk.Label(
            self.root,
            text="Testing mouse tracking...",
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='white'
        )
        self.info_label.place(x=10, y=10)
        
        # Start animation
        self.animate()
        
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        # Calculate deltas
        prev_x, prev_y = self.current_x, self.current_y
        new_x, new_y = event.x, event.y
        
        self.raw_delta_x = new_x - prev_x
        self.raw_delta_y = new_y - prev_y
        
        # Calculate velocity
        self.movement_velocity = math.sqrt(self.raw_delta_x**2 + self.raw_delta_y**2)
        
        # Update position
        self.current_x = new_x
        self.current_y = new_y
        self.movement_count += 1
        
    def animate(self):
        """Animation loop"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw tracking circle with velocity-based color
        radius = 20
        velocity_factor = min(self.movement_velocity / 50.0, 1.0)
        color_intensity = min(255, 150 + int(velocity_factor * 105))
        color = f"#{color_intensity:02x}{color_intensity//4:02x}{color_intensity//4:02x}"
        
        self.canvas.create_oval(
            self.current_x - radius, self.current_y - radius,
            self.current_x + radius, self.current_y + radius,
            fill=color, outline='white', width=2
        )
        
        # Draw crosshair
        self.canvas.create_line(
            0, self.current_y, 800, self.current_y,
            fill='#ff4757', width=1
        )
        self.canvas.create_line(
            self.current_x, 0, self.current_x, 600,
            fill='#ff4757', width=1
        )
        
        # Update info
        self.info_label.config(
            text=f"Position: ({self.current_x}, {self.current_y}) | Δ: ({self.raw_delta_x:+3d}, {self.raw_delta_y:+3d}) | Velocity: {self.movement_velocity:.1f} | Moves: {self.movement_count}"
        )
        
        # Schedule next frame
        self.root.after(16, self.animate)
        
    def run(self):
        """Start the test"""
        print("🔍 Minimal Advanced Tracker Test")
        print("   Move your mouse to test tracking")
        print("   Circle should follow cursor with velocity-based colors")
        print("   Press ESC to exit")
        self.root.mainloop()

if __name__ == "__main__":
    app = MinimalAdvancedTracker()
    app.run()