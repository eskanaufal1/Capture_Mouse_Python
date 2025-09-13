#!/usr/bin/env python3
"""
Modern Touch Tracker with Kivy
===============================

A simple and modern touch tracking application that captures touch movements
with visual effects and real-time statistics, inspired by modern design principles.
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Line, Color, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
import time
import math

class TouchTracker(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Touch tracking variables
        self.touch_positions = []
        self.trail_positions = []
        self.max_trail_length = 20
        self.max_history_points = 300
        
        # Visual settings
        self.pointer_radius = 15
        
        # Control variables
        self.show_trail = True
        self.show_coordinates = True
        self.show_lines = True
        
        # Statistics
        self.total_touches = 0
        self.current_touch_id = None
        self.touch_start_time = None
        self.total_distance = 0.0
        self.last_touch_pos = None
        
        # Animation timer
        Clock.schedule_interval(self.update_animation, 1/30.0)  # 30 FPS
        
    def reset_history(self):
        """Reset all touch history and trails"""
        self.touch_positions.clear()
        self.trail_positions.clear()
        self.total_touches = 0
        self.total_distance = 0.0
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.clear()
        print("🧹 Touch history and trails reset!")
        
    def toggle_trail(self):
        """Toggle trail visualization"""
        self.show_trail = not self.show_trail
        if not self.show_trail:
            self.trail_positions.clear()
        status = "ON" if self.show_trail else "OFF"
        print(f"🎨 Trail animation: {status}")
        
    def toggle_lines(self):
        """Toggle line display"""
        self.show_lines = not self.show_lines
        status = "ON" if self.show_lines else "OFF"
        print(f"� Line display: {status}")
        
    def toggle_coordinates(self):
        """Toggle coordinates display"""
        self.show_coordinates = not self.show_coordinates
        status = "ON" if self.show_coordinates else "OFF"
        print(f"📍 Coordinates display: {status}")
        
    def on_touch_down(self, touch):
        """Handle touch down event"""
        self.total_touches += 1
        self.current_touch_id = touch.id
        self.touch_start_time = time.time()
        self.last_touch_pos = touch.pos
        
        # Add to position history
        self.touch_positions.append(touch.pos)
        
        # Add to trail
        if self.show_trail:
            self.trail_positions.append(touch.pos)
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
                
        print(f"🎯 Touch DOWN at ({touch.x:.0f}, {touch.y:.0f}) | Touch #{self.total_touches}")
        return True
        
    def on_touch_move(self, touch):
        """Handle touch move event - Core functionality"""
        if touch.id == self.current_touch_id:
            # Calculate distance moved
            if self.last_touch_pos:
                dx = touch.x - self.last_touch_pos[0]
                dy = touch.y - self.last_touch_pos[1]
                distance = math.sqrt(dx*dx + dy*dy)
                self.total_distance += distance
                
            self.last_touch_pos = touch.pos
            
            # Add to position history
            self.touch_positions.append(touch.pos)
            if len(self.touch_positions) > self.max_history_points:
                self.touch_positions.pop(0)
                
            # Add to trail
            if self.show_trail:
                self.trail_positions.append(touch.pos)
                if len(self.trail_positions) > self.max_trail_length:
                    self.trail_positions.pop(0)
                    
            # Print movement data with delta information
            delta_info = ""
            if len(self.touch_positions) > 1:
                prev_pos = self.touch_positions[-2]
                delta_x = touch.x - prev_pos[0]
                delta_y = touch.y - prev_pos[1]
                delta_info = f" | Δ({delta_x:+.0f}, {delta_y:+.0f})"
                
            print(f"🖱️  Touch MOVE at ({touch.x:.0f}, {touch.y:.0f}){delta_info} | Total Distance: {self.total_distance:.1f}px")
            
        return True
        
    def on_touch_up(self, touch):
        """Handle touch up event"""
        if touch.id == self.current_touch_id:
            duration = time.time() - self.touch_start_time if self.touch_start_time else 0
            print(f"✋ Touch UP at ({touch.x:.0f}, {touch.y:.0f}) | Duration: {duration:.2f}s | Total Distance: {self.total_distance:.1f}px")
            print(f"📊 Session Stats: {len(self.touch_positions)} points recorded")
            
            self.current_touch_id = None
            self.touch_start_time = None
            
        return True
        
    def update_animation(self, dt):
        """Update animations and redraw"""
        # Redraw if we have touch data
        if self.touch_positions or self.trail_positions:
            self.draw_touch_visualization()
            
    def draw_touch_visualization(self):
        """Draw all touch visualizations"""
        if not hasattr(self, 'canvas') or not self.canvas:
            return
            
        try:
            self.canvas.clear()
            
            with self.canvas:
                # Draw trail with fade effect
                if self.show_trail and self.trail_positions:
                    for i, pos in enumerate(self.trail_positions):
                        alpha = (i + 1) / len(self.trail_positions)
                        trail_radius = self.pointer_radius * (0.3 + 0.7 * alpha)
                        
                        # Create fading color (light red)
                        Color(1, 0.6, 0.6, alpha * 0.8)
                        Ellipse(
                            pos=(pos[0] - trail_radius, pos[1] - trail_radius),
                            size=(trail_radius * 2, trail_radius * 2)
                        )
                        
                # Draw touch history as connected lines
                if self.show_lines and len(self.touch_positions) > 1:
                    for i in range(len(self.touch_positions) - 1):
                        alpha = (i + 1) / len(self.touch_positions)
                        
                        Color(0, 0.824, 0.827, alpha)  # Cyan with varying alpha
                        Line(
                            points=[
                                self.touch_positions[i][0], self.touch_positions[i][1],
                                self.touch_positions[i+1][0], self.touch_positions[i+1][1]
                            ],
                            width=max(1, int(3 * alpha))
                        )
                        
                # Draw current touch point and effects
                if self.touch_positions:
                    current_pos = self.touch_positions[-1]
                    
                    # Draw main touch point
                    Color(1, 0.278, 0.341, 1)  # Red
                    Ellipse(
                        pos=(current_pos[0] - self.pointer_radius, current_pos[1] - self.pointer_radius),
                        size=(self.pointer_radius * 2, self.pointer_radius * 2)
                    )
                    
                    # Draw crosshair if enabled
                    if self.show_coordinates:
                        Color(1, 0.278, 0.341, 0.5)  # Semi-transparent red
                        Line(points=[0, current_pos[1], self.width, current_pos[1]], width=1)
                        Line(points=[current_pos[0], 0, current_pos[0], self.height], width=1)
                        
        except Exception as e:
            print(f"Drawing error: {e}")

class ModernTouchApp(App):
    def build(self):
        self.title = 'Modern Touch Tracker'
        
        # Set dark background
        Window.clearcolor = (0.104, 0.104, 0.104, 1)
        
        # Create main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Create control panel
        control_panel = BoxLayout(
            orientation='horizontal', 
            size_hint=(1, None), 
            height=60,
            spacing=10,
            padding=[10, 10, 10, 10]
        )
        
        # Create buttons with proper event handling
        reset_btn = Button(text='Reset History (R)', size_hint=(None, 1), width=200)
        trail_btn = Button(text='Toggle Trail (T)', size_hint=(None, 1), width=170)
        lines_btn = Button(text='Toggle Lines (L)', size_hint=(None, 1), width=170)
        coords_btn = Button(text='Toggle Coords (C)', size_hint=(None, 1), width=190)
        exit_btn = Button(text='Exit (ESC)', size_hint=(None, 1), width=110)
        
        # Create touch tracker
        self.touch_tracker = TouchTracker()
        
        # Bind button events manually since linter doesn't recognize bind()
        try:
            reset_btn.bind(on_press=lambda x: self.touch_tracker.reset_history())
            trail_btn.bind(on_press=lambda x: self.touch_tracker.toggle_trail())
            lines_btn.bind(on_press=lambda x: self.touch_tracker.toggle_lines())
            coords_btn.bind(on_press=lambda x: self.touch_tracker.toggle_coordinates())
            exit_btn.bind(on_press=lambda x: self.stop())
        except AttributeError:
            print("Note: Button binding not available in static analysis")
        
        # Statistics label
        self.stats_label = Label(
            text='Touch Statistics: Ready to track',
            text_size=(300, None),
            halign='center'
        )
        
        # Add widgets to control panel
        control_panel.add_widget(reset_btn)
        control_panel.add_widget(trail_btn)
        control_panel.add_widget(lines_btn) 
        control_panel.add_widget(coords_btn)
        control_panel.add_widget(self.stats_label)
        control_panel.add_widget(exit_btn)
        
        # Add to main layout
        main_layout.add_widget(control_panel)
        main_layout.add_widget(self.touch_tracker)
        
        # Bind keyboard events
        try:
            Window.bind(on_key_down=self.on_keyboard_down)
        except AttributeError:
            print("Note: Keyboard binding not available in static analysis")
        
        # Update stats periodically
        Clock.schedule_interval(self.update_stats, 0.5)
        
        return main_layout
        
    def update_stats(self, dt):
        """Update statistics display"""
        tracker = self.touch_tracker
        active_status = "ACTIVE" if tracker.current_touch_id is not None else "IDLE"
        stats_text = f"Touches: {tracker.total_touches} | Points: {len(tracker.touch_positions)} | Distance: {tracker.total_distance:.1f}px | Status: {active_status}"
        self.stats_label.text = stats_text
        
    def on_keyboard_down(self, window, keycode, *args):
        """Handle keyboard shortcuts"""
        try:
            # Handle different keycode formats
            if isinstance(keycode, tuple) and len(keycode) > 1:
                key = keycode[1].lower()
            elif isinstance(keycode, int):
                # Convert keycode integer to character
                key = chr(keycode).lower() if 32 <= keycode <= 126 else ''
            else:
                key = str(keycode).lower()
            
            if key == 'r':
                self.touch_tracker.reset_history()
            elif key == 't':
                self.touch_tracker.toggle_trail()
            elif key == 'l':
                self.touch_tracker.toggle_lines()
            elif key == 'c':
                self.touch_tracker.toggle_coordinates()
            elif keycode == 27:  # ESC key code
                self.stop()
                
        except Exception as e:
            print(f"Keyboard handling error: {e}")
            
        return True

if __name__ == "__main__":
    print("🎯 Modern Touch Tracker Started!")
    print("=" * 50)
    print("✨ Features:")
    print("  - Real-time touch movement tracking")
    print("  - Visual trail and line animations")
    print("  - Live statistics and distance calculation")
    print("  - Modern UI with toggle controls")
    print("  - Crosshair and coordinate display")
    print("  - High-precision delta movement capture")
    print()
    print("🎮 Controls:")
    print("  - Touch and drag to see tracking")
    print("  - Use buttons to toggle features")
    print()
    print("⌨️  Keyboard Shortcuts:")
    print("  R - Reset History and Trails")
    print("  T - Toggle Trail Animation")
    print("  L - Toggle Line Display")
    print("  C - Toggle Coordinates/Crosshair")
    print("  ESC - Exit Application")
    print()
    print("🔥 Touch the screen to start tracking!")
    print("   Watch console for detailed movement data")
    print("=" * 50)
    
    ModernTouchApp().run()
