import tkinter as tk
from tkinter import ttk
import time

class MouseCircleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Position Circle")
        self.root.overrideredirect(False)  # No frame, but keep window controls
        self.root.attributes('-topmost', True)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, highlightthickness=0, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create reset button on main window
        self.reset_button = tk.Button(
            self.root, 
            text="Reset Trail", 
            command=self.reset_trail_history,
            font=('Arial', 10, 'bold'),
            bg='red',
            fg='white',
            activebackground='darkred',
            activeforeground='white',
            relief='raised',
            bd=2
        )
        self.reset_button.place(x=10, y=10, width=100, height=30)
        
        self.circle = None
        self.radius = 20
        self.anim_radius = 40
        self.anim_grow = True
        self.trail_positions = []
        self.max_trail_length = 15
        self.position_history = []
        self.max_history = 100
        
        # Control variables
        self.show_trail = tk.BooleanVar(value=True)
        self.show_animation = tk.BooleanVar(value=True)
        self.show_history = tk.BooleanVar(value=False)
        
        self.root.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Configure>', self.on_resize)
        self.current_x = None
        self.current_y = None
        
        # Add keyboard shortcut to show control window
        self.root.bind('<F1>', lambda e: self.show_or_create_control_window())
        self.root.focus_set()
        
        # Create control window immediately
        self.create_control_window()
        self.animate()

    def reset_trail_history(self):
        """Reset all trail positions and history data"""
        self.trail_positions.clear()
        self.position_history.clear()
        
        # Visual feedback - briefly change button color
        original_bg = self.reset_button.cget('bg')
        self.reset_button.config(bg='darkgreen', text='Reset!')
        self.root.after(200, lambda: self.reset_button.config(bg=original_bg, text='Reset Trail'))
        
        # Update control window history display if it exists
        if hasattr(self, 'history_text'):
            self.update_history_display()
        
        # Clear canvas and redraw current position if available
        if self.current_x is not None and self.current_y is not None:
            self.draw_circle(self.current_x, self.current_y)
        
        print("Trail and history reset!")

    def create_control_window(self):
        try:
            # Create separate control window
            self.control_window = tk.Toplevel(self.root)
            self.control_window.title("Mouse Tracker Controls")
            self.control_window.geometry("400x600+200+100")
            self.control_window.configure(bg='lightgray')
            self.control_window.attributes('-topmost', True)
            
            print("Creating control window...")
            
            # Create the UI elements
            self.setup_control_ui()
            
            # Make sure window appears
            self.control_window.lift()
            self.control_window.focus_force()
            
            print("Control window created successfully!")
            
        except Exception as e:
            print(f"Error creating control window: {e}")

    def setup_control_ui(self):
        # Title label
        title_label = tk.Label(self.control_window, text="Mouse Tracker Controls", 
                              font=('Arial', 14, 'bold'), bg='lightgray')
        title_label.pack(pady=10)
        
        # Trail controls
        trail_frame = tk.LabelFrame(self.control_window, text="Trail Settings", 
                                   font=('Arial', 10, 'bold'), bg='lightgray')
        trail_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(trail_frame, text="Show Snake Trail", variable=self.show_trail,
                      font=('Arial', 10), bg='lightgray').pack(anchor='w', padx=10, pady=5)
        
        # Animation controls
        anim_frame = tk.LabelFrame(self.control_window, text="Animation Settings", 
                                  font=('Arial', 10, 'bold'), bg='lightgray')
        anim_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(anim_frame, text="Show Pulsing Animation", variable=self.show_animation,
                      font=('Arial', 10), bg='lightgray').pack(anchor='w', padx=10, pady=5)
        
        # History controls
        history_frame = tk.LabelFrame(self.control_window, text="Position History", 
                                     font=('Arial', 10, 'bold'), bg='lightgray')
        history_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Checkbutton(history_frame, text="Enable History Tracking", variable=self.show_history,
                      font=('Arial', 10), bg='lightgray').pack(anchor='w', padx=10, pady=5)
        
        # History display
        self.history_text = tk.Text(history_frame, height=15, width=45, font=('Courier', 9))
        self.history_text.pack(padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(history_frame, bg='lightgray')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_frame, text="Clear History Only", command=self.reset_history_only,
                 font=('Arial', 9), bg='orange', fg='white').pack(side='left', padx=5)
        tk.Button(button_frame, text="Reset All", command=self.reset_trail_history,
                 font=('Arial', 9), bg='red', fg='white').pack(side='left', padx=5)
        tk.Button(button_frame, text="Save History", command=self.save_history,
                 font=('Arial', 9), bg='green', fg='white').pack(side='left', padx=5)
        
        # Instructions
        instructions = tk.Label(self.control_window, 
                               text="Press F1 in main window to show/hide this control panel",
                               font=('Arial', 8), bg='lightgray', fg='blue')
        instructions.pack(pady=5)

    def show_or_create_control_window(self):
        try:
            if hasattr(self, 'control_window') and self.control_window.winfo_exists():
                self.control_window.deiconify()
                self.control_window.lift()
                self.control_window.focus_force()
            else:
                self.create_control_window()
        except:
            self.create_control_window()

    def animate(self):
        # Animate the radius for pulsing effect
        if self.show_animation.get():
            if self.anim_grow:
                self.anim_radius += 2
                if self.anim_radius > 60:
                    self.anim_grow = False
            else:
                self.anim_radius -= 2
                if self.anim_radius < 30:
                    self.anim_grow = True
        # Redraw if mouse position is known
        if self.current_x is not None and self.current_y is not None:
            self.draw_circle(self.current_x, self.current_y)
        self.root.after(30, self.animate)

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        self.current_x = x
        self.current_y = y
        
        # Add current position to trail
        if self.show_trail.get():
            self.trail_positions.append((x, y))
            # Keep trail length limited
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
        
        # Add to history with timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.position_history.append((x, y, timestamp))
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
        
        # Update history display in control window
        self.update_history_display()
        
        self.draw_circle(x, y)

    def on_resize(self, event):
        # Redraw crosshair and circle at last known position
        if self.current_x is not None and self.current_y is not None:
            self.draw_circle(self.current_x, self.current_y)

    def draw_circle(self, x, y):
        # Remove previous drawings
        self.canvas.delete("all")
        # Get current canvas size
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Draw snake trail
        if self.show_trail.get() and self.trail_positions:
            for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                # Calculate trail properties (fade from back to front)
                alpha = (i + 1) / len(self.trail_positions)
                trail_radius = self.radius * (0.3 + 0.7 * alpha)
                
                # Create color with opacity effect using different shades
                if alpha < 0.3:
                    color = '#E8E8E8'  # Very light gray
                elif alpha < 0.6:
                    color = '#B0B0B0'  # Light gray
                else:
                    color = '#808080'  # Medium gray
                
                # Draw trail circle
                self.canvas.create_oval(
                    trail_x - trail_radius, trail_y - trail_radius,
                    trail_x + trail_radius, trail_y + trail_radius,
                    fill=color, outline='', width=0)
        
        # Draw animated circle behind the pointer
        if self.show_animation.get():
            self.canvas.create_oval(
                x - self.anim_radius, y - self.anim_radius,
                x + self.anim_radius, y + self.anim_radius,
                fill='', outline='lightblue', width=4)
        
        # Draw circle at pointer
        self.circle = self.canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill='blue', outline='black', width=2)
        
        # Draw crosshair spanning the visible canvas
        self.canvas.create_line(0, y, width, y, fill='red', width=2)
        self.canvas.create_line(x, 0, x, height, fill='red', width=2)
        
        # Draw coordinates text in top left near the circle (pointer)
        text_offset_x = -60  # left of the circle
        text_offset_y = -30  # above the circle
        coord_text = f"({x}, {y})"
        
        # Add trail count indicator
        if self.trail_positions:
            coord_text += f" | Trail: {len(self.trail_positions)}"
        
        self.canvas.create_text(x + text_offset_x, y + text_offset_y, 
                               text=coord_text, anchor='nw', 
                               font=('Arial', 14), fill='black')
        
        # Ensure reset button stays on top
        self.reset_button.lift()

    def clear_history(self):
        """Clear history from control window - calls the main reset method"""
        self.reset_trail_history()

    def reset_history_only(self):
        """Reset only position history, keep trail"""
        self.position_history.clear()
        self.update_history_display()
        print("Position history cleared!")

    def save_history(self):
        if not self.position_history:
            return
        
        try:
            import tkinter.filedialog as fd
            filename = fd.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Mouse Position History"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write("Mouse Position History\n")
                    f.write("=" * 30 + "\n\n")
                    for i, (x, y, timestamp) in enumerate(self.position_history, 1):
                        f.write(f"{i:3d}: ({x:4d}, {y:4d}) at {timestamp}\n")
        except Exception as e:
            print(f"Error saving history: {e}")

    def update_history_display(self):
        if hasattr(self, 'history_text'):
            self.history_text.delete(1.0, tk.END)
            
            if self.show_history.get() and self.position_history:
                self.history_text.insert(tk.END, "Recent Mouse Positions:\n")
                self.history_text.insert(tk.END, "-" * 30 + "\n")
                
                # Show last 50 positions
                for i, (x, y, timestamp) in enumerate(self.position_history[-50:], 1):
                    self.history_text.insert(tk.END, f"{i:2d}: ({x:4d}, {y:4d}) - {timestamp}\n")
                
                self.history_text.see(tk.END)
            else:
                self.history_text.insert(tk.END, "History tracking is disabled.\nCheck 'Enable History Tracking' to start.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MouseCircleApp()
    app.run()
