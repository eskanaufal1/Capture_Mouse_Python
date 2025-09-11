
import tkinter as tk

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
        self.circle = None
        self.radius = 20
        self.anim_radius = 40
        self.anim_grow = True
        self.trail_positions = []
        self.max_trail_length = 15
        self.root.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Configure>', self.on_resize)
        self.current_x = None
        self.current_y = None
        self.animate()

    def animate(self):
        # Animate the radius for pulsing effect
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
        self.trail_positions.append((x, y))
        # Keep trail length limited
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
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
        self.canvas.create_text(x + text_offset_x, y + text_offset_y, text=f"({x}, {y})", anchor='nw', font=('Arial', 16), fill='black')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MouseCircleApp()
    app.run()
