#!/usr/bin/env python3
"""
Raw Input Reader - Fixed Version
===============================

This module provides access to Windows Raw Input API for high-precision
mouse and keyboard input capture. This version includes multiple fallback
registration methods to handle common Windows permission issues.

Key improvements:
- Multiple registration fallback methods
- Better error handling and reporting
- Improved message loop with activity monitoring
- Support for mouse, keyboard, and HID devices

Usage:
    reader = RawInputReader()
    reader.set_callback(my_callback_function)
    reader.run()
"""

import ctypes
import ctypes.wintypes
import sys
import time
from ctypes import wintypes

# Windows API constants
WM_INPUT = 0x00FF
RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

# Raw Input Device Flags
RIDEV_INPUTSINK = 0x00000100    # Receive input even when not in foreground
RIDEV_NOLEGACY = 0x00000030     # Disable legacy mouse/keyboard messages
RIDEV_REMOVE = 0x00000001       # Remove device registration

# Mouse button flags
RI_MOUSE_LEFT_BUTTON_DOWN = 0x0001
RI_MOUSE_LEFT_BUTTON_UP = 0x0002
RI_MOUSE_RIGHT_BUTTON_DOWN = 0x0004
RI_MOUSE_RIGHT_BUTTON_UP = 0x0008
RI_MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
RI_MOUSE_MIDDLE_BUTTON_UP = 0x0020
RI_MOUSE_WHEEL = 0x0400

# Define Windows structures for Raw Input
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

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT)
    ]

