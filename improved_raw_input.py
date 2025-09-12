#!/usr/bin/env python3
"""
Improved Raw Input Reader with Proper Window
============================================

This version creates a proper window to receive raw input messages.
Raw input requires a window handle to work properly on most Windows systems.
"""

import ctypes
import ctypes.wintypes
import sys
import threading
import time
import tkinter as tk
from ctypes import wintypes

# Windows API constants
WM_INPUT = 0x00FF
RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

RIDEV_INPUTSINK = 0x00000100
RIDEV_NOLEGACY = 0x00000030

# Mouse button flags
RI_MOUSE_LEFT_BUTTON_DOWN = 0x0001
RI_MOUSE_LEFT_BUTTON_UP = 0x0002
RI_MOUSE_RIGHT_BUTTON_DOWN = 0x0004
RI_MOUSE_RIGHT_BUTTON_UP = 0x0008
RI_MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
RI_MOUSE_MIDDLE_BUTTON_UP = 0x0020
RI_MOUSE_WHEEL = 0x0400

# Define structures (same as before)
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND)
    ]

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM)
    ]

class RAWMOUSE(ctypes.Structure):
    _fields_ = [
        ("usFlags", wintypes.USHORT),
        ("usButtonFlags", wintypes.USHORT),
        ("usButtonData", wintypes.USHORT),
        ("ulRawButtons", wintypes.ULONG),
        ("lLastX", wintypes.LONG),
        ("lLastY", wintypes.LONG),
        ("ulExtraInformation", wintypes.ULONG)
    ]

class RAWKEYBOARD(ctypes.Structure):
    _fields_ = [
        ("MakeCode", wintypes.USHORT),
        ("Flags", wintypes.USHORT),
        ("Reserved", wintypes.USHORT),
        ("VKey", wintypes.USHORT),
        ("Message", wintypes.UINT),
        ("ExtraInformation", wintypes.ULONG)
    ]

class RAWHID(ctypes.Structure):
    _fields_ = [
        ("dwSizeHid", wintypes.DWORD),
        ("dwCount", wintypes.DWORD),
        ("bRawData", ctypes.c_byte * 1)
    ]

class RAWINPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mouse", RAWMOUSE),
        ("keyboard", RAWKEYBOARD),
        ("hid", RAWHID)
    ]

class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_UNION)
    ]

