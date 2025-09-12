import tkinter as tk
from tkinter import ttk
import time
import math
import numpy as np
import threading
from rawInput import RawInputReader
import queue

class AdvancedMouseTracker:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Advanced Mouse Tracker with Raw Input")
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
        
        # Mouse tracking variables (enhanced with raw input data)
        # Get initial cursor position
        import ctypes
        from ctypes import wintypes
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        
        self.current_x = point.x if 0 <= point.x <= self.screen_width else self.screen_width // 2
        self.current_y = point.y if 0 <= point.y <= self.screen_height else self.screen_height // 2
        self.raw_delta_x = 0
        self.raw_delta_y = 0
        self.movement_velocity = 0
        self.movement_direction = 0
        
        # Trail positions with velocity information
        self.trail_positions = []
        
        # Line history using numpy array for efficiency (enhanced for raw input)
        self.max_history_points = 5000  # Increased for raw input precision
        self.history_points = np.zeros((self.max_history_points, 4), dtype=np.float32)  # x, y, delta_x, delta_y
        self.history_count = 0
        self.history_index = 0
        
        self.max_trail_length = 30  # Increased for smoother trails
        
        # Animation variables
        self.grow_radius = 30
        self.grow_direction = 1
        self.pointer_radius = 15
        
        # Control variables
        self.show_trail = True
        self.show_grow_animation = True
        self.show_line_history = True
        self.is_fullscreen = True
        self.show_coordinates = True
        self.show_velocity_info = True
        self.show_raw_delta = True
        
        # Plinko animation system (enhanced)
        self.show_plinko = True
        self.pin_radius = 8
        self.pin_spacing_x = 80
        self.pin_spacing_y = 60
        self.bounce_strength = 20
        self.collision_distance = self.pointer_radius + self.pin_radius
        
        # Initialize plinko pins
        self.setup_plinko_pins()
        
        # Bounce effects for collisions
        self.bounce_effects = []
        
        # Raw input statistics
        self.total_mouse_movements = 0
        self.total_raw_distance = 0
        self.max_velocity = 0
        self.click_count = 0
        self.wheel_delta = 0
        self.movement_count = 0  # For debugging
        
        # Raw input status tracking
        self.raw_input_active = False
        self.last_raw_input_time = 0
        
        # Initialize raw input reader
        self.raw_input_reader = RawInputReader()
        self.input_queue = queue.Queue()
        self.raw_input_thread = None
        
        # Create modern UI elements
        self.create_modern_ui()
        
        # Bind events
        self.root.bind('<Motion>', self.on_mouse_move)  # Fallback mouse tracking
        self.canvas.bind('<Motion>', self.on_mouse_move)  # Also bind to canvas
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<Escape>', lambda e: self.stop_and_quit())
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Bind keyboard shortcuts
        self.bind_keyboard_shortcuts()
        
        # Set focus to root window to capture key events
        self.root.focus_set()
        
        # Start raw input processing
        self.start_raw_input()
        
        # Start animation loop
        self.animate()
        
    def bind_keyboard_shortcuts(self):
        """Bind all keyboard shortcuts"""
        shortcuts = [
            ('c', 'C', self.shortcut_reset_history),
            ('l', 'L', self.shortcut_toggle_history),
            ('t', 'T', self.shortcut_toggle_trail),
            ('g', 'G', self.shortcut_toggle_grow),
            ('f', None, self.shortcut_toggle_fullscreen),
            ('p', 'P', self.shortcut_toggle_plinko),
            ('o', 'O', self.shortcut_toggle_coordinates),
            ('v', 'V', self.shortcut_toggle_velocity),
            ('r', 'R', self.shortcut_toggle_raw_delta)
        ]
        
        for lower, upper, func in shortcuts:
            self.root.bind(f'<KeyPress-{lower}>', lambda e, f=func: f())
            if upper:
                self.root.bind(f'<KeyPress-{upper}>', lambda e, f=func: f())
        
        self.root.bind('<F11>', lambda e: self.shortcut_toggle_fullscreen())
        
    def start_raw_input(self):
        """Start the raw input reader in a separate thread"""
        def raw_input_callback(data):
            """Callback to handle raw input data"""
            self.input_queue.put(data)
            
        def raw_input_worker():
            """Worker thread for raw input processing"""
            try:
                self.raw_input_reader.set_callback(raw_input_callback)
                self.raw_input_reader.register_devices()
                self.raw_input_reader.start_message_loop() # type: ignore
            except Exception as e:
                print(f"Raw input thread error: {e}")
                
        # Start raw input thread
        self.raw_input_thread = threading.Thread(target=raw_input_worker, daemon=True)
        self.raw_input_thread.start()
        print("🚀 Advanced Mouse Tracker with Raw Input started!")
        print("   Enhanced precision with Windows Raw Input API")
        
    def process_raw_input_data(self):
        """Process queued raw input data"""
        try:
            while not self.input_queue.empty():
                data = self.input_queue.get_nowait()
                
                if data['type'] == 'mouse_move':
                    self.handle_raw_mouse_movement(data)
                elif data['type'] == 'mouse_button':
                    self.handle_raw_mouse_button(data)
                elif data['type'] == 'mouse_wheel':
                    self.handle_raw_mouse_wheel(data)
                elif data['type'] == 'keyboard':
                    self.handle_raw_keyboard(data)
                    
        except queue.Empty:
            pass
            
    def handle_raw_mouse_movement(self, data):
        """Handle raw mouse movement data with enhanced precision"""
        # Mark raw input as active
        self.raw_input_active = True
        self.last_raw_input_time = time.time()
        
        # Get raw deltas
        self.raw_delta_x = data['delta_x']
        self.raw_delta_y = data['delta_y']
        
        # Calculate movement velocity and direction
        velocity = math.sqrt(self.raw_delta_x**2 + self.raw_delta_y**2)
        self.movement_velocity = velocity
        
        if velocity > 0:
            self.movement_direction = math.atan2(self.raw_delta_y, self.raw_delta_x)
            
        # Update max velocity tracking
        if velocity > self.max_velocity:
            self.max_velocity = velocity
            
        # Update total statistics
        self.total_mouse_movements += 1
        self.total_raw_distance += velocity
        
        # Get actual cursor position (more reliable than raw deltas for absolute position)
        import ctypes
        from ctypes import wintypes
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        
        # Update current position
        self.current_x = point.x
        self.current_y = point.y
        
        # Ensure coordinates are within screen bounds
        self.current_x = max(0, min(self.current_x, self.screen_width))
        self.current_y = max(0, min(self.current_y, self.screen_height))
        
        # Check for plinko pin collisions with velocity-based effects
        if self.show_plinko:
            self.check_plinko_collisions_with_velocity(self.current_x, self.current_y, velocity)
        
        # Store current position in history array with raw input data
        if self.show_line_history:
            self.history_points[self.history_index] = [
                self.current_x, self.current_y, 
                self.raw_delta_x, self.raw_delta_y
            ]
            self.history_index = (self.history_index + 1) % self.max_history_points
            if self.history_count < self.max_history_points:
                self.history_count += 1
        
        # Add to trail with velocity information
        if self.show_trail:
            self.trail_positions.append((self.current_x, self.current_y, velocity))
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
                
    def handle_raw_mouse_button(self, data):
        """Handle raw mouse button events"""
        if data['state'] == 'Down':
            self.click_count += 1
            # Create enhanced click effect with button information
            self.click_effect = {
                'x': self.current_x, 
                'y': self.current_y, 
                'radius': 5, 
                'lifetime': 30,
                'button': data['button'],
                'max_radius': 50
            }
            
    def handle_raw_mouse_wheel(self, data):
        """Handle raw mouse wheel events"""
        self.wheel_delta += data['delta']
        # Create wheel effect
        self.wheel_effect = {
            'x': self.current_x,
            'y': self.current_y,
            'delta': data['delta'],
            'lifetime': 20
        }
        
    def handle_raw_keyboard(self, data):
        """Handle raw keyboard events for enhanced shortcuts"""
        if data['state'] == 'Down':
            # Additional keyboard shortcuts can be added here
            pass
            
    def check_plinko_collisions_with_velocity(self, x, y, velocity):
        """Enhanced plinko collision detection with velocity-based effects"""
        if len(self.plinko_pins) == 0:
            return
            
        # Calculate distances to all pins using numpy
        distances = np.sqrt(np.sum((self.plinko_pins - [x, y]) ** 2, axis=1))
        
        # Find pins within collision distance
        collision_indices = np.where(distances <= self.collision_distance)[0]
        
        for idx in collision_indices:
            pin_x, pin_y = self.plinko_pins[idx]
            
            # Create velocity-enhanced bounce effect
            self.create_velocity_bounce_effect(pin_x, pin_y, velocity)
            
    def create_velocity_bounce_effect(self, pin_x, pin_y, velocity):
        """Create velocity-enhanced bounce effect"""
        current_time = time.time()
        
        # Check for recent effects at this location
        for effect in self.bounce_effects:
            if (abs(effect['x'] - pin_x) < 10 and 
                abs(effect['y'] - pin_y) < 10 and 
                current_time - effect['start_time'] < 0.1):
                return
        
        # Velocity affects bounce intensity
        velocity_factor = min(velocity / 50.0, 3.0)  # Cap at 3x effect
        
        bounce_effect = {
            'x': pin_x,
            'y': pin_y,
            'radius': self.pin_radius,
            'max_radius': self.pin_radius * (2 + velocity_factor),
            'start_time': current_time,
            'duration': 0.3 + (velocity_factor * 0.2),
            'color_intensity': min(255, 150 + int(velocity * 2)),
            'velocity': velocity
        }
        self.bounce_effects.append(bounce_effect)
        
    def create_modern_ui(self):
        """Create modern UI elements with enhanced controls"""
        
        # Main control buttons
        button_config = {
            'font': ('Segoe UI', 11, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'cursor': 'hand2',
            'height': 35
        }
        
        # Reset button
        self.reset_button = tk.Button(
            self.root,
            text="Reset History (C)",
            command=self.reset_history,
            bg='#ff4757',
            fg='white',
            activebackground='#ff3838',
            activeforeground='white',
            **button_config
        )
        self.reset_button.place(x=20, y=20, width=180, height=40)
        
        # Control buttons frame
        self.controls_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.controls_frame.place(x=220, y=20)
        
        # Create individual toggle buttons
        self.trail_button = tk.Button(
            self.controls_frame,
            text="Trail: ON (T)",
            command=self.toggle_trail,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.trail_button.pack(side='left', padx=3)
        
        self.grow_button = tk.Button(
            self.controls_frame,
            text="Grow: ON (G)",
            command=self.toggle_grow,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.grow_button.pack(side='left', padx=3)
        
        self.history_button = tk.Button(
            self.controls_frame,
            text="Lines: ON (L)",
            command=self.toggle_history,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.history_button.pack(side='left', padx=3)
        
        self.fullscreen_button = tk.Button(
            self.controls_frame,
            text="Full: ON (F)",
            command=self.toggle_fullscreen,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.fullscreen_button.pack(side='left', padx=3)
        
        self.plinko_button = tk.Button(
            self.controls_frame,
            text="Plinko: ON (P)",
            command=self.toggle_plinko,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.plinko_button.pack(side='left', padx=3)
        
        self.coordinates_button = tk.Button(
            self.controls_frame,
            text="Coords: ON (O)",
            command=self.toggle_coordinates,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.coordinates_button.pack(side='left', padx=3)
        
        self.velocity_button = tk.Button(
            self.controls_frame,
            text="Velocity: ON (V)",
            command=self.toggle_velocity_info,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.velocity_button.pack(side='left', padx=3)
        
        self.raw_delta_button = tk.Button(
            self.controls_frame,
            text="Raw: ON (R)",
            command=self.toggle_raw_delta,
            font=('Segoe UI', 10),
            bg='#2ed573',
            fg='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        self.raw_delta_button.pack(side='left', padx=3)
        
        # Exit button
        self.exit_button = tk.Button(
            self.root,
            text="Exit (ESC)",
            command=self.stop_and_quit,
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
        
        # Statistics display
        self.stats_label = tk.Label(
            self.root,
            text="Raw Input Statistics",
            font=('Segoe UI', 10),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        self.stats_label.place(x=20, y=self.screen_height-40)
        
    def toggle_velocity_info(self):
        """Toggle velocity information display"""
        self.show_velocity_info = not self.show_velocity_info
        self.velocity_button.config(
            text=f"Velocity: {'ON' if self.show_velocity_info else 'OFF'} (V)",
            bg='#2ed573' if self.show_velocity_info else '#ff4757'
        )
        
    def toggle_raw_delta(self):
        """Toggle raw delta information display"""
        self.show_raw_delta = not self.show_raw_delta
        self.raw_delta_button.config(
            text=f"Raw: {'ON' if self.show_raw_delta else 'OFF'} (R)",
            bg='#2ed573' if self.show_raw_delta else '#ff4757'
        )
        
    def shortcut_toggle_velocity(self):
        """Toggle velocity via keyboard shortcut"""
        self.toggle_velocity_info()
        status = "ON" if self.show_velocity_info else "OFF"
        print(f"Keyboard shortcut: Velocity info {status} (V)")
        
    def shortcut_toggle_raw_delta(self):
        """Toggle raw delta via keyboard shortcut"""
        self.toggle_raw_delta()
        status = "ON" if self.show_raw_delta else "OFF"
        print(f"Keyboard shortcut: Raw delta info {status} (R)")
        
    # Include all other toggle methods from the original
    def toggle_trail(self):
        self.show_trail = not self.show_trail
        self.trail_button.config(
            text=f"Trail: {'ON' if self.show_trail else 'OFF'} (T)",
            bg='#2ed573' if self.show_trail else '#ff4757'
        )
        if not self.show_trail:
            self.trail_positions.clear()
            
    def toggle_grow(self):
        self.show_grow_animation = not self.show_grow_animation
        self.grow_button.config(
            text=f"Grow: {'ON' if self.show_grow_animation else 'OFF'} (G)",
            bg='#2ed573' if self.show_grow_animation else '#ff4757'
        )
        
    def toggle_history(self):
        self.show_line_history = not self.show_line_history
        self.history_button.config(
            text=f"Lines: {'ON' if self.show_line_history else 'OFF'} (L)",
            bg='#2ed573' if self.show_line_history else '#ff4757'
        )
        if not self.show_line_history:
            self.reset_history_points()
            
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.root.attributes('-fullscreen', True)
            self.fullscreen_button.config(text="Full: ON (F)", bg='#2ed573')
        else:
            self.root.attributes('-fullscreen', False)
            self.root.geometry('1200x800')
            self.fullscreen_button.config(text="Full: OFF (F)", bg='#ff4757')
            
    def toggle_plinko(self):
        self.show_plinko = not self.show_plinko
        self.plinko_button.config(
            text=f"Plinko: {'ON' if self.show_plinko else 'OFF'} (P)",
            bg='#2ed573' if self.show_plinko else '#ff4757'
        )
        if not self.show_plinko:
            self.bounce_effects.clear()
            
    def toggle_coordinates(self):
        self.show_coordinates = not self.show_coordinates
        self.coordinates_button.config(
            text=f"Coords: {'ON' if self.show_coordinates else 'OFF'} (O)",
            bg='#2ed573' if self.show_coordinates else '#ff4757'
        )
        
    # Include shortcut methods
    def shortcut_reset_history(self):
        self.reset_history()
        print("Keyboard shortcut: History cleared (C)")
        
    def shortcut_toggle_history(self):
        self.toggle_history()
        print(f"Keyboard shortcut: Line history {'ON' if self.show_line_history else 'OFF'} (L)")
        
    def shortcut_toggle_trail(self):
        self.toggle_trail()
        print(f"Keyboard shortcut: Trail {'ON' if self.show_trail else 'OFF'} (T)")
        
    def shortcut_toggle_grow(self):
        self.toggle_grow()
        print(f"Keyboard shortcut: Grow {'ON' if self.show_grow_animation else 'OFF'} (G)")
        
    def shortcut_toggle_fullscreen(self):
        self.toggle_fullscreen()
        print(f"Keyboard shortcut: Fullscreen {'ON' if self.is_fullscreen else 'OFF'} (F)")
        
    def shortcut_toggle_plinko(self):
        self.toggle_plinko()
        print(f"Keyboard shortcut: Plinko {'ON' if self.show_plinko else 'OFF'} (P)")
        
    def shortcut_toggle_coordinates(self):
        self.toggle_coordinates()
        print(f"Keyboard shortcut: Coordinates {'ON' if self.show_coordinates else 'OFF'} (O)")
        
    def setup_plinko_pins(self):
        """Initialize plinko pin positions"""
        pins = []
        rows = int(self.screen_height // self.pin_spacing_y) + 1
        cols = int(self.screen_width // self.pin_spacing_x) + 1
        
        for row in range(rows):
            for col in range(cols):
                offset_x = (self.pin_spacing_x // 2) if row % 2 == 1 else 0
                x = col * self.pin_spacing_x + offset_x + self.pin_spacing_x // 2
                y = row * self.pin_spacing_y + self.pin_spacing_y // 2
                
                if 0 <= x <= self.screen_width and 0 <= y <= self.screen_height:
                    pins.append([x, y])
        
        self.plinko_pins = np.array(pins, dtype=np.float32)
        print(f"📍 Created {len(self.plinko_pins)} plinko pins")
        
    def reset_history_points(self):
        """Reset the history points array"""
        self.history_points.fill(0)
        self.history_count = 0
        self.history_index = 0
        
    def reset_history(self):
        """Reset all history and trails"""
        self.trail_positions.clear()
        self.reset_history_points()
        self.total_mouse_movements = 0
        self.total_raw_distance = 0
        self.max_velocity = 0
        
        # Visual feedback
        original_bg = self.reset_button.cget('bg')
        self.reset_button.config(bg='#00d2d3', text='Cleared!')
        self.root.after(300, lambda: self.reset_button.config(bg=original_bg, text='Reset History (C)'))
        
    def on_mouse_move(self, event):
        """Handle mouse movement as fallback when raw input is not available"""
        # Check if raw input is active (received data in the last 100ms)
        current_time = time.time()
        if self.raw_input_active and (current_time - self.last_raw_input_time) < 0.1:
            return  # Raw input is working, don't use fallback
        
        # Calculate deltas from previous position
        prev_x, prev_y = self.current_x, self.current_y
        new_x, new_y = event.x, event.y
        
        self.movement_count += 1
        
        # Update raw deltas for fallback
        self.raw_delta_x = new_x - prev_x
        self.raw_delta_y = new_y - prev_y
        
        # Calculate movement velocity and direction
        velocity = math.sqrt(self.raw_delta_x**2 + self.raw_delta_y**2)
        self.movement_velocity = velocity
        
        if velocity > 0:
            self.movement_direction = math.atan2(self.raw_delta_y, self.raw_delta_x)
            
        # Update max velocity tracking
        if velocity > self.max_velocity:
            self.max_velocity = velocity
            
        # Update total statistics
        self.total_mouse_movements += 1
        self.total_raw_distance += velocity
        
        # Update current position
        self.current_x = new_x
        self.current_y = new_y
        
        # Ensure coordinates are within screen bounds
        self.current_x = max(0, min(self.current_x, self.screen_width))
        self.current_y = max(0, min(self.current_y, self.screen_height))
        
        # Check for plinko pin collisions with velocity-based effects
        if self.show_plinko:
            self.check_plinko_collisions_with_velocity(self.current_x, self.current_y, velocity)
        
        # Store current position in history array with movement data
        if self.show_line_history:
            self.history_points[self.history_index] = [
                self.current_x, self.current_y, 
                self.raw_delta_x, self.raw_delta_y
            ]
            self.history_index = (self.history_index + 1) % self.max_history_points
            if self.history_count < self.max_history_points:
                self.history_count += 1
        
        # Add to trail with velocity information
        if self.show_trail:
            self.trail_positions.append((self.current_x, self.current_y, velocity))
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
        
    def on_mouse_click(self, event):
        """Handle mouse click"""
        self.click_count += 1
        
    def on_resize(self, event):
        """Handle window resize"""
        if hasattr(self, 'current_x'):
            self.draw_all()
            
    def update_bounce_effects(self):
        """Update bounce effects with velocity information"""
        current_time = time.time()
        active_effects = []
        
        for effect in self.bounce_effects:
            elapsed = current_time - effect['start_time']
            progress = elapsed / effect['duration']
            
            if progress <= 1.0:
                # Velocity-enhanced animation
                velocity_factor = effect.get('velocity', 1) / 20.0
                effect['radius'] = self.pin_radius + (effect['max_radius'] - self.pin_radius) * progress
                effect['color_intensity'] = int(effect['color_intensity'] * (1 - progress))
                active_effects.append(effect)
        
        self.bounce_effects = active_effects
        
    def animate(self):
        """Enhanced animation loop with raw input processing"""
        # Process raw input data
        self.process_raw_input_data()
        
        # Animate growing circle
        if self.show_grow_animation:
            self.grow_radius += self.grow_direction * 2
            if self.grow_radius > 60:
                self.grow_direction = -1
            elif self.grow_radius < 20:
                self.grow_direction = 1
                
        # Update bounce effects
        if self.show_plinko:
            self.update_bounce_effects()
            
        # Update statistics display
        self.update_statistics_display()
                
        # Draw everything
        self.draw_all()
            
        # Schedule next frame (higher framerate for smoother raw input)
        self.root.after(16, self.animate)  # ~60 FPS
        
    def update_statistics_display(self):
        """Update the statistics display"""
        if hasattr(self, 'stats_label'):
            avg_velocity = self.total_raw_distance / max(1, self.total_mouse_movements)
            
            # Check input method being used
            current_time = time.time()
            input_method = "Raw Input" if (self.raw_input_active and (current_time - self.last_raw_input_time) < 0.1) else "Tkinter Fallback"
            
            stats_text = f"{input_method} | Movements: {self.total_mouse_movements} | Distance: {self.total_raw_distance:.1f} | Avg Vel: {avg_velocity:.1f} | Max Vel: {self.max_velocity:.1f} | Clicks: {self.click_count}"
            self.stats_label.config(text=stats_text)
        
    def draw_all(self):
        """Enhanced drawing with raw input visualization"""
        # Clear canvas
        self.canvas.delete("all")
        
        x, y = self.current_x, self.current_y
        
        # Draw plinko pins with velocity-enhanced effects
        if self.show_plinko:
            self.draw_enhanced_plinko_pins()
        
        # Draw enhanced line history with velocity gradients
        if self.show_line_history and self.history_count > 1:
            self.draw_velocity_enhanced_history()
        
        # Draw enhanced trail with velocity information
        if self.show_trail and self.trail_positions:
            self.draw_velocity_enhanced_trail()
        
        # Draw growing animation circle
        if self.show_grow_animation:
            # Velocity affects grow animation
            velocity_factor = min(self.movement_velocity / 30.0, 2.0)
            grow_color_intensity = min(255, 100 + int(velocity_factor * 100))
            grow_color = f"#{grow_color_intensity//4:02x}{grow_color_intensity//2:02x}{grow_color_intensity:02x}"
            
            self.canvas.create_oval(
                x - self.grow_radius, y - self.grow_radius,
                x + self.grow_radius, y + self.grow_radius,
                outline=grow_color, width=3, fill=''
            )
            
        # Draw main pointer circle with velocity indication
        velocity_factor = min(self.movement_velocity / 50.0, 1.0)
        pointer_color_intensity = min(255, 150 + int(velocity_factor * 105))
        pointer_color = f"#{pointer_color_intensity:02x}{pointer_color_intensity//4:02x}{pointer_color_intensity//4:02x}"
        
        self.canvas.create_oval(
            x - self.pointer_radius, y - self.pointer_radius,
            x + self.pointer_radius, y + self.pointer_radius,
            fill=pointer_color, outline='#ffffff', width=2
        )
        
        # Draw enhanced crosshair
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        crosshair_color = '#ff4757' if self.movement_velocity < 10 else '#ffff00'
        self.canvas.create_line(0, y, canvas_width, y, fill=crosshair_color, width=1, stipple='gray50')
        self.canvas.create_line(x, 0, x, canvas_height, fill=crosshair_color, width=1, stipple='gray50')
        
        # Draw enhanced coordinates and raw input information
        if self.show_coordinates:
            self.draw_enhanced_coordinates(x, y)
        
        # Draw click and wheel effects
        self.draw_enhanced_effects()
        
        # Keep UI elements on top
        self.lift_ui_elements()
        
    def draw_enhanced_plinko_pins(self):
        """Draw plinko pins with enhanced velocity-based effects"""
        # Draw static pins
        for pin in self.plinko_pins:
            pin_x, pin_y = pin[0], pin[1]
            self.canvas.create_oval(
                pin_x - self.pin_radius, pin_y - self.pin_radius,
                pin_x + self.pin_radius, pin_y + self.pin_radius,
                fill='#ffa726', outline='#ff6f00', width=2
            )
            
        # Draw velocity-enhanced bounce effects
        for effect in self.bounce_effects:
            velocity = effect.get('velocity', 1)
            velocity_factor = min(velocity / 30.0, 2.0)
            
            # Velocity affects color intensity
            intensity = effect['color_intensity']
            red = min(255, intensity + int(velocity_factor * 50))
            green = max(0, intensity - int(velocity_factor * 25))
            blue = max(0, int(velocity_factor * 100))
            color = f"#{red:02x}{green:02x}{blue:02x}"
            
            # Draw multiple concentric circles for high velocity
            for i in range(int(1 + velocity_factor)):
                radius_offset = i * 5
                self.canvas.create_oval(
                    effect['x'] - effect['radius'] - radius_offset,
                    effect['y'] - effect['radius'] - radius_offset,
                    effect['x'] + effect['radius'] + radius_offset,
                    effect['y'] + effect['radius'] + radius_offset,
                    outline=color, width=max(1, 4 - i), fill=''
                )
        
    def draw_velocity_enhanced_history(self):
        """Draw line history with velocity-based visualization"""
        if self.history_count < self.max_history_points:
            points = self.history_points[:self.history_count]
        else:
            points = np.concatenate([
                self.history_points[self.history_index:],
                self.history_points[:self.history_index]
            ])
        
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            
            # Calculate velocity from delta information
            delta_magnitude = math.sqrt(start[2]**2 + start[3]**2)
            velocity_factor = min(delta_magnitude / 20.0, 1.0)
            
            # Alpha for gradient effect
            alpha = (i + 1) / len(points)
            
            # Velocity affects color and width
            base_intensity = int(100 + (155 * alpha))
            velocity_boost = int(velocity_factor * 100)
            
            red = min(255, base_intensity//3 + velocity_boost)
            green = min(255, base_intensity//2 + velocity_boost//2)
            blue = min(255, base_intensity + velocity_boost//3)
            color = f"#{red:02x}{green:02x}{blue:02x}"
            
            # Width varies with velocity and position
            width = max(1, int(3 * alpha * (1 + velocity_factor)))
            
            self.canvas.create_line(
                start[0], start[1], end[0], end[1],
                fill=color, width=width, capstyle='round'
            )
        
    def draw_velocity_enhanced_trail(self):
        """Draw trail with velocity information"""
        for i, (trail_x, trail_y, velocity) in enumerate(self.trail_positions):
            alpha = (i + 1) / len(self.trail_positions)
            velocity_factor = min(velocity / 30.0, 1.0)
            
            # Radius varies with velocity
            trail_radius = self.pointer_radius * (0.2 + 0.8 * alpha) * (1 + velocity_factor * 0.5)
            
            # Color intensity varies with velocity
            if velocity_factor < 0.3:
                color = f'#{int(255 * alpha):02x}{int(200 * alpha):02x}{int(200 * alpha):02x}'
            elif velocity_factor < 0.6:
                color = f'#{int(255 * alpha):02x}{int(255 * alpha * velocity_factor):02x}{int(100 * alpha):02x}'
            else:
                color = f'#{int(255 * alpha):02x}{int(100 * alpha):02x}{int(255 * alpha * velocity_factor):02x}'
                
            self.canvas.create_oval(
                trail_x - trail_radius, trail_y - trail_radius,
                trail_x + trail_radius, trail_y + trail_radius,
                fill=color, outline='', width=0
            )
        
    def draw_enhanced_coordinates(self, x, y):
        """Draw enhanced coordinate information with raw input data"""
        coord_lines = []
        
        # Basic position
        coord_lines.append(f"Position: ({x}, {y})")
        
        # Raw delta information
        if self.show_raw_delta:
            coord_lines.append(f"Raw Δ: ({self.raw_delta_x:+3d}, {self.raw_delta_y:+3d})")
        
        # Velocity information
        if self.show_velocity_info:
            coord_lines.append(f"Velocity: {self.movement_velocity:.1f}")
            if self.movement_velocity > 0:
                direction_deg = math.degrees(self.movement_direction)
                coord_lines.append(f"Direction: {direction_deg:.0f}°")
        
        # Trail and history counts
        if self.trail_positions:
            coord_lines.append(f"Trail: {len(self.trail_positions)}")
        if self.history_count > 0:
            coord_lines.append(f"Points: {self.history_count}")
        
        # Create text display
        coord_text = " | ".join(coord_lines)
        
        # Position text near cursor
        text_x = x + 25
        text_y = y - 45
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Keep text on screen
        text_width = len(coord_text) * 8
        if text_x + text_width > canvas_width:
            text_x = x - text_width - 25
        if text_y < 20:
            text_y = y + 45
            
        # Draw background
        self.canvas.create_rectangle(
            text_x - 5, text_y - 20, text_x + text_width + 5, text_y + 20,
            fill='#2b2b2b', outline='#ff4757', width=1
        )
        
        # Draw text
        self.canvas.create_text(
            text_x, text_y, text=coord_text, anchor='w',
            font=('Segoe UI', 11), fill='#ffffff'
        )
        
    def draw_enhanced_effects(self):
        """Draw enhanced click and wheel effects"""
        # Enhanced click effect
        if hasattr(self, 'click_effect') and self.click_effect:
            effect = self.click_effect
            button_colors = {
                'Left': '#ff4757',
                'Right': '#2ed573',
                'Middle': '#ffa726'
            }
            color = button_colors.get(effect.get('button', 'Left'), '#ff4757')
            
            # Multiple expanding rings
            for ring in range(3):
                ring_radius = effect['radius'] + (ring * 10)
                alpha = max(0, effect['lifetime'] - (ring * 5)) / 30
                
                if alpha > 0:
                    self.canvas.create_oval(
                        effect['x'] - ring_radius, effect['y'] - ring_radius,
                        effect['x'] + ring_radius, effect['y'] + ring_radius,
                        outline=color, width=max(1, 4-ring), fill=''
                    )
            
            effect['radius'] += 3
            effect['lifetime'] -= 1
            if effect['lifetime'] <= 0:
                del self.click_effect
        
        # Enhanced wheel effect
        if hasattr(self, 'wheel_effect') and self.wheel_effect:
            effect = self.wheel_effect
            direction = "↑" if effect['delta'] > 0 else "↓"
            
            self.canvas.create_text(
                effect['x'], effect['y'] - 30,
                text=f"Wheel {direction} {abs(effect['delta'])}",
                font=('Segoe UI', 14, 'bold'),
                fill='#00d2d3'
            )
            
            effect['lifetime'] -= 1
            if effect['lifetime'] <= 0:
                del self.wheel_effect
        
    def lift_ui_elements(self):
        """Keep UI elements on top"""
        elements = [
            'reset_button', 'controls_frame', 'exit_button', 'stats_label'
        ]
        for element_name in elements:
            if hasattr(self, element_name):
                getattr(self, element_name).lift()
        
    def stop_and_quit(self):
        """Safely stop the application"""
        print("🛑 Stopping Advanced Mouse Tracker...")
        if self.raw_input_reader:
            self.raw_input_reader.stop()
        self.root.quit()
        
    def run(self):
        """Start the application"""
        print("🚀 Advanced Mouse Tracker with Raw Input API Started!")
        print("Enhanced Features:")
        print("- Raw Windows input capture for maximum precision")
        print("- Velocity-based visual effects and plinko collisions")
        print("- Real-time movement analysis and statistics")
        print("- Enhanced trail rendering with speed visualization")
        print()
        print("Keyboard Shortcuts:")
        print("  C - Clear/Reset History & Statistics")
        print("  L - Toggle Line History")
        print("  T - Toggle Trail Animation")
        print("  G - Toggle Grow Animation")
        print("  P - Toggle Plinko Animation")
        print("  O - Toggle Coordinates Display")
        print("  V - Toggle Velocity Information")
        print("  R - Toggle Raw Delta Display")
        print("  F/F11 - Toggle Fullscreen")
        print("  ESC - Exit Application")
        print()
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedMouseTracker()
    app.run()