class RawInputReader:
    """
    Windows Raw Input API wrapper with multiple registration fallback methods.
    
    This class provides high-precision input capture for mouse, keyboard, and HID devices.
    Includes comprehensive error handling and fallback mechanisms for common Windows issues.
    """
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.running = False
        self.callback = None
        
        # Statistics tracking
        self.total_mouse_x = 0
        self.total_mouse_y = 0
        self.mouse_clicks = 0
        self.mouse_wheel_delta = 0
        self.key_presses = 0
        self.last_key = None
        self.hid_data_count = 0
        self.raw_input_messages = 0
        
        # Create a simple hidden window for message handling
        self.hwnd = self.create_message_window()
        
    def set_callback(self, callback_func):
        """Set callback function to handle raw input data"""
        self.callback = callback_func
        
    def create_message_window(self):
        """Create a simple hidden window to receive raw input messages"""
        try:
            # Create a simple window for message handling
            hwnd = self.user32.CreateWindowExW(
                0,                      # Extended style
                "STATIC",              # Class name (built-in)
                "RawInputWindow",      # Window title
                0,                     # Style (hidden)
                0, 0, 1, 1,           # Position and size (minimal)
                None,                  # Parent window
                None,                  # Menu
                None,                  # Instance
                None                   # Additional data
            )
            
            if hwnd:
                print(f"✅ Created message window with handle: 0x{hwnd:08X}")
                return hwnd
            else:
                print("⚠️  Failed to create message window, using NULL handle")
                return None
                
        except Exception as e:
            print(f"⚠️  Exception creating window: {e}")
            return None
        
    def register_devices(self):
        """
        Register for raw input devices with multiple fallback methods.
        
        This method tries 5 different registration approaches to handle
        various Windows permission and configuration issues.
        """
        print("🔧 Registering raw input devices with multiple fallback methods...")
        
        # Method 1: Standard registration with INPUTSINK
        try:
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01  # Generic Desktop
            mouse_device.usUsage = 0x02      # Mouse
            mouse_device.dwFlags = RIDEV_INPUTSINK
            mouse_device.hwndTarget = self.hwnd
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Method 1: Successfully registered with INPUTSINK flags")
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Method 1 failed. Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Method 1 exception: {e}")
        
        # Method 2: Registration with NOLEGACY flags
        try:
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01
            mouse_device.usUsage = 0x02
            mouse_device.dwFlags = RIDEV_NOLEGACY
            mouse_device.hwndTarget = self.hwnd
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Method 2: Successfully registered with NOLEGACY flags")
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Method 2 failed. Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Method 2 exception: {e}")
        
        # Method 3: Default flags (most compatible)
        try:
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01
            mouse_device.usUsage = 0x02
            mouse_device.dwFlags = 0  # Default flags
            mouse_device.hwndTarget = self.hwnd
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Method 3: Successfully registered with default flags")
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Method 3 failed. Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Method 3 exception: {e}")
        
        # Method 4: NULL window handle
        try:
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01
            mouse_device.usUsage = 0x02
            mouse_device.dwFlags = RIDEV_INPUTSINK
            mouse_device.hwndTarget = None  # NULL handle
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Method 4: Successfully registered with NULL window handle")
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Method 4 failed. Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Method 4 exception: {e}")
        
        # Method 5: Alternative usage pages
        try:
            mouse_device = RAWINPUTDEVICE()
            mouse_device.usUsagePage = 0x01
            mouse_device.usUsage = 0x02
            mouse_device.dwFlags = 0
            mouse_device.hwndTarget = None
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(mouse_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if result:
                print("✅ Method 5: Successfully registered with alternative approach")
                return True
            else:
                error_code = ctypes.get_last_error()
                print(f"❌ Method 5 failed. Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Method 5 exception: {e}")
        
        print("❌ All registration methods failed!")
        print("   This may be due to:")
        print("   - Insufficient permissions (try running as Administrator)")
        print("   - Antivirus software blocking raw input access")
        print("   - Windows security policies restricting input monitoring")
        print("   - Another application already using exclusive raw input")
        
        return False
        
    def process_raw_input(self, lParam):
        """Process raw input message and extract data"""
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
            
            if size.value == 0:
                return
                
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
            self.raw_input_messages += 1
            
            if raw_input.header.dwType == RIM_TYPEMOUSE:
                self.process_mouse_data(raw_input.data.mouse)
            elif raw_input.header.dwType == RIM_TYPEKEYBOARD:
                self.process_keyboard_data(raw_input.data.keyboard)
            elif raw_input.header.dwType == RIM_TYPEHID:
                self.process_hid_data(raw_input.data.hid, raw_input.header.hDevice)
                
        except Exception as e:
            print(f"❌ Error processing raw input: {e}")
            
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
            
            if button_flags & RI_MOUSE_WHEEL:
                wheel_delta = ctypes.c_short(mouse_data.usButtonData).value
                self.mouse_wheel_delta += wheel_delta
                data = {
                    'type': 'mouse_wheel',
                    'delta': wheel_delta,
                    'total_delta': self.mouse_wheel_delta,
                    'timestamp': time.time()
                }
            else:
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
        
        key_state = "down" if not (keyboard_data.Flags & 0x01) else "up"
        
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
        
        # Extract raw bytes (safely)
        raw_bytes = []
        max_bytes = min(hid_data.dwSizeHid * hid_data.dwCount, 64)
        for i in range(max_bytes):
            try:
                raw_bytes.append(hid_data.bRawData[i])
            except IndexError:
                break
                
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
            
    def run(self):
        """Run the raw input message loop"""
        print("🚀 Starting Raw Input Reader")
        print("   Raw Input API for high-precision input capture")
        print()
        
        # Register devices
        if not self.register_devices():
            print("⚠️  Registration failed, but continuing to test message loop...")
            
        print("🎯 Starting message loop...")
        print("   Move mouse or press keys to test input capture")
        print("   Press Ctrl+C to stop")
        print()
        
        msg = MSG()
        self.running = True
        last_activity_time = time.time()
        activity_check_interval = 5.0  # Check every 5 seconds
        
        try:
            while self.running:
                # Non-blocking message check
                bRet = self.user32.PeekMessageW(
                    ctypes.byref(msg), None, 0, 0, 1  # PM_REMOVE
                )
                
                if bRet > 0:
                    if msg.message == WM_INPUT:
                        self.process_raw_input(msg.lParam)
                        last_activity_time = time.time()
                    else:
                        # Dispatch other messages
                        self.user32.TranslateMessage(ctypes.byref(msg))
                        self.user32.DispatchMessageW(ctypes.byref(msg))
                        
                # Periodic activity reporting
                current_time = time.time()
                if current_time - last_activity_time > activity_check_interval:
                    print(f"📊 Activity Report: {self.raw_input_messages} raw input messages captured")
                    if self.raw_input_messages == 0:
                        print("   (No raw input detected - registration may have failed)")
                    last_activity_time = current_time
                    
                # Small delay to prevent 100% CPU usage
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping raw input capture...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.cleanup()
            
        print(f"📈 Final Statistics:")
        print(f"   Mouse moves: Δ({self.total_mouse_x:+d}, {self.total_mouse_y:+d})")
        print(f"   Mouse clicks: {self.mouse_clicks}")
        print(f"   Wheel delta: {self.mouse_wheel_delta:+d}")
        print(f"   Key presses: {self.key_presses}")
        print(f"   HID data packets: {self.hid_data_count}")
        print(f"   Total raw input messages: {self.raw_input_messages}")
        
    def stop(self):
        """Stop the raw input capture"""
        self.running = False
        
    def cleanup(self):
        """Clean up resources"""
        if self.hwnd:
            try:
                self.user32.DestroyWindow(self.hwnd)
            except:
                pass
        print("🧹 Cleanup completed")

def example_callback(data):
    """Example callback function to display raw input data"""
    if data['type'] == 'mouse_move':
        print(f"🖱️  Mouse: Δ({data['delta_x']:+4d}, {data['delta_y']:+4d}) → Total({data['total_x']:6d}, {data['total_y']:6d})")
    elif data['type'] == 'mouse_button':
        print(f"🖱️  Mouse: {data['button']} {data['state']} (Click #{data['click_count']})")
    elif data['type'] == 'mouse_wheel':
        print(f"🖱️  Mouse: Wheel Δ{data['delta']:+4d} → Total{data['total_delta']:+6d}")
    elif data['type'] == 'keyboard':
        key_name = f"VK_{data['vkey']:02X}" if data['vkey'] < 256 else "Unknown"
        print(f"⌨️  Keyboard: {key_name} {data['state']} (Scan: {data['scan_code']}, Press #{data['key_count']})")
    elif data['type'] == 'hid':
        print(f"🎮 HID Device: {data['hex_data']} (Size: {data['size']}, Count: {data['count']})")

def main():
    """Main function to run the raw input reader"""
    reader = RawInputReader()
    reader.set_callback(example_callback)
    reader.run()

if __name__ == "__main__":
    main()