class ImprovedRawInputReader:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.running = False
        self.callback = None
        
        # Statistics
        self.total_mouse_x = 0
        self.total_mouse_y = 0
        self.mouse_clicks = 0
        self.mouse_wheel_delta = 0
        self.key_presses = 0
        self.last_key = None
        self.hid_data_count = 0
        
        # Tkinter window for proper message handling
        self.root = None
        self.hwnd = None
        
    def set_callback(self, callback_func):
        """Set callback function to handle raw input data"""
        self.callback = callback_func
        
    def create_window(self):
        """Create a Tkinter window to receive raw input messages"""
        self.root = tk.Tk()
        self.root.title("Raw Input Monitor")
        self.root.geometry("400x300")
        self.root.configure(bg='#2b2b2b')
        
        # Get window handle
        self.root.update()  # Make sure window is created
        self.hwnd = self.root.winfo_id()
        
        # Create UI
        info_label = tk.Label(
            self.root,
            text="Raw Input Monitor\nWindow handle: 0x{:08X}".format(self.hwnd),
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='white',
            justify='center'
        )
        info_label.pack(expand=True)
        
        self.stats_label = tk.Label(
            self.root,
            text="Waiting for input...",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            justify='left'
        )
        self.stats_label.pack(side='bottom', padx=10, pady=10)
        
        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        print(f"✅ Created window with handle: 0x{self.hwnd:08X}")
        return True
        
    def register_devices(self):
        """Register for raw input with window handle"""
        if not self.hwnd:
            print("❌ No window handle available for registration")
            return False
            
        print("🔧 Registering raw input devices with window handle...")
        
        try:
            # Mouse device
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01  # Generic Desktop
            mouse_device.usUsage = 0x02      # Mouse
            mouse_device.dwFlags = RIDEV_INPUTSINK
            mouse_device.hwndTarget = self.hwnd
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Successfully registered mouse for raw input")
                
                # Try keyboard too
                keyboard_device = RAWINPUTDEVICE()
                keyboard_device.usUsagePage = 0x01  # Generic Desktop
                keyboard_device.usUsage = 0x06      # Keyboard
                keyboard_device.dwFlags = RIDEV_INPUTSINK
                keyboard_device.hwndTarget = self.hwnd
                
                kb_result = self.user32.RegisterRawInputDevices(
                    ctypes.byref(keyboard_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
                )
                
                if kb_result:
                    print("✅ Successfully registered keyboard for raw input")
                else:
                    print("⚠️  Keyboard registration failed, but mouse should work")
                    
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Failed to register devices. Error: {error_code}")
                return False
                
        except Exception as e:
            print(f"❌ Registration exception: {e}")
            return False
            
    def process_raw_input(self, lParam):
        """Process raw input message"""
        try:
            # Get the size of raw input data
            size = wintypes.UINT()
            self.user32.GetRawInputData(
                lParam, 
                0x10000003,  # RID_INPUT
                None, 
                ctypes.byref(size), 
                ctypes.sizeof(RAWINPUTHEADER)
            )
            
            # Allocate buffer and get the data
            buffer = ctypes.create_string_buffer(size.value)
            result = self.user32.GetRawInputData(
                lParam,
                0x10000003,  # RID_INPUT
                buffer,
                ctypes.byref(size),
                ctypes.sizeof(RAWINPUTHEADER)
            )
            
            if result != size.value:
                return
                
            # Parse the raw input
            raw_input = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents
            
            if raw_input.header.dwType == RIM_TYPEMOUSE:
                self.process_mouse_data(raw_input.data.mouse)
            elif raw_input.header.dwType == RIM_TYPEKEYBOARD:
                self.process_keyboard_data(raw_input.data.keyboard)
            elif raw_input.header.dwType == RIM_TYPEHID:
                self.process_hid_data(raw_input.data.hid, raw_input.header.hDevice)
                
        except Exception as e:
            print(f"Error processing raw input: {e}")
            
    def process_mouse_data(self, mouse_data):
        """Process raw mouse input data"""
        # Mouse movement
        if mouse_data.lLastX != 0 or mouse_data.lLastY != 0:
            self.total_mouse_x += mouse_data.lLastX
            self.total_mouse_y += mouse_data.lLastY
            
            data = {
                'type': 'mouse_move',
                'delta_x': mouse_data.lLastX,
                'delta_y': mouse_data.lLastY,
                'total_x': self.total_mouse_x,
                'total_y': self.total_mouse_y,
                'flags': mouse_data.usFlags,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
                
        # Mouse buttons
        button_flags = mouse_data.usButtonFlags
        if button_flags:
            self.mouse_clicks += 1
            button_name = "Unknown"
            button_state = "Unknown"
            
            if button_flags & RI_MOUSE_LEFT_BUTTON_DOWN:
                button_name, button_state = "Left", "Down"
            elif button_flags & RI_MOUSE_LEFT_BUTTON_UP:
                button_name, button_state = "Left", "Up"
            elif button_flags & RI_MOUSE_RIGHT_BUTTON_DOWN:
                button_name, button_state = "Right", "Down"
            elif button_flags & RI_MOUSE_RIGHT_BUTTON_UP:
                button_name, button_state = "Right", "Up"
            elif button_flags & RI_MOUSE_MIDDLE_BUTTON_DOWN:
                button_name, button_state = "Middle", "Down"
            elif button_flags & RI_MOUSE_MIDDLE_BUTTON_UP:
                button_name, button_state = "Middle", "Up"
            elif button_flags & RI_MOUSE_WHEEL:
                wheel_delta = ctypes.c_short(mouse_data.usButtonData).value
                self.mouse_wheel_delta += wheel_delta
                data = {
                    'type': 'mouse_wheel',
                    'delta': wheel_delta,
                    'total_delta': self.mouse_wheel_delta,
                    'timestamp': time.time()
                }
                if self.callback:
                    self.callback(data)
                return
                
            data = {
                'type': 'mouse_button',
                'button': button_name,
                'state': button_state,
                'click_count': self.mouse_clicks,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
                
    def process_keyboard_data(self, keyboard_data):
        """Process raw keyboard input data"""
        self.key_presses += 1
        self.last_key = keyboard_data.VKey
        
        key_state = "Down" if not (keyboard_data.Flags & 0x01) else "Up"
        
        data = {
            'type': 'keyboard',
            'vkey': keyboard_data.VKey,
            'scan_code': keyboard_data.MakeCode,
            'flags': keyboard_data.Flags,
            'state': key_state,
            'key_count': self.key_presses,
            'timestamp': time.time()
        }
        
        if self.callback:
            self.callback(data)
            
    def process_hid_data(self, hid_data, device_handle):
        """Process raw HID device data"""
        self.hid_data_count += 1
        
        # Extract raw bytes
        raw_bytes = []
        for i in range(min(hid_data.dwSizeHid * hid_data.dwCount, 64)):
            raw_bytes.append(hid_data.bRawData[i])
            
        data = {
            'type': 'hid',
            'device_handle': device_handle,
            'size': hid_data.dwSizeHid,
            'count': hid_data.dwCount,
            'raw_bytes': raw_bytes,
            'hex_data': ' '.join(f'{b:02X}' for b in raw_bytes),
            'data_count': self.hid_data_count,
            'timestamp': time.time()
        }
        
        if self.callback:
            self.callback(data)
            
    def update_stats_display(self):
        """Update the statistics display in the window"""
        if self.stats_label and self.root:
            try:
                stats_text = f"Mouse: Δ({self.total_mouse_x:+6d}, {self.total_mouse_y:+6d}) | Clicks: {self.mouse_clicks} | Keys: {self.key_presses}"
                self.stats_label.config(text=stats_text)
            except:
                pass  # Window might be closing
                
    def run(self):
        """Run the raw input reader with GUI"""
        self.running = True
        
        # Create window
        if not self.create_window():
            return False
            
        # Register devices
        if not self.register_devices():
            print("⚠️  Registration failed, but continuing...")
            
        print("🎯 Starting improved raw input capture...")
        print("   Move mouse over the window or press keys")
        print("   Close window or press Ctrl+C to stop")
        
        # Custom event handler for WM_INPUT
        def wm_input_handler(hwnd, msg, wParam, lParam):
            if msg == WM_INPUT:
                self.process_raw_input(lParam)
                self.update_stats_display()
            return self.user32.DefWindowProcW(hwnd, msg, wParam, lParam)
        
        # Register custom window procedure (this is complex, so we'll use polling instead)
        def check_for_input():
            if self.running and self.root:
                # Update stats display
                self.update_stats_display()
                # Schedule next check
                self.root.after(100, check_for_input)
        
        # Start checking for input
        if self.root:
            check_for_input()
        
            try:
                # Run the Tkinter main loop
                self.root.mainloop()
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
            finally:
                self.stop()
        else:
            print("❌ Failed to create window")
            
    def stop(self):
        """Stop the raw input capture"""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        print("👋 Raw input capture stopped.")

def improved_callback(data):
    """Improved callback function to display raw input data"""
    if data['type'] == 'mouse_move':
        print(f"🖱️  Mouse: Δ({data['delta_x']:+4d}, {data['delta_y']:+4d}) → Total({data['total_x']:6d}, {data['total_y']:6d})")
    elif data['type'] == 'mouse_button':
        print(f"🖱️  Mouse: {data['button']} {data['state']} (Click #{data['click_count']})")
    elif data['type'] == 'mouse_wheel':
        print(f"🖱️  Mouse: Wheel Δ{data['delta']:+4d} → Total{data['total_delta']:+6d}")
    elif data['type'] == 'keyboard':
        key_name = f"VK_{data['vkey']:02X}" if data['vkey'] < 256 else "Unknown"
        print(f"⌨️  Keyboard: {key_name} {data['state']} (Scan: {data['scan_code']}, Press #{data['key_count']})")

def main():
    """Main function to run the improved raw input reader"""
    print("🚀 Improved Raw Input Reader with Window")
    print("   This version creates a proper window for message handling")
    print()
    
    reader = ImprovedRawInputReader()
    reader.set_callback(improved_callback)
    reader.run()

if __name__ == "__main__":
    main()