import tkinter as tk
from tkinter import ttk
import time
import math
import numpy as np

class ModernMouseTracker:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Modern Mouse Pointer Tracker")
        self.root.configure(bg='#2b2b2b')  # Dark theme
        
        # Set window to fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Create canvas with dark background
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_width, 
            height=self.screen_height,
            bg='#1a1a1a',  # Dark canvas
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse tracking variables
        self.current_x = None
        self.current_y = None
        self.trail_positions = []
        
        # Line history using numpy array for efficiency
        self.max_history_points = 300
        self.history_points = np.zeros((self.max_history_points, 2), dtype=np.float32)
        self.history_count = 0
        self.history_index = 0
        
        self.max_trail_length = 20
        
        # Animation variables
        self.grow_radius = 30
        self.grow_direction = 1
        self.pointer_radius = 15
        
        # Control variables
        self.show_trail = True
        self.show_grow_animation = True
        self.show_line_history = True
        self.is_fullscreen = True
        
        # Create modern UI elements
        self.create_modern_ui()
        
        # Bind events
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Bind keyboard shortcuts
        self.root.bind('<KeyPress-c>', lambda e: self.shortcut_reset_history())
        self.root.bind('<KeyPress-C>', lambda e: self.shortcut_reset_history())
        self.root.bind('<KeyPress-l>', lambda e: self.shortcut_toggle_history())
        self.root.bind('<KeyPress-L>', lambda e: self.shortcut_toggle_history())
        self.root.bind('<KeyPress-t>', lambda e: self.shortcut_toggle_trail())
        self.root.bind('<KeyPress-T>', lambda e: self.shortcut_toggle_trail())
        self.root.bind('<KeyPress-g>', lambda e: self.shortcut_toggle_grow())
        self.root.bind('<KeyPress-G>', lambda e: self.shortcut_toggle_grow())
        self.root.bind('<KeyPress-f>', lambda e: self.shortcut_toggle_fullscreen())
        self.root.bind('<KeyPress-F>', lambda e: self.shortcut_toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self.shortcut_toggle_fullscreen())
        
        # Set focus to root window to capture key events
        self.root.focus_set()
        
        # Start animation loop
        self.animate()
        
    def create_modern_ui(self):
        """Create modern UI elements with sleek design"""
        
        # Create reset button with modern styling
        self.reset_button = tk.Button(
            self.root,
            text="Reset History (C)",
            command=self.reset_history,
            font=('Segoe UI', 12, 'bold'),
            bg='#ff4757',  # Modern red
            fg='white',
            activebackground='#ff3838',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        self.reset_button.place(x=20, y=20, width=160, height=40)
        
        # Add hover effects to button
        self.reset_button.bind('<Enter>', lambda e: self.reset_button.config(bg='#ff3838'))
        self.reset_button.bind('<Leave>', lambda e: self.reset_button.config(bg='#ff4757'))
        
        # Create toggle buttons frame
        self.controls_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.controls_frame.place(x=200, y=20)
        
        # Toggle trail button
        self.trail_button = tk.Button(
            self.controls_frame,
            text="Trail: ON (T)",
            command=self.toggle_trail,
            font=('Segoe UI', 10),
            bg='#2ed573',  # Green for ON
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.trail_button.pack(side='left', padx=5)
        
        # Toggle grow animation button
        self.grow_button = tk.Button(
            self.controls_frame,
            text="Grow: ON (G)",
            command=self.toggle_grow,
            font=('Segoe UI', 10),
            bg='#2ed573',  # Green for ON
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.grow_button.pack(side='left', padx=5)
        
        # Toggle line history button
        self.history_button = tk.Button(
            self.controls_frame,
            text="Lines: ON (L)",
            command=self.toggle_history,
            font=('Segoe UI', 10),
            bg='#2ed573',  # Green for ON
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.history_button.pack(side='left', padx=5)
        
        # Toggle fullscreen button
        self.fullscreen_button = tk.Button(
            self.controls_frame,
            text="Fullscreen: ON (F)",
            command=self.toggle_fullscreen,
            font=('Segoe UI', 10),
            bg='#2ed573',  # Green for ON
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.fullscreen_button.pack(side='left', padx=5)
        
        # Exit button
        self.exit_button = tk.Button(
            self.root,
            text="Exit (ESC)",
            command=self.root.quit,
            font=('Segoe UI', 10),
            bg='#747d8c',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.exit_button.place(x=self.screen_width-120, y=20, width=100, height=30)
        
    def toggle_trail(self):
        """Toggle trail animation on/off"""
        self.show_trail = not self.show_trail
        if self.show_trail:
            self.trail_button.config(text="Trail: ON (T)", bg='#2ed573')
        else:
            self.trail_button.config(text="Trail: OFF (T)", bg='#ff4757')
            self.trail_positions.clear()
            
    def toggle_grow(self):
        """Toggle grow animation on/off"""
        self.show_grow_animation = not self.show_grow_animation
        if self.show_grow_animation:
            self.grow_button.config(text="Grow: ON (G)", bg='#2ed573')
        else:
            self.grow_button.config(text="Grow: OFF (G)", bg='#ff4757')
            
    def toggle_history(self):
        """Toggle line history on/off"""
        self.show_line_history = not self.show_line_history
        if self.show_line_history:
            self.history_button.config(text="Lines: ON (L)", bg='#2ed573')
        else:
            self.history_button.config(text="Lines: OFF (L)", bg='#ff4757')
            self.reset_history_points()
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode on/off"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.root.attributes('-fullscreen', True)
            self.fullscreen_button.config(text="Fullscreen: ON (F)", bg='#2ed573')
        else:
            self.root.attributes('-fullscreen', False)
            self.root.geometry('800x600')  # Set windowed size
            self.fullscreen_button.config(text="Fullscreen: OFF (F)", bg='#ff4757')
            
    def reset_history_points(self):
        """Reset the history points array"""
        self.history_points.fill(0)
        self.history_count = 0
        self.history_index = 0
        
    def shortcut_reset_history(self):
        """Reset history via keyboard shortcut with enhanced feedback"""
        self.reset_history()
        print("Keyboard shortcut: History cleared (C)")
        
    def shortcut_toggle_history(self):
        """Toggle history via keyboard shortcut with feedback"""
        self.toggle_history()
        status = "ON" if self.show_line_history else "OFF"
        print(f"Keyboard shortcut: Line history {status} (L)")
        
    def shortcut_toggle_trail(self):
        """Toggle trail via keyboard shortcut with feedback"""
        self.toggle_trail()
        status = "ON" if self.show_trail else "OFF"
        print(f"Keyboard shortcut: Trail animation {status} (T)")
        
    def shortcut_toggle_grow(self):
        """Toggle grow via keyboard shortcut with feedback"""
        self.toggle_grow()
        status = "ON" if self.show_grow_animation else "OFF"
        print(f"Keyboard shortcut: Grow animation {status} (G)")
        
    def shortcut_toggle_fullscreen(self):
        """Toggle fullscreen via keyboard shortcut with feedback"""
        self.toggle_fullscreen()
        status = "ON" if self.is_fullscreen else "OFF"
        print(f"Keyboard shortcut: Fullscreen {status} (F/F11)")
            
    def reset_history(self):
        """Reset all history and trails"""
        self.trail_positions.clear()
        self.reset_history_points()
        
        # Visual feedback
        original_bg = self.reset_button.cget('bg')
        self.reset_button.config(bg='#00d2d3', text='Cleared!')
        self.root.after(300, lambda: self.reset_button.config(bg=original_bg, text='Reset History'))
        
        print("History and trails reset!")
        
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        x, y = event.x, event.y
        
        # Store current position in history array
        if self.show_line_history:
            self.history_points[self.history_index] = [x, y]
            self.history_index = (self.history_index + 1) % self.max_history_points
            if self.history_count < self.max_history_points:
                self.history_count += 1
        
        # Update current position
        self.current_x = x
        self.current_y = y
        
        # Add to trail
        if self.show_trail:
            self.trail_positions.append((x, y))
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
                
    def on_mouse_click(self, event):
        """Handle mouse click - add special effect"""
        x, y = event.x, event.y
        # Create click effect (will be drawn in next frame)
        self.click_effect = {'x': x, 'y': y, 'radius': 5, 'lifetime': 20}
        
    def on_resize(self, event):
        """Handle window resize"""
        if self.current_x is not None and self.current_y is not None:
            self.draw_all()
            
    def animate(self):
        """Main animation loop"""
        # Animate growing circle
        if self.show_grow_animation:
            self.grow_radius += self.grow_direction * 2
            if self.grow_radius > 60:
                self.grow_direction = -1
            elif self.grow_radius < 20:
                self.grow_direction = 1
                
        # Draw everything only if mouse position is available
        if self.current_x is not None and self.current_y is not None:
            self.draw_all()
            
        # Schedule next frame
        self.root.after(30, self.animate)
        
    def draw_all(self):
        """Draw all visual elements"""
        # Clear canvas
        self.canvas.delete("all")
        
        x, y = self.current_x, self.current_y
        
        # Return early if no mouse position yet
        if x is None or y is None:
            return
        
        # Draw line history with gradient effect
        if self.show_line_history and self.history_count > 1:
            # Get the points in order, handling circular buffer
            if self.history_count < self.max_history_points:
                # Buffer not full yet, use from 0 to history_count
                points = self.history_points[:self.history_count]
            else:
                # Buffer is full, arrange from oldest to newest
                points = np.concatenate([
                    self.history_points[self.history_index:],
                    self.history_points[:self.history_index]
                ])
            
            # Draw lines between consecutive points
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                
                # Calculate alpha for gradient effect
                alpha = (i + 1) / len(points)
                
                # Create color gradient from dark to bright blue
                intensity = int(100 + (155 * alpha))
                color = f"#{intensity//3:02x}{intensity//2:02x}{intensity:02x}"
                
                # Draw line with varying width
                width = max(1, int(3 * alpha))
                self.canvas.create_line(
                    start[0], start[1], end[0], end[1],
                    fill=color, width=width, capstyle='round'
                )
        
        # Draw trail with fade effect
        if self.show_trail and self.trail_positions:
            for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                # Calculate fade effect
                alpha = (i + 1) / len(self.trail_positions)
                trail_radius = self.pointer_radius * (0.2 + 0.8 * alpha)
                
                # Create gradient colors from transparent to solid
                if alpha < 0.3:
                    color = '#ffcccc'  # Very light red
                elif alpha < 0.6:
                    color = '#ff8888'  # Medium red
                else:
                    color = '#ff4444'  # Bright red
                    
                # Draw trail circle
                self.canvas.create_oval(
                    trail_x - trail_radius, trail_y - trail_radius,
                    trail_x + trail_radius, trail_y + trail_radius,
                    fill=color, outline='', width=0
                )
        
        # Draw growing animation circle
        if self.show_grow_animation:
            self.canvas.create_oval(
                x - self.grow_radius, y - self.grow_radius,
                x + self.grow_radius, y + self.grow_radius,
                outline='#00d2d3', width=3, fill=''
            )
            
        # Draw main red pointer circle
        self.canvas.create_oval(
            x - self.pointer_radius, y - self.pointer_radius,
            x + self.pointer_radius, y + self.pointer_radius,
            fill='#ff4757', outline='#ffffff', width=2
        )
        
        # Draw crosshair
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Horizontal line
        self.canvas.create_line(0, y, canvas_width, y, fill='#ff4757', width=1, stipple='gray50')
        # Vertical line
        self.canvas.create_line(x, 0, x, canvas_height, fill='#ff4757', width=1, stipple='gray50')
        
        # Draw coordinates with modern styling
        coord_text = f"Position: ({x}, {y})"
        if self.trail_positions:
            coord_text += f" | Trail: {len(self.trail_positions)}"
        if self.history_count > 0:
            coord_text += f" | Points: {self.history_count}"
            
        # Background for text
        text_x = x + 25
        text_y = y - 35
        
        # Ensure text stays within screen bounds
        if text_x + 200 > canvas_width:
            text_x = x - 225
        if text_y < 20:
            text_y = y + 35
            
        # Draw text background
        self.canvas.create_rectangle(
            text_x - 5, text_y - 15, text_x + 250, text_y + 15,
            fill='#2b2b2b', outline='#ff4757', width=1
        )
        
        # Draw text
        self.canvas.create_text(
            text_x, text_y, text=coord_text, anchor='w',
            font=('Segoe UI', 11), fill='#ffffff'
        )
        
        # Draw click effect if exists
        if hasattr(self, 'click_effect') and self.click_effect:
            effect = self.click_effect
            self.canvas.create_oval(
                effect['x'] - effect['radius'], effect['y'] - effect['radius'],
                effect['x'] + effect['radius'], effect['y'] + effect['radius'],
                outline='#00d2d3', width=3, fill=''
            )
            effect['radius'] += 3
            effect['lifetime'] -= 1
            if effect['lifetime'] <= 0:
                del self.click_effect
        
        # Keep UI elements on top
        self.reset_button.lift()
        self.controls_frame.lift()
        self.exit_button.lift()
        
    def run(self):
        """Start the application"""
        print("Modern Mouse Tracker Started!")
        print("- Move mouse to see tracking")
        print("- Click to create effects")
        print("- Use buttons to toggle features")
        print("Keyboard Shortcuts:")
        print("  C - Clear/Reset History")
        print("  L - Toggle Line History")
        print("  T - Toggle Trail Animation")
        print("  G - Toggle Grow Animation")
        print("  F/F11 - Toggle Fullscreen")
        print("  ESC - Exit Application")
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernMouseTracker()
    app.run